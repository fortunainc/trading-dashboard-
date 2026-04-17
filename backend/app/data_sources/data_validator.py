"""
Data Validation Module
Validates data quality and integrity from all sources
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from app.models.price_data import TickerPriceData
from app.models.ohlcv import OHLCVSeries, OHLCVCandle

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class ValidationResult:
    """Result of data validation"""
    
    def __init__(
        self,
        is_valid: bool,
        data: Optional[Any] = None,
        errors: List[str] = None,
        warnings: List[str] = None
    ):
        self.is_valid = is_valid
        self.data = data
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        """Add an error"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning"""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "is_valid": self.is_valid,
            "has_errors": len(self.errors) > 0,
            "has_warnings": len(self.warnings) > 0,
            "errors": self.errors,
            "warnings": self.warnings
        }


class DataValidator:
    """Validates data quality and integrity"""
    
    # Validation thresholds
    PRICE_STALENESS_THRESHOLD_MINUTES = 60  # Data older than this is stale
    PRICE_REASONABLE_MIN = 0.01  # Minimum reasonable price
    PRICE_REASONABLE_MAX = 100000  # Maximum reasonable price
    VOLUME_MIN = 100  # Minimum reasonable volume
    PRICE_REASONABLE_CHANGE_PERCENT = 50  # Max reasonable daily change
    
    # OHLCV validation
    OHLCV_MIN_CANDLES = 20  # Minimum candles for analysis
    OHLCV_MISSING_DATA_THRESHOLD = 0.2  # Max 20% missing data
    
    def __init__(self, enable_strict_mode: bool = True):
        self.strict_mode = enable_strict_mode
    
    def validate_price_data(self, price_data: TickerPriceData) -> ValidationResult:
        """
        Validate price data
        
        Args:
            price_data: TickerPriceData to validate
        
        Returns:
            ValidationResult with validation results
        """
        result = ValidationResult(is_valid=True, data=price_data)
        
        # Required fields
        if not price_data.symbol:
            result.add_error("Symbol is required")
        
        if not price_data.official_close or not price_data.official_close.price:
            result.add_error("Official close price is required")
        
        # Validate official close
        if price_data.official_close:
            self._validate_price_point(
                price_data.official_close.price,
                price_data.official_close.change,
                price_data.official_close.timestamp,
                result,
                "official_close"
            )
        
        # Validate after-hours data if present
        if price_data.after_hours and price_data.after_hours.price > 0:
            self._validate_price_point(
                price_data.after_hours.price,
                price_data.after_hours.change,
                price_data.after_hours.timestamp,
                result,
                "after_hours"
            )
        
        # Validate premarket data if present
        if price_data.premarket and price_data.premarket.price > 0:
            self._validate_price_point(
                price_data.premarket.price,
                price_data.premarket.change,
                price_data.premarket.timestamp,
                result,
                "premarket"
            )
        
        # Validate live data if present
        if price_data.live and price_data.live.price > 0:
            self._validate_live_price(
                price_data.live,
                result
            )
        
        # Validate data quality
        self._validate_data_quality(price_data, result)
        
        return result
    
    def _validate_price_point(
        self,
        price: float,
        change: float,
        timestamp: Optional[datetime],
        result: ValidationResult,
        field_name: str
    ):
        """Validate a single price point"""
        # Check price range
        if not (self.PRICE_REASONABLE_MIN <= price <= self.PRICE_REASONABLE_MAX):
            result.add_error(
                f"{field_name}: Price {price} is outside reasonable range "
                f"[{self.PRICE_REASONABLE_MIN}, {self.PRICE_REASONABLE_MAX}]"
            )
        
        # Check change reasonableness
        if abs(change / price * 100) > self.PRICE_REASONABLE_CHANGE_PERCENT if price > 0 else True:
            result.add_warning(
                f"{field_name}: Change {change} implies "
                f"{abs(change / price * 100):.2f}% which is unusual"
            )
        
        # Check timestamp freshness
        if timestamp:
            age_minutes = (datetime.now() - timestamp).total_seconds() / 60
            if field_name == "official_close":
                # Official close should be from previous day
                if datetime.now().date() - timestamp.date() > timedelta(days=2):
                    result.add_warning(f"{field_name}: Data is stale (age: {age_minutes:.0f} minutes)")
            else:
                # Other prices should be recent
                if age_minutes > self.PRICE_STALENESS_THRESHOLD_MINUTES:
                    result.add_warning(f"{field_name}: Data is stale (age: {age_minutes:.0f} minutes)")
    
    def _validate_live_price(self, live_data: Any, result: ValidationResult):
        """Validate live price data"""
        # Check bid/ask spread
        if live_data.bid > 0 and live_data.ask > 0:
            spread_percent = (live_data.ask - live_data.bid) / live_data.bid * 100
            if spread_percent > 20:  # More than 20% spread is suspicious
                result.add_warning(
                    f"live: Wide bid-ask spread - {spread_percent:.2f}% "
                    f"(bid: {live_data.bid}, ask: {live_data.ask})"
                )
        
        # Check volume
        if live_data.volume < self.VOLUME_MIN:
            result.add_warning(f"live: Low volume - {live_data.volume}")
        
        # Check OHLC consistency
        if live_data.high < live_data.low:
            result.add_error(f"live: High {live_data.high} is less than low {live_data.low}")
        
        if not (live_data.low <= live_data.close <= live_data.high):
            result.add_error(
                f"live: Close {live_data.close} is outside high/low range "
                f"[{live_data.low}, {live_data.high}]"
            )
    
    def _validate_data_quality(self, price_data: TickerPriceData, result: ValidationResult):
        """Validate overall data quality"""
        quality = price_data.data_quality.lower()
        
        if quality == "low":
            result.add_warning(f"Data quality is marked as 'low'")
        elif quality == "unknown":
            result.add_warning(f"Data quality is unknown")
        
        # Check for complete price separation
        if not price_data.official_close:
            result.add_error("Missing official close data - critical requirement")
        
        # Warn if after-hours is expected but missing
        if price_data.after_hours and price_data.after_hours.price == 0:
            result.add_warning("After-hours price is expected but not available")
    
    def validate_ohlcv(self, ohlcv: OHLCVSeries) -> ValidationResult:
        """
        Validate OHLCV data
        
        Args:
            ohlcv: OHLCVSeries to validate
        
        Returns:
            ValidationResult with validation results
        """
        result = ValidationResult(is_valid=True, data=ohlcv)
        
        # Required fields
        if not ohlcv.symbol:
            result.add_error("Symbol is required")
        
        if not ohlcv.timeframe:
            result.add_error("Timeframe is required")
        
        # Check minimum candle count
        if len(ohlcv.candles) < self.OHLCV_MIN_CANDLES:
            result.add_error(
                f"Insufficient candles: {len(ohlcv.candles)} "
                f"(minimum required: {self.OHLCV_MIN_CANDLES})"
            )
        
        # Validate each candle
        invalid_candles = 0
        candles_with_zero_volume = 0
        candles_with_inconsistent_ohlc = 0
        
        for i, candle in enumerate(ohlcv.candles):
            # Check OHLC consistency
            if not candle.valid():
                candle_errors = candle.get_validation_errors()
                for error in candle_errors:
                    result.add_error(f"Candle {i}: {error}")
                invalid_candles += 1
            
            # Check for zero volume
            if candle.volume == 0:
                candles_with_zero_volume += 1
            
            # Check OHLC ordering
            if not (candle.low <= candle.close <= candle.high and
                    candle.low <= candle.open <= candle.high):
                candles_with_inconsistent_ohlc += 1
        
        # Warn about data quality issues
        if candles_with_zero_volume > 0:
            percent = candles_with_zero_volume / len(ohlcv.candles) * 100
            result.add_warning(
                f"{candles_with_zero_volume}/{len(ohlcv.candles)} candles "
                f"({percent:.1f}%) have zero volume"
            )
        
        if candles_with_inconsistent_ohlc > 0:
            percent = candles_with_inconsistent_ohlc / len(ohlcv.candles) * 100
            result.add_warning(
                f"{candles_with_inconsistent_ohlc}/{len(ohlcv.candles)} candles "
                f"({percent:.1f}%) have inconsistent OHLC data"
            )
        
        # Reject if too many invalid candles
        invalid_percent = invalid_candles / len(ohlcv.candles)
        if invalid_percent > self.OHLCV_MISSING_DATA_THRESHOLD:
            result.add_error(
                f"Too many invalid candles: {percent:.1f}% "
                f"(threshold: {self.OHLCV_MISSING_DATA_THRESHOLD * 100}%)"
            )
            result.is_valid = False
    
    def validate_time_series_consistency(
        self,
        price_data: TickerPriceData,
        ohlcv: OHLCVSeries
    ) -> ValidationResult:
        """
        Validate consistency between price data and OHLCV
        
        Args:
            price_data: TickerPriceData
            ohlcv: OHLCVSeries
        
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        if not price_data.official_close or ohlcv.candles.length == 0:
            return result
        
        # Get most recent candle close
        recent_candle = ohlcv.candles[0]
        
        # Compare with official close (should be close if timeframe is daily)
        if ohlcv.timeframe == "1d":
            price_diff_pct = abs(price_data.official_close.price - recent_candle.close) / recent_candle.close * 100
            if price_diff_pct > 5:  # More than 5% difference is suspicious
                result.add_warning(
                    f"Price data inconsistency: "
                    f"official_close ({price_data.official_close.price}) vs recent candle close ({recent_candle.close}) "
                    f"diff: {price_diff_pct:.2f}%"
                )
        
        return result
    
    def validate_required_fields(
        self,
        data: Dict[str, Any],
        required_fields: List[str],
        data_type: str
    ) -> ValidationResult:
        """
        Validate that required fields are present
        
        Args:
            data: Data dictionary
            required_fields: List of required field names
            data_type: Type of data being validated
        
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        for field in required_fields:
            if field not in data or data[field] is None:
                result.add_error(f"{data_type}: Missing required field '{field}'")
                result.is_valid = False
        
        return result
    
    def validate_numeric_range(
        self,
        value: float,
        field_name: str,
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        allow_zero: bool = True
    ) -> ValidationResult:
        """
        Validate numeric value is within range
        
        Args:
            value: Numeric value to validate
            field_name: Name of the field
            min_val: Minimum allowed value (None = no minimum)
            max_val: Maximum allowed value (None = no maximum)
            allow_zero: Whether zero is allowed
        
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        # Check numeric type
        if not isinstance(value, (int, float)):
            result.add_error(f"{field_name}: Must be numeric, got {type(value)}")
            result.is_valid = False
            return result
        
        # Check zero
        if not allow_zero and value == 0:
            result.add_error(f"{field_name}: Zero is not allowed")
            result.is_valid = False
        
        # Check minimum
        if min_val is not None and value < min_val:
            result.add_error(
                f"{field_name}: Value {value} is below minimum {min_val}"
            )
            result.is_valid = False
        
        # Check maximum
        if max_val is not None and value > max_val:
            result.add_error(
                f"{field_name}: Value {value} is above maximum {max_val}"
            )
            result.is_valid = False
        
        return result
    
    def validate_timestamp_freshness(
        self,
        timestamp: datetime,
        field_name: str,
        max_age_minutes: int
    ) -> ValidationResult:
        """
        Validate timestamp is fresh enough
        
        Args:
            timestamp: Timestamp to validate
            field_name: Name of the field
            max_age_minutes: Maximum age in minutes
        
        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)
        
        if not timestamp:
            result.add_error(f"{field_name}: Timestamp is required")
            result.is_valid = False
            return result
        
        age_minutes = (datetime.now() - timestamp).total_seconds() / 60
        
        if age_minutes > max_age_minutes:
            result.add_warning(
                f"{field_name}: Timestamp is stale ({age_minutes:.0f} minutes old, "
                f"max allowed: {max_age_minutes} minutes)"
            )
        
        return result
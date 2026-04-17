"""
Main API Router
"""
from fastapi import APIRouter
from .price_routes import router as price_router
from .analysis_routes import router as analysis_router

router = APIRouter()

# Include sub-routers
router.include_router(price_router, prefix="/price", tags=["Price Data"])
router.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])

# Additional routers will be added as they are implemented
# router.include_router(contract_router, prefix="/contracts", tags=["Contracts"])
# router.include_router(journal_router, prefix="/journal", tags=["Journal"])
# router.include_router(status_router, prefix="/status", tags=["Status"])
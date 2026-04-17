# Vercel Deployment Guide

## 🚀 Deploying Trading Dashboard to Vercel

This guide will help you deploy the Trading Dashboard to Vercel.

---

## 📋 Prerequisites

- ✅ GitHub repository created
- ✅ Code pushed to main branch
- ✅ Vercel account (free at vercel.com)
- ✅ Tradier API key (for real data)

---

## 🎯 Deployment Strategy

### Part 1: Deploy Frontend (Vercel Native)
Vercel excels at deploying Next.js applications.

### Part 2: Deploy Backend (Vercel Serverless)
Use Vercel's serverless functions for the Python backend.

### Part 3: External Services
- Database: Use Vercel Postgres (or Neon/Supabase)
- Redis: Use Upstash Redis (free tier available)

---

## 🔄 Step-by-Step Deployment

### Step 1: Import Project to Vercel

1. Go to: https://vercel.com/new
2. Click "Continue with GitHub"
3. Authorize Vercel to access your GitHub
4. Select `trading-dashboard-` repository
5. Click "Import"

---

### Step 2: Configure Frontend Deployment

**Framework Preset**: Next.js
- Vercel should auto-detect Next.js

**Root Directory**: `./frontend`
- Set this to deploy only the frontend folder

**Build Command**: 
```
npm run build
```

**Output Directory**:
```
.next
```

**Install Command**:
```
npm install
```

---

### Step 3: Configure Environment Variables

Go to **Environment Variables** section and add:

**Frontend Variables:**
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.vercel.app
NODE_ENV=production
```

**Backend Variables** (for serverless functions later):
```bash
TRADIER_API_KEY=crLRfVuLACApmxY0sg5dKvpfu8t9
DATABASE_URL=your_postgres_url
REDIS_URL=your_redis_url
```

⚠️ **Important**: Add all variables with appropriate environments (Production, Preview, Development)

---

### Step 4: Deploy Frontend

1. Click **Deploy**
2. Wait for deployment (1-2 minutes)
3. Note the deployment URL: `https://your-project.vercel.app`

**Test the frontend:**
```bash
curl https://your-project.vercel.app
```

---

## 🐍 Part 5: Deploy Backend (Serverless Options)

### Option A: Vercel Serverless (Recommended for Simple APIs)

1. Create `vercel.json` in root directory (I'll provide this)
2. Create `api` directory structure for serverless functions
3. Deploy both frontend and backend together

### Option B: Separate Backend Deployment

1. Create separate Vercel project for backend
2. Use serverless functions
3. Connect to same database/redis

### Option C: Render/Railway for Backend (Easiest)

1. Deploy backend to Render.com or Railway.app
2. Update `NEXT_PUBLIC_API_URL` in Vercel
3. Vercel frontend calls external backend API

**Recommendation**: **Option C** - Keep backend separate, simpler to manage

---

## 🗄️ Part 6: Set Up Database

### Option A: Vercel Postgres (Easiest)

1. In Vercel dashboard → Storage → Create Database
2. Choose "Postgres"
3. Create database
4. Get connection URL
5. Add to environment variables: `DATABASE_URL`

### Option B: Neon (Free PostgreSQL Alternative)

1. Go to: https://neon.tech
2. Create free account
3. Create database
4. Get connection URL
5. Add to environment variables

### Option C: Supabase (Free PostgreSQL)

1. Go to: https://supabase.com
2. Create free project
3. Get database connection URL
4. Add to environment variables

---

## 🔴 Part 7: Set Up Redis

### Option A: Upstash Redis (Recommended - Free Tier)

1. Go to: https://upstash.com
2. Create free account
3. Create Redis database
4. Get connection URL: `redis://default:password@host:port`
5. Add to environment variables: `REDIS_URL`

**Free Tier Limits:**
- 10,000 commands/day
- 256MB storage
- Good for development

### Option B: Redis Cloud (More Resources)

1. Go to: https://redis.com/try-free/
2. Create free account
3. Create database
4. Get connection URL

---

## 📝 Part 8: Configuration Files

### For Vercel Deployment

Create these files in the repository:

**`vercel.json`** (in root):
```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/.next",
  "framework": "nextjs",
  "installCommand": "cd frontend && npm install",
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url"
  }
}
```

**`.vercelignore`**:
```
backend/node_modules
backend/.env
backend/__pycache__
backend/*.pyc
.DS_Store
```

**`backend/requirements.txt`** - Already exists, verified

---

## 🧪 Part 9: Testing Deployment

### Test Frontend
```bash
curl https://your-project.vercel.app
```

### Test Backend (if separate)
```bash
curl https://your-backend.vercel.app/health
```

### Test Data Fetching
```bash
curl https://your-backend.vercel.app/api/price/NVDA
```

---

## 🔗 Part 10: Connecting Frontend to Backend

If using separate deployment:

1. Update Vercel environment variable:
   ```bash
   NEXT_PUBLIC_API_URL=https://your-backend-url.vercel.app
   ```

2. Redeploy frontend (automatic or manual)

3. Verify connection in browser console

---

## 📊 Part 11: Monitoring

### Vercel Dashboard

- **Overview**: Deployments status
- **Analytics**: Request counts, response times
- **Logs**: Real-time logs
- **Functions**: Serverless function performance

### Database Monitoring

- **Vercel Postgres**: Built-in dashboard
- **Neon**: Dashboard at console.neon.tech
- **Supabase**: Dashboard at supabase.com

### Redis Monitoring

- **Upstash**: Dashboard at console.upstash.com
- **Redis Cloud**: Dashboard at redis.com

---

## 💰 Cost Estimates

### Vercel (Frontend)
- **Free Tier**: 100GB bandwidth, unlimited deployments
- **Hobby**: $20/month (more bandwidth)
- **Recommended**: Start with FREE tier

### Backend
- **Vercel Serverless**: Pay per execution (cheaper for low traffic)
- **Render/Railway**: Free tier available
- **Estimated**: $0-20/month depending on traffic

### Database
- **Vercel Postgres**: Free tier available
- **Neon**: Free tier available
- **Supabase**: Free tier available
- **Recommended**: Start with FREE tier

### Redis
- **Upstash**: Free tier (10K commands/day)
- **Redis Cloud**: Free tier available
- **Estimated**: $0-5/month

### **Total Monthly Cost**: $0-45/month

---

## 🚀 Deployment Checklist

- [ ] Create Vercel account
- [ ] Import GitHub repository
- [ ] Configure Next.js build settings
- [ ] Add environment variables
- [ ] Deploy frontend
- [ ] Choose backend deployment strategy
- [ ] Set up database
- [ ] Set up Redis
- [ ] Test all endpoints
- [ ] Configure domain (optional)
- [ ] Set up monitoring

---

## 🐛 Common Issues

### Issue: "Could not find module"

**Solution**: Make sure `frontend` is set as root directory in Vercel settings.

### Issue: Environment variables not accessible

**Solution**: 
- Redeploy after adding environment variables
- Check variable names match exactly (case-sensitive)
- `NEXT_PUBLIC_*` variables are accessible in browser

### Issue: Backend API calls failing

**Solution**:
- Check `NEXT_PUBLIC_API_URL` is correct
- Verify backend is running
- Check CORS settings in backend
- Check Vercel logs

### Issue: Database connection failed

**Solution**:
- Verify DATABASE_URL format
- Check database is running
- Test connection string in local environment
- Check Vercel logs for error messages

---

## 📚 Additional Resources

- Vercel Docs: https://vercel.com/docs
- Next.js on Vercel: https://vercel.com/docs/frameworks/nextjs
- Vercel Postgres: https://vercel.com/docs/storage/vercel-postgres
- Upstash Redis: https://docs.upstash.com

---

## 🎯 Next Steps After Deployment

1. **Test the dashboard** at your Vercel URL
2. **Verify data fetching** with Tradier API
3. **Monitor performance** in Vercel dashboard
4. **Set up alerts** for errors
5. **Configure custom domain** (optional)
6. **Scale up tiers** if needed

---

## 💡 Pro Tips

1. **Use Preview Deployments**: Automatic deploys for every branch/PR
2. **Environment-Specific Variables**: Set different vars for dev/prod
3. **Automatic Rollbacks**: Vercel can auto-rollback on errors
4. **Edge Functions**: Use for API routes that need to run closer to users
5. **Analytics**: Enable Vercel Analytics for traffic insights

---

**Ready to deploy?** Let me know when you've completed the Vercel setup and I can help with any issues!
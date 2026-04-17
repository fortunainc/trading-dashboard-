# 🚀 Vercel Deployment - Quick Start

## Step 1: Import to Vercel (5 minutes)

1. Go to: **https://vercel.com/new**
2. Click **"Continue with GitHub"**
3. Select repository: **trading-dashboard-**
4. Click **"Import"**

---

## Step 2: Configure Project (2 minutes)

**Framework Preset**: Next.js ✅

**Root Directory**: `frontend` ⚠️ IMPORTANT!

**Build Command**: `npm run build`

**Output Directory**: `.next`

---

## Step 3: Add Environment Variables (3 minutes)

In Vercel → Settings → Environment Variables, add:

```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.vercel.app
NODE_ENV=production
```

**Add to**: All environments (Production, Preview, Development)

⚠️ Note: Backend URL will be set after backend deployment

---

## Step 4: Deploy Frontend (2 minutes)

1. Click **"Deploy"**
2. Wait 1-2 minutes
3. Note your URL: `https://your-project-name.vercel.app`

---

## Step 5: Deploy Backend (Choose One)

### Option A: Render.com (Easiest - Recommended)

1. Go to: **https://dashboard.render.com**
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repository
4. Runtime: **Python 3**
5. Build Command: `cd backend && pip install -r requirements.txt`
6. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Environment Variables:
   ```bash
   TRADIER_API_KEY=crLRfVuLACApmxY0sg5dKvpfu8t9
   DATABASE_URL=your_db_url
   REDIS_URL=your_redis_url
   ```
8. Click **"Deploy Web Service"**
9. Note your backend URL
10. Update `NEXT_PUBLIC_API_URL` in Vercel
11. Redeploy Vercel frontend

### Option B: Railway (Simple Cloud)

1. Go to: **https://railway.app**
2. Click **"New Project"**
3. Deploy from GitHub repo
4. Add environment variables
5. Note backend URL and update Vercel

---

## Step 6: Set Up Database (5 minutes)

### Vercel Postgres (Easiest)

1. In Vercel dashboard → **Storage** → **Create Database**
2. Click **"Postgres"**
3. Click **"Create"**
4. Copy the **DATABASE_URL**
5. Add to backend environment variables:
   - Vercel (if using serverless)
   - Render/Railway (if using external backend)

### OR Use Neon (Free Alternative)

1. Go to: **https://neon.tech**
2. Create free account → Create database
3. Copy connection string
4. Add to environment variables

---

## Step 7: Set Up Redis (3 minutes)

### Upstash Redis (Recommended - Free)

1. Go to: **https://upstash.com**
2. Create free account → **"Create Redis Database"**
3. Get connection URL: `redis://default:password@host:port`
4. Add to backend environment variables as `REDIS_URL`

---

## Step 8: Test Deployment (2 minutes)

### Test Frontend:
```bash
curl https://your-project.vercel.app
```

### Test Backend:
```bash
curl https://your-backend-url.onrender.com/health
```

### Test API:
```bash
curl https://your-backend-url.onrender.com/api/price/NVDA
```

---

## 📊 Total Time: ~22 minutes

---

## 🎯 Recommended Setup

**Frontend**: Vercel (Free tier)
**Backend**: Render (Free tier)
**Database**: Vercel Postgres or Neon (Free)
**Redis**: Upstash (Free)

**Total Cost**: $0/month (free tiers)

---

## ✅ Deployment Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Render/Railway
- [ ] Database created and connected
- [ ] Redis created and connected
- [ ] Environment variables configured
- [ ] `NEXT_PUBLIC_API_URL` updated
- [ ] All endpoints tested
- [ ] Dashboard accessible in browser

---

## 🐛 Troubleshooting

### Frontend Error: "Could not find module"
→ Make sure Root Directory is set to `frontend`

### Backend Error: "Module not found"
→ Check requirements.txt includes all dependencies

### API Calls Failing
→ Verify `NEXT_PUBLIC_API_URL` is correct
→ Check CORS settings in backend

### Database Connection Failed
→ Verify DATABASE_URL format
→ Check database is running

---

## 📚 Full Documentation

- **VERCEL_DEPLOYMENT.md** - Complete deployment guide
- **DEPLOYMENT.md** - General deployment options
- **README.md** - Project overview
- **QUICK_START.md** - Local development

---

## 🎉 Done!

Your trading dashboard is now live! 

**Access at**: `https://your-project.vercel.app`

**Backend API**: `https://your-backend-url.onrender.com`

---

**Need help?** Check logs in Vercel and Render dashboards!
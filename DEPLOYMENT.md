# Cloud Deployment Guide — Vortex Search Engine

This repository is fully configured for cloud deployment across leading PaaS platforms:
- **Backend**: [Render](https://render.com) or [Railway](https://railway.app) (Docker + Persistent Volume for SQLite & ChromaDB)
- **Frontend**: [Vercel](https://vercel.com) or [Netlify](https://netlify.com) (Static React + Vite SPA)

---

## Step 1: Push Code to GitHub

Create a new repository on GitHub (e.g. `vortex-search-engine`) and link this local Git repository:

```powershell
git remote add origin https://github.com/<your-username>/vortex-search-engine.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Backend

### Option A: Render (Recommended with `render.yaml`)

We already added `render.yaml` to the repository, which sets up the Docker service with a persistent 5GB volume for the SQLite database and ChromaDB vector store.

1. Go to [dashboard.render.com](https://dashboard.render.com) and click **"New" &rarr; "Blueprint"**.
2. Connect your GitHub repository `vortex-search-engine`.
3. Render will detect `render.yaml` and configure:
   - **Service Name**: `vortex-search-backend`
   - **Dockerfile**: `backend/Dockerfile`
   - **Environment Variables**:
     - `DATA_DIR`: `/app/data`
     - `ALLOWED_ORIGINS`: `*`
     - `EMBEDDING_BATCH_SIZE`: `16`
   - **Persistent Disk**: 5 GB mounted at `/app/data`
4. Click **Apply**. Once deployed, Render will provide your public backend URL, e.g.:
   `https://vortex-search-backend.onrender.com`

---

### Option B: Railway (Alternative with `railway.json`)

1. Go to [railway.app](https://railway.app) and click **"New Project" &rarr; "Deploy from GitHub repo"**.
2. Select your repository.
3. In service **Settings**:
   - **Build**: Uses `backend/Dockerfile` automatically (configured via `railway.json`).
   - Add a **Volume**: Mount Path `/app/data`.
   - Add Environment Variables:
     - `DATA_DIR`: `/app/data`
     - `ALLOWED_ORIGINS`: `*`
     - `EMBEDDING_BATCH_SIZE`: `16`
4. In **Networking**, click **Generate Domain** to get your backend URL.

---

## Step 3: Deploy Frontend (Vercel)

1. Go to [vercel.com](https://vercel.com) and click **"Add New Project"**.
2. Import your GitHub repository.
3. In **Project Settings**:
   - **Root Directory**: Select `frontend`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. In **Environment Variables**, add:
   - `VITE_API_BASE_URL`: `https://vortex-search-backend.onrender.com` *(use your actual backend URL from Step 2)*
5. Click **Deploy**.
6. Vercel will build and assign you a live production URL, e.g. `https://vortex-search.vercel.app`.

---

## Step 4: Seed & Crawl More Pages Live in Production

Once both services are live:
1. Open your live frontend URL.
2. Click **"Crawl URLs"** on the live UI.
3. Paste batches of target domains or topics to expand your live search index.
4. All crawled documents and vector embeddings persist permanently in `/app/data` on the mounted disk volume!

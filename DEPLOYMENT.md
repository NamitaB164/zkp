# Vercel Deployment Guide: ZK-Vault

This project is now optimized for **Vercel** as a serverless Flask application. Follow these instructions to go live.

## Quick Start (Vercel CLI)

If you have the [Vercel CLI](https://vercel.com/download) installed:

1. Open your terminal in the project root.
2. Run `vercel`.
3. Follow the prompts (use default settings for framework: *Other*).
4. Once finished, run `vercel --prod` to deploy to production.

## Git Deployment (Recommended)

1. **Initialize Git** (if not already):
   ```powershell
   git init
   git add .
   git commit -m "Initial commit for ZKP"
   ```
2. **Push to GitHub**: Create a repository and push your code.
3. **Connect to Vercel**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard).
   - Click **Add New...** > **Project**.
   - Import your GitHub repository.
   - Vercel will automatically detect the `vercel.json` and deploy.

---

## Technical Details

- **Entry Point**: `api/index.py` (imports `app.py`).
- **Config**: `vercel.json` rewrites all traffic to the serverless function.
- **Static Files**: Flask serves the `frontend/` directory directly.

## Local Verification

Before deploying, you can verify everything works locally in the new structure:

```powershell
python app.py
```
Visit `http://localhost:5000` to ensure all ZKP modules (Login, Finance, Vote, Rollup) load correctly.

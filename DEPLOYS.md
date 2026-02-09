# Deployment Guide: Render Backend & Vercel Frontend

This guide explains how to deploy your FastAPI backend to Render and connect it with your Next.js frontend on Vercel.

## Step 1: Push Code to GitHub

1. Ensure all changes are committed:
   ```bash
   git add .
   git commit -m "Add Render deployment config and initialize Citizen platform"
   git push origin main
   ```

## Step 2: Deploy Backend to Render

1. Log in to [Render.com](https://render.com).
2. Click **New +** and select **Blueprint**.
3. Connect your GitHub repository.
4. Render will automatically detect the `render.yaml` file.
5. Review the plan and click **Apply**.
6. **Important**: You must provide the following environment variables in the Render dashboard (if not already set in Blueprint):
   - `DATABASE_URL`: Your PostgreSQL connection string.
   - `BETTER_AUTH_SECRET`: A secure 32+ character key.
   - `CORS_ORIGINS`: Your Vercel frontend URL (e.g., `https://todo-frontend.vercel.app`).
   - `JWT_ALGORITHM`: `HS256`.

## Step 3: Connect Frontend to Render

1. Go to your **Vercel Dashboard**.
2. Select your `todo-frontend` project.
3. Go to **Settings** -> **Environment Variables**.
4. Create/Update `NEXT_PUBLIC_API_URL` (or equivalent used in your code) to your new Render Backend URL (e.g., `https://todo-backend.onrender.com`).
5. Trigger a new deployment on Vercel to pick up the change.

## Project Structure (Initialized)

You now have the foundation for the **Citizen Reporting & Transparency Platform**:
- `/citizen`: Reporting portal for users.
- `/admin`: Management hub for city officials.
- `/reporting`: Public transparency dashboard.
- `/backend/src/api/v1/citizen.py`: Backend API for reports.

---

**Note**: Once the Render URL is ready, update the `CORS_ORIGINS` in Render to match your Vercel URL exactly.

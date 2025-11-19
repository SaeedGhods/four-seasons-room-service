# Deployment Guide - GitHub to Render

This guide will help you deploy your Four Seasons Room Service Agent to Render using GitHub.

## Prerequisites

1. GitHub account
2. Render account (free tier available at https://render.com)
3. Your Twilio credentials (already configured)

## Step 1: Push to GitHub

1. **Initialize Git repository** (if not already done):
   ```bash
   cd "/Users/saeedghods/Phone Agent"
   git init
   git add .
   git commit -m "Initial commit: Four Seasons Room Service Agent"
   ```

2. **Create a GitHub repository**:
   - Go to https://github.com/new
   - Create a new repository (e.g., "four-seasons-room-service")
   - Don't initialize with README

3. **Push your code**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/four-seasons-room-service.git
   git branch -M main
   git push -u origin main
   ```

## Step 2: Deploy to Render

1. **Sign up/Login to Render**:
   - Go to https://render.com
   - Sign up or log in (you can use GitHub to sign in)

2. **Create a New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository: `four-seasons-room-service`

3. **Configure the Service**:
   - **Name:** `four-seasons-room-service` (or your preferred name)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

4. **Set Environment Variables**:
   Click "Advanced" and add these environment variables:
   ```
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   OPENAI_API_KEY=your_openai_api_key_here
   PORT=5000
   ```

5. **Deploy**:
   - Click "Create Web Service"
   - Render will build and deploy your app
   - Wait for deployment to complete (usually 2-3 minutes)

6. **Get Your Public URL**:
   - Once deployed, you'll get a URL like: `https://four-seasons-room-service.onrender.com`
   - Copy this URL - you'll need it for Twilio configuration

## Step 3: Configure Twilio Webhooks

1. **Go to Twilio Console**:
   - Visit: https://console.twilio.com/
   - Navigate to: Phone Numbers → Manage → Active Numbers

2. **Configure Your Phone Number**:
   - Click on your phone number
   - Scroll to "Voice & Fax" section
   - Under "A CALL COMES IN", set:
     - **Webhook URL:** `https://YOUR_RENDER_URL.onrender.com/voice`
       (Replace YOUR_RENDER_URL with your actual Render URL)
     - **HTTP Method:** POST
   - Under "CALL STATUS CHANGES", set:
     - **Status Callback URL:** `https://YOUR_RENDER_URL.onrender.com/status`
     - **HTTP Method:** POST
   - Click "Save"

## Step 4: Test Your Deployment

1. **Test the Health Endpoint**:
   - Visit: `https://YOUR_RENDER_URL.onrender.com/`
   - You should see: "Four Seasons Room Service Agent is running!"

2. **Make a Test Call**:
   - Call your Twilio phone number
   - The agent should answer and help with menu inquiries!

## Automatic Deployments

Render automatically deploys when you push to the `main` branch on GitHub. Just:
1. Make changes to your code
2. Commit and push to GitHub
3. Render will automatically rebuild and redeploy

## Important Notes

- **Free Tier Limitations**: Render's free tier spins down after 15 minutes of inactivity. First request after spin-down may take 30-60 seconds.
- **Environment Variables**: Never commit your `.env` file to GitHub. Use Render's environment variables instead.
- **OpenAI API Key**: Add your OpenAI API key in Render's environment variables for better conversation quality.
- **Custom Domain**: You can add a custom domain in Render settings if needed.

## Troubleshooting

- **Service won't start**: Check Render logs for errors
- **Webhooks not working**: Verify your Render URL is correct in Twilio settings
- **Slow response**: First request after spin-down is normal on free tier

## Alternative: Railway Deployment

If you prefer Railway instead of Render:

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables
6. Railway will auto-deploy

Your Twilio credentials are already configured in the codebase!


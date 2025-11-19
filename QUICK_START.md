# Quick Start Guide

## Your Twilio Configuration

✅ **Configure in Render Environment Variables:**
- Account SID: (add your Twilio Account SID)
- Phone Number: (add your Twilio phone number)
- Auth Token: (add your Twilio Auth Token)

## Deploy in 3 Steps

### Step 1: Push to GitHub

```bash
cd "/Users/saeedghods/Phone Agent"
./setup_github.sh

# Then create a repo on GitHub and push:
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Render

1. Go to https://render.com and sign up (free tier available)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Add Environment Variables:
   ```
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   OPENAI_API_KEY=your_key_here (optional)
   PORT=5000
   ```
6. Click "Create Web Service"
7. Wait for deployment (2-3 minutes)
8. Copy your Render URL (e.g., `https://your-app.onrender.com`)

### Step 3: Configure Twilio Webhooks

1. Go to https://console.twilio.com/
2. Phone Numbers → Manage → Active Numbers
3. Click on your Twilio phone number
4. Under "Voice & Fax" → "A CALL COMES IN":
   - URL: `https://YOUR_RENDER_URL.onrender.com/voice`
   - Method: POST
5. Under "CALL STATUS CHANGES":
   - URL: `https://YOUR_RENDER_URL.onrender.com/status`
   - Method: POST
6. Save

### Step 4: Test!

Call your Twilio phone number and the agent will answer! 🎉

## Need Help?

See `DEPLOYMENT.md` for detailed instructions.


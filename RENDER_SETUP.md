# Render Setup Instructions

## Steps 4-7: Complete Your Render Deployment

### Step 4: Configure Your Render Service

In your Render dashboard, configure these settings:

**Basic Settings:**
- **Name:** `four-seasons-room-service` (or your preferred name)
- **Region:** Choose the closest region to you
- **Branch:** `main`
- **Root Directory:** (leave empty)

**Build & Deploy:**
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

### Step 5: Add Environment Variables

Click "Advanced" → "Environment Variables" and add:

```
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
OPENAI_API_KEY=your_openai_api_key_here (optional)
PORT=5000
```

**Important:** Replace `your_openai_api_key_here` with your actual OpenAI API key if you have one (optional but recommended for better conversations).

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Wait 2-3 minutes for the build and deployment to complete
3. Once deployed, you'll see a URL like: `https://four-seasons-room-service.onrender.com`
4. **Copy this URL** - you'll need it for Step 7

### Step 7: Configure Twilio Webhooks

You have two options:

#### Option A: Use the Automated Script (Recommended)

1. Make sure your Render URL is ready (from Step 6)
2. Run this command:
   ```bash
   cd "/Users/saeedghods/Phone Agent"
   source venv/bin/activate
   python configure_twilio.py https://YOUR_RENDER_URL.onrender.com
   ```
   (Replace `YOUR_RENDER_URL` with your actual Render URL)

#### Option B: Manual Configuration

1. Go to: https://console.twilio.com/
2. Navigate to: **Phone Numbers** → **Manage** → **Active Numbers**
3. Click on your Twilio phone number
4. Scroll to **"Voice & Fax"** section
5. Under **"A CALL COMES IN"**:
   - **Webhook URL:** `https://YOUR_RENDER_URL.onrender.com/voice`
   - **HTTP Method:** `POST`
6. Under **"CALL STATUS CHANGES"**:
   - **Status Callback URL:** `https://YOUR_RENDER_URL.onrender.com/status`
   - **HTTP Method:** `POST`
7. Click **"Save"**

### Step 8: Test!

1. Call your Twilio phone number
2. The agent should answer and help with menu inquiries! 🎉

## Troubleshooting

- **Service won't start:** Check Render logs for errors
- **Webhooks not working:** Verify your Render URL is correct
- **Slow first response:** Normal on Render's free tier (spins down after 15 min inactivity)

## Your Render URL

Once you have your Render URL, run:
```bash
python configure_twilio.py YOUR_RENDER_URL
```

This will automatically configure all Twilio webhooks!


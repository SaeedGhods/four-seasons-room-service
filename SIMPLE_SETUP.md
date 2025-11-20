# Simple Step-by-Step Setup Guide

Let me walk you through this step by step. You've already done steps 1-3, so let's continue from step 4.

## What You've Already Done ✅
1. ✅ Signed up for Render
2. ✅ Created a new Web Service
3. ✅ Connected your GitHub repository

## Step 4: Fill in the Render Settings

In your Render dashboard, you should see a form. Fill it in like this:

### Basic Information Section:
- **Name:** Type: `four-seasons-room-service`
- **Region:** Choose any (e.g., "Oregon (US West)")
- **Branch:** Should already say `main` (leave it)
- **Root Directory:** Leave this EMPTY

### Build Settings Section:
- **Runtime:** Select `Python 3` from the dropdown
- **Build Command:** Type: `pip install -r requirements.txt`
- **Start Command:** Type: `gunicorn app:app`

## Step 5: Add Your Twilio Credentials

1. Look for a section called **"Environment Variables"** or **"Advanced"** (might be a button or tab)
2. Click on it
3. You'll see a form to add environment variables
4. Add these 5 variables one by one:

**Variable 1:**
- Key: `TWILIO_ACCOUNT_SID`
- Value: `AC36ff73cbbfb07d269517144a89ccb775`

**Variable 2:**
- Key: `TWILIO_AUTH_TOKEN`
- Value: `cec236a8769009bda915975b80bd7b3c`

**Variable 3:**
- Key: `TWILIO_PHONE_NUMBER`
- Value: `+18566991536`

**Variable 4:**
- Key: `OPENAI_API_KEY`
- Value: `your_key_here` (or leave empty if you don't have one)

**Variable 5:**
- Key: `PORT`
- Value: `5000`

## Step 6: Deploy

1. Scroll down and click the big button that says **"Create Web Service"** or **"Save"**
2. Wait 2-3 minutes - you'll see it building
3. When it's done, you'll see a green checkmark ✅
4. At the top of the page, you'll see a URL like: `https://four-seasons-room-service-xxxx.onrender.com`
5. **Copy that URL** - you'll need it for the next step!

## Step 7: Connect Twilio to Your Render URL

Once you have your Render URL, I'll help you connect it to Twilio. 

**Just tell me your Render URL and I'll run the configuration script for you!**

Or if you prefer to do it manually:
1. Go to: https://console.twilio.com/
2. Click "Phone Numbers" → "Manage" → "Active Numbers"
3. Click on the number `+18566991536`
4. Scroll down to "Voice & Fax"
5. Under "A CALL COMES IN", paste your Render URL + `/voice`
   - Example: `https://four-seasons-room-service-xxxx.onrender.com/voice`
6. Set method to `POST`
7. Under "CALL STATUS CHANGES", paste your Render URL + `/status`
   - Example: `https://four-seasons-room-service-xxxx.onrender.com/status`
8. Set method to `POST`
9. Click "Save"

## Step 8: Test It!

Call `+18566991536` and the agent should answer! 🎉

---

## Need Help?

**What part are you stuck on?**
- Can't find where to enter the settings?
- Don't see the environment variables section?
- Not sure what your Render URL is?
- Something else?

Just let me know and I'll help you through it!




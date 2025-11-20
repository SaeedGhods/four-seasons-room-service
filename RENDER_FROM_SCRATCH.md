# Render Setup - Complete Guide from Start

Let's set this up step by step from the very beginning.

## Step 1: Go to Render Dashboard

1. Go to: https://dashboard.render.com
2. Make sure you're logged in
3. You should see your dashboard

## Step 2: Create New Web Service

1. Click the **"New +"** button (usually in the top right or center)
2. Click **"Web Service"** from the dropdown menu
3. If you see a message about free tier limitations, click **"OK"** or **"Continue"**

## Step 3: Connect Your GitHub Repository

1. You'll see options to connect a repository
2. Click **"Connect account"** or **"Connect GitHub"** if you haven't already
3. Authorize Render to access your GitHub
4. Find and select: **`SaeedGhods/four-seasons-room-service`**
5. Click **"Connect"** or **"Select"**

## Step 4: Configure Basic Settings

Fill in these fields:

**Name:**
- Type: `four-seasons-room-service`

**Region:**
- Pick any region (e.g., "Oregon (US West)")

**Branch:**
- Should auto-fill as `main` (leave it)

**Root Directory:**
- Leave this **EMPTY** (don't type anything)

## Step 5: Configure Build Settings

**Runtime:**
- Select: `Python 3` from the dropdown

**Build Command:**
- Type exactly: `pip install -r requirements.txt`

**Start Command:**
- Type exactly: `gunicorn app:app`

## Step 6: Add Environment Variables

1. Look for a section called **"Environment Variables"** 
   - It might be a button, tab, or expandable section
   - Sometimes it's under "Advanced" settings
2. Click to open it
3. You'll see a form with "Key" and "Value" fields
4. Add these **one by one**:

**Variable 1:**
- Key: `TWILIO_ACCOUNT_SID`
- Value: `AC36ff73cbbfb07d269517144a89ccb775`
- Click "Add" or the + button

**Variable 2:**
- Key: `TWILIO_AUTH_TOKEN`
- Value: `cec236a8769009bda915975b80bd7b3c`
- Click "Add"

**Variable 3:**
- Key: `TWILIO_PHONE_NUMBER`
- Value: `+18566991536`
- Click "Add"

**Variable 4:**
- Key: `PORT`
- Value: `5000`
- Click "Add"

**Variable 5 (Optional - only if you have OpenAI key):**
- Key: `OPENAI_API_KEY`
- Value: `your_actual_openai_key_here`
- Click "Add"

## Step 7: Deploy

1. Scroll down to the bottom
2. Click the big button: **"Create Web Service"** or **"Save"**
3. Wait 2-3 minutes
4. You'll see it building (logs will scroll)
5. When it says "Live" with a green checkmark ✅, it's done!

## Step 8: Get Your URL

1. Once it's live, look at the top of the page
2. You'll see a URL like: `https://four-seasons-room-service-xxxx.onrender.com`
3. **Copy that entire URL** (including the https://)
4. Share it with me and I'll configure Twilio!

## Step 9: Configure Twilio (I'll Do This)

Once you give me your Render URL, I'll run a script to automatically connect Twilio to your Render service.

## Step 10: Test!

Call `+18566991536` and your agent should answer! 🎉

---

## Troubleshooting

**Can't find Environment Variables?**
- Look for "Advanced" button/section
- Or scroll down - it might be below the build settings

**Build fails?**
- Check the logs in Render
- Make sure all environment variables are added correctly

**Service won't start?**
- Check that Start Command is exactly: `gunicorn app:app`
- Make sure PORT is set to 5000

---

**Ready? Start at Step 1 and let me know when you get to Step 8!**




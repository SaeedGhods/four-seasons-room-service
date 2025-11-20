# Quick Checklist - What to Do in Render

## In Your Render Dashboard Right Now:

### ☐ Step 4: Basic Settings
- [ ] Name: `four-seasons-room-service`
- [ ] Region: (pick any)
- [ ] Branch: `main` (should already be set)
- [ ] Root Directory: (leave empty)

### ☐ Step 5: Build Settings
- [ ] Runtime: `Python 3`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `gunicorn app:app`

### ☐ Step 6: Environment Variables
Click "Environment Variables" or "Advanced" and add:

- [ ] `TWILIO_ACCOUNT_SID` = `AC36ff73cbbfb07d269517144a89ccb775`
- [ ] `TWILIO_AUTH_TOKEN` = `cec236a8769009bda915975b80bd7b3c`
- [ ] `TWILIO_PHONE_NUMBER` = `+18566991536`
- [ ] `PORT` = `5000`
- [ ] `OPENAI_API_KEY` = (optional, can skip)

### ☐ Step 7: Deploy
- [ ] Click "Create Web Service" or "Save"
- [ ] Wait for it to build (2-3 minutes)
- [ ] Copy the URL it gives you (looks like: `https://something.onrender.com`)

### ☐ Step 8: Tell Me Your URL
- [ ] Share your Render URL with me
- [ ] I'll configure Twilio for you automatically!

---

**That's it! Just check these off as you go.**




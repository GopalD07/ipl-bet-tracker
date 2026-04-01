# 🚀 IPL Bet Tracker — Complete Hosting Guide
## Supabase (Database) + Render (Backend) + Vercel (Frontend)
### All 100% Free

---

## What You'll Have at the End
- `https://ipl-bets.vercel.app` — your live website
- `https://ipl-bets-api.onrender.com` — your live backend API
- Supabase Postgres database storing all your bets permanently

---

## ═══════════════════════════════════
## STEP 1 — Set Up Supabase (Database)
## ═══════════════════════════════════

**1a. Create account**
- Go to https://supabase.com
- Click "Start your project" → sign up with GitHub

**1b. Create new project**
- Click "New project"
- Name it: `ipl-bet-tracker`
- Choose a strong database password (save it!)
- Region: pick closest to you (e.g., Southeast Asia)
- Click "Create new project" — wait ~2 minutes

**1c. Create the two tables**
- In your project dashboard, click "SQL Editor" in the left sidebar
- Click "New query"
- Paste this SQL and click "Run":

```sql
-- Table 1: Match configuration (wallet amounts + result)
CREATE TABLE match_configs (
  match_no    INTEGER PRIMARY KEY,
  home_wallet NUMERIC(10, 4) DEFAULT 0,
  away_wallet NUMERIC(10, 4) DEFAULT 0,
  result      TEXT DEFAULT 'pending',
  updated_at  TIMESTAMPTZ DEFAULT now()
);

-- Table 2: Individual bets
CREATE TABLE bets (
  id         BIGSERIAL PRIMARY KEY,
  match_no   INTEGER NOT NULL REFERENCES match_configs(match_no) ON DELETE CASCADE,
  side       TEXT NOT NULL CHECK (side IN ('home', 'away')),
  placed     NUMERIC(10, 4) NOT NULL,
  win        NUMERIC(10, 4) NOT NULL DEFAULT 0,
  odd        NUMERIC(10, 4) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for faster queries
CREATE INDEX idx_bets_match_no ON bets(match_no);
CREATE INDEX idx_bets_side     ON bets(match_no, side);
```

**1d. Get your API keys**
- Click "Project Settings" (gear icon) in the left sidebar
- Click "API" tab
- Copy two values — you'll need these later:
  - **Project URL** → looks like `https://xyzxyzxyz.supabase.co`
  - **anon/public key** → long string starting with `eyJ...`

✅ Supabase is done!

---

## ═══════════════════════════════════════
## STEP 2 — Push Code to GitHub
## ═══════════════════════════════════════

**2a. Create a GitHub account** (if you don't have one)
- Go to https://github.com → Sign up

**2b. Create a new repository**
- Click the "+" icon → "New repository"
- Name: `ipl-bet-tracker`
- Set to **Public** (required for free Vercel/Render)
- Click "Create repository"

**2c. Upload your files**

Your project folder should contain these 4 files:
```
ipl-bet-tracker/
├── app.py
├── requirements.txt
├── Procfile
└── index.html
```

Option A — via GitHub website (easiest):
- In your new repo, click "uploading an existing file"
- Drag all 4 files into the upload area
- Click "Commit changes"

Option B — via terminal:
```bash
cd your-project-folder
git init
git add app.py requirements.txt Procfile index.html
git commit -m "Initial commit — IPL Bet Tracker"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ipl-bet-tracker.git
git push -u origin main
```

✅ GitHub is done!

---

## ══════════════════════════════════════
## STEP 3 — Deploy Backend on Render
## ══════════════════════════════════════

**3a. Create Render account**
- Go to https://render.com
- Click "Get Started" → sign up with GitHub (use same account)

**3b. Create new Web Service**
- Click "New +" → "Web Service"
- Click "Connect" next to your `ipl-bet-tracker` repo
- If you don't see it, click "Configure account" to give Render access

**3c. Configure the service**

Fill in these fields:
```
Name:              ipl-bet-tracker-api
Region:            Singapore (or closest to you)
Branch:            main
Root Directory:    (leave empty)
Runtime:           Python 3
Build Command:     pip install -r requirements.txt
Start Command:     gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
```

Scroll down to **"Instance Type"** → select **Free**

**3d. Add Environment Variables** (CRITICAL — this is where your Supabase keys go)

Click "Advanced" → "Add Environment Variable"

Add these two:
```
Key:   SUPABASE_URL
Value: https://xyzxyzxyz.supabase.co    ← paste your Supabase Project URL

Key:   SUPABASE_KEY
Value: eyJhbGciOiJIUzI1NiIs...          ← paste your Supabase anon key

Key:   FLASK_ENV
Value: production
```

**3e. Deploy**
- Click "Create Web Service"
- Wait 3–5 minutes while it builds
- You'll see logs scrolling — wait for "Your service is live 🎉"
- Copy your backend URL: `https://ipl-bet-tracker-api.onrender.com`

**3f. Test the backend**
- Open your browser and visit: `https://ipl-bet-tracker-api.onrender.com/schedule`
- You should see a JSON list of all 20 IPL matches
- If yes → ✅ backend is live!

> ⚠️ NOTE: On Render's free tier, the service "sleeps" after 15 minutes of no traffic.
> The first request after sleep takes ~30 seconds. It wakes automatically — just wait.

---

## ══════════════════════════════════════
## STEP 4 — Update index.html with your Render URL
## ══════════════════════════════════════

**4a. Edit index.html**

Open `index.html` in any text editor. Find this line near the top of the `<script>` section:

```javascript
const API = window.location.hostname === "localhost" || ...
```

Replace that entire line with just:
```javascript
const API = "https://ipl-bet-tracker-api.onrender.com";
```

(Use YOUR actual Render URL, not this example)

**4b. Commit the change to GitHub**

Via website: go to your repo → click `index.html` → click the pencil ✏️ edit icon → make the change → "Commit changes"

Via terminal:
```bash
git add index.html
git commit -m "Update API URL to Render backend"
git push
```

---

## ══════════════════════════════════════
## STEP 5 — Deploy Frontend on Vercel
## ══════════════════════════════════════

**5a. Create Vercel account**
- Go to https://vercel.com
- Click "Sign Up" → sign up with GitHub

**5b. Import your project**
- On the Vercel dashboard, click "Add New..." → "Project"
- Find `ipl-bet-tracker` in the list → click "Import"

**5c. Configure**
- Framework Preset: **Other**
- Root Directory: `.` (leave as is)
- Build Command: (leave empty)
- Output Directory: `.` (leave as is)
- Click "Deploy"

**5d. Wait ~1 minute**
- Vercel deploys instantly
- You'll get a URL like: `https://ipl-bet-tracker-abc123.vercel.app`
- Click "Visit" to open it

✅ Your site is live!

---

## ══════════════════════════════════════
## STEP 6 — Get a Clean Custom URL (Optional)
## ══════════════════════════════════════

Vercel gives you a free permanent URL like `ipl-bet-tracker.vercel.app`:
- On your Vercel project → Settings → Domains
- Type `ipl-bets.vercel.app` (pick any name that's available)
- Click "Add" — done!

---

## ══════════════════════════════════════
## SUMMARY — Your Free Stack
## ══════════════════════════════════════

| Service  | What It Does        | Free Limits                    |
|----------|---------------------|--------------------------------|
| Supabase | Postgres database   | 500MB storage, 2GB bandwidth   |
| Render   | Flask backend API   | 750 hrs/month, sleeps at 15min |
| Vercel   | Frontend hosting    | Unlimited bandwidth            |
| GitHub   | Code storage        | Unlimited public repos         |

**All free. No credit card needed.**

---

## ══════════════════════════════════════
## TROUBLESHOOTING
## ══════════════════════════════════════

**"Cannot connect to backend" toast on website**
→ Your Render service is sleeping. Wait 30 seconds and refresh.

**"Failed to fetch" error in browser console**
→ CORS issue — make sure your index.html API URL exactly matches your Render URL (no trailing slash)

**Render build fails**
→ Check the build logs on Render. Usually means requirements.txt is wrong. Make sure all 4 packages are listed.

**Supabase "row-level security" error**
→ In Supabase → Table Editor → click each table → "RLS" tab → disable RLS for both tables (since this is a personal app)

**Data not saving between sessions**
→ Check Render environment variables — SUPABASE_URL and SUPABASE_KEY must be set exactly right.

---

## ══════════════════════════════════════
## UPDATING YOUR CODE LATER
## ══════════════════════════════════════

Whenever you make changes:
```bash
git add .
git commit -m "Update: describe your change"
git push
```

Both Render and Vercel auto-detect the push and redeploy automatically within 2 minutes.

---

## ══════════════════════════════════════
## TO RUN LOCALLY (while developing)
## ══════════════════════════════════════

Create a file called `.env` in your project folder:
```
SUPABASE_URL=https://xyzxyzxyz.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...
```

Then run:
```bash
pip install python-dotenv flask flask-cors supabase gunicorn
python app.py
```

Add to the top of app.py for local .env loading:
```python
from dotenv import load_dotenv
load_dotenv()
```

This way your local app also uses Supabase, same database as production!

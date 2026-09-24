# IGNIS Production Deployment Guide

This guide provides three reliable paths to deploy IGNIS **indefinitely**, in **near real-time**, with **no free trial traps** (no expiring 30-day trials, no sleep timeouts, no auto-deleted databases).

---

## Architecture Breakdown

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Database** | PostgreSQL 16 + PostGIS | Stores thermal events, 31,900 OSM industrial facilities, spatial clusters, risk scores |
| **Backend API** | FastAPI + Uvicorn | High-throughput REST API serving map data, events, alerts, and live ML inference |
| **Worker Pipeline** | APScheduler + XGBoost | Runs 24/7 every 15–30 min to fetch NASA VIIRS NRT data, update clusters, score anomalies |
| **Frontend** | React 19 + Vite + Nginx | High-performance SPA with Leaflet maps, live dashboards, and facility inspection |

---

## The "Free Trial" Trap to Avoid

Many common recommendations will fail the "indefinite" and "near real-time" requirements:
- **Render.com**: Free web services sleep after 15 minutes of inactivity (50s cold start), breaking near real-time background jobs. **Render free PostgreSQL is permanently deleted after 30 days**.
- **AWS / GCP / Azure**: 12-month, 90-day, or 30-day trials expire and convert to high paid tiers.
- **Heroku / Railway**: No permanent free tier; trial credits expire quickly.

Below are the 3 production-grade solutions that honor your requirements.

---

## Option 1: 100% Free Forever Self-Hosted + Cloudflare Tunnel (Immediate)

If you have an always-on PC, home server, mini-PC, or spare computer, you can run the stack locally and expose it to the entire internet over a permanent, secure HTTPS domain.

- **Cost**: $0.00 forever.
- **Trial**: None. Zero expiration.
- **Real-Time**: 0ms cold starts, background worker never sleeps.

### Step 1: Start IGNIS Locally
Your local PostgreSQL already contains the 31,900 industrial facilities and 12,155 events.

Run the master runner:
```powershell
python start_ignis.py
```
This boots:
1. FastAPI Backend on `http://localhost:8000`
2. Automation Worker polling NASA FIRMS NRT data every 30 minutes
3. React Frontend on `http://localhost:80` (or `5173`)

### Step 2: Expose to the Internet with Cloudflare Tunnel (Zero Cost Forever)
1. Download `cloudflared` from Cloudflare (free):
   ```powershell
   winget install Cloudflare.cloudflared
   ```
2. Start an instant, zero-configuration public tunnel:
   ```powershell
   cloudflared tunnel --url http://localhost:80
   ```
3. Cloudflare gives you a permanent, free HTTPS URL (e.g. `https://random-words.trycloudflare.com`) or you can bind your own custom domain for free in Cloudflare Zero Trust.

---

## Option 2: Dedicated Cloud VPS via Docker Compose (Permanent, ~$4/mo)

If you want a 24/7 dedicated server hosted in a cloud data center without any trial deception:
- **Recommended Provider**: Hetzner Cloud (CX22: 2 vCPU, 4GB RAM, 40GB NVMe, 20TB traffic for ~€3.79/mo) or DigitalOcean Droplet ($4–$6/mo).
- **Trial**: None. Standard flat-rate unmetered server. Runs 24/7/365 indefinitely.

### 1-Click Deployment Steps on VPS:

1. **Connect to your VPS**:
   ```bash
   ssh root@<YOUR_VPS_IP>
   ```

2. **Install Docker and Git**:
   ```bash
   apt-get update && apt-get install -y docker.io docker-compose git
   ```

3. **Clone the IGNIS repository**:
   ```bash
   git clone <YOUR_GIT_REPO_URL>
   cd IGNIS
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.production.example .env
   nano .env
   ```
   Add your `FIRMS_MAP_KEY`, `SENTINEL_CLIENT_ID`, and `SENTINEL_CLIENT_SECRET`.

5. **Start all 4 services**:
   ```bash
   docker compose up -d --build
   ```

6. **Seed initial 31,900 OSM facilities & historical data**:
   ```bash
   docker compose exec backend python database/seed_initial_data.py
   ```

7. **Verify Health**:
   ```bash
   curl http://localhost/api/health
   ```
   Output:
   ```json
   {"api":"ok","database":"ok","row_counts":{"events":12155,"facilities":31900,"clusters":1832,"classified":12155}}
   ```

---

## Option 3: Permanent Free Tier Cloud Stack (Hybrid $0)

If you want cloud hosting with zero cost and no expiring trials:

1. **Frontend**: Deploy to **Cloudflare Pages** or **Vercel** (100% Free Forever, unlimited bandwidth, global CDN, automated Git builds).
   - Set build command: `npm run build`
   - Set output directory: `dist`
   - Set root directory: `frontend`
   - Set environment variable: `VITE_API_BASE_URL=https://your-backend-api.com`

2. **Database**: Deploy to **Supabase** (Free Tier):
   - 500 MB PostgreSQL with PostGIS pre-installed.
   - Run `database/init.sql` in the Supabase SQL Editor.
   - *Note on Supabase free tier*: Projects pause after 7 days of inactivity. Because the IGNIS automation scheduler runs every 30 minutes, it continuously pings the database, preventing it from ever falling asleep!

3. **Backend & Worker**: Deploy to **Koyeb** or **Hugging Face Spaces (Docker)**:
   - Free permanent container running `Dockerfile.backend`.
   - Set environment variables to point to the Supabase database.

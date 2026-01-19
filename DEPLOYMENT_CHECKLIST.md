# ✅ Pre-Deployment Checklist for Railway

Use this checklist before deploying to Railway to ensure everything is configured correctly.

## 📦 Code Changes (Already Done ✅)
- [x] Removed `psycopg2-binary` from `requirements.txt`
- [x] Created `nixpacks.toml` to prevent PostgreSQL installation
- [x] Updated `config.py` to use MySQL only
- [x] Updated `.env.example` for MySQL configuration
- [x] Verified no PostgreSQL references in Python code

## 🔧 Before Pushing to GitHub

- [ ] **Review your `.env` file** (DO NOT commit it!)
  - Make sure `.env` is in `.gitignore`
  - Keep your secrets local

- [ ] **Commit all changes:**
  ```bash
  git status
  git add .
  git commit -m "Convert to MySQL for Railway deployment"
  git push origin main
  ```

## 🚂 Railway Setup

### 1. Create Railway Project
- [ ] Go to https://railway.app
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose your repository

### 2. Add MySQL Database
- [ ] In your Railway project, click "+ New"
- [ ] Select "Database" → "MySQL"
- [ ] Wait for provisioning (takes ~1 minute)
- [ ] Verify these variables are auto-set in your database service:
  - `MYSQL_URL`
  - `MYSQLHOST`
  - `MYSQLUSER`
  - `MYSQLPASSWORD`
  - `MYSQLDATABASE`

### 3. Configure Your App Service

#### Required Environment Variables:
- [ ] `FLASK_ENV` = `production`
- [ ] `SECRET_KEY` = `<generate-random-string>`
- [ ] `JWT_SECRET_KEY` = `<generate-random-string>`

**Generate secrets using:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Optional but Recommended:

**Email Configuration** (for order notifications):
- [ ] `MAIL_SERVER` = `smtp.gmail.com`
- [ ] `MAIL_PORT` = `587`
- [ ] `MAIL_USE_TLS` = `true`
- [ ] `MAIL_USERNAME` = `your-email@gmail.com`
- [ ] `MAIL_PASSWORD` = `your-app-password`
- [ ] `MAIL_DEFAULT_SENDER` = `support@komplyte.com`

**Razorpay** (for payments):
- [ ] `RAZORPAY_KEY_ID` = `your_key_id`
- [ ] `RAZORPAY_KEY_SECRET` = `your_key_secret`

**Business Settings** (optional, defaults exist):
- [ ] `SHIPPING_FREE_THRESHOLD` = `2000`
- [ ] `SHIPPING_CHARGE` = `49`
- [ ] `ADMIN_WHATSAPP` = `918149550229`

### 4. Deploy
- [ ] Railway auto-deploys from GitHub
- [ ] Monitor deployment logs in Railway dashboard
- [ ] Wait for "Deployed" status

### 5. Run Database Migrations

**Option A: Railway CLI** (Recommended)
```bash
# Install CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Run migrations
railway run flask db upgrade
```

**Option B: Temporary Deploy Command**
- [ ] Go to Service Settings → Deploy
- [ ] Set custom start command:
  ```
  flask db upgrade && gunicorn wsgi:app --workers 4 --bind 0.0.0.0:$PORT
  ```
- [ ] Trigger redeploy
- [ ] After success, revert to original command or remove (Railway uses railway.json)

### 6. Create Admin User

Using Railway CLI:
```bash
railway run python scripts/create_admin.py
```

Or manually:
```bash
railway shell
python
>>> from app import create_app, db
>>> from app.models.user import User
>>> from werkzeug.security import generate_password_hash
>>> app = create_app()
>>> with app.app_context():
...     admin = User(
...         email='admin@komplyte.com',
...         password_hash=generate_password_hash('YourSecurePassword123!'),
...         username='admin',
...         role='admin',
...         is_guest=False
...     )
...     db.session.add(admin)
...     db.session.commit()
...     print('Admin created!')
```

## 🧪 Testing After Deployment

- [ ] **Test health endpoint:**
  ```bash
  curl https://your-app.up.railway.app/health
  ```
  Expected: `{"status": "healthy", "database": "connected", ...}`

- [ ] **Test user registration:**
  ```bash
  curl -X POST https://your-app.up.railway.app/api/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"Test123!","username":"testuser"}'
  ```

- [ ] **Test admin login:**
  ```bash
  curl -X POST https://your-app.up.railway.app/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@komplyte.com","password":"YourSecurePassword123!"}'
  ```

- [ ] **Import Postman collection:**
  - Import `postman_collection_validated.json`
  - Update base URL to your Railway URL
  - Test all endpoints

## 🎯 Post-Deployment (Optional)

### Set up Keep-Alive (Prevent Sleep)
- [ ] Sign up at https://uptimerobot.com
- [ ] Add new monitor:
  - URL: `https://your-app.up.railway.app/ping`
  - Interval: 5 minutes
  - Type: HTTP(s)

### Monitor Your App
- [ ] Check Railway "Observability" tab
- [ ] Review logs regularly
- [ ] Monitor usage (Dashboard → Usage)

## ⚠️ Common Issues

### Build Fails
- ✅ **Fixed!** Your build should now succeed
- If it fails, check:
  - `nixpacks.toml` is committed
  - `psycopg2-binary` is NOT in requirements.txt
  - Railway logs for specific error

### Database Connection Fails
- Check MySQL service is running in Railway
- Verify `MYSQL_URL` is set in app service
- Check Railway logs for connection errors

### Migration Errors
```bash
railway run flask db stamp head
railway run flask db migrate -m "Initial migration"
railway run flask db upgrade
```

### Workers Timeout
- Reduce workers in `railway.json`: `--workers 2`
- Increase timeout if needed

## 📝 Notes

- Railway free tier: $5 credit/month
- MySQL on Railway: Included in credit
- Cold start time: ~10-30 seconds
- Logs retention: 7 days on free tier

## ✅ All Done!

Once you complete this checklist, your app should be:
- ✅ Live on Railway
- ✅ Using MySQL database
- ✅ Ready for production traffic
- ✅ Accessible via HTTPS

**Your Railway URL:** `https://[your-project].up.railway.app`

---

Need help? Check:
- `RAILWAY_DEPLOY_MYSQL.md` - Detailed deployment guide
- `MIGRATION_SUMMARY.md` - What changed from PostgreSQL to MySQL
- Railway Docs: https://docs.railway.app

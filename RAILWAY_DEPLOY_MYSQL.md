# Railway MySQL Deployment Guide

## Overview
Your application is now configured to use **MySQL only** (PostgreSQL has been removed). Follow these steps to deploy successfully to Railway.

## Prerequisites
- GitHub repository with your code pushed
- Railway account (https://railway.app)

## Step-by-Step Deployment

### 1. Create a New Railway Project
1. Log in to Railway: https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `komp-y_te-test-`

### 2. Add MySQL Database
1. In your Railway project, click **"+ New"**
2. Select **"Database"**
3. Choose **"Add MySQL"**
4. Railway will automatically create a MySQL database and set these environment variables:
   - `MYSQL_URL`
   - `MYSQLHOST`
   - `MYSQLPORT`
   - `MYSQLDATABASE`
   - `MYSQLUSER`
   - `MYSQLPASSWORD`

### 3. Configure Environment Variables
In your Railway service (not the database), add these environment variables:

#### Required Variables
```
FLASK_ENV=production
SECRET_KEY=<generate-a-long-random-string>
JWT_SECRET_KEY=<generate-another-long-random-string>
```

#### Email Configuration (for order notifications)
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=support@komplyte.com
```

#### Razorpay Payment Gateway
```
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

#### Business Configuration (Optional - defaults are set)
```
SHIPPING_FREE_THRESHOLD=2000
SHIPPING_CHARGE=49
CONSULTATION_FREE_MINUTES=20
CONSULTATION_PAID_PRICE=250
```

#### Company Contact
```
ADMIN_WHATSAPP=918149550229
SUPPORT_EMAIL=support@komplyte.com
```

### 4. Deploy
1. Railway will automatically deploy once you push to GitHub
2. The build should now succeed without PostgreSQL errors
3. Your app will be available at: `https://your-app.up.railway.app`

### 5. Run Database Migrations
After the first deployment, you need to initialize the database:

**Option A: Using Railway CLI**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Run migrations
railway run flask db upgrade
```

**Option B: Using Railway Dashboard**
1. Go to your service in Railway
2. Click on **"Settings"**
3. Scroll to **"Deploy"**
4. Add a custom deploy command temporarily:
   ```
   flask db upgrade && gunicorn wsgi:app --workers 4 --bind 0.0.0.0:$PORT
   ```
5. Trigger a redeploy

### 6. Create Admin User
Run this command using Railway CLI:
```bash
railway run python -c "from app import create_app, db; from app.models.user import User; from werkzeug.security import generate_password_hash; app = create_app(); ctx = app.app_context(); ctx.push(); admin = User(email='admin@komplyte.com', password_hash=generate_password_hash('your-password'), username='admin', role='admin', is_guest=False); db.session.add(admin); db.session.commit(); print('Admin created!')"
```

Or create a script and run it via Railway.

## What Changed from PostgreSQL to MySQL

### Files Modified:
1. **requirements.txt**: Removed `psycopg2-binary` (PostgreSQL driver)
2. **config.py**: Removed PostgreSQL connection string handling
3. **.env.example**: Removed PostgreSQL DATABASE_URL example
4. **nixpacks.toml** (NEW): Prevents Railway from installing PostgreSQL

### Database Compatibility:
- Your SQLAlchemy models are database-agnostic
- PyMySQL driver handles MySQL connections
- No code changes needed in your models or routes

## Troubleshooting

### Build Fails with "attribute 'dev' missing"
This was the original error you encountered. It's now fixed by:
- Removing `psycopg2-binary` from requirements.txt
- Adding `nixpacks.toml` to prevent PostgreSQL detection

### Database Connection Errors
1. Make sure you added a MySQL database to your Railway project
2. Check that `MYSQL_URL` is automatically set by Railway
3. Verify your app service is linked to the database

### Migration Errors
If migrations fail:
```bash
railway run flask db stamp head
railway run flask db migrate -m "Initial migration"
railway run flask db upgrade
```

### Runtime Errors
Check Railway logs:
1. Go to your service in Railway
2. Click on **"Deployments"**
3. View the latest deployment logs

## Testing the Deployment

After deployment, test these endpoints:

```bash
# Health check
curl https://your-app.up.railway.app/

# Register a user
curl -X POST https://your-app.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "username": "testuser"
  }'

# Login
curl -X POST https://your-app.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

## Support
- Railway Docs: https://docs.railway.app
- Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com
- PyMySQL: https://pymysql.readthedocs.io

---

**Note**: Railway's free tier includes:
- 500 hours of usage per month
- $5 credit per month
- Choose resource limits wisely

**Estimated monthly cost**: ~$5-10 for small applications

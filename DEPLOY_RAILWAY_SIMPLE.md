# 🚀 Simple Railway Deployment Guide (MySQL - No Migrations)

## ✅ What Was Fixed

Your code is now **100% ready for Railway deployment**:

1. ✅ **Removed PostgreSQL** - No more `psycopg2-binary`
2. ✅ **MySQL-only** - Using `PyMySQL` driver
3. ✅ **Removed nixpacks.toml** - Was breaking pip installation
4. ✅ **Simplified deployment** - No migrations required
5. ✅ **Auto-detection** - Railway will detect Python from `requirements.txt`
6. ✅ **Lightweight build** - Minimal dependencies, fast deployment

---

## 📋 Deployment Steps

### 1️⃣ Deploy to Railway

1. Go to **https://railway.app**
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose **`komp-y_te-test-`**
5. Railway will automatically:
   - Detect Python from `requirements.txt` and `runtime.txt`
   - Install all dependencies with pip
   - Start your app with gunicorn

### 2️⃣ Add MySQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"MySQL"**
3. Railway will automatically set these variables:
   - `MYSQL_URL`
   - `MYSQLHOST`, `MYSQLPORT`, `MYSQLDATABASE`
   - `MYSQLUSER`, `MYSQLPASSWORD`

### 3️⃣ Set Environment Variables

Click on your **app service** (not the database) and add:

```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

**Generate secrets:**
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
```

**Optional (for full features):**
```bash
# Email (for order notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=support@komplyte.com

# Razorpay (for payments)
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret

# Business settings (optional - defaults exist)
SHIPPING_FREE_THRESHOLD=2000
SHIPPING_CHARGE=49
ADMIN_WHATSAPP=918149550229
```

### 4️⃣ Wait for Deployment

- Railway will build and deploy automatically
- Check the **"Deployments"** tab for logs
- Build should succeed in 2-3 minutes
- Your app will be at: `https://your-app.up.railway.app`

### 5️⃣ Initialize Database (ONE TIME ONLY)

After first successful deployment, run:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Initialize database tables
railway run python init_db.py
```

This will create all database tables without migrations.

### 6️⃣ Create Admin User

```bash
railway run python scripts/admin_setup.py
```

Or set these environment variables and the script will use them:
```
ADMIN_EMAIL=admin@komplyte.com
ADMIN_PASSWORD=your-secure-password
ADMIN_NAME=Admin
```

---

## 🧪 Testing Your Deployment

### Test Health Endpoint
```bash
curl https://your-app.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "service": "KOMPLYTE API"
}
```

### Test User Registration
```bash
curl -X POST https://your-app.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "username": "testuser"
  }'
```

### Test Admin Login
```bash
curl -X POST https://your-app.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@komplyte.com",
    "password": "your-password"
  }'
```

---

## 🔧 How It Works

### Build Process (Railway does this automatically):

1. **Detects Python** from `requirements.txt` and `runtime.txt` (Python 3.9.18)
2. **Installs dependencies**: `pip install -r requirements.txt`
3. **Starts app**: Uses command from `railway.json` or `Procfile`

### No Migrations Needed:

- Database tables are created with `db.create_all()` via `init_db.py`
- Simpler, faster, lighter for first release
- Can add migrations later if needed

### Database Connection:

- Railway sets `MYSQL_URL` automatically
- Your `config.py` detects and uses it
- PyMySQL driver handles all MySQL communication

---

## ⚠️ Troubleshooting

### Build Fails with "pip: command not found"
**Fixed!** We removed `nixpacks.toml` that was breaking pip.

### Build Fails with PostgreSQL Error
**Fixed!** We removed `psycopg2-binary` from requirements.

### Database Connection Errors
- Make sure MySQL database is added to your project
- Check that `MYSQL_URL` is set in app service
- Verify both services are in the same project

### "Table doesn't exist" Errors
- Run `railway run python init_db.py` to create tables
- Make sure database initialization completed successfully

### App Starts but 500 Errors
- Check Railway logs: Click on deployment → View Logs
- Look for Python errors or missing environment variables
- Verify `SECRET_KEY` and `JWT_SECRET_KEY` are set

---

## 📊 What's Deployed

Your backend includes:

### ✅ Core Features:
- User authentication (JWT + Bcrypt)
- Product catalog with categories
- Shopping cart
- Order management
- Payment integration (Razorpay)
- Email notifications

### ✅ Special Features:
- Guest account limitations
- Tiered shipping charges
- Consultation booking system
- Admin dashboard routes
- WhatsApp returns/refunds
- Newsletter subscription

### ✅ API Endpoints:
- `/` - Health check
- `/health` - Database status
- `/ping` - Keep-alive endpoint
- `/api/auth/*` - Authentication
- `/api/products/*` - Products
- `/api/cart/*` - Shopping cart
- `/api/orders/*` - Orders
- `/api/admin/*` - Admin routes
- `/api/bookings/*` - Consultation bookings
- And many more...

---

## 💡 Post-Deployment Tips

### Keep App Awake (Prevent Sleep):
Use **UptimeRobot** (free):
1. Sign up at https://uptimerobot.com
2. Add monitor for `https://your-app.up.railway.app/ping`
3. Set interval to 5 minutes

### Monitor Your App:
- Railway Dashboard → Observability
- Check CPU, memory, request count
- Review error logs regularly

### Cost Management:
- Railway free tier: $5 credit/month
- Monitor usage in Dashboard → Usage
- Optimize if approaching limits

---

## ✅ Deployment Verification Checklist

Before deploying, verify:
- [ ] Code pushed to GitHub
- [ ] No `psycopg2-binary` in requirements.txt
- [ ] `nixpacks.toml` is deleted
- [ ] Railway project created
- [ ] MySQL database added
- [ ] Environment variables set
- [ ] Deployment successful
- [ ] Database initialized (`init_db.py`)
- [ ] Admin user created
- [ ] Health endpoint working
- [ ] Test endpoints working

---

## 🆘 Need Help?

- **Railway Docs**: https://docs.railway.app
- **Check Logs**: Railway Dashboard → Deployments → View Logs
- **Database Issues**: Verify MYSQL_URL in environment variables
- **Build Issues**: Check deployment logs for specific errors

---

## 🎉 Success!

Once deployed, your **KOMPLYTE E-commerce Backend** will be:
- ✅ Live on Railway
- ✅ Using MySQL database
- ✅ Accessible via HTTPS
- ✅ Production-ready
- ✅ Auto-scaling capable

**Your URL**: `https://[project-name].up.railway.app`

**Admin Panel**: Use Postman collection to test admin endpoints

**Ready to scale**: Railway handles scaling automatically

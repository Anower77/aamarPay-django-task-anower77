# 🌍 Environment Configuration Guide

## 📁 Environment Files Setup

### **1. Development Environment (.env)**

Create a `.env` file in your project root:

```bash
# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings (SQLite for development)
# DATABASE_URL=sqlite:///db.sqlite3

# Celery Settings
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# aamarPay Settings
AAMARPAY_STORE_ID=aamarpaytest
AAMARPAY_SIGNATURE_KEY=dbb74894e82415a2f7ff0ec3a97e4183
AAMARPAY_ENDPOINT=https://sandbox.aamarpay.com/jsonpost.php

# Media Settings
MEDIA_URL=/media/
MEDIA_ROOT=media/
```

### **2. Production Environment (Render)**

Set these environment variables in your Render dashboard:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ALLOWED_HOSTS=your-app-name.onrender.com,localhost,127.0.0.1

# Database Settings (PostgreSQL on Render)
DATABASE_URL=postgresql://username:password@host:port/database

# Celery Settings
CELERY_BROKER_URL=redis://your-redis-url:6379/0
CELERY_RESULT_BACKEND=redis://your-redis-url:6379/0

# aamarPay Settings
AAMARPAY_STORE_ID=aamarpaytest
AAMARPAY_SIGNATURE_KEY=dbb74894e82415a2f7ff0ec3a97e4183
AAMARPAY_ENDPOINT=https://sandbox.aamarpay.com/jsonpost.php

# Media Settings
MEDIA_URL=/media/
MEDIA_ROOT=media/
```

## 🗄️ PostgreSQL Setup

### **Local PostgreSQL Setup**

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create Database and User**
   ```bash
   sudo -u postgres psql
   
   CREATE DATABASE ammerpay;
   CREATE USER ammerpay_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE ammerpay TO ammerpay_user;
   \q
   ```

3. **Update .env for Local PostgreSQL**
   ```bash
   DATABASE_URL=postgresql://ammerpay_user:your_password@localhost:5432/ammerpay
   ```

### **Render PostgreSQL Setup**

1. **Create PostgreSQL Service**
   - Go to Render Dashboard
   - Click "New +" → "PostgreSQL"
   - Choose your plan
   - Set database name: `ammerpay`
   - Set user: `ammerpay_user`
   - Note down the connection details

2. **Get Connection String**
   - Copy the "External Database URL" from Render
   - It looks like: `postgresql://username:password@host:port/database`

## 🚀 Render Deployment Steps

### **1. Prepare Your Repository**

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Ensure these files are in your repo:**
   - `requirements.txt`
   - `build.sh`
   - `Dockerfile.prod` (optional)
   - `backend/wsgi.py`

### **2. Create Web Service on Render**

1. **Connect Repository**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   ```
   Name: ammerpay-backend
   Environment: Python 3
   Build Command: ./build.sh
   Start Command: gunicorn backend.wsgi:app
   ```

3. **Set Environment Variables**
   - Add all the production environment variables listed above
   - Make sure `DEBUG=False`
   - Set a strong `SECRET_KEY`

### **3. Create Redis Service (Optional)**

1. **Create Redis Service**
   - Go to Render Dashboard
   - Click "New +" → "Redis"
   - Choose your plan

2. **Update Environment Variables**
   - Copy the Redis connection URL
   - Update `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`

### **4. Deploy and Test**

1. **Deploy**
   - Click "Deploy" in Render
   - Wait for build to complete

2. **Run Migrations**
   - Go to your service's shell
   - Run: `python manage.py migrate`

3. **Create Superuser**
   - Run: `python manage.py createsuperuser`

4. **Test Your App**
   - Visit your Render URL
   - Test the payment flow
   - Upload some files

## 🔧 Troubleshooting

### **Common Issues**

1. **Build Failures**
   - Check `requirements.txt` for typos
   - Ensure `build.sh` has execute permissions
   - Check Python version compatibility

2. **Database Connection Issues**
   - Verify `DATABASE_URL` format
   - Check PostgreSQL service status
   - Ensure database exists

3. **Static Files Not Loading**
   - Check `STATIC_ROOT` setting
   - Ensure `build.sh` runs `collectstatic`
   - Verify WhiteNoise configuration

4. **Environment Variables**
   - Double-check all variables are set in Render
   - Ensure no typos in variable names
   - Check for missing quotes

### **Useful Commands**

```bash
# Check environment variables
python manage.py shell
>>> import os
>>> print(os.getenv('DATABASE_URL'))

# Test database connection
python manage.py dbshell

# Check static files
python manage.py collectstatic --dry-run

# Run migrations
python manage.py migrate --plan
```

## 📱 Testing Your Deployment

1. **Health Check**
   - Visit your app URL
   - Should see login page

2. **Database Test**
   - Try to register a user
   - Check if data is saved

3. **Payment Flow**
   - Complete registration
   - Test payment initiation
   - Verify file upload after payment

4. **File Processing**
   - Upload .txt or .docx file
   - Check if word count is processed
   - Verify activity logging

## 🎯 Next Steps

After successful deployment:

1. **Set up custom domain** (optional)
2. **Configure SSL certificates** (automatic on Render)
3. **Set up monitoring and logging**
4. **Configure backups** for PostgreSQL
5. **Set up CI/CD pipeline**

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)

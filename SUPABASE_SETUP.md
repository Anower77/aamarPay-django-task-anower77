# 🗄️ Supabase PostgreSQL Setup Guide

## 🚀 **Quick Setup for Supabase**

### **1. Get Your Supabase Connection String**

1. **Go to [Supabase Dashboard](https://supabase.com/dashboard)**
2. **Select your project**
3. **Go to Settings → Database**
4. **Copy the "URI" connection string**

The connection string looks like this:
```
postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

### **2. Create .env File**

Create a `.env` file in your project root with this content:

```bash
# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

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

### **3. Replace Placeholders**

- Replace `[YOUR-PASSWORD]` with your actual Supabase database password
- Replace `[YOUR-PROJECT-REF]` with your actual project reference

## 🔧 **Alternative: Set Environment Variables Directly**

If you can't create a `.env` file, set these environment variables directly:

### **Windows PowerShell:**
```powershell
$env:DATABASE_URL="postgresql://postgres:your_password@db.your_project_ref.supabase.co:5432/postgres"
$env:DEBUG="True"
$env:SECRET_KEY="django-insecure-change-this-in-development"
```

### **Windows Command Prompt:**
```cmd
set DATABASE_URL=postgresql://postgres:your_password@db.your_project_ref.supabase.co:5432/postgres
set DEBUG=True
set SECRET_KEY=django-insecure-change-this-in-development
```

## 🧪 **Test Your Connection**

### **1. Test Django Configuration**
```bash
python manage.py check
```

### **2. Test Database Connection**
```bash
python manage.py dbshell
```

### **3. Run Migrations**
```bash
python manage.py migrate
```

### **4. Create Superuser**
```bash
python manage.py createsuperuser
```

## 🚨 **Common Issues & Solutions**

### **Issue 1: Port Error**
**Error:** `Port could not be cast to integer value as 'port'`

**Solution:** Check your DATABASE_URL format. It should be:
```
postgresql://username:password@host:port/database
```

### **Issue 2: Connection Refused**
**Error:** `Connection refused` or `timeout`

**Solution:** 
1. Check if your IP is whitelisted in Supabase
2. Go to Supabase → Settings → Database → Connection pooling
3. Add your IP address to the allowed list

### **Issue 3: Authentication Failed**
**Error:** `authentication failed`

**Solution:**
1. Verify your password is correct
2. Check if the user exists in Supabase
3. Ensure the database name is correct

## 🔒 **Security Best Practices**

### **1. IP Whitelisting**
- Only allow connections from your development machine
- Add your IP to Supabase allowed list

### **2. Strong Passwords**
- Use a strong, unique password for your database
- Don't commit passwords to version control

### **3. Environment Variables**
- Use `.env` files for local development
- Set environment variables in production

## 📱 **Supabase Dashboard Features**

### **1. Database Browser**
- View and edit data directly
- Run SQL queries
- Monitor database performance

### **2. Authentication**
- User management
- OAuth providers
- Row Level Security (RLS)

### **3. Real-time Features**
- Database changes in real-time
- WebSocket connections
- Live updates

## 🚀 **Production Deployment**

### **1. Render Deployment**
When deploying to Render, set these environment variables:

```bash
DEBUG=False
SECRET_KEY=your-super-secret-production-key
DATABASE_URL=your-supabase-connection-string
ALLOWED_HOSTS=your-app-name.onrender.com
```

### **2. Environment Variables in Render**
1. Go to your Render service
2. Click on "Environment"
3. Add each variable from the list above

## 🔍 **Testing Your Setup**

### **1. Basic Connection Test**
```bash
python manage.py shell
>>> from django.db import connection
>>> cursor = connection.cursor()
>>> cursor.execute("SELECT version();")
>>> cursor.fetchone()
```

### **2. Model Creation Test**
```bash
python manage.py shell
>>> from core.models import User
>>> User.objects.count()
```

### **3. Full System Test**
```bash
# Start the development server
python manage.py runserver

# Visit http://localhost:8000
# Try to register a user
# Check if data is saved in Supabase
```

## 📚 **Useful Commands**

```bash
# Check current database
python manage.py dbshell

# Show migrations
python manage.py showmigrations

# Reset database (WARNING: deletes all data)
python manage.py flush

# Backup database
python manage.py dumpdata > backup.json

# Restore database
python manage.py loaddata backup.json
```

## 🎯 **Next Steps**

After successful Supabase connection:

1. ✅ **Test the complete payment flow**
2. ✅ **Upload and process files**
3. ✅ **Verify data is saved in Supabase**
4. ✅ **Deploy to Render with Supabase**
5. ✅ **Set up monitoring and backups**

## 📞 **Getting Help**

- **Supabase Documentation:** https://supabase.com/docs
- **Supabase Discord:** https://discord.supabase.com
- **Django Documentation:** https://docs.djangoproject.com
- **PostgreSQL Documentation:** https://www.postgresql.org/docs/

---

**Note:** Make sure to replace all placeholder values with your actual Supabase credentials!

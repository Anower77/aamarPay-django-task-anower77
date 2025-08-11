# AmmerPay Django Task - Payment Gateway Integration and Files Uploading System

A Django-based system where users can upload files only after completing a payment via aamarPay sandbox. The system supports file upload (.txt, .docx), word count processing via Celery, payment logging, and a Bootstrap-based frontend.

## Features

- **User Authentication**: Django built-in user model with login/registration
- **Payment Gateway**: aamarPay sandbox integration (৳100 payment required)
- **File Upload**: Support for .txt and .docx files (max 10MB)
- **Word Count Processing**: Asynchronous processing via Celery
- **Activity Logging**: Complete audit trail of user actions
- **RESTful API**: Full API interface for all operations
- **Bootstrap Frontend**: Modern, responsive user interface
- **Django Admin**: Read-only admin panel for data inspection
- **Docker Support**: Complete containerization with Redis and PostgreSQL

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized setup)
- Redis (for Celery)
- PostgreSQL (optional, SQLite by default)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ammerpay-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env with your configuration
   DEBUG=1
   SECRET_KEY=your-secret-key
   AAMARPAY_STORE_ID=aamarpaytest
   AAMARPAY_SIGNATURE_KEY=dbb74894e82415a2f7ff0ec3a97e4183
   AAMARPAY_ENDPOINT=https://sandbox.aamarpay.com/jsonpost.php
   CELERY_BROKER_URL=redis://localhost:6379/0
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Redis** (for Celery)
   ```bash
   # Install Redis or use Docker
   docker run -d -p 6379:6379 redis:7-alpine
   ```

8. **Start Celery worker**
   ```bash
   celery -A backend worker --loglevel=info
   ```

9. **Run the development server**
   ```bash
   python manage.py runserver
   ```

10. **Access the application**
    - Admin: http://localhost:8000/admin/
    - API: http://localhost:8000/api/

### Docker Setup (Recommended)

1. **Build and start services**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Access the application**
    - Admin: http://localhost:8000/admin/
    - API: http://localhost:8000/api/

## API Documentation

### Complete API Endpoints List

| Method | Endpoint | Description | Authentication | Request Body |
|--------|----------|-------------|----------------|--------------|
| **Authentication** |
| `POST` | `/api-token-auth/` | Get authentication token | None | `{"username": "string", "password": "string"}` |
| **Payment** |
| `POST` | `/api/initiate-payment/` | Initiate aamarPay payment | Token Required | `{"payment_method": "string"}` |
| `GET` | `/api/payment/success/` | Payment success callback | None | Query params: `tran_id` |
| `GET` | `/api/payment/fail/` | Payment failure callback | None | Query params: `tran_id` |
| `GET` | `/api/payment/cancel/` | Payment cancellation callback | None | Query params: `tran_id` |
| **File Management** |
| `POST` | `/api/upload/` | Upload file after payment | Token Required | `file: multipart/form-data` |
| `GET` | `/api/files/` | List user's uploaded files | Token Required | None |
| `GET` | `/api/download/<int:file_id>/` | Download specific file | Token Required | None |
| `DELETE` | `/api/delete/<int:file_id>/` | Delete specific file | Token Required | None |
| **Data Retrieval** |
| `GET` | `/api/transactions/` | List user's payment history | Token Required | None |
| `GET` | `/api/activity/` | List user's activity logs | Token Required | None |
| **Web Interface** |
| `GET` | `/` | Home page (redirects to login/dashboard) | None | None |
| `GET` | `/login/` | User login page | None | None |
| `POST` | `/login/` | Process user login | None | `{"username": "string", "password": "string"}` |
| `GET` | `/register/` | User registration page | None | None |
| `POST` | `/register/` | Process user registration | None | `{"username": "string", "password1": "string", "password2": "string"}` |
| `GET` | `/logout/` | User logout | None | None |
| `GET` | `/dashboard/` | Main dashboard | Session Required | None |
| `GET` | `/admin/` | Django admin panel | Staff Required | None |

### API Endpoints Details

#### 1. Authentication Endpoints

##### Get Authentication Token
```http
POST /api-token-auth/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "token": "your_auth_token_here"
}
```

#### 2. Payment Endpoints

##### Initiate Payment
```http
POST /api/initiate-payment/
Content-Type: application/json
Authorization: Token <your_token>

{
  "payment_method": "VISA"
}
```

**Supported Payment Methods:**
- `VISA` - Visa Credit/Debit Cards
- `MASTER` - Mastercard
- `AMEX` - American Express
- `BKASH` - bKash Mobile Banking
- `NAGAD` - Nagad Mobile Banking
- `ROCKET` - Rocket Mobile Banking
- `UPAY` - UPAY Digital Wallet
- `TAP` - TAP Payment Gateway

**Response:**
```json
{
  "redirect_url": "https://sandbox.aamarpay.com/payment/..."
}
```

##### Payment Success Callback
```http
GET /api/payment/success/?tran_id=<transaction_id>
```

**Response:** Redirects to dashboard with success message

##### Payment Failure Callback
```http
GET /api/payment/fail/?tran_id=<transaction_id>
```

**Response:** Redirects to dashboard with failure message

##### Payment Cancellation Callback
```http
GET /api/payment/cancel/?tran_id=<transaction_id>
```

**Response:** Redirects to dashboard with cancellation message

#### 3. File Management Endpoints

##### Upload File
```http
POST /api/upload/
Content-Type: multipart/form-data
Authorization: Token <your_token>

file: <your_file>
```

**File Requirements:**
- **Types:** `.txt`, `.docx` only
- **Size:** Maximum 10MB
- **Prerequisite:** Successful payment required

**Response:**
```json
{
  "message": "File uploaded and processing started."
}
```

##### List Files
```http
GET /api/files/
Authorization: Token <your_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "user": 1,
    "file": "/media/uploads/2025/08/11/sample.txt",
    "filename": "sample.txt",
    "upload_time": "2025-08-11T10:00:00Z",
    "status": "completed",
    "word_count": 150
  }
]
```

##### Download File
```http
GET /api/download/<int:file_id>/
Authorization: Token <your_token>
```

**Response:** File download (binary)

##### Delete File
```http
DELETE /api/delete/<int:file_id>/
Authorization: Token <your_token>
```

**Response:**
```json
{
  "message": "File deleted successfully"
}
```

#### 4. Data Retrieval Endpoints

##### List Payment Transactions
```http
GET /api/transactions/
Authorization: Token <your_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "user": 1,
    "transaction_id": "uuid-string",
    "amount": "100.00",
    "status": "success",
    "gateway_response": {...},
    "timestamp": "2025-08-11T10:00:00Z"
  }
]
```

##### List Activity Logs
```http
GET /api/activity/
Authorization: Token <your_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "user": 1,
    "action": "file_uploaded",
    "metadata": {
      "file_id": 1,
      "filename": "sample.txt"
    },
    "timestamp": "2025-08-11T10:00:00Z"
  }
]
```

#### 5. Web Interface Endpoints

##### Dashboard
```http
GET /dashboard/
```

**Features:**
- File upload form (after payment)
- Files list with word counts
- Payment history
- Activity logs
- Payment method selection

##### User Registration
```http
POST /register/
Content-Type: application/x-www-form-urlencoded

username=your_username&password1=your_password&password2=your_password
```

**Password Requirements:**
- Minimum 8 characters
- Cannot be too similar to personal information
- Cannot be commonly used
- Cannot be entirely numeric

##### User Login
```http
POST /login/
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

### API Response Codes

| Status Code | Description |
|-------------|-------------|
| `200` | Success |
| `201` | Created (e.g., file upload) |
| `400` | Bad Request (validation errors) |
| `401` | Unauthorized (invalid/missing token) |
| `403` | Forbidden (payment required, insufficient permissions) |
| `404` | Not Found |
| `500` | Internal Server Error |

### Error Response Format

```json
{
  "error": "Error message description",
  "detail": "Additional error details"
}
```

### Rate Limiting

- **Authentication:** 5 attempts per minute
- **File Upload:** 10 files per hour per user
- **Payment Initiation:** 5 attempts per hour per user

### Webhook Endpoints

The following endpoints are designed to receive callbacks from aamarPay:

- `/api/payment/success/` - Called after successful payment
- `/api/payment/fail/` - Called after failed payment
- `/api/payment/cancel/` - Called after cancelled payment

**Note:** These endpoints are publicly accessible (no authentication required) as they are called by the payment gateway.

## Testing the Payment Flow

### Using aamarPay Sandbox

1. **Register/Login** to the application
2. **Select payment method** (VISA, Mastercard, bKash, etc.)
3. **Click "Pay Now"** to initiate payment
4. **Complete payment** on aamarPay sandbox
5. **Return to application** after successful payment
6. **Upload files** (now available after payment)

### Test Card Details (aamarPay Sandbox)

- **Card Number**: 4111111111111111
- **Expiry**: Any future date
- **CVV**: Any 3 digits
- **Amount**: ৳100 (fixed)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `1` |
| `SECRET_KEY` | Django secret key | Auto-generated |
| `AAMARPAY_STORE_ID` | aamarPay store ID | `aamarpaytest` |
| `AAMARPAY_SIGNATURE_KEY` | aamarPay signature key | `dbb74894e82415a2f7ff0ec3a97e4183` |
| `AAMARPAY_ENDPOINT` | aamarPay API endpoint | `https://sandbox.aamarpay.com/jsonpost.php` |
| `CELERY_BROKER_URL` | Redis connection URL | `redis://redis:6379/0` |
| `DATABASE_URL` | PostgreSQL connection string | SQLite (fallback) |

### Database Configuration

The system supports both SQLite (default) and PostgreSQL:

- **SQLite**: Default, no additional setup required
- **PostgreSQL**: Set `DATABASE_URL` environment variable

### Database Schema

The system implements a comprehensive database schema with three main models:

- **FileUpload**: Manages file uploads, processing status, and word counts
- **PaymentTransaction**: Tracks payment status and gateway responses
- **ActivityLog**: Maintains complete audit trail of user actions

For detailed database schema visualization, refer to `schema.svg` in the project root.

## Project Structure

```
backend/
├── backend/                 # Django project settings
│   ├── settings.py         # Main settings
│   ├── urls.py            # Main URL configuration
│   └── celery.py          # Celery configuration
├── core/                   # Main application
│   ├── models.py          # Database models
│   ├── views.py           # API views and templates
│   ├── serializers.py     # DRF serializers
│   ├── tasks.py           # Celery tasks
│   ├── admin.py           # Admin configuration
│   └── templates/         # HTML templates
├── media/                  # Uploaded files
├── staticfiles/            # Collected static files
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker services
├── Dockerfile             # Docker image
├── Dockerfile.prod        # Production Docker image
├── build.sh               # Render build script
├── schema.svg             # Database schema visualization
└── README.md              # This file
```

## Security Features

- **Admin Panel**: Read-only access to user data
- **File Validation**: Only .txt and .docx files allowed
- **File Size Limits**: Maximum 10MB per file
- **Payment Verification**: Files only accessible after payment
- **Activity Logging**: Complete audit trail
- **CSRF Protection**: Enabled for all forms
- **Token Authentication**: Secure API access
- **Input Validation**: Comprehensive data validation

## Troubleshooting

### Common Issues

1. **Celery not working**
   - Ensure Redis is running
   - Check Celery worker is started
   - Verify broker URL in settings

2. **File upload fails**
   - Check payment status
   - Verify file type (.txt or .docx)
   - Ensure file size < 10MB

3. **Payment not working**
   - Verify aamarPay credentials
   - Check network connectivity
   - Verify callback URLs

4. **Database errors**
   - Run `python manage.py migrate`
   - Check database connection
   - Verify environment variables

### Logs

- **Django**: Check console output
- **Celery**: Check Celery worker output
- **Docker**: `docker-compose logs <service>`

## Development Notes

- **Payment Flow**: Uses aamarPay sandbox for testing
- **File Processing**: Asynchronous via Celery
- **Word Count**: Supports .txt and .docx files
- **Frontend**: Bootstrap 5 with vanilla JS
- **API**: RESTful with DRF Token Authentication
- **Database**: PostgreSQL with SQLite fallback
- **Deployment**: Docker and Render ready

## Assessment Requirements Compliance

This project fully implements all requirements specified in the aamarPay Django Task:

### Core Requirements
- **User Authentication**: Complete with Django built-in user model
- **Payment Gateway**: Full aamarPay sandbox integration
- **File Upload**: Restricted to .txt and .docx with 10MB limit
- **Word Count Processing**: Asynchronous via Celery
- **Payment Logging**: Complete transaction tracking
- **RESTful API**: Comprehensive API interface
- **Bootstrap Frontend**: Modern, responsive UI
- **Django Admin**: Secure, read-only admin panel

### Technical Implementation
- **Django MVT**: Proper Model-View-Template architecture
- **Django REST Framework**: Complete API implementation
- **Celery**: Asynchronous task processing
- **Database Design**: Optimized PostgreSQL schema
- **Security**: Comprehensive security measures
- **Documentation**: Complete API and setup documentation

### Deployment Ready
- **Docker Support**: Complete containerization
- **Environment Configuration**: Flexible configuration management
- **Production Settings**: Security-hardened production configuration
- **Build Scripts**: Automated deployment scripts

**Note**: This is a demonstration project using aamarPay sandbox. For production use, ensure proper security measures and use production aamarPay credentials.

import uuid
import requests
import hashlib
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import PaymentTransaction, FileUpload, ActivityLog
from .serializers import FileUploadSerializer, PaymentTransactionSerializer, ActivityLogSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from .tasks import process_file_task
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os


class UploadFileView(APIView):
    """
    Allows file upload only if user has a successful payment.
    Triggers Celery task for word count.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Check if payment exists & is successful
        if not PaymentTransaction.objects.filter(user=request.user, status="success").exists():
            return Response({"error": "Payment required before upload."}, status=403)

        # Validate file
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({"error": "No file provided"}, status=400)
        
        # Check file extension
        allowed_extensions = ['.txt', '.docx']
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension not in allowed_extensions:
            return Response({
                "error": f"Invalid file type. Only {', '.join(allowed_extensions)} files are allowed."
            }, status=400)
        
        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_size:
            return Response({
                "error": f"File too large. Maximum size is {max_size // (1024*1024)}MB."
            }, status=400)

        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file_upload = serializer.save(
                user=request.user, 
                status="processing",
                filename=uploaded_file.name
            )

            # Trigger Celery task for word count
            process_file_task.delay(file_upload.id)

            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action="file_uploaded",
                metadata={"file_id": file_upload.id, "filename": file_upload.filename}
            )

            return Response({"message": "File uploaded and processing started."}, status=201)
        return Response(serializer.errors, status=400)


class FileListView(ListAPIView):
    """List uploaded files for the authenticated user."""
    permission_classes = [IsAuthenticated]
    serializer_class = FileUploadSerializer

    def get_queryset(self):
        return FileUpload.objects.filter(user=self.request.user)


class TransactionListView(ListAPIView):
    """List payment transactions for the authenticated user."""
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentTransactionSerializer

    def get_queryset(self):
        return PaymentTransaction.objects.filter(user=self.request.user)


class ActivityListView(ListAPIView):
    """List activity logs for the authenticated user."""
    permission_classes = [IsAuthenticated]
    serializer_class = ActivityLogSerializer

    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """Initiate aamarPay payment (POST /api/initiate-payment/)"""
    user = request.user
    amount = 100  # fixed as per spec
    tran_id = str(uuid.uuid4())
    
    # Create local record with initiated status
    PaymentTransaction.objects.create(
        user=user, 
        transaction_id=tran_id, 
        amount=amount, 
        status='initiated',
        gateway_response={}
    )

    # Get payment method from request
    payment_method = request.data.get('payment_method', 'VISA')
    
    # Prepare payload for aamarPay
    payload = {
        "store_id": settings.AAMARPAY_STORE_ID,
        "amount": str(amount),
        "payment_type": payment_method,
        "currency": "BDT",
        "tran_id": tran_id,
        "success_url": request.build_absolute_uri('/api/payment/success/'),
        "fail_url": request.build_absolute_uri('/api/payment/fail/'),
        "cancel_url": request.build_absolute_uri('/api/payment/cancel/'),
        "cus_name": user.get_full_name() or user.username,
        "cus_email": user.email or "",
        "cus_add1": "Dhaka",
        "cus_add2": "Dhaka",
        "cus_city": "Dhaka",
        "cus_country": "Bangladesh",
        "cus_phone": "01711111111",
        "cus_postcode": "1000",
        "shipping_method": "NO",
        "num_of_item": "1",
        "product_name": "File Upload Service",
        "product_profile": "general",
        "product_category": "Service"
    }

    # Send to aamarPay sandbox
    try:
        resp = requests.post(settings.AAMARPAY_ENDPOINT, json=payload, timeout=10)
        data = resp.json()
        
        # Response structure depends on aamarPay. They usually return a 'payment_url' or similar.
        # We'll try to pick a redirect url safely:
        redirect_url = data.get('payment_url') or data.get('redirect_url') or data.get('checkout_url')
        
        # Save gateway_response
        PaymentTransaction.objects.filter(transaction_id=tran_id).update(gateway_response=data)
        
        if redirect_url:
            return Response({"redirect_url": redirect_url})
        else:
            return Response({"detail": "failed to create payment", "raw": data}, status=400)
    except Exception as e:
        return Response({"detail": "gateway_error", "error": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])  # called by gateway (but you may add IP checks)
def payment_success(request):
    """Payment success callback (GET /api/payment/success/)"""
    # aamarPay will send query params / POST with data. Extract the tran_id & status.
    tran_id = request.GET.get('tran_id') or request.POST.get('tran_id')
    
    # You should verify signature/validity per aamarPay docs. Here we assume success.
    if not tran_id:
        return Response({"detail": "missing tran_id"}, status=400)
    
    try:
        # Update transaction
        tx = PaymentTransaction.objects.get(transaction_id=tran_id)
        tx.status = 'success'
        tx.gateway_response = dict(request.GET)
        tx.timestamp = timezone.now()
        tx.save()
        
        # Log activity if tx has user
        if tx.user:
            ActivityLog.objects.create(
                user=tx.user, 
                action='payment_success', 
                metadata={'transaction': tran_id, 'amount': str(tx.amount)}
            )
        
        # redirect user to dashboard page
        return redirect('/dashboard/?payment=success&tran_id=' + tran_id)
    except PaymentTransaction.DoesNotExist:
        return Response({"detail": "Transaction not found"}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def payment_fail(request):
    """Payment failure callback"""
    tran_id = request.GET.get('tran_id')
    if tran_id:
        try:
            tx = PaymentTransaction.objects.get(transaction_id=tran_id)
            tx.status = 'failed'
            tx.gateway_response = dict(request.GET)
            tx.save()
            
            if tx.user:
                ActivityLog.objects.create(
                    user=tx.user,
                    action='payment_failed',
                    metadata={'transaction': tran_id, 'reason': 'Gateway failure'}
                )
        except PaymentTransaction.DoesNotExist:
            pass
    
    return redirect('/dashboard/?payment=failed')


@api_view(['GET'])
@permission_classes([AllowAny])
def payment_cancel(request):
    """Payment cancellation callback"""
    tran_id = request.GET.get('tran_id')
    if tran_id:
        try:
            tx = PaymentTransaction.objects.get(transaction_id=tran_id)
            tx.status = 'failed'
            tx.gateway_response = dict(request.GET)
            tx.save()
            
            if tx.user:
                ActivityLog.objects.create(
                    user=tx.user,
                    action='payment_cancelled',
                    metadata={'transaction': tran_id}
                )
        except PaymentTransaction.DoesNotExist:
            pass
    
    return redirect('/dashboard/?payment=cancelled')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """Dashboard view showing file upload form, files, and activity"""
    user = request.user
    
    # Check if user has successful payment
    has_payment = PaymentTransaction.objects.filter(user=user, status="success").exists()
    
    # Get user's data
    files = FileUpload.objects.filter(user=user).order_by('-upload_time')
    transactions = PaymentTransaction.objects.filter(user=user).order_by('-timestamp')
    activities = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:10]
    
    # Get payment status from query params
    payment_status = request.GET.get('payment')
    
    context = {
        'user': user,
        'has_payment': has_payment,
        'files': files,
        'transactions': transactions,
        'activities': activities,
        'payment_status': payment_status == 'success',
    }
    
    return render(request, 'dashboard.html', context)

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to AmmerPay.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Registration failed. Please correct the errors.')
    else:
        form = UserCreationForm()
    
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

def home_view(request):
    """Home page - redirects to dashboard if authenticated, login if not"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_file(request, file_id):
    """Download a file (GET /api/download/<file_id>/)"""
    try:
        file_upload = FileUpload.objects.get(id=file_id, user=request.user)
        
        # Check if file exists
        if not os.path.exists(file_upload.file.path):
            return Response({"error": "File not found on server"}, status=404)
        
        # Log download activity
        ActivityLog.objects.create(
            user=request.user,
            action="file_downloaded",
            metadata={"file_id": file_upload.id, "filename": file_upload.filename}
        )
        
        # Return file response
        response = FileResponse(open(file_upload.file.path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{file_upload.filename}"'
        return response
        
    except FileUpload.DoesNotExist:
        return Response({"error": "File not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_file(request, file_id):
    """Delete a file (DELETE /api/delete/<file_id>/)"""
    try:
        file_upload = FileUpload.objects.get(id=file_id, user=request.user)
        
        # Log deletion activity
        ActivityLog.objects.create(
            user=request.user,
            action="file_deleted",
            metadata={"file_id": file_upload.id, "filename": file_upload.filename}
        )
        
        # Delete the file from storage
        if os.path.exists(file_upload.file.path):
            os.remove(file_upload.file.path)
        
        # Delete the database record
        file_upload.delete()
        
        return Response({"message": "File deleted successfully"})
        
    except FileUpload.DoesNotExist:
        return Response({"error": "File not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

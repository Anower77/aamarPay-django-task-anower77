from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.home_view, name='home'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # API URLs
    path('initiate-payment/', views.initiate_payment, name='initiate-payment'),
    path('payment/success/', views.payment_success, name='payment-success'),
    path('payment/fail/', views.payment_fail, name='payment-fail'),
    path('payment/cancel/', views.payment_cancel, name='payment-cancel'),
    path('upload/', views.UploadFileView.as_view(), name='file-upload'),
    path('files/', views.FileListView.as_view(), name='file-list'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('activity/', views.ActivityListView.as_view(), name='activity-list'),
    path('download/<int:file_id>/', views.download_file, name='download-file'),
    path('delete/<int:file_id>/', views.delete_file, name='delete-file'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]

from django.contrib import admin
from .models import FileUpload, PaymentTransaction, ActivityLog


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'filename', 'status', 'word_count', 'upload_time')
    readonly_fields = ('user', 'filename', 'upload_time', 'word_count', 'status', 'file')
    list_filter = ('status', 'upload_time')
    search_fields = ('filename', 'user__username')
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        # prevent updates through admin (read only)
        return False


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'status', 'timestamp')
    readonly_fields = ('transaction_id', 'user', 'amount', 'status', 'gateway_response', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('transaction_id', 'user__username')
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    readonly_fields = ('user', 'action', 'metadata', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'action')
    
    def has_delete_permission(self, request, obj=None):
        return False

from rest_framework import serializers
from .models import FileUpload, PaymentTransaction, ActivityLog

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['id', 'user', 'file', 'filename', 'upload_time', 'status', 'word_count']
        read_only_fields = ['user', 'filename', 'upload_time', 'status', 'word_count']

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ['id', 'user', 'transaction_id', 'amount', 'status', 'gateway_response', 'timestamp']
        read_only_fields = ['user', 'transaction_id', 'gateway_response', 'timestamp']

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'action', 'metadata', 'timestamp']
        read_only_fields = ['user', 'timestamp']


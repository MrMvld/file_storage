from django.urls import path
from .views import upload_file, download_file, upload_api_test_view, download_api_test_view

urlpatterns = [
    path('upload/', upload_file),
    path('download/<str:file_id>/', download_file),
    path('upload-test/', upload_api_test_view),
    path('download-test/', download_api_test_view),
]
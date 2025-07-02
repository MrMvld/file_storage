from django.http import JsonResponse, HttpResponse
from .models import FileUpload, ActionLog
from .utils import split_and_zip, unzip_and_combine
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import UploadedFile
import uuid
from django.shortcuts import render
from django.contrib.auth.models import User
import mimetypes


@csrf_exempt
def upload_file(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    uploaded_file: UploadedFile = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    if uploaded_file.size > 16 * 1024 * 1024:
        return JsonResponse({'error': 'File too large'}, status=400)

    file_id = str(uuid.uuid4())
    split_and_zip(uploaded_file, file_id)

    user = request.user if request.user.is_authenticated else User.objects.first()

    FileUpload.objects.create(
        file_id=file_id,
        original_filename=uploaded_file.name,
        user=user
    )

    ActionLog.objects.create(user=user, action='upload', file_id=file_id)
    return JsonResponse({'file_id': file_id})


def download_file(request, file_id):
    try:
        file_record = FileUpload.objects.get(file_id=file_id)
    except FileUpload.DoesNotExist:
        return JsonResponse({'error': 'File not found'}, status=404)

    file_bytes = unzip_and_combine(file_id)

    user = request.user if request.user.is_authenticated else User.objects.first()
    ActionLog.objects.create(user=user, action='download', file_id=file_id)

    original_name = file_record.original_filename
    content_type, _ = mimetypes.guess_type(original_name)
    if not content_type:
        content_type = 'application/octet-stream'

    response = HttpResponse(file_bytes, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{original_name}"'
    return response


def upload_api_test_view(request):
    return render(request, 'storage/upload_api_test.html')


def download_api_test_view(request):
    return render(request, 'storage/download_api_test.html')
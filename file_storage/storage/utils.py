import os, zipfile, uuid
from django.conf import settings


def split_and_zip(file, file_id):
    chunk_dir = os.path.join(settings.MEDIA_ROOT, file_id)
    os.makedirs(chunk_dir, exist_ok=True)

    file.seek(0)
    content = file.read()
    size = len(content)
    chunk_size = size // 16

    for i in range(16):
        chunk_data = content[i * chunk_size: (i + 1) * chunk_size] if i < 15 else content[i * chunk_size:]
        zip_path = os.path.join(chunk_dir, f"chunk_{i}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr(f"chunk_{i}", chunk_data)


def unzip_and_combine(file_id):
    chunk_dir = os.path.join(settings.MEDIA_ROOT, file_id)
    combined = b''
    for i in range(16):
        zip_path = os.path.join(chunk_dir, f"chunk_{i}.zip")
        with zipfile.ZipFile(zip_path, 'r') as zf:
            combined += zf.read(f"chunk_{i}")
    return combined

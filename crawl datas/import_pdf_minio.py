import os
from minio import Minio
from minio.error import S3Error

# MinIO configuration
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET = "policy-files"

def get_minio_client():
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

def upload_pdf_to_minio(minio_client, file_path, object_name):
    try:
        # Check if object already exists
        try:
            minio_client.stat_object(MINIO_BUCKET, object_name)
            print(f"Đã tồn tại: {object_name}")
            return f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{object_name}"
        except S3Error:
            pass
        with open(file_path, "rb") as f:
            minio_client.put_object(
                MINIO_BUCKET,
                object_name,
                f,
                os.path.getsize(file_path),
                content_type="application/pdf"
            )
        print(f"Đã upload: {object_name}")
        return f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{object_name}"
    except Exception as e:
        print(f"Lỗi upload {file_path}: {e}")
        return None

def main():
    minio_client = get_minio_client()
    # Ensure bucket exists
    try:
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
            print(f"Đã tạo bucket: {MINIO_BUCKET}")
    except S3Error as e:
        print(f"Lỗi với MinIO bucket: {e}")
        return

    # Lấy danh sách tất cả file PDF trước
    all_pdf_files = []
    pdf_stats = {
        'total': 0,
        'processed': 0,
        'skipped': 0,
        'uploaded': 0,
        'failed': 0
    }

    dir = os.path.dirname(os.path.abspath(__file__)) + "/policies"

    print(f"Đang quét thư mục: {dir}")
    
    # Quét tất cả file PDF
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_stats['total'] += 1
                file_path = os.path.join(root, file)
                all_pdf_files.append(file_path)
                
    print(f"\nTổng số file PDF tìm thấy: {pdf_stats['total']}")
    print("-" * 80)

    # Upload từng file
    for file_path in all_pdf_files:
        pdf_stats['processed'] += 1
        # Tạo object_name là đường dẫn tương đối so với thư mục cha
        rel_path = os.path.relpath(file_path, dir)
        object_name = rel_path.replace('\\', '/').replace(' ', '_')
        
        print(f"[{pdf_stats['processed']}/{pdf_stats['total']}] Đang xử lý: {rel_path}")
        
        url = upload_pdf_to_minio(minio_client, file_path, object_name)
        if url:
            pdf_stats['uploaded'] += 1
            print(f"MinIO URL: {url}")
        else:
            pdf_stats['failed'] += 1
            print(f"Lỗi upload file: {file_path}")
        print("-" * 80)

    # In thống kê
    print("\nKết quả:")
    print(f"Tổng số file PDF: {pdf_stats['total']}")
    print(f"Đã xử lý: {pdf_stats['processed']}")
    print(f"Upload thành công: {pdf_stats['uploaded']}")
    print(f"Lỗi: {pdf_stats['failed']}")

if __name__ == "__main__":
    main()

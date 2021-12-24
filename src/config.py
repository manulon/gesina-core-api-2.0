import os

database_user = os.getenv("DATABASE_USER", "user")
database_password = os.getenv("DATABASE_PASSWORD", "password")
database_name = os.getenv("DATABASE_NAME", "main")
database_host = os.getenv("DATABASE_HOST", "localhost:5432")
minio_url = os.getenv("MINIO_URL", "localhost:9000")
minio_user = os.getenv("MINIO_ROOT_USER", "minioadmin")
minio_password = os.getenv("MINIO_ROOT_PASSWORD", "password")
secret_key = os.getenv("SECRET_KEY", "default")

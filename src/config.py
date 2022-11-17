import os

# Infra
database_user = os.getenv("DATABASE_USER", "user")
database_password = os.getenv("DATABASE_PASSWORD", "password")
database_name = os.getenv("DATABASE_NAME", "main")
database_host = os.getenv("DATABASE_HOST", "localhost:5432")
database_schema = os.getenv("DATABASE_SCHEMA", "gesina")
minio_url = os.getenv("MINIO_URL", "localhost:9000")
minio_user = os.getenv("MINIO_ROOT_USER", "minioadmin")
minio_bucket = os.getenv("MINIO_BUCKET", "gesina")
minio_password = os.getenv("MINIO_ROOT_PASSWORD", "password")
secret_key = os.getenv("SECRET_KEY", "default")

# Application
dry_run = os.getenv("DRY_RUN", False)
fake_activity = os.getenv("FAKE_ACTIVITY", True)
ina_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Imdlc2luYSIsImlhdCI6MTUxNjIzOTAyMn0.OaYf4LiEegSuD--xIXIb0Aocbf-mhiNvnUJXlfo7Ovc"
ina_url = os.getenv("INA_URL", "https://alerta.ina.gob.ar/a5")
ina_token_envio = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.c1_USoWnK3cCAH-EtJH-AspJGZqFnjSQ6yI_2TYpwqo"
ina_url_envio = os.getenv("INA_URL_ENVIO", "https://alerta.ina.gob.ar/test")
max_retries = 3

# Scheduler
scheduler_database_user = os.getenv("DATABASE_USER", "user")
scheduler_database_password = os.getenv("DATABASE_PASSWORD", "password")
scheduler_database_name = os.getenv("DATABASE_NAME", "main")
scheduler_database_host = os.getenv("DATABASE_HOST", "localhost:5432")
scheduler_database_schema = os.getenv("DATABASE_SCHEMA", "scheduler")

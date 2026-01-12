import os
from dataclasses import dataclass, field
from dotenv import find_dotenv, load_dotenv

dotenv_path = find_dotenv()

load_dotenv(dotenv_path)

@dataclass
class AppConfig:
    # ================ CFG. FROM .ENV FILE (REQUIRED)================
    project_name:str = os.getenv("PROJECT_NAME")
    env:str = os.getenv("ENV")
    debug_mode:bool = os.getenv("DEBUG_MODE")
    console_log:bool = os.getenv("CONSOLE_LOG")
    file_log:bool = os.getenv("FILE_LOG")
    # =================== CFG. OUTSIDE .ENV FILE ====================

@dataclass
class DataBaseConfig:
    # ================ CFG. FROM .ENV FILE (REQUIRED)================
    postgres_user:str = os.getenv("POSTGRES_USER")
    postgres_password:str = os.getenv("POSTGRES_PASSWORD")
    postgres_db:str = os.getenv("POSTGRES_DB")

    pgadmin_default_email:str = os.getenv("PGADMIN_DEFAULT_EMAIL")
    pgadmin_default_password:str = os.getenv("PGADMIN_DEFAULT_PASSWORD")
    # =================== CFG. OUTSIDE .ENV FILE ====================

@dataclass
class BucketConfig:
    name: str
    create_backup: bool = True
@dataclass
class MinIOConfig:
    # ================ CFG. FROM .ENV FILE (REQUIRED)================
    minio_root_user:str = os.getenv("MINIO_ROOT_USER")
    minio_root_password:str = os.getenv("MINIO_ROOT_PASSWORD")
    # =================== CFG. OUTSIDE .ENV FILE ====================
    endpoint:str = "localhost:9000"
    secure:bool = False
    bucket_bronze:BucketConfig = field(default_factory=lambda: BucketConfig(name="bucket-bronze"))
    bucket_silver:BucketConfig = field(default_factory=lambda: BucketConfig(name="bucket-silver"))
    bucket_gold:BucketConfig = field(default_factory=lambda: BucketConfig(name="bucket-gold"))



# Create a singleton config object
app_cfg = AppConfig()
data_base_cfg = DataBaseConfig()
minio_cfg = MinIOConfig()


if __name__ == "__main__":
    print(app_cfg)
    print(data_base_cfg)
    print(minio_cfg)
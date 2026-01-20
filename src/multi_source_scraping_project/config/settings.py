"""
Centralized project configuration.
Uses environment variables.
"""

import os
from dataclasses import dataclass, field
from typing import Tuple

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

# =======================================================================================================
#                                              USEFUL FNCS.
# =======================================================================================================
def str2bool(input_str: str) -> bool | None:
    if input_str.lower() in ["true", "yes", "y", "1"]:
        return True
    elif input_str.lower() in ["false", "no", "n", "0"]:
        return False
    else:
        return None

# =======================================================================================================
#                                              APP. CONFIG.
# =======================================================================================================
@dataclass
class AppConfig:
    # ---------------- CFG. FROM .ENV FILE (REQUIRED) ---------------
    project_name: str = os.getenv("PROJECT_NAME")
    env: str = os.getenv("ENV")
    debug_mode: bool = str2bool(os.getenv("DEBUG_MODE"))
    console_log: bool = str2bool(os.getenv("CONSOLE_LOG"))
    file_log: bool = str2bool(os.getenv("FILE_LOG"))
    # ------------------- CFG. OUTSIDE .ENV FILE --------------------

# =======================================================================================================
#                                             DB. CONFIG.
# =======================================================================================================
@dataclass
class DataBaseConfig:
    # ---------------- CFG. FROM .ENV FILE (REQUIRED) ---------------
    # local_pgdb_host: str = os.getenv("LOCAL_PGDB_HOST")
    # postgres_user: str = os.getenv("POSTGRES_USER")
    # postgres_password: str = os.getenv("POSTGRES_PASSWORD")
    # postgres_db: str = os.getenv("POSTGRES_DB")
    # port: int = os.getenv("PORT")
    dsn: str = os.getenv("DSN")

    pgadmin_default_email: str = os.getenv("PGADMIN_DEFAULT_EMAIL")
    pgadmin_default_password: str = os.getenv("PGADMIN_DEFAULT_PASSWORD")
    # ------------------- CFG. OUTSIDE .ENV FILE --------------------

# =======================================================================================================
#                                            MINIO CONFIG.
# =======================================================================================================
@dataclass(frozen=True)
class SpaceConfig:
    name: str
    flow_dir_name: str
    backup_dir_name: str
    backup: bool = False
@dataclass(frozen=True)
class BucketConfig:
    name: str
    spaces: Tuple[SpaceConfig, ...] = field(default_factory=SpaceConfig)
@dataclass
class MinIOConfig:
    # ---------------- CFG. FROM .ENV FILE (REQUIRED) ---------------
    minio_root_user: str = os.getenv("MINIO_ROOT_USER")
    minio_root_password: str = os.getenv("MINIO_ROOT_PASSWORD")
    endpoint: str = os.getenv("ENDPOINT")
    secure: bool = str2bool(os.getenv("SECURE"))
    # ------------------- CFG. OUTSIDE .ENV FILE --------------------
    buckets: Tuple[BucketConfig] = field(default_factory=lambda:
    (
        BucketConfig(
            name="bucket-bronze",
            spaces=(
                SpaceConfig(
                    name="space-site-quotes",
                    flow_dir_name="flow-dir",
                    backup_dir_name="backup-dir",
                    backup=True
                ),
                SpaceConfig(
                    name="space-site-books",
                    flow_dir_name="flow-dir",
                    backup_dir_name="backup-dir",
                    backup=True
                ),
                SpaceConfig(
                    name="space-api-address",
                    flow_dir_name="flow-dir",
                    backup_dir_name="backup-dir",
                    backup=True
                ),
                SpaceConfig(
                    name="space-xslt-bookstores",
                    flow_dir_name="flow-dir",
                    backup_dir_name="backup-dir",
                    backup=True
                )
            ),
        ),
        BucketConfig(
            name="bucket-silver",
            spaces=(
                SpaceConfig(
                    name="space-site-quotes",
                    flow_dir_name="flow-dir",
                    backup_dir_name="backup-dir",
                    backup=True
                ),
                SpaceConfig(
                    name="space-site-books",
                    flow_dir_name="flow-dir",
                    backup_dir_name="backup-dir",
                    backup=True
                ),
                SpaceConfig(
                    name="space-api-address",
                    flow_dir_name="flow-dir",
                    backup_dir_name="backup-dir",
                    backup=True
                ),
                SpaceConfig(
                    name="space-xslt-bookstores",
                    flow_dir_name="flow-dir",
                    backup_dir_name="backup-dir",
                    backup=True
                )
            ),
        ),
        BucketConfig(
            name="bucket-gold",
            spaces=(
                SpaceConfig(
                    name="space-site-quotes",
                    flow_dir_name="flow-dir",
                    backup_dir_name="backup-dir",
                    backup=True
                ),
                SpaceConfig(
                    name="space-site-books",
                    flow_dir_name="flow-dir",
                    backup_dir_name="backup-dir",
                    backup=True
                ),
                SpaceConfig(
                    name="space-api-address",
                    flow_dir_name="flow-dir",
                    backup_dir_name="backup-dir",
                    backup=True
                ),
                SpaceConfig(
                    name="space-xslt-bookstores",
                    flow_dir_name="flow-dir",
                    backup_dir_name="backup-dir",
                    backup=True
                )
            ),
        )
    ))

# =======================================================================================================
#                                             SCRAPER CONFIG.
# =======================================================================================================
@dataclass
class ScraperConfig:
    base_url_quotes:str = "https://quotes.toscrape.com"
    delay: float = 1.0
    timeout: int = 30
    max_retries: int = 3
    max_pages: int = 20

# --- Create a singleton config object
app_cfg = AppConfig()
data_base_cfg = DataBaseConfig()
minio_cfg = MinIOConfig()
scraper_config = ScraperConfig()

if __name__ == "__main__":
    print(app_cfg)
    print(data_base_cfg)
    print(minio_cfg)
    print(scraper_config)
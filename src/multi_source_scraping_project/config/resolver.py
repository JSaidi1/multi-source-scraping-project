from typing import Optional
from config.settings import MinIOConfig, BucketConfig, SpaceConfig
# from settings import MinIOConfig, BucketConfig, SpaceConfig


# -----------------------------------
# Bucket / Space resolver helpers
# -----------------------------------
def get_bucket(minio_cfg: MinIOConfig, bucket_name: str) -> Optional[BucketConfig]:
    """Return the BucketConfig with the given name, or None if not found."""
    for bucket in minio_cfg.buckets:
        if bucket.name == bucket_name:
            return bucket
    return None


def get_space(minio_cfg: MinIOConfig, bucket_name: str, space_name: str) -> Optional[SpaceConfig]:
    """Return the SpaceConfig for the given bucket and space name."""
    bucket = get_bucket(minio_cfg, bucket_name)
    if not bucket:
        return None
    for space in bucket.spaces:
        if space.name == space_name:
            return space
    return None


def list_bucket_names(minio_cfg: MinIOConfig) -> list[str]:
    """Return all bucket names."""
    return [bucket.name for bucket in minio_cfg.buckets]


def list_space_names(minio_cfg: MinIOConfig, bucket_name: str) -> list[str]:
    """Return all space names in a bucket."""
    bucket = get_bucket(minio_cfg, bucket_name)
    if not bucket:
        return []
    return [space.name for space in bucket.spaces]


def bucket_has_space(minio_cfg: MinIOConfig, bucket_name: str, space_name: str) -> bool:
    """Check if a bucket contains a given space."""
    return get_space(minio_cfg, bucket_name, space_name) is not None


def all_backed_up_spaces(minio_cfg: MinIOConfig) -> list[tuple[str, str]]:
    """
    Return a list of (bucket_name, space_name) for all spaces with backup=True
    """
    result = []
    for bucket in minio_cfg.buckets:
        for space in bucket.spaces:
            if space.backup:
                result.append((bucket.name, space.name))
    return result

def all_not_backed_up_spaces(minio_cfg: MinIOConfig) -> list[tuple[str, str]]:
    """
    Return a list of (bucket_name, space_name) for all spaces with backup=False
    """
    result = []
    for bucket in minio_cfg.buckets:
        for space in bucket.spaces:
            if not space.backup:
                result.append((bucket.name, space.name))
    return result

def get_flow_dir_name(minio_cfg: MinIOConfig, bucket_name: str, space_name: str) -> str | None:
    """Return the flow_dir_name for the given bucket and space name."""
    for bucket in minio_cfg.buckets:
        if bucket.name == bucket_name:
            for space in bucket.spaces:
                if space.name == space_name:
                    return space.flow_dir_name
    return None

def get_backup(minio_cfg: MinIOConfig, bucket_name: str, space_name: str) -> bool:
    """Return True if the given bucket name and space name have bucket = True, False otherwise."""
    for bucket in minio_cfg.buckets:
        if bucket.name == bucket_name:
            for space in bucket.spaces:
                if space.name == space_name:
                    if isinstance(space.backup, bool):
                        if space.backup:
                            return True
                    return False
    return False

def get_backup_dir_name(minio_cfg: MinIOConfig, bucket_name: str, space_name: str) -> str | None:
    """Return the backup_dir_name for the given bucket and space name."""
    for bucket in minio_cfg.buckets:
        if bucket.name == bucket_name:
            for space in bucket.spaces:
                if space.name == space_name:
                    return space.backup_dir_name
    return None

def print_config_summary(minio_cfg: MinIOConfig) -> None:
    """Print a simple summary of buckets and spaces."""
    for bucket in minio_cfg.buckets:
        print(f"Bucket: {bucket.name}")
        for space in bucket.spaces:
            backup_str = "yes" if space.backup else "no"
            print(f"  Space: {space.name}, Flow dir: {space.flow_dir_name}, Backup dir: {backup_str}")

if __name__ == "__main__":
    minio_cfg = MinIOConfig()
    # print("\n=== get_bucket()")
    # print(get_bucket(minio_cfg, "bucket-bronze"))
    # print("\n=== get_space()")
    # print(get_space(minio_cfg, "bucket-bronze", "space-site-books"))
    # print("\n=== list_bucket_names()")
    # print(list_bucket_names(minio_cfg))
    # print("\n=== list_space_names()")
    # print(list_space_names(minio_cfg, "bucket-bronze"))
    # print("\n=== all_backed_up_spaces()")
    # print(all_backed_up_spaces(minio_cfg))
    # print("\n=== bucket_has_space()")
    # print(bucket_has_space(minio_cfg, "bucket-bronze", "space-site-books"))
    # print("\n=== all_backed_up_spaces()")
    # print(all_backed_up_spaces(minio_cfg))
    print("\n=== get_flow_dir_name()")
    print(get_flow_dir_name(minio_cfg, "bucket-gold", "space-site-books"))
    # print("\n=== get_backup()")
    # print(get_backup(minio_cfg, "bucket-gold", "space-site-books"))
    # print("\n=== get_backup_dir_name()")
    # print(get_backup_dir_name(minio_cfg, "bucket-gold", "space-site-books"))
    # print("\n=== all_not_backed_up_spaces()")
    # print(all_not_backed_up_spaces(minio_cfg))
    # print("\n=== print_config_summary()")
    # print_config_summary(minio_cfg)


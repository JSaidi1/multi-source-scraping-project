"""
MinIO client for object storage.
main functions:
    put_object(): Put flow object in a space in a bucket. Creates a timestamped backup if backup = True
    list_objects(): List objects in a bucket
    pull_object_flow(): Download a flow object from a MinIO bucket (from a space) to the local file
    pull_object_archive(): Download a backup object from a MinIO bucket (from a space) to the local file
    delete_object_flow(): Delete a flow object from a space in a bucket
    delete_object_archive(): Delete an archive object from a space in a bucket
    reset_minio(): Completely resets a MinIO instance by deleting all objects and all buckets
"""
import inspect
from datetime import datetime
from io import BytesIO
from pathlib import Path

from minio import Minio
from minio.deleteobjects import DeleteObject
from minio.error import S3Error
from config.settings import minio_cfg, app_cfg
from config.resolver import list_bucket_names, list_space_names, get_space, get_backup, get_flow_dir_name, get_backup_dir_name
from utils.utils_logs import log_message


class MinIOStorage:

    def __init__(self):
        # === Get log cfg.
        self.debug_mode = app_cfg.debug_mode
        self.console_log = app_cfg.console_log
        self.file_log = app_cfg.file_log
        # === Initiate MinIO client
        self.client = Minio(
            endpoint=minio_cfg.endpoint,
            access_key=minio_cfg.minio_root_user,
            secret_key=minio_cfg.minio_root_password,
            secure=minio_cfg.secure
        )
        # === Ensure buckets and folders
        self._ensure_buckets_and_folders()
        # === Ensure local storage folder
        self.local_storage_folder = self._ensure_local_storage_folder()

    def _ensure_local_storage_folder(self) -> str | None:
        """Ensure local storage folder (minio_local_storage)."""
        local_storage_folder_name = "minio_local_storage"
        try:
            frame = inspect.currentframe()
            file_path = inspect.getfile(frame)
            minio_local_storage_path = os.path.join(os.path.dirname(os.path.abspath(file_path)), local_storage_folder_name)
            # Create folder if it doesn't exist
            os.makedirs(minio_local_storage_path, exist_ok=True)
            return minio_local_storage_path
        except Exception as e:
            log_message("error",
                        f"fail to ensure local storage folder '{local_storage_folder_name}' : {e}",
                        self.file_log, self.console_log, self.debug_mode)
            return None


    def _ensure_folder_in_bucket(self, bucket_name:str, folder_name:str):
        """Check if a folder exists in a bucket, and create it if it doesn't."""
        if not folder_name.endswith('/'):
            folder_name += '/'  # Ensure trailing slash

        try:
            ## Check if any object exists with this prefix
            objects = self.client.list_objects(bucket_name, prefix=folder_name, recursive=True)
            first_object = next(objects, None)
            if first_object is None:
                ## Create a zero-byte object to represent the folder
                self.client.put_object(bucket_name, folder_name, BytesIO(b""), length=0)
                log_message("info", f"Folder '{folder_name}' created in bucket '{bucket_name}'", self.file_log, self.console_log, self.debug_mode)
        except S3Error as e:
            log_message("error", f"minio error: fail to ensure folder '{folder_name}' inside bucket '{bucket_name}': {e}", self.file_log, self.console_log, self.debug_mode)
            return None
        except Exception as e:
            log_message("error", f"unknown error: fail to ensure folder '{folder_name}' inside bucket '{bucket_name}': {e}", self.file_log, self.console_log, self.debug_mode)
            return None

    def _ensure_buckets_and_folders(self) -> None:
        """
        Ensure buckets and required folders exist in MinIO based on the config.

        Folder structure:

        <bucket 1>/
            <folder 1>/
                ...
        <bucket 2>/
            <folder 1>/
                ...
        ...
        """
        try:
            bucket_names = list_bucket_names(minio_cfg)
            for bucket_name in bucket_names:
                ## 1. Ensure bucket exists
                if not self.client.bucket_exists(bucket_name):
                    self.client.make_bucket(bucket_name)
                    log_message("info", f"created bucket: {bucket_name}", self.file_log, self.console_log, self.debug_mode)
                ## 2. Ensure folders in the buckets
                space_names = list_space_names(minio_cfg, bucket_name) # get space cfg. for bucket
                for space_name in space_names:
                    space_cfg = get_space(minio_cfg, bucket_name, space_name)
                    self._ensure_folder_in_bucket(bucket_name, space_name + "/" + space_cfg.flow_dir_name)
                    if space_cfg.backup:
                        self._ensure_folder_in_bucket(bucket_name, space_name + "/" + space_cfg.backup_dir_name)
        except S3Error as e:
            log_message("error", f"minio error: failed to ensure buckets & folders: {e}", self.file_log, self.console_log, self.debug_mode)
            return None
        except Exception as e:
            log_message("error", f"unknown error: failed to ensure buckets & folders: {e}", self.file_log, self.console_log, self.debug_mode)
            return None

    def _upload_object(self, bucket_name:str, object_path_remote:str, object_path_local:str) -> None:
        """
        Upload an object in the bucket.
        :param bucket_name:
        :param object_name:
        :return:
        """

        try:
            self.client.fput_object(
                bucket_name=bucket_name,
                object_name=object_path_remote, # remote (to choose)
                file_path=object_path_local # local
            )
            log_message("info", f"upload successful of object '{object_path_remote}' into bucket '{bucket_name}'", self.file_log, self.console_log, self.debug_mode)
        except S3Error as e:
            log_message("error", f"minio error: failed to upload object '{object_path_local}' into bucket '{bucket_name}': {e}", self.file_log, self.console_log, self.debug_mode)
            return None
        except Exception as e:
            log_message("error", f"unknown error: failed to upload object '{object_path_local}' into bucket '{bucket_name}': {e}", self.file_log, self.console_log, self.debug_mode)
            return None

    def _object_exists(self, bucket_name: str, object_name:str) -> bool:
        """Check if an object exists in the bucket. Returns True if it exists. Otherwise, returns False."""
        try:
            self.client.stat_object(bucket_name, object_name)
            return True
        except S3Error as exc:
            if exc.code in ("NoSuchKey", "NoSuchObject", "NoSuchBucket"):
                return False
            raise  # re-raise unexpected errors

    def put_object(
            self,
            bucket_name: str,
            space_name: str,
            object_name_local: str,
            new_object_name_remote: str=None
    ) -> None:
        """
        Put flow object in a space in a bucket. Creates a timestamped backup if backup = True.

        Kinematic: local -> MinIO.
        """
        try:
            ## === Get object local path
            object_local_path = os.path.join(self.local_storage_folder, object_name_local)
            ## Check that object_name exists in local
            if not os.path.exists(object_local_path):
                if self.debug_mode:
                    raise FileNotFoundError(f"local object not found: '{object_local_path}'")
                else:
                    raise FileNotFoundError(f"local object not found: '{object_name_local}'")
            ## === Get remote flow path for this bucket & this space_name
            flow_dir_name = get_flow_dir_name(minio_cfg, bucket_name, space_name)
            flow_dir_path = space_name + "/" + flow_dir_name
            if new_object_name_remote is not None:
                object_flow_path = flow_dir_path + "/" + new_object_name_remote
            else:
                object_flow_path = flow_dir_path + "/" + object_name_local
            ## === Upload flow object in the bucket
            self._upload_object(bucket_name, object_flow_path, object_local_path)

            ## === Upload object in back up folder (if backup == True)
            backup = get_backup(minio_cfg, bucket_name, space_name)  # True or False
            if backup:
                # Get backup_dir_name for this bucket & this space_name
                backup_dir_name = get_backup_dir_name(minio_cfg, bucket_name, space_name)
                backup_dir_path = space_name + "/" + backup_dir_name
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                # === Naming operations
                # Get extension of object name (if exists)
                ext = Path(object_name_local).suffix
                # Remove extension from object name (if exists)
                object_name = Path(object_name_local).stem
                # Concat
                object_path_bck = backup_dir_path + "/" + object_name + "-" + timestamp
                # Finally, add extension at the end of the new name of the object
                object_path_bck = object_path_bck + ext
                # Check if object_name_bck already exists in bucket
                if self._object_exists(bucket_name, object_path_bck):
                    # Remove extension from object name (if exists)
                    object_path_bck = os.path.splitext(object_path_bck)[0]
                    # Add "_" to object name
                    object_path_bck = object_path_bck + "_"
                    # Add extension at the end of the new name of the object
                    object_path_bck = object_path_bck + ext
                # === Upload object
                self._upload_object(bucket_name, object_path_bck, object_local_path)
        except S3Error as e:
            log_message("error", f"minio error: failed to put object '{object_name_local}' in space '{space_name}' in bucket '{bucket_name}': {e}", self.file_log, self.console_log, self.debug_mode)
            return None
        except Exception as e:
            log_message("error", f"unknown error: failed to put object '{object_name_local}' in space '{space_name}' in bucket '{bucket_name}': {e}", self.file_log, self.console_log, self.debug_mode)
            return None


    def list_objects(self, bucket: str, prefix: str = "") -> list[dict]:
        """List objects in a bucket."""
        objects = self.client.list_objects(bucket, prefix=prefix, recursive=True)
        return [
            {
                "name": obj.object_name,
                "size": obj.size,
                "modified": obj.last_modified
            }
            for obj in objects
        ]

    def pull_object_flow(
            self,
            bucket_name: str,
            space_name: str,
            object_name: str
    ) -> None:
        """
        Download a flow object from a MinIO bucket (from a space) to the local file.

        Kinematic: MinIO -> local.
        """
        try:
            # Get flow_dir_name for this bucket & this space_name
            flow_dir_name = get_flow_dir_name(minio_cfg, bucket_name, space_name)
            flow_dir_path = space_name + "/" + flow_dir_name
            object_path = flow_dir_path + "/" + object_name
            # Download object
            self.client.fget_object(bucket_name, object_path, os.path.join(self.local_storage_folder, object_name))
            log_message("info",
                        f"flow object '{object_name}' from the space '{space_name}' from bucket '{bucket_name}' downloaded successfully in local storage folder",
                        self.file_log, self.console_log, self.debug_mode)
        except S3Error as e:
            log_message("error",
                            f"minio error: failed to download flow object '{object_name}' from the space '{space_name}' from bucket '{bucket_name}': {e}",
                            self.file_log, self.console_log, self.debug_mode)
            return None
        except Exception as e:
            log_message("error",
                        f"unknown error: failed to download flow object '{object_name}' from the space '{space_name}' from bucket '{bucket_name}': {e}",
                        self.file_log, self.console_log, self.debug_mode)
            return None

    def pull_object_archive(
            self,
            bucket_name: str,
            space_name: str,
            object_name: str
    ) -> None:
        """
        Download a backup object from a MinIO bucket (from a space) to the local file.

        Kinematic: MinIO -> local.
        """
        try:
            # Get backup_dir_name for this bucket & this space_name
            backup_dir_name = get_backup_dir_name(minio_cfg, bucket_name, space_name)
            backup_dir_path = space_name + "/" + backup_dir_name
            object_path = backup_dir_path + "/" + object_name
            # Download object
            self.client.fget_object(bucket_name, object_path, os.path.join(self.local_storage_folder, object_name))
            log_message("info",
                        f"backup object '{object_name}' from the space '{space_name}' from bucket '{bucket_name}' downloaded successfully in local storage folder",
                        self.file_log, self.console_log, self.debug_mode)
        except S3Error as e:
            log_message("error",
                            f"minio error: failed to download backup object '{object_name}' from the space '{space_name}' from bucket '{bucket_name}': {e}",
                            self.file_log, self.console_log, self.debug_mode)
            return None
        except Exception as e:
            log_message("error",
                        f"unknown error: failed to download backup object '{object_name}' from the space '{space_name}' from bucket '{bucket_name}': {e}",
                        self.file_log, self.console_log, self.debug_mode)
            return None

    # def upload_image(
    #         self,
    #         image_data: bytes,
    #         filename: str,
    #         content_type: str = "image/jpeg"
    # ) -> Optional[str]:
    #     """Upload une image d'auteur."""
    #     try:
    #         self.client.put_object(
    #             bucket_name=minio_cfg.bucket_images,
    #             object_name=filename,
    #             data=io.BytesIO(image_data),
    #             length=len(image_data),
    #             content_type=content_type
    #         )
    #
    #         return f"minio://{minio_cfg.bucket_images}/{filename}"
    #
    #     except S3Error as e:
    #         logger.error("image_upload_failed", error=str(e))
    #         return None
    #

    def delete_object_flow(self, bucket_name: str, space_name: str, object_name: str) -> bool:
        """Delete a flow object from a space in a bucket."""
        try:
            # Get flow_dir_name for this bucket & this space_name
            flow_dir_name = get_flow_dir_name(minio_cfg, bucket_name, space_name)
            flow_dir_path = space_name + "/" + flow_dir_name
            object_path = flow_dir_path + "/" + object_name
            # Remove object
            self.client.stat_object(bucket_name, object_path)
            self.client.remove_object(bucket_name, object_path)
            log_message("info",
                        f"flow object '{object_name}' in the space '{space_name}' deleted from bucket '{bucket_name}' successfully",
                        self.file_log, self.console_log, self.debug_mode)
            return True
        except S3Error as e:
            if e.code in ("NoSuchKey", "NotFound"):
                log_message("error",
                            f"minio error: failed to delete flow object '{object_name}' in the space '{space_name}' from bucket '{bucket_name}'. object not found",
                            self.file_log, self.console_log, self.debug_mode)
                return False
            else:
                log_message("error",
                            f"minio error: failed to delete flow object '{object_name}' in the space '{space_name}' from bucket '{bucket_name}': {e}",
                            self.file_log, self.console_log, self.debug_mode)
                return False
        except Exception as e:
            log_message("error",
                        f"unknown error: failed to delete flow object '{object_name}' in the space '{space_name}' from bucket '{bucket_name}': {e}",
                        self.file_log, self.console_log, self.debug_mode)
            return False

    def delete_object_archive(self, bucket_name: str, space_name: str, object_name: str) -> bool:
        """Delete an archive object from a space in a bucket."""
        try:
            # Get backup_dir_name for this bucket & this space_name
            backup_dir_name = get_backup_dir_name(minio_cfg, bucket_name, space_name)
            backup_dir_path = space_name + "/" + backup_dir_name
            object_path = backup_dir_path + "/" + object_name
            # Remove object
            self.client.stat_object(bucket_name, object_path)
            self.client.remove_object(bucket_name, object_path)
            log_message("info",
                        f"backup object '{object_name}' in the space '{space_name}' deleted from bucket '{bucket_name}' successfully",
                        self.file_log, self.console_log, self.debug_mode)
            return True
        except S3Error as e3:
            if e3.code in ("NoSuchKey", "NotFound"):
                log_message("error",
                            f"minio error: failed to delete backup object '{object_name}' in the space '{space_name}' from bucket '{bucket_name}'. object not found",
                            self.file_log, self.console_log, self.debug_mode)
                return False
            else:
                log_message("error",
                            f"minio error: failed to delete backup object '{object_name}' in the space '{space_name}' from bucket '{bucket_name}': {e}",
                            self.file_log, self.console_log, self.debug_mode)
                return False
        except Exception as e:
            log_message("error",
                        f"unknown error: failed to delete backup object '{object_name}' in the space '{space_name}' from bucket '{bucket_name}': {e}",
                        self.file_log, self.console_log, self.debug_mode)
            return False

    def reset_minio(self) -> bool:
        """
        Completely resets a MinIO instance by deleting all objects
        and all buckets.

        This function performs a destructive operation:
        - Iterates over every bucket in the MinIO instance
        - Deletes all objects within each bucket
        - Removes each bucket once empty

        ⚠️ WARNING:
            This operation is irreversible and will permanently delete
            all stored data. It should only be used in development,
            testing, or controlled administrative environments.
        """
        try:
            buckets = self.client.list_buckets()

            for bucket in buckets:
                bucket_name = bucket.name
                log_message("info", f"processing bucket: {bucket_name}", self.file_log, self.console_log, self.debug_mode)

                ## 1) delete all bucket objects
                objects = self.client.list_objects(bucket_name, recursive=True)
                delete_objects = (
                    DeleteObject(obj.object_name) for obj in objects
                )

                errors = self.client.remove_objects(bucket_name, delete_objects)
                for error in errors:
                    log_message("error", f"delete error in {bucket_name}: {error}", self.file_log, self.console_log, self.debug_mode)
                ## 2) delete the bucket
                self.client.remove_bucket(bucket_name)
                log_message("info", f"bucket removed: {bucket_name}", self.file_log, self.console_log, self.debug_mode)
            log_message("info", f"minio reset completed", self.file_log, self.console_log, self.debug_mode)
            return True
        except S3Error as e:
            log_message("error", f"minio error: minio reset failed:, {e}", self.file_log, self.console_log, self.debug_mode)
            return False
        except Exception as e:
            log_message("error", f"unknown error: minio reset failed:, {e}", self.file_log, self.console_log, self.debug_mode)
            return False


if __name__ == '__main__':
    print("=== in minio_client.py ===")
    import os
    script_dir = os.getcwd()
    print(script_dir)
import os
import pytest
from unittest.mock import MagicMock
from storage.minio_client import MinIOStorage

# === Dummy Configs ===
class DummyAppCfg:
    debug_mode = True
    console_log = True
    file_log = False

class DummyMinioCfg:
    endpoint = "localhost:9000"
    minio_root_user = "minioadmin"
    minio_root_password = "minioadmin"
    secure = False

# === Global patch for configs and Minio client ===
@pytest.fixture(autouse=True)
def patch_globals(monkeypatch):
    monkeypatch.setattr("storage.minio_client.app_cfg", DummyAppCfg)
    monkeypatch.setattr("storage.minio_client.minio_cfg", DummyMinioCfg)
    monkeypatch.setattr("storage.minio_client.Minio", MagicMock())
    yield


# === Patch _ensure_local_storage_folder to avoid real file I/O ===
@pytest.fixture
def patch_local_folder(monkeypatch, tmp_path):
    def _mock_ensure_local_storage_folder(self):
        folder = tmp_path / "local_storage"
        folder.mkdir(exist_ok=True)
        return str(folder)

    monkeypatch.setattr("storage.minio_client.MinIOStorage._ensure_local_storage_folder", _mock_ensure_local_storage_folder)
    yield


# === Patch _ensure_buckets_and_folders to allow call tracking ===
@pytest.fixture
def patch_buckets(monkeypatch):
    mock_method = MagicMock()
    monkeypatch.setattr("storage.minio_client.MinIOStorage._ensure_buckets_and_folders", mock_method)
    return mock_method


# --- Test 1: Initialization attributes & Minio client ---
def test_minio_storage_init(patch_local_folder, patch_buckets):
    storage = MinIOStorage()

    # Attributes from app_cfg
    assert storage.debug_mode is True
    assert storage.console_log is True
    assert storage.file_log is False

    # Minio client called with correct arguments
    from storage.minio_client import Minio
    Minio.assert_called_once_with(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )


# --- Test 2: _ensure_local_storage_folder creates folder in tmp_path ---
def test_ensure_local_storage_folder(tmp_path, patch_local_folder, patch_buckets):
    storage = MinIOStorage()

    # Folder should exist
    assert os.path.exists(storage.local_storage_folder)
    # Folder path should be inside tmp_path
    assert str(tmp_path) in storage.local_storage_folder


# --- Test 3: _ensure_buckets_and_folders is called during __init__ ---
def test_ensure_buckets_called(patch_local_folder, patch_buckets):
    storage = MinIOStorage()

    # Ensure _ensure_buckets_and_folders was called exactly once
    patch_buckets.assert_called_once()

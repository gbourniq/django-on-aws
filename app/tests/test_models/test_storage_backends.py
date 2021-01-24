"""This module defines tests for the S3 storage backend configuration"""

from app.main.storage_backends import PublicMediaStorage, StaticStorage


def test_static_storage_instance():
    """Tests AWS storage backend variables are set"""
    static_storage = StaticStorage()
    assert static_storage.location == "staticfiles/"
    assert static_storage.default_acl == "public-read"


def test_public_media_storage_instance():
    """Tests AWS storage backend variables are set"""
    public_media_storage = PublicMediaStorage()
    assert public_media_storage.location == "mediafiles/"
    assert public_media_storage.default_acl == "public-read"
    assert not public_media_storage.file_overwrite

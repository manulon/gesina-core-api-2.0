from unittest import TestCase
from unittest.mock import Mock

import pytest

from src.service import file_storage_service
from src.service.exception.file_exception import FileUploadEmpty

MOCK_OBJECT = Mock()


class TestFileStorageService(TestCase):
    def test_throw_file_upload_exception_on_empty_files(self):
        with pytest.raises(FileUploadEmpty):
            file_storage_service.validate_file([])

    def test_throw_file_upload_exception_on_invalid_files(self):
        with pytest.raises(FileUploadEmpty):
            file_storage_service.validate_file({"some": "thing"})

    # @mock.patch('src.service.file_storage_service.current_app')
    # def test_throw_file_upload_exception_on_storage_error(self, app):
    #     app.get_logger.logger.error = lambda x: print(x)
    #
    #     file_path = Path(__file__).with_name('dummy_geometry.g01')
    #     with file_path.open('rb') as file:
    #         file_storage_service.save_geometry(file)

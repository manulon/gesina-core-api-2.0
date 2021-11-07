import pytest
from unittest import TestCase, mock
from unittest.mock import Mock
from src.service import geometry_service
from src.service.exception.geometry_exception import GeometryMissingValue

MOCK_OBJECT = Mock()


class TestGeometryService(TestCase):
    def test_throw_geometry_exception_on_invalid_creation_form(self):
        with pytest.raises(GeometryMissingValue):
            request = Mock()
            request.form = None
            geometry_service.validate_creation_request(request)

    def test_throw_geometry_exception_on_missing_description(self):
        with pytest.raises(GeometryMissingValue):
            request = Mock()
            request.form = {"description": None}
            geometry_service.validate_creation_request(request)

    def test_creation_data_without_errors(self):
        request = Mock()
        request.form = {"description": "some_description"}
        file = Mock()
        file.filename = "some_geometry.g01"
        request.files = {"file": file}
        geometry_service.validate_creation_request(request)

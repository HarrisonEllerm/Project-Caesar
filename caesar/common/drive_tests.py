import unittest
from unittest.mock import patch, Mock
import pytest
import googleapiclient.errors


from caesar.common.drive_utils import DriveUtilities


class MyTestCase(unittest.TestCase):

    @patch('caesar.common.drive_utils.DriveUtilities.upload_file')
    def test_successful_upload(self, mock_request):
        mock_request.return_value.ok = True
        response = DriveUtilities.upload_file()
        assert(response is not None)

    @patch('caesar.common.drive_utils.DriveUtilities.upload_file')
    def test_404_upload_response(self, mock_request):
        exc = googleapiclient.errors.HttpError(resp=Mock(status=404), content=str.encode("not found"))
        mock_request.side_effect = exc

        with pytest.raises(googleapiclient.errors.HttpError) as error_info:
            DriveUtilities.upload_file()
            assert error_info == exc


if __name__ == '__main__':
    unittest.main()

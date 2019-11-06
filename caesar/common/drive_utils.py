"""
drive_utils.py: Provides utility methods for common drive operations
"""
from googleapiclient.http import MediaFileUpload
from apiclient import errors
import backoff


def fatal_upload_code(e):
    """
    Used to determine if a HTTP error code is fatal or not.
    :param e: The HTTP error.
    :return: False if error status is 404 or in the 500's, True otherwise.
    """
    if e.resp.status == 404 or 500 <= e.resp.status:
        return False
    else:
        return True


class DriveUtilities:

    def __init__(self, drive_service, logger):
        self.drive_service = drive_service
        self.logger = logger

    @backoff.on_exception(backoff.expo,
                          errors.HttpError,
                          max_time=100,
                          giveup=fatal_upload_code,
                          logger='app')
    def upload_file(self, drive_file_name, drive_folder_id, file_path):
        """
        Uploads a file to the folder specified.
        :param drive_file_name: the name of the file being uploaded.
        :param drive_folder_id: the id of the folder being uploaded to.
        :param file_path: the file path of the file being uploaded.
        :return: True if upload successful, False otherwise.
        :raises HttpError if upload is unsuccessful, which may trigger a
        retry. See https://developers.google.com/drive/api/v3/manage-uploads#errors.
        """

        file_metadata = {'name': drive_file_name, 'parents': [drive_folder_id]}

        media = MediaFileUpload(file_path,
                                mimetype='video/mp4',
                                resumable=True)

        uploaded_file = self.drive_service.files().create(body=file_metadata,
                                                          media_body=media,
                                                          fields='id').execute()

        self.logger.info(f">>>Google Drive: File uploaded with id: {uploaded_file.get('id')}")


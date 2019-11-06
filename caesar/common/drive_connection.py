import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Google drive scope - allows this app to manage files it has created.
# See: https://developers.google.com/identity/protocols/googlescopes#drivev3
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def get_drive_service():
    """
    Authenticates the app and grabs connection to Google Drive.
    :return: An instance of the Google drive service.
    """
    creds = None
    # Token.pickle is used to store the access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as tk:
            creds = pickle.load(tk)

    # If there are no (valid) creds log app in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

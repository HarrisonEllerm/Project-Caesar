"""
detect.py: Detects & records motion through Pi Security Cam.
"""

import datetime
import sys
import time
import configparser
import subprocess
from apiclient import errors
from gpiozero import MotionSensor
from picamera import PiCamera, Color
from caesar.common.drive_connection import get_drive_service
from caesar.common.logging_utils import LogUtils
from caesar.common.drive_utils import DriveUtilities

# Logger used to output logs to file and console
logger = LogUtils.get_file_and_console_logger('app', 'a')

# Service instance used to store recordings in Google Drive
drive_service = get_drive_service()


def detect_and_record_motion():
    """
    Detects and records motion via interfacing with PIR sensor and camera.
    Saves the recording locally then triggers a function to upload/clean up
    """
    # Grab folder id from config file
    conf = configparser.ConfigParser()
    conf.read('config.ini')
    vid_pth = conf['tmp_dir']['path']
    drive_folder_id = conf['google_drive']['folder_id']

    # Create utilities instance
    drive_utils = DriveUtilities(drive_service, logger)

    # Motion sensor module connected to pin 4 (5v)
    pir = MotionSensor(4)
    camera = PiCamera()
    camera.resolution = (1280, 720)
    camera.vflip = True

    try:

        while True:

            # PIR sensor triggered, camera starts recording for a minimum of 10 seconds
            pir.wait_for_active()
            logger.info('>>>PIR sensor: Motion detected')
            triggered_datetime = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
            file_path = vid_pth + triggered_datetime + '.h264'
            camera.start_recording(file_path)
            camera.annotate_background = Color('red')
            camera.annotate_text_size = 20
            camera.annotate_text = triggered_datetime
            time.sleep(10)

            # PIR sensor becomes inactive, camera stops recording and file is uploaded
            pir.wait_for_inactive()
            camera.stop_recording()
            logger.info('>>>PIR sensor: Motion ended')
            clean_and_upload(file_path, drive_utils, drive_folder_id)

    except KeyboardInterrupt:
        camera.close()
        sys.exit()


def clean_and_upload(h264_filepath, drive_utils, drive_folder_id):
    """
    Converts the .h264 file which is the raw output of the camera
    to an MP4 file locally, then attempts to upload the file to
    Google drive. Uses the MP4Box tool, see: https://gpac.wp.imt.fr/mp4box/
    :param h264_filepath: The original raw output file path.
    :param drive_utils: The drive utilities instance.
    :param drive_folder_id: The ID of the folder being uploaded to.
    :return:
    """
    mp4_file_path, drive_file_name = get_mp4_file_path_and_drive_name(h264_filepath)

    # Convert the .h264 file to .MP4
    subprocess.run([f'MP4Box -fps 30 -add {h264_filepath} {mp4_file_path}'],
                   capture_output=True, shell=True)

    # Clean up .h264 file
    subprocess.run([f'rm {h264_filepath}'],
                   capture_output=False, shell=True)

    try:
        drive_utils.upload_file(drive_file_name, drive_folder_id, mp4_file_path)
        subprocess.run([f'rm {mp4_file_path}'],
                       capture_output=False, shell=True)

    except errors.HttpError as e:
        logger.info(f'>>>Google Drive: An HTTP error occurred and was fatal: {e.resp}')


def get_mp4_file_path_and_drive_name(h264_filepath):
    """
    Manipulates original file path with .h264 extension.
    Returns an .mp4 file path for conversion and a file
    name for Google Drive.
    :param h264_filepath:
    :return: The mp4 file path and drive file name.
    """
    # Splits by '.' to get path before extension
    h264_filepath_split_no_ext = h264_filepath.split('.')
    mp4_filepath = h264_filepath_split_no_ext[0] + '.mp4'

    # Splits by '/' to get filename at end of path for storage in Drive
    h264_filepath_split_no_slashes = h264_filepath_split_no_ext[0].split('/')
    drive_file_name = h264_filepath_split_no_slashes[len(h264_filepath_split_no_slashes) - 1] + '.mp4'

    return mp4_filepath, drive_file_name


if __name__ == '__main__':
    logger.info("Security System Armed")
    detect_and_record_motion()

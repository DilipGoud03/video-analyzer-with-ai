from apscheduler.schedulers.background import BackgroundScheduler
from services.utility import UtilityService
from logger_app import setup_logger

# Initialize services and logger
utility_service = UtilityService()
logger = setup_logger(__name__)
scheduler = BackgroundScheduler()


# ------------------------------------------------------------
# Method: remove_unwanted_videos
# Description:
#   Scans the ORG_DIR for video files and deletes any file that
#   does not exist in the database. This ensures only valid,
#   database-linked videos remain on disk.
# ------------------------------------------------------------
def remove_org_videos():
    logger.info("===remove_org_videos===")
    utility_service.remove_org_videos()


# ------------------------------------------------------------
# Method: remove_temp_videos
# Description:
#   Iterates through the TEMP_DIR and removes any temporary
#   video files older than 180 seconds (3 minutes). Each file
#   is expected to start with a timestamp prefix (e.g., 1699478123_filename.mp4).
#   Logs every action for audit and debugging purposes.
# ------------------------------------------------------------
def remove_temp_videos():
    logger.info('===remove_temp_videos===')
    utility_service.remove_temp_videos()


# ------------------------------------------------------------
# Scheduler Configuration
# Description:
#   Adds recurring jobs to the background scheduler for:
#     1. Cleaning up temporary videos every 10 seconds
#     2. Removing unwanted videos every 20 seconds
#   These jobs run continuously in the background.
# ------------------------------------------------------------
scheduler.add_job(remove_temp_videos, 'interval', id='remove_temp_videos', seconds=10)
scheduler.add_job(remove_org_videos, 'interval', id='remove_unwanted_videos', seconds=20)

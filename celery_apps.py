# celery_apps.py
from celery import Celery
from services.utility import UtilityService
from logger_app import setup_logger
from dotenv import load_dotenv


load_dotenv()

app = Celery('celery_apps', broker='redis://localhost:6379/0')
app.conf.update(
    result_backend='redis://localhost:6379/0',
    beat_schedule={
        'remove_temp_videos-every-10-seconds': {
            'task': 'celery_apps.remove_temp_videos',
            'schedule': 10.0, # run every 10 seconds
        },
        'remove_org_videos-at-every-10-seconds': {
            'task': 'celery_apps.remove_org_videos',
            'schedule': 10.0, # run every 10 seconds
        }
    },
    include=['celery_apps']
)


# Initialize the utility service and logger
utility_service = UtilityService()
logger = setup_logger(__name__)

# ------------------------------------------------------------
# Method: remove_temp_videos
# Description:
#   Iterates through the TEMP_DIR and removes any temporary
#   video files older than 180 seconds (3 minutes). Each file
#   is expected to start with a timestamp prefix (e.g., 1699478123_filename.mp4).
#   Logs every action for audit and debugging purposes.
# ------------------------------------------------------------
@app.task(bind=True)
def remove_temp_videos(self):
    try:
        logger.info("===remove_temp_videos===")
        utility_service.remove_temp_videos()
    except Exception as e:
        logger.error(f"Failed to remove temp videos: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=5, max_retries=3)

    


# ------------------------------------------------------------
# Method: remove_org_videos
# Description:
#   Scans the ORG_DIR for video files and deletes any file that
#   does not exist in the database. This ensures only valid,
#   database-linked videos remain on disk.
# ------------------------------------------------------------
@app.task
def remove_org_videos():
    logger.info("===remove_org_videos===")
    utility_service.remove_org_videos()
    return True
from apscheduler.schedulers.background import BackgroundScheduler
import os
import time
import logging
import sys
from database.video_table import VideoTableService
from decouple import config
from services.vector_store_service import VectorStoreService

# ------------------------------------------------------------
# Module: Video Cleanup Scheduler
# Description:
#   Handles automated cleanup of temporary and unwanted video
#   files using scheduled background jobs. Ensures that:
#     - Old temporary uploads are periodically deleted
#     - Unreferenced videos (not in DB) are removed
#   Logging is configured for visibility and debugging.
# ------------------------------------------------------------


# ------------------------------------------------------------
# Initialization Section
# ------------------------------------------------------------

# Initialize database service
video_table = VideoTableService()

# Load directory configurations
TEMP_DIR = config("TEMP_DIR")
ORG_DIR = config("ORG_DIR")

# Ensure required directories exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(ORG_DIR, exist_ok=True)

# Configure logging for scheduler activities
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Initialize logger and background scheduler
logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


# ------------------------------------------------------------
# Function: remove_temp_videos
# Description:
#   Iterates through the TEMP_DIR and removes any temporary
#   video files older than 180 seconds (3 minutes). Each file
#   is expected to start with a timestamp prefix (e.g., 1699478123_filename.mp4).
#   Logs every action for audit and debugging purposes.
# ------------------------------------------------------------
def remove_temp_videos():
    logger.info("========= remove_temp_videos ============")
    current_time = int(time.time())
    cutoff = current_time - 180  # 3-minute age limit

    for fname in os.listdir(TEMP_DIR):
        uploaded_time = 0
        logger.info("========= Processing file entry ==========")
        path = os.path.join(TEMP_DIR, fname)

        # Skip directories
        if not os.path.isfile(path):
            logger.debug("Skipping non-file path: %s", path)
            continue

        try:
            uploaded_time = int(fname.split('_', 1)[0])
        except (ValueError, IndexError):
            logger.debug("Skipping non-timestamp file: %s", path)
            continue

        logger.info(f"Uploaded time: {uploaded_time}, Current time: {current_time}, Cutoff: {cutoff}")

        # Delete if file timestamp <= cutoff
        if uploaded_time > 0 and uploaded_time <= cutoff:
            try:
                os.remove(path)
                logger.info("Removed temp video: %s", path)
            except OSError:
                logger.exception("Failed to remove temp video: %s", path)


# ------------------------------------------------------------
# Function: remove_unwanted_videos
# Description:
#   Scans the ORG_DIR for video files and deletes any file that
#   does not exist in the database. This ensures only valid,
#   database-linked videos remain on disk.
# ------------------------------------------------------------
def remove_unwanted_videos():
    logger.info("========= remove_unwanted_videos =========")

    for fname in os.listdir(ORG_DIR):
        path = os.path.join(ORG_DIR, fname)
        logger.info(f"Processing file: {fname}")

        # Skip non-file paths
        if not os.path.isfile(path):
            logger.debug("Skipping non-file path: %s", path)
            continue

        # Check if file exists in the database
        video_data = video_table.get_video_by_name(fname)
        logger.debug(f"DB Lookup for {fname}: {video_data}")

        if not video_data:
            try:
                os.remove(path)
                VectorStoreService()._delete_documents(fname)
                logger.info("Removed unwanted video: %s", path)
            except OSError:
                logger.exception("Failed to remove unwanted video: %s", path)
        else:
            logger.info(f"{fname} exists in the database — skipping removal.")


# ------------------------------------------------------------
# Scheduler Configuration
# Description:
#   Adds recurring jobs to the background scheduler for:
#     1. Cleaning up temporary videos every 10 seconds
#     2. Removing unwanted videos every 20 seconds
#   These jobs run continuously in the background.
# ------------------------------------------------------------
scheduler.add_job(remove_temp_videos, 'interval', id='remove_temp_videos', seconds=10)
scheduler.add_job(remove_unwanted_videos, 'interval', id='remove_unwanted_videos', seconds=20)

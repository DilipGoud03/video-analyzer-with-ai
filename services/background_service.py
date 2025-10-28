from apscheduler.schedulers.background import BackgroundScheduler
import os
import time
import logging
import sys
from database.video_table import VideoTableService
from decouple import config

video_table = VideoTableService()
TEMP_DIR = config("TEMP_DIR")
ORG_DIR = config("ORG_DIR")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(ORG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def remove_temp_videos():
    logger.info("=========remove_temp_videos============")
    current_time = int(time.time())
    cutoff = current_time - 180
    for fname in os.listdir(TEMP_DIR):
        uploaded_time = 0
        logger.info("=========fname=======1===")
        path = os.path.join(TEMP_DIR, fname)
        if not os.path.isfile(path):
            logger.info("=========fname=======2===")
            pass
        try:
            logger.info("=========fname=======3===")
            uploaded_time = int(fname.split('_', 1)[0])
        except (ValueError, IndexError):
            logger.debug("Skipping non-timestamp file: %s", path)
            pass
        logger.info(
            f"===========uploaded_time================ {uploaded_time}")
        logger.info(f"===========current_time================ {current_time}")
        logger.info(
            f"===========cutoff= current_time - 180 ================ {cutoff}")
        if uploaded_time > 0 and uploaded_time <= cutoff:
            try:
                os.remove(path)
                logger.info("Removed temp video: %s", path)
            except OSError:
                logger.exception("Failed to remove temp video: %s", path)


def remove_unwanted_videos():
    logger.info("==========remove_unwanted_videos===========")
    for fname in os.listdir(ORG_DIR):
        logger.info(f"=========fname======={fname}===")
        path = os.path.join(ORG_DIR, fname)
        if not os.path.isfile(path):
            logger.info("=========fname=======2===")
            pass
        video_data = video_table.get_video_by_name(fname)
        print(video_data)
        if not video_data:
            try:
                os.remove(path)
                logger.info("Removed Unwanted video: %s", path)
            except OSError:
                logger.exception("Failed to remove temp video: %s", path)
        else:
            logger.info(f"{fname} This video exist in db")


scheduler.add_job(remove_temp_videos, 'interval', id='remove_temp_videos', seconds=10)
scheduler.add_job(remove_unwanted_videos, 'interval', id='remove_unwanted_videos', seconds=20)

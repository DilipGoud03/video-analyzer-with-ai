from apscheduler.schedulers.background import BackgroundScheduler
import os
import time
import logging
import sys

TEMP_DIR = "temp_videos"
os.makedirs(TEMP_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def remove_temp_videos():
    logger.info("=====================")
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
        logger.info(f"===========uploaded_time================ {uploaded_time}")
        logger.info(f"===========current_time================ {current_time}")
        logger.info(f"===========cutoff= current_time - 180 ================ {cutoff}")
        if uploaded_time > 0 and uploaded_time <= cutoff:
            try:
                os.remove(path)
                logger.info("Removed temp video: %s", path)
            except OSError:
                logger.exception("Failed to remove temp video: %s", path)


scheduler.add_job(remove_temp_videos, 'interval', id='main_loop1', seconds=10)

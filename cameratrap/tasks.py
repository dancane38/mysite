from time import sleep
from celery import shared_task
import logging
from celery.utils.log import get_task_logger

from cameratrap.VideoProcessor import VideoProcessor
from cameratrap.models import VideoFile

logger = get_task_logger('tasks')
logger.setLevel(logging.DEBUG)


@shared_task()
def process_video_async(video_pkid):
    logger.info('CELERY RUNNING')
    """Processes the video file asyncronously."""
    print("***** Yawn. Good morning. Waking up to process a video.")
    video_file = VideoFile.objects.get(pk=video_pkid)
    vp = VideoProcessor(video_file)
    vp.processVideo()
    print("***** Ok, I'm done. Going back to sleep for a while...")

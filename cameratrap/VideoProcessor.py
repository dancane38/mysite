import logging

class VideoProcessor:

    def __init__(self, videoFile):
        self.videoFile = videoFile



    def processVideo(self):
        logging.debug("running process video")
        logging.debug(self.videoFile.document.path)





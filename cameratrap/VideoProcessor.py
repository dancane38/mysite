import logging
import ntpath
import os
import subprocess

class VideoProcessor:

    def __init__(self, videoFile):
        self.videoFile = videoFile

    def processVideo(self):
        logging.debug("-=-=-=-=-=-=-=-=-=-=-=-= start process video -=-=-=-=-=-=-=-=-=-=-=-=")
        # logging.debug("- "self.videoFile.document.path)
        self.convertVideoToImages()
        logging.debug("-=-=-=-=-=-=-=-=-=-=-=-=  end process video  -=-=-=-=-=-=-=-=-=-=-=-=")

    def convertVideoToImages(self):
        logging.debug("- Converting Video to Images")

        path_to_video = self.videoFile.document.path
        video_filename = ntpath.basename(path_to_video)
        parent_dir = ntpath.dirname(path_to_video)
        output_directory = video_filename + "_frames"

        # Path
        path_output_dir = os.path.join(parent_dir, output_directory)
        isExist = os.path.exists(path_output_dir)
        if not isExist:
            os.mkdir(path_output_dir)

        logging.debug("- Path: "+ path_to_video)
        logging.debug("- Filename: "+ video_filename)
        logging.debug("- Output Dir: "+ path_output_dir)

        # ffmpeg -i input.mp4 -vf fps=15 frame%d.png
        ffmpeg_cmd = "/opt/homebrew/bin/ffmpeg -i " + path_to_video + " -vf fps=15 " + path_output_dir + "/frame%d.jpg"

        logging.debug("- Running ffmpeg command: " + ffmpeg_cmd)

        #subprocess.call("date")

        ffmpeg = subprocess.Popen(ffmpeg_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        out, err = ffmpeg.communicate()
        if (err): print(err)

        #if subprocess.run(ffmpeg_cmd).returncode == 0:
        #    print("- SUCCESS: FFmpeg Script Ran Successfully")
        #else:
        #    print("-- ERROR: There was an error running your FFmpeg script")




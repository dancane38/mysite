import glob
import logging
import ntpath
import os
import subprocess

from ultralytics import YOLO
from PIL import Image
from numpy import asarray

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
        path_output_dir = self.create_video_frames_dir(output_directory, parent_dir)

        logging.debug("- Path: "+ path_to_video)
        logging.debug("- Filename: "+ video_filename)
        logging.debug("- Output Dir: "+ path_output_dir)

        # convert video to images
        self.process_video_using_ffmpeg(path_output_dir, path_to_video)

        # Load a model
        model = YOLO('model/v10best.pt')  # load a pretrained model (recommended for training)

        # run inference on all images
        for filename in sorted(glob.glob(os.path.join(path_output_dir, '*.jpg'))):
            img = Image.open(filename)

            # do your stuff
            logging.debug ("- Running inference on image "+ filename)
            self.run_inference(model, img)

    def run_inference(self, model, img):
        numpydata = asarray(img)

        results = model(numpydata)  # generator of Results objects
        logging.debug("-- Inference Complete ")
        logging.debug(results)
        for r in results:
            boxes = r.boxes  # Boxes object for bbox outputs
            # masks = r.masks  # Masks object for segmenation masks outputs
            # probs = r.probs  # Class probabilities for classification outputs
            if boxes is not None:
                logging.debug("---- boxes: " )
                logging.debug(boxes)

                boxXY = boxes.xywh # box with xywh format, (N, 4)
                boxConf = boxes.conf # confidence score, (N, 1)

                logging.debug("-- boxXY ")
                logging.debug(boxXY)
                logging.debug("-- boxConf ")
                logging.debug(boxConf)

        res_plotted = results[0].plot()
        res_plotted.save(results[0].path + "testOut.jpg")


    def process_video_using_ffmpeg(self, path_output_dir, path_to_video):
        # ffmpeg -i input.mp4 -vf fps=15 frame%d.png
        ffmpeg_cmd = "/opt/homebrew/bin/ffmpeg -i " + path_to_video + " -vf fps=15 " + path_output_dir + "/frame%d.jpg"
        logging.debug("- Running ffmpeg command: " + ffmpeg_cmd)
        ffmpeg = subprocess.Popen(ffmpeg_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        out, err = ffmpeg.communicate()
        if err:
            print("-- ERROR: There was an error running your FFmpeg script")
            print(err)
        else:
            print("- SUCCESS: FFmpeg Script Ran Successfully")

    def create_video_frames_dir(self, output_directory, parent_dir):
        path_output_dir = os.path.join(parent_dir, output_directory)
        isExist = os.path.exists(path_output_dir)
        if not isExist:
            os.mkdir(path_output_dir)
        return path_output_dir




import glob
import logging
import ntpath
import os
import subprocess

from ultralytics import YOLO
from PIL import Image
from numpy import asarray
from ultralytics.yolo.utils.plotting import Annotator

def create_video_frames_dir(parent_dir, new_dir):
    path_full_dir = os.path.join(parent_dir, new_dir)
    is_exist = os.path.exists(path_full_dir)
    if not is_exist:
        os.mkdir(path_full_dir)
    return path_full_dir


class VideoProcessor:
    FPS = "2"  # change the video FPS processing rate
    FRAMES_DIR = "_frames"  # subdir for image frames of each video
    ANNOTATION_DIR = "_annotations"  # subdir of annotated frames

    path_to_video = ""
    video_filename = ""
    parent_dir = ""
    path_frames_dir = ""
    path_annotation_dir = ""

    def __init__(self, videoFile):
        self.videoFile = videoFile

    def processVideo(self):
        logging.debug("-=-=-=-=-=-=-=-=-=-=-=-= start process video -=-=-=-=-=-=-=-=-=-=-=-=")
        # logging.debug("- "self.videoFile.document.path)
        self.convertVideoToImages()
        logging.debug("-=-=-=-=-=-=-=-=-=-=-=-=  end process video  -=-=-=-=-=-=-=-=-=-=-=-=")

    def convertVideoToImages(self):
        logging.debug("- Converting Video to Images")

        # configure all the directories
        self.configureDirectories()

        # convert video to images
        self.process_video_using_ffmpeg()

        # Load a model
        model = YOLO('model/v10best.pt')  # load a pretrained model (recommended for training)

        # run inference on all images
        for filename in sorted(glob.glob(os.path.join(self.path_frames_dir, '*.jpg'))):
            img = Image.open(filename)

            # do your stuff
            logging.debug("- Running inference on image " + filename)
            self.run_inference(filename, model, img)

    def configureDirectories(self):
        self.path_to_video = self.videoFile.document.path
        self.video_filename = ntpath.basename(self.path_to_video)
        self.parent_dir = ntpath.dirname(self.path_to_video)
        # Paths
        frames_working_dir = self.video_filename + self.FRAMES_DIR
        annotations_working_dir = self.video_filename + self.ANNOTATION_DIR
        self.path_frames_dir = create_video_frames_dir(self.parent_dir, frames_working_dir)
        self.path_annotation_dir = create_video_frames_dir(self.parent_dir, annotations_working_dir)
        logging.debug("- Path: " + self.path_to_video)
        logging.debug("- Filename: " + self.video_filename)
        logging.debug("- Frames Dir: " + self.path_frames_dir)
        logging.debug("- Annotation Dir: " + self.path_annotation_dir)

    def process_video_using_ffmpeg(self):
        # ffmpeg -i input.mp4 -vf fps=15 frame%d.png
        ffmpeg_cmd = "/opt/homebrew/bin/ffmpeg -i " + self.path_to_video + " -vf fps=" + self.FPS + " " + self.path_frames_dir + "/frame%d.jpg"
        logging.debug("- Running ffmpeg command: " + ffmpeg_cmd)
        ffmpeg = subprocess.Popen(ffmpeg_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        out, err = ffmpeg.communicate()
        if err:
            print("-- ERROR: There was an error running your FFmpeg script")
            print(err)
        else:
            print("- SUCCESS: FFmpeg Script Ran Successfully")

    def run_inference(self, filename, model, img):
        img_as_numpy = asarray(img)

        results = model(img_as_numpy)  # generator of Results objects
        logging.debug("-- Inference Complete ")
        # logging.debug(results)
        for r in results:
            boxes = r.boxes  # Boxes object for bbox outputs
            # masks = r.masks  # Masks object for segmenation masks outputs
            # probs = r.probs  # Class probabilities for classification outputs
            annotator = Annotator(img_as_numpy, line_width=1)
            if boxes is not None:
                for box in boxes:
                    b = box.xyxy[0]  # get box coordinates in (top, left, bottom, right) format
                    c = box.cls
                    conf = box.conf[0]
                    # logging.debug("-=-=-=-=-=-=--=-=-=-=-=-=-=-")
                    # logging.debug(conf)
                    # logging.debug("-=-=-=-=-=-=--=-=-=-=-=-=-=-")
                    class_with_conf = '{label} - {con:.2f}%'.format(label=model.names[int(c)], con=conf * 100)
                    annotator.box_label(b, class_with_conf, color=(255, 0, 0))

        img_annotated = annotator.result()
        image_final = Image.fromarray(img_annotated)

        video_filename = ntpath.basename(filename)
        annotated_path_to_output = self.path_annotation_dir + "/" + video_filename
        image_final.save(annotated_path_to_output)

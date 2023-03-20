import glob
import logging
import ntpath
import os
import subprocess
from ultralytics import YOLO
from PIL import Image
from numpy import asarray
from ultralytics.yolo.utils.plotting import Annotator
from .models import VideoFile, VideoFrame, Prediction
import re
import cv2
import torch

def create_video_frames_dir(parent_dir, new_dir):
    path_full_dir = os.path.join(parent_dir, new_dir)
    is_exist = os.path.exists(path_full_dir)
    if not is_exist:
        os.mkdir(path_full_dir)
    return path_full_dir


class VideoProcessor:
    PATH_TO_FFMPEG = "/opt/homebrew/bin/ffmpeg"
    FPS_INFERENECE = "2"  # change the video FPS processing rate
    FRAMES_DIR = "_frames"  # subdir for image frames of each video
    ANNOTATION_DIR = "_annotations"  # subdir of annotated frames

    video_fps = 0
    path_to_video = ""
    video_filename = ""
    parent_dir = ""
    path_frames_dir = ""
    path_annotation_dir = ""
    max_objects_detected_in_video = 0
    max_confidence_in_video = 0

    def __init__(self, videoFile):
        self.videoFile = videoFile
        self.pattern_frame_number = re.compile('.*frame(\d+)', re.IGNORECASE)

    def processVideo(self):
        logging.debug("-=-=-=-=-=-=-=-=-=-=-=-= start process video -=-=-=-=-=-=-=-=-=-=-=-=")
        self.configureDirectories()
        self.saveVideoMetadata()
        self.convertVideoToImages()
        self.saveFinalMetadata()
        logging.debug("-=-=-=-=-=-=-=-=-=-=-=-=  end process video  -=-=-=-=-=-=-=-=-=-=-=-=")

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

    def saveVideoMetadata(self):
        cam = cv2.VideoCapture(self.path_to_video)
        fps = cam.get(cv2.CAP_PROP_FPS) # float 'fps'
        width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)  # float `width`
        height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
        fps_string = '{fpsString:.0f}'.format(fpsString=fps)
        logging.debug("- Saving Video FPS as: "+ fps_string)
        self.video_fps = fps
        self.videoFile.fps_video = round(fps)
        self.videoFile.video_width = width
        self.videoFile.video_height = height
        self.videoFile.fps_inference = self.FPS_INFERENECE
        self.videoFile.save()
        pass

    def saveFinalMetadata(self):
        logging.debug(" -- max_objects_detected is {max_obj:.0f}".format(max_obj=self.max_objects_detected_in_video))
        logging.debug(" -- max_confidence is {max_conf:.0f}".format(max_conf=self.max_confidence_in_video * 100))
        self.videoFile.max_objects_detected = self.max_objects_detected_in_video
        self.videoFile.max_confidence = torch.round(self.max_confidence_in_video * 100)
        self.videoFile.save()
        pass

    def convertVideoToImages(self):
        logging.debug("- Converting Video to Images")

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

    def process_video_using_ffmpeg(self):
        # ffmpeg -i input.mp4 -vf fps=15 frame%d.png
        ffmpeg_cmd = self.PATH_TO_FFMPEG + " -i " + self.path_to_video + " -vf fps=" + self.FPS_INFERENECE + " " + self.path_frames_dir + "/frame%d.jpg"
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

        m_filename = self.pattern_frame_number.match(filename)
        frame_number = m_filename.group(1)
        logging.debug(" -- filename has a frame number of " + frame_number)

        fps_factor = int(self.video_fps) / int(self.FPS_INFERENECE)
        logging.debug(" -- Video FPS is {fps:.0f}".format(fps=self.video_fps))
        logging.debug(" -- FPS_INFERENECE is " + self.FPS_INFERENECE)
        logging.debug(" -- FPS Factor is {fps:.0f}".format(fps=fps_factor))
        actual_frame_number = int(frame_number) * fps_factor
        logging.debug(" -- Computer video frame is {act_fps:.0f}".format(act_fps=actual_frame_number))

        results = model(img_as_numpy)  # generator of Results objects
        logging.debug("-- Inference Complete ")
        # logging.debug(results)

        count_detections = 0
        for r in results:
            boxes = r.boxes  # Boxes object for bbox outputs
            # masks = r.masks  # Masks object for segmenation masks outputs
            # probs = r.probs  # Class probabilities for classification outputs
            annotator = Annotator(img_as_numpy, line_width=1)
            if boxes is not None:
                # VideoFrame vFrame = VideoFrame(video_file=self.videoFile, frame_number=, objects_detected=boxes.length, filename=filename)

                for box in boxes:
                    b = box.xyxy[0]  # get box coordinates in (top, left, bottom, right) format
                    c = box.cls
                    conf = box.conf[0]

                    if conf > 0.5:
                        count_detections += 1
                        class_with_conf = '{label} - {con:.2f}%'.format(label=model.names[int(c)], con=conf * 100)
                        annotator.box_label(b, class_with_conf, color=(255, 0, 0))

                        if conf > self.max_confidence_in_video:
                            self.max_confidence_in_video = conf


        if count_detections > 0:
            img_annotated = annotator.result()
            image_final = Image.fromarray(img_annotated)

            video_filename = ntpath.basename(filename)
            annotated_path_to_output = self.path_annotation_dir + "/" + video_filename
            image_final.save(annotated_path_to_output)

            if count_detections > self.max_objects_detected_in_video:
                self.max_objects_detected_in_video = count_detections



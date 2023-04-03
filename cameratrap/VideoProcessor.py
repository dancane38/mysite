import glob
import logging
import ntpath
import os
import re
import subprocess

import cv2
import torch
from PIL import Image
from numpy import asarray
from ultralytics import YOLO
from ultralytics.yolo.utils.plotting import Annotator

from .models import VideoFrame, Prediction


def create_video_frames_dir(parent_dir, new_dir):
    path_full_dir = os.path.join(parent_dir, new_dir)
    is_exist = os.path.exists(path_full_dir)
    if not is_exist:
        os.mkdir(path_full_dir)
    return path_full_dir


class VideoProcessor:
    PATH_TO_FFMPEG = "/opt/homebrew/bin/ffmpeg"
    MODEL = "v10best.pt"
    MIN_CONFIDENCE = 0.5
    FPS_INFERENECE = "6"  # change the video FPS processing rate
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
        self.pattern_media = re.compile('.*media/(.*)', re.IGNORECASE)

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
        pass

    def saveVideoMetadata(self):
        cam = cv2.VideoCapture(self.path_to_video)
        fps = cam.get(cv2.CAP_PROP_FPS)  # float 'fps'
        width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)  # float `width`
        height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
        fps_string = '{fpsString:.0f}'.format(fpsString=fps)
        logging.debug("- Saving Video FPS as: " + fps_string)
        self.video_fps = fps
        self.videoFile.fps_video = round(fps)
        self.videoFile.video_width = width
        self.videoFile.video_height = height
        self.videoFile.fps_inference = self.FPS_INFERENECE
        self.videoFile.video_status = self.videoFile.VideoStatus.PROCESSED
        self.videoFile.inference_model = self.MODEL
        self.videoFile.save()
        pass

    def saveFinalMetadata(self):
        logging.debug(" -- max_objects_detected is {max_obj:.0f}".format(max_obj=self.max_objects_detected_in_video))
        logging.debug(" -- max_confidence is {max_conf:.0f}".format(max_conf=self.max_confidence_in_video * 100))
        self.videoFile.max_objects_detected = self.max_objects_detected_in_video
        self.videoFile.max_confidence = int(self.max_confidence_in_video * 100)
        self.videoFile.save()
        pass

    def convertVideoToImages(self):
        logging.debug("- Converting Video to Images")

        # convert video to images
        self.process_video_using_ffmpeg()

        # Load a model
        model = YOLO('model/'+ self.MODEL)  # load a pretrained model (recommended for training)

        # run inference on all images
        for filename in sorted(glob.glob(os.path.join(self.path_frames_dir, '*.jpg'))):
            img = Image.open(filename)

            # do your stuff
            logging.debug("- Running inference on image " + filename)
            self.run_inference(filename, model, img)

        pass

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
        pass

    def run_inference(self, filename, model, img):
        img_as_numpy = asarray(img)

        m_filename = self.pattern_frame_number.match(filename)
        frame_number = m_filename.group(1)
        logging.debug(" -- filename has a frame number of " + frame_number)

        fps_factor = int(self.video_fps) / int(self.FPS_INFERENECE)
        logging.debug(" -- Video FPS is {fps:.0f}".format(fps=self.video_fps))
        logging.debug(" -- FPS_INFERENECE is " + self.FPS_INFERENECE)
        logging.debug(" -- FPS Factor is {fps:.0f}".format(fps=fps_factor))

        results = model(img_as_numpy)  # generator of Results objects
        logging.debug("-- Inference Complete ")

        count_detections = 0
        for r in results:
            boxes = r.boxes  # Boxes object for bbox outputs
            # masks = r.masks  # Masks object for segmenation masks outputs
            # probs = r.probs  # Class probabilities for classification outputs
            annotator = Annotator(img_as_numpy, line_width=1)
            if boxes is not None:
                frame_max_confidence = 0
                for box in boxes:
                    b = box.xyxy[0]  # get box coordinates in (top, left, bottom, right) format
                    c = box.cls
                    conf = box.conf[0]
                    if conf > self.MIN_CONFIDENCE:
                        try:
                            video_frame = VideoFrame.objects.get(video_file=self.videoFile,
                                                                 frame_number=frame_number)
                        except VideoFrame.DoesNotExist:
                            video_frame = VideoFrame(video_file=self.videoFile, frame_number=frame_number)

                        video_frame.objects_detected = frame_number_of_objects = boxes.__len__()
                        video_frame.filename = filename

                        count_detections += 1
                        classification = model.names[int(c)]
                        conf_as_int = int(conf * 100)

                        if conf_as_int > frame_max_confidence:
                            video_frame.max_confidence = conf_as_int

                        video_frame.save()

                        class_with_conf = '{label} - {con:.2f}%'.format(label=classification, con=conf_as_int)
                        annotator.box_label(b, class_with_conf, color=(255, 0, 0))

                        try:
                            prediction = Prediction.objects.get(video_frame=video_frame,
                                                                pred_class=classification,
                                                                coord_top=torch.round(b[0]),
                                                                coord_left=torch.round(b[1]),
                                                                coord_bottom=torch.round(b[2]),
                                                                coord_right=torch.round(b[3])
                                                                )
                        except Prediction.DoesNotExist:
                            prediction = Prediction(video_frame=video_frame,
                                                    pred_class=classification,
                                                    coord_top=torch.round(b[0]),
                                                    coord_left=torch.round(b[1]),
                                                    coord_bottom=torch.round(b[2]),
                                                    coord_right=torch.round(b[3])
                                                    )

                        prediction.confidence = conf_as_int
                        prediction.save()

                        if conf > self.max_confidence_in_video:
                            self.max_confidence_in_video = conf

        if count_detections > 0:
            img_annotated = annotator.result()
            image_final = Image.fromarray(img_annotated)

            video_filename = ntpath.basename(filename)
            annotated_path_to_output = self.path_annotation_dir + "/" + video_filename
            image_final.save(annotated_path_to_output)
            m_path_to_framefile = self.pattern_media.match(annotated_path_to_output)
            frame_file_path = m_path_to_framefile.group(1)

            video_frame.filename = frame_file_path
            video_frame.save()

            if count_detections > self.max_objects_detected_in_video:
                self.max_objects_detected_in_video = count_detections
    pass

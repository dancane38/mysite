from coco_lib.common import Info, Image, License
from coco_lib.objectdetection import ObjectDetectionAnnotation, ObjectDetectionCategory, ObjectDetectionDataset
from datetime import datetime
from .models import VideoFrame, Prediction
import logging
import glob
import os
from roboflow import Roboflow


class CocoUtils:

    COCO_JSON_FILENAME = 'image.json'

    def __init__(self, videoFrame: VideoFrame):
        """

        :type videoFrame: VideoFrame
        """
        self.videoFrame = videoFrame

    def process_frame_to_coco(self):
        logging.debug("-=-=-=-=-=-=-=-=-=-=-=-= start coco process_frame_to_coco -=-=-=-=-=-=-=-=-=-=-=-=")
        self.create_coco_output()
        self.process_roboflow()
        logging.debug("-=-=-=-=-=-=-=-=-=-=-=-=  end coco process_frame_to_coco  -=-=-=-=-=-=-=-=-=-=-=-=")

    def process_roboflow(self):

        ## DEFINITIONS
        # roboflow params
        api_key = "7NFZ6rPnodFibw7bIQG9"
        upload_project_name = "monkeyct"

        ## INITIALIZATION
        # pull down reference project
        rf = Roboflow(api_key=api_key)
        upload_project = rf.workspace().project(upload_project_name)

        ## MAIN
        # upload images
        logging.debug("Image Filename is: ")
        response = upload_project.upload(self.videoFrame.filename.path, self.COCO_JSON_FILENAME)
        logging.debug("Roboflow Response:")
        logging.debug(response)

    def create_coco_output(self):
        info = Info(  # Describe the dataset
            year=datetime.now().year,
            version='1.0',
            description='CameraTrap Monkey Detector',
            contributor='Daniel Cane',
            url='https://',
            date_created=datetime.now()
        )

        mit_license = License(  # Set the license
            id=0,
            name='MIT',
            url='https://opensource.org/licenses/MIT'
        )

        images = [  # Describe the images
            Image(
                id=0,
                width=self.videoFrame.video_file.video_width,
                height=self.videoFrame.video_file.video_height,
                file_name=self.videoFrame.filename.name,
                license=mit_license.id,
                flickr_url='',
                coco_url='',
                date_captured=self.videoFrame.video_file.date_end
            ),

        ]
        categories = [  # Describe the categories
            ObjectDetectionCategory(
                id=0,
                name='monkey',
                supercategory=''
            ),

        ]

        annotations = []

        for predection in self.videoFrame.prediction_set.all():
            logging.debug("-=-=- Prediction -=-=-=-")
            logging.debug(predection)

            posx = predection.coord_left
            posy = predection.coord_top
            bbox_width = predection.coord_right - predection.coord_left
            bbox_height = predection.coord_bottom - predection.coord_top

            # The COCO bounding box format is [top left x position, top left y position, width, height].
            annotation = ObjectDetectionAnnotation(
                id=0,
                image_id=0,
                category_id=0,
                segmentation=[],
                area=800.0,
                bbox=[posx, posy, bbox_width, bbox_height],
                iscrowd=0
            )

            annotations.append(annotation)

        dataset = ObjectDetectionDataset(  # Create the dataset
            info=info,
            images=images,
            licenses=[mit_license],
            categories=categories,
            annotations=annotations
        )

        dataset.save(self.COCO_JSON_FILENAME, indent=2)  # Save the dataset

from datetime import datetime

import cv2
import pytesseract
import re
import dateparser
import logging

class OCRUtils:

    def __init__(self, image):
        self.imageToParse = image

    def extractDateTime(self):
        logging.debug("-=-=-=-=-=-=-=-=-=-=-=-= start extractDateTime -=-=-=-=-=-=-=-=-=-=-=-=")
        dt = self.processImage()
        logging.debug("-=-=-=-=-=-=-=-=-=-=-=-=  end extractDateTime  -=-=-=-=-=-=-=-=-=-=-=-=")
        return dt

    def processImage(self):
        # Validate date
        date_extract_pattern = "[0-9]{1,2}.[0-9]{1,2}.[0-9]{4}" #MM/DD/YYYY
        time_pattern_1 = "\\b([0-5][0-9]:[0-5][0-9]\\w{2})\\b" #01:22PM
        time_extract_2 = "\\b([0-5][0-9]:[0-5][0-9]:[0-5][0-9])\\b" #14:22:56
        time_all_patterns = time_pattern_1 +"|"+ time_extract_2

        pattern_date = re.compile(date_extract_pattern, re.IGNORECASE)
        pattern_time = re.compile(time_all_patterns, re.IGNORECASE)

        # Direct from the command line - the whole image
        #print(pytesseract.image_to_string('../media/videos/sit1/ct1/TEST.mp4_frames/time.jpg', lang="eng", config="--psm 7"))

        #img_cv = cv2.imread(r'../media/videos/sit1/ct1/TEST.mp4_frames/frame1.jpg')
        #img_cv = cv2.imread(r'../media/videos/444/333/14sCameraType2.mov_annotations/frame8.jpg')
        #image_bytes = cv2.imencode('.jpg', img_cv)[1].tobytes()

        # By default OpenCV stores images in BGR format and since pytesseract assumes RGB format,
        # we need to convert from BGR to RGB format/mode:
        #img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        img_rgb = cv2.cvtColor(self.imageToParse, cv2.COLOR_BGR2RGB)

        dimensions = img_rgb.shape
        height = img_rgb.shape[0]
        width = img_rgb.shape[1]
        #print(f"height: %2d" % height);
        #print(f"width: %2d " % width);

        #subimage = image[Y_start : Y_end, X_start : X_end].
        crop_img = img_rgb[height-44:height, 100:width]

        #cv2.imwrite("/Users/daniel.cane/PycharmProjects/mysite/media/last_ocr_crop.jpg", crop_img)
        #cv2.imshow("orig", crop_img)
        #cv2.waitKey(0)

        ocr_string = pytesseract.image_to_string(crop_img, lang="eng", config="--psm 7")
        logging.debug(ocr_string)

        search_date = pattern_date.search(ocr_string) # Returns Match object
        date_as_string = ''
        time_as_string = ''

        #print(search_date)
        if search_date is not None:
            date_as_string = search_date.group()
            logging.debug('Date is: {0}'.format(date_as_string))

        search_time = pattern_time.search(ocr_string) # Returns Match object
        #print(search_time)
        if search_time is not None:
            time_as_string = search_time.group()
            logging.debug('Time is: {0}'.format(time_as_string))

        date_time_string = date_as_string +" "+ time_as_string +" UTC"
        dt: datetime | None = dateparser.parse(date_time_string)
        logging.debug(dt)

        return dt

        # OR
        #img_rgb = Image.frombytes('RGB', img_cv.shape[:2], img_cv, 'raw', 'BGR', 0, 0)
        #print(pytesseract.image_to_string(img_rgb))

    pass




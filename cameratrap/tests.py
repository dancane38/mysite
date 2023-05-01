import dateparser
from PIL import Image
from django.test import TestCase
from numpy import asarray
from cameratrap.OCRUtils import OCRUtils


class OCRUtilTests(TestCase):


    def test_ocr_bushnell(self):
        img = Image.open(r'./cameratrap/testdata/bushnell.jpg')
        img_as_numpy = asarray(img)
        ocr = OCRUtils(image=img_as_numpy)
        dt = ocr.extractDateTime()
        dt_in_image = dateparser.parse('2022-05-04 16:08:36+00:00')
        self.assertEqual(dt.date(), dt_in_image.date())
        self.assertEqual(dt.time(), dt_in_image.time())
        print(dt)

    def test_ocr_deer(self):
        img = Image.open(r'./cameratrap/testdata/deer.jpg')
        img_as_numpy = asarray(img)
        ocr = OCRUtils(image=img_as_numpy)
        dt = ocr.extractDateTime()
        dt_in_image = dateparser.parse('2022-03-04 07:18:00+00:00')
        self.assertEqual(dt.date(), dt_in_image.date())
        self.assertEqual(dt.time(), dt_in_image.time())
        print(dt)
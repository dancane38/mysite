import cv2
from PIL import Image
import pytesseract

print(pytesseract.image_to_string('../media/videos/sit1/ct1/TEST.mp4_frames/time.jpg', lang="eng", config="--psm 7"))



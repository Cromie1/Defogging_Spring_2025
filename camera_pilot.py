from picamera2 import Picamera2, Preview
from time import sleep
picam0 = Picamera2(0)
picam1 = Picamera2(1)
picam0.start_preview(Preview.QTGL)
picam1.start_preview(Preview.QTGL)
picam0.start()
picam1.start()
sleep(100)
picam0.capture_file("cam0.jpg")
picam1.capture_file("cam1.jpg")
picam0.stop()
picam1.stop()
picam0.stop_preview()
picam1.stop_preview()

import m3u8
import cv2
import subprocess as sp
import numpy as np

VIDEO_URL = r'https://5e0da72d486c5.streamlock.net:8443/ayalon/Yosseftal.stream/playlist.m3u8'
VIDEO_URL = r'https://stream.cawamo.com/4a6658b6-2ac7-4715-b54e-5d6d3b97a191'
FFMPEG_BIN = r"C:\ffmpeg-n4.4-latest-win64-lgpl-4.4\bin\ffmpeg.exe"

from threading import Thread
import cv2


class VideoStreamWidget(object):
    def __init__(self, src=0):
        # Create a VideoCapture object
        self.capture = cv2.VideoCapture(src)

        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()

    def show_frame(self):
        # Display frames in main program
        if self.status:
            self.frame = self.maintain_aspect_ratio_resize(self.frame, width=600)
            cv2.imshow('IP Camera Video Streaming', self.frame)

        # Press Q on keyboard to stop recording
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)

    # Resizes a image and maintains aspect ratio
    def maintain_aspect_ratio_resize(self, image, width=None, height=None, inter=cv2.INTER_AREA):
        # Grab the image size and initialize dimensions
        dim = None
        (h, w) = image.shape[:2]

        # Return original image if no need to resize
        if width is None and height is None:
            return image

        # We are resizing height if width is none
        if width is None:
            # Calculate the ratio of the height and construct the dimensions
            r = height / float(h)
            dim = (int(w * r), height)
        # We are resizing width if height is none
        else:
            # Calculate the ratio of the 0idth and construct the dimensions
            r = width / float(w)
            dim = (width, int(h * r))

        # Return the resized image
        return cv2.resize(image, dim, interpolation=inter)


if __name__ == '__main__':
    stream_link = VIDEO_URL
    video_stream_widget = VideoStreamWidget(stream_link)
    while True:
        try:
            video_stream_widget.show_frame()
        except Exception as e:
            print(e)
            pass

if __name__ == '__main__':
    ffmpeg_attempt = False
    if ffmpeg_attempt:
        pipe = sp.Popen([FFMPEG_BIN, "-i", VIDEO_URL,
                         "-loglevel", "quiet",  # no text output
                         "-an",  # disable audio
                         "-f", "image2pipe",
                         "-pix_fmt", "bgr24",
                         "-vcodec", "rawvideo", "-"],
                        stdin=sp.PIPE, stdout=sp.PIPE)
        while True:
            raw_image = pipe.stdout.read(432 * 240 * 3)  # read 432*240*3 bytes (= 1 frame)
            image = np.frombuffer(raw_image, dtype='uint8').reshape(
                (240, 432, 3))  # np.fromstring(raw_image, dtype='uint8').reshape((240, 432, 3))
            cv2.imshow("GoPro", image)
            if cv2.waitKey(5) == 27:
                break
        cv2.destroyAllWindows()

    geeks_attempt = False
    if geeks_attempt:
        # Import Required Module
        import requests
        from bs4 import BeautifulSoup

        # Web URL
        Web_url = r'https://stream.cawamo.com/rl/#'

        # Get URL Content
        r = requests.get(Web_url)

        # Parse HTML Code
        soup = BeautifulSoup(r.content, 'html.parser')

        # List of all video tag
        video_tags = soup.findAll('video')
        print("Total ", len(video_tags), "videos found")

        if len(video_tags) != 0:
            for video_tag in video_tags:
                video_url = video_tag.find("a")['href']
                print(video_url)
        else:
            print("no videos found")

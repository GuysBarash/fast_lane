import time
from tqdm import tqdm
import m3u8
import cv2
import subprocess
import multiprocessing
import matplotlib.pyplot as plt
import numpy as np

from selenium import webdriver
from bs4 import BeautifulSoup
import re
import requests
import os

import copy

import numpy as np
import cv2
from PIL import ImageGrab, ImageFont, ImageDraw, Image

VIDEO_URL = r'https://5e0da72d486c5.streamlock.net:8443/ayalon/Yosseftal.stream/playlist.m3u8'
VIDEO_URL_2 = r'https://5e0d15ab12687.streamlock.net/live/BILU.stream/playlist.m3u8'
FFMPEG_BIN = r"C:\ffmpeg-n4.4-latest-win64-lgpl-4.4\bin\ffmpeg.exe"

from threading import Thread
import cv2


class Observer:
    @staticmethod
    def runner(q, info):
        x = info['x']
        y = info['y']
        w = info['w']
        h = info['h']

        while True:
            if q.qsize() > 100:
                time.sleep(2)
            else:
                img = ImageGrab.grab(bbox=(x, y, w, h))  # x, y, w, h
                img_np = np.array(img)
                img_pil = Image.fromarray(img_np)
                q.put(img_pil)
                time.sleep(0.1)

    def __init__(self):
        self.info = dict()

        self.p = None
        self.q = None
        self.active = False

    def start(self, x=None, y=None, w=None, h=None, capture=False):

        self.info['x'] = x
        self.info['y'] = y
        self.info['w'] = w
        self.info['h'] = h

        self.q = multiprocessing.Queue()
        self.p = multiprocessing.Process(target=Observer.runner, args=(self.q, self.info,))
        self.p.start()
        self.active = True
        print("Started.")

    def kill(self):
        self.p.kill()
        self.p.join()

        self.info = dict()
        self.p = None
        self.q = None
        self.active = False
        print("Ended.")

    def get(self):
        if not self.active:
            raise Exception("Cannot get image. No active thread.")

        return self.q.get()


class TrafficLord:
    def __init__(self):
        self.prev_frame = None
        self.curr_frame = None

    def process_image(self, frame):
        self.prev_frame = self.curr_frame
        self.curr_frame = frame

        if self.prev_frame is None:
            return None

        dpath = r"C:\myprojects\fast_lane\carsexample.jpg"
        img = Image.open(dpath)
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        self.curr_frame = frame

        blur = cv2.GaussianBlur(self.curr_frame, (5, 5), 0)
        dilated = cv2.dilate(blur, np.ones((3, 3)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        closing = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)

        car_cascade_src = 'haarcascade_cas4.xml'
        car_cascade = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades,car_cascade_src))
        cars = car_cascade.detectMultiScale(closing, 1.1, 1)

        for (x, y, w, h) in cars:
            closing = cv2.rectangle(closing, (x, y), (x + w, y + h), (255, 0, 0), 2)

        plt.imshow(closing)
        plt.show()


if __name__ == '__main__':

    section_record = False
    if section_record:

        seubsection_define_image_bounds = True
        if seubsection_define_image_bounds:

            from pynput import mouse

            clicks = 1
            x, y, w, h = None, None, None, None
            with mouse.Events() as events:
                print("Click upper left corner")
                for event in events:
                    if type(event) == mouse.Events.Click and event.pressed:
                        if clicks == 1:
                            x, y = event.x, event.y
                            print(f"Click 1: {x}x{y}")
                            print("Click lower right corner")
                            clicks += 1
                            time.sleep(0.3)
                        elif clicks == 2:
                            xt, yt = event.x, event.y
                            print(f"Click 2: {xt}x{yt}")
                            w, h = xt, yt  # x - xt, y - yt
                            break
                    else:
                        pass

        frame_size = w, h
        print(f'X = {x}')
        print(f'Y = {y}')
        print(f'W = {w}')
        print(f'H = {h}')

        observer = Observer()
        observer.start(x, y, frame_size[0], frame_size[1])
        frames = list()
        frames_count = 0
        frames_total = 250

        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # XVID, MP4V DIVX
        writer = cv2.VideoWriter('output.avi', fourcc, 5, (w - x, h - y), 0)
        while True:
            img_pil = observer.get()
            draw = ImageDraw.Draw(img_pil)

            font = ImageFont.truetype("Roboto-Regular.ttf", 50)
            draw.text((0, 0), f"Frame {frames_count + 1}/{frames_total}", font=font)

            frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_BGR2GRAY)
            writer.write(frame)

            cv2.imshow(f"frame (q: {observer.q.qsize()})", frame)
            frames_count += 1
            print(frame.mean())
            print(frame.shape)

            if cv2.waitKey(1) & 0Xff == ord('q'):
                break
            if frames_count > frames_total:
                break

        observer.kill()
        writer.release()

    section_read_video = True
    if section_read_video:
        path = 'output.avi'
        cap = cv2.VideoCapture(path)
        count = 0

        trlrd = TrafficLord()
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            trlrd.process_image(frame)
            cv2.imshow('window-name', frame)
            count = count + 1
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        print(f"Viewed {count} frames")
        cap.release()
        cv2.destroyAllWindows()  # destroy all opened windows

if __name__ == '__main__':
    cv2.destroyAllWindows()

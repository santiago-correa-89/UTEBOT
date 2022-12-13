import cv2
import numpy as np
import tkinter as tk
from tkinter import *

import PIL
from PIL import ImageTk, Image

import os
import time
import datetime as dt
import argparse

class App:
    def __init__(self, window, window_title, video_source):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.ok = False

        # Call DEF that computes and estimate the local time
        self.timer = ElapsedTimeClock(self.window)
        self.timeSave = str(self.timer.t[1]) + '-' + str(self.timer.t[2]) + '-' + str(self.timer.t[3]) + '-' + str(self.timer.t[4]) + '-' + str(self.timer.t[5])

        # open video source (by default this will try to open the computer webcam)
        self.vid = VideoCapture(self.video_source, self.timeSave)

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width = self.vid.width, height = self.vid.height)
        self.canvas.pack()

        # Button that lets the user take a snapshot
        self.btn_snapshot=tk.Button(window, text='SNASPSHOT', command=self.snapshot)
        self.btn_snapshot.pack(side=tk.LEFT)

        #video control buttons

        self.btn_start=tk.Button(window, text='START', command=self.open_camera)
        self.btn_start.pack(side=tk.LEFT)

        self.btn_stop=tk.Button(window, text='STOP', command=self.close_camera)
        self.btn_stop.pack(side=tk.LEFT)

        # quit button
        self.btn_quit=tk.Button(window, text='QUIT', command=quit)
        self.btn_quit.pack(side=tk.RIGHT)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay=10
        self.update()

        self.window.mainloop()

    def snapshot(self):
        # Get a frame from the video source
        ret,frame=self.vid.get_frame()

        if ret:
            cv2.imwrite(r"code/src/Captures/UTEBOT" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame,cv2.COLOR_RGB2BGR))

    def open_camera(self):
        self.ok = True
        self.timer.start()
        print("camera opened => Recording")



    def close_camera(self):
        self.ok = False
        self.timer.stop()
        print("camera closed => Not Recording")

       
    def update(self):

        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        if self.ok:
            height, width, layers = frame.shape
            frame = cv2.resize(frame, (width, height))
            self.vid.out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
        self.window.after(self.delay,self.update)


class VideoCapture:
    def __init__(self, video_source, timer):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)

        try:
            if not self.vid.isOpened():
                raise ValueError("Unable to open video source", video_source)

            # Command Line Parser
            args=CommandLineParser().args

            #create videowriter
            # 1. Video Type
            VIDEO_TYPE = {
                    'avi': cv2.VideoWriter_fourcc(*'mjpg'),
                    'mp4': cv2.VideoWriter_fourcc(*'mp4v'),
                    }

            self.fourcc = VIDEO_TYPE[args.type[0]]

                # 2. Video Dimension
            STD_DIMENSIONS =  {
                    '480p': (640, 480),
                    '720p': (1280, 720),
                    'HD': (1920, 1080),
                    '4k': (3840, 2160),
                }
                
            self.res = STD_DIMENSIONS[args.res[0]]
                
                
                # 3. Frame per second
            FRAME_PER_SECOND =  {
                    '10': 10,
                    '20': 20,
                    '30': 30,
                    '40': 60,
                }
            self.FPS = FRAME_PER_SECOND[args.fps[0]]
                
            print(args.name, self.fourcc, self.res, self.FPS)
                
            self.out = cv2.VideoWriter(r'code/src/Videos/' + args.name[0] + timer + '.' + args.type[0], self.fourcc, self.FPS, self.res)

            #set video sourec width and height
            self.vid.set(3, self.res[0])
            self.vid.set(4, self.res[1])

                # Get video source width and height
            self.width, self.height = self.res
       
        except:
            print('Video source was not opened correctly')

    # To get frames
    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            self.out.release()
            cv2.destroyAllWindows()


class ElapsedTimeClock:
    def __init__(self, window):
        self.T = tk.Label(window, text='00:00:00', font=('times', 14, 'bold'), bg ='green')
        self.T.pack(fill = tk.BOTH, expand=1)
        self.elapsedTime = dt.datetime(1,1,1)
        self.running = 0
        self.lastTime = ''
        self.t = time.localtime()
        self.zeroTime = dt.timedelta(hours=self.t[3], minutes=self.t[4], seconds=self.t[5])
        print(self.t)
        # self.tick()

 
    def tick(self):
        # get the current local time from the PC
        self.now = dt.datetime(1, 1, 1).now()
        self.elapsedTime = self.now - self.zeroTime
        self.time2 = self.elapsedTime.strftime('%H:%M:%S')
        # if time string has changed, update it
        if self.time2 != self.lastTime:
            self.lastTime = self.time2
            self.T.config(text=self.time2)
        # calls itself every 200 milliseconds
        # to update the time display as needed
        # could use >200 ms, but display gets jerky
        self.updwin=self.T.after(100, self.tick)


    def start(self):
            if not self.running:
                self.zeroTime=dt.datetime(1, 1, 1).now()-self.elapsedTime
                self.tick()
                self.running=1

    def stop(self):
            if self.running:
                self.T.after_cancel(self.updwin)
                self.elapsedTime=dt.datetime(1, 1, 1).now()-self.zeroTime
                self.time2=self.elapsedTime
                self.running=0


class CommandLineParser:
    
    def __init__(self):

        # Create object of the Argument Parser
        parser = argparse.ArgumentParser(description = 'UTEBOT GUI definitions')

        # Only values is supporting for the tag --type. So nargs will be '1' to get
        parser.add_argument('--type', nargs=1, default=['avi'], type=str, help = 'Type of the video output: for now we have only AVI & MP4')

        # Only one values are going to accept for the tag --res. So nargs will be '1'
        parser.add_argument('--res', nargs=1, default=['480p'], type=str, help = 'Resolution of the video output: for now we have 480p, 720p, 1080p & 4k')

        # Only one values are going to accept for the tag --fps. So nargs will be '1'
        parser.add_argument('--fps', nargs=1, default=['30'], type=str, help = 'Frames per Second output: for BRIOs cam we have 10, 20, 30, 60 FPS')

        # Only one values are going to accept for the tag --name. So nargs will be '1'
        parser.add_argument('--name', nargs=1, default=['UTEBOT'], type=str, help = 'Enter Output video title/name')

        # Parse the arguments and get all the values in the form of namespace.
        # Here args is of namespace and values will be accessed through tag names
        self.args = parser.parse_args()



def main():
    # Create a window and pass it to the Application object
    
    #stream = 'rtsp://10.20.1.1:8081/unicast'
    stream = 0
    
    App(tk.Tk(),'UTEBOT', stream)

main()

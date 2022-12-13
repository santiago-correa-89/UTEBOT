import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import *
import PIL
from PIL import ImageTk, Image
import time
import datetime as dt
import argparse

RTSP_URL = 'rtsp://10.20.1.1:8081/unicast'
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'

class App:
    def __init__(self, window, project, video_source=RTSP_URL):

        self.window = window # Definition of atribute window need to create the screen
        self.window.title(project) # Definition of atribute title needed to be shown on the app screen
        self.video_source = video_source # Definition of atribute video_source that contains the link to the RTSP link
        self.ok = False

        self.timer = ElapsedTimeClock(self.window)  # Atribute timer of the app (check definition of the class timer)

        self.vid = VideoCapture(self.video_source)  # Atribute that open video source (check definition of the class video capture)

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width = self.vid.width , height = self.vid.height ) 
        self.canvas.pack()

        # Button that lets the user take a snapshot
        self.btn_snapshot=tk.Button(window, text='SNAPSHOT', command=self.snapshot)
        self.btn_snapshot.pack(side=tk.CENTER)
        self.btn_start=tk.Button(window, text='START', command=self.open_camera)
        self.btn_start.pack(side=tk.CENTER)
        self.btn_stop=tk.Button(window, text='STOP', command=self.close_camera)
        self.btn_stop.pack(side=tk.CENTER)
        self.btn_quit=tk.Button(window, text='QUIT', command=quit)
        self.btn_quit.pack(side=tk.LEFT)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay=10
        self.update()

        self.window.mainloop()

        # Add the method able to create the snapshot of the recording
        def snapshot(self):
            # Get a frame from the video source
            ret,frame=self.vid.get_frame()

            # Create the screenshot, indicating time and fixing color difference with opencv
            if ret:
                cv2.imwrite("frame-"+time.strftime("%d-%m-%Y-%H-%M-%S")+".jpg",cv2.cvtColor(frame,cv2.COLOR_RGB2BGR))

        # Add the method able indicate that camera is open and recording
        def open_camera(self):
            self.ok = True
            self.timer.start()
            print("camera opened and Recording")

        # Add the method able indicate that camera is closed and recording is stopped
        def close_camera(self):
            self.ok = False
            self.timer.stop()
            print("camera closed and Not Recording")

        def update(self):

        # Get a frame from the video source
            ret, frame = self.vid.get_frame()
            if self.ok:
                self.vid.out.write(cv2.cvtColor(frame,cv2.COLOR_RGB2BGR))

            if ret:
                self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
                self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
                self.window.after(self.delay,self.update)

# Build the class VideoCapture to start the video capture process from RTSP source
 
class VideoCapture:
    def __init__(self, video_source):

        self.RTSP = cv2.VideoCapture(video_source, cv2.CAP_FFMPEG)

        if not self.RTSP.isOpened():
            print('Cannot open RTSP stream')

        while True:
            ret,frame = self.RTSP.read()

            if ret:
            #Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            else:
                return (ret, None)

            if cv2.waitKey(1) == 27:
                break

            # Command Line Parser
            args=CommandLineParser().args

            #create videowriter

            # 1. Video Type
            VIDEO_TYPE = {
                'avi': cv2.VideoWriter_fourcc(*'XVID'),
                'mp4': cv2.VideoWriter_fourcc(*'mp4v'),
            }

            self.fourcc = VIDEO_TYPE[args.type[0]]

            # 2. Video Dimension
            STD_DIMENSIONS =  {
                '480p': (640, 480),
                '720p': (1280, 720),
                '1920': (1920, 1080),
                '3840': (3840, 2160),
            }

            res = STD_DIMENSIONS[args.res[0]]
            print(args.name, self.fourcc, res)
            self.RTSP.out = cv2.VideoWriter(args.name[0]+'.'+args.type[0], self.fourcc, cap.get(cv2.CAP_PROP_FPS), res)
        
            #set video sourec width and height
            self.RTSP.set(3,res[0])
            self.RTSP.set(4,res[1])

            # Get video source width and height
            self.width, self.height=res

            # Release the video source when the object is destroyed
            def __del__(self):
                if self.RTSP.isOpened():
                    
                    self.RTSP.release()
                    self.RTSP.out.release()
                    cv2.destroyAllWindows()


# Build the class ElapsedTimeClock to start the timer and indicate the recording time process

class ElapsedTimeClock:
    def __init__(self,window):
        self.T=tk.Label(window,text='00:00:00',font=('times', 20, 'bold'), bg='green')
        self.T.pack(fill=tk.BOTH, expand=1)
        self.elapsedTime=dt.datetime(1,1,1)
        self.running=0
        self.lastTime=''
        t = time.localtime()
        self.zeroTime = dt.timedelta(hours=t[3], minutes=t[4], seconds=t[5])
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

# Build the class CommandLineParser to establish the video parameters

class CommandLineParser:
    
    def __init__(self):

        # Create object of the Argument Parser
        parser=argparse.ArgumentParser(description='Script to record videos')

        # Create a group for requirement 
        # for now no required arguments 
        # required_arguments=parser.add_argument_group('Required command line arguments')

        # Only values is supporting for the tag --type. So nargs will be '1' to get
        parser.add_argument('--type', nargs=1, default=['mp4'], type=str, help='Type of the video output: for now we have only AVI & MP4')

        # Only one values are going to accept for the tag --res. So nargs will be '1'
        parser.add_argument('--res', nargs=1, default=['480p'], type=str, help='Resolution of the video output: for now we have 480p, 720p, 1080p & 4k')

        # Only one values are going to accept for the tag --name. So nargs will be '1'
        parser.add_argument('--name', nargs=1, default=['video'], type=str, help='Enter Output video title/name')

        # Parse the arguments and get all the values in the form of namespace.
        # Here args is of namespace and values will be accessed through tag names
        self.args = parser.parse_args()

def main():
    # Create a window and pass it to the Application object
    App(tk.Tk(),'UTEBOT')

main()
            

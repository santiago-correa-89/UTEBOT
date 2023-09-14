import cv2
import numpy as np
import time
import datetime as dt
import tkinter as tk
import paramiko
from tkinter import *
import PIL
from PIL import ImageTk, Image
import argparse
import os

class App:
    def __init__(self, window, window_title, url, folder):
        
        self.window = window
        self.window.title(window_title)
        self.video_source = url
        self.ok = False
        self.folder = folder

        # TIMER
        self.timer=ElapsedTimeClock(self.window)
        
        # OPEN VIDEO SOURCE
        self.vid = VideoCapture(self.video_source, self.folder)

        # CREATE A CANVAS THAT CAN FIT THE ABOVE VIDEO SOURCE SIZE
        self.canvas = tk.Canvas(window, width = self.vid.width, height = self.vid.height)
        self.canvas.pack()

        # VIDEO CONTROL BUTTONS
        # BUTTON THAT ALLOW TO TAKE A SNAPSHOT
        self.btn_snapshot=tk.Button(window, text="SNAPSHOT", command=self.snapshot)
        self.btn_snapshot.pack(side=tk.LEFT)

        # START RECODING BUTTON
        self.btn_start=tk.Button(window, text='START', command=self.open_camera)
        self.btn_start.pack(side=tk.LEFT)

        # STOP RECORDING BUTTON
        self.btn_stop=tk.Button(window, text='STOP', command=self.close_camera)
        self.btn_stop.pack(side=tk.LEFT)

        # QUIT BUTTON TO CLOSE SYSTEM
        self.btn_quit=tk.Button(window, text='QUIT', command=quit)
        self.btn_quit.pack(side=tk.LEFT)

        # After it is called once, the update method will be automatically called every delay milliseconds
        args=CommandLineParser().args
        _, _, _, self.delay = get_video_parameters(args)
        self.update()

        self.window.mainloop()
    
    def snapshot(self):
        # Get a frame from the video source
        ret, frame=self.vid.get_frame()

        if ret:
            cv2.imwrite(self.folder + "/Images/FRAME-" + time.strftime("%d-%m-%Y-%H-%M-%S")+".jpg",cv2.cvtColor(frame,cv2.COLOR_RGB2BGR))

    def open_camera(self):
        self.ok = True
        self.timer.start()
        
        print("CAMERA OPENED")

    def close_camera(self):
        self.ok = False
        self.timer.stop()
        print("CAMERA CLOSED")
     
    def update(self):

        # Capturar el cuadro de video
        ret, frame = self.vid.get_frame()
        
        if self.ok:
            self.vid.out.write(cv2.cvtColor(frame,cv2.COLOR_RGB2BGR))

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)

        self.window.after(self.delay, self.update)

class VideoCapture:
       
    def __init__(self, video_source, folder):
        # Open the video source
        
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("UNABLE TO OPEN VIDEO SOURCE", video_source)

        # Command Line Parser
        args=CommandLineParser().args

        fourcc, res, fps, _= get_video_parameters(args)
        
        print(args.name, fourcc, res)
        self.out = cv2.VideoWriter(folder + "/Videos/" + args.name[0] + "-" + time.strftime("%d-%m-%Y-%H-%M-%S") + '.' + args.type[0], fourcc, fps, res)

        #set video source width and height
        self.vid.set(3,res[0])
        self.vid.set(4,res[1])

        # Get video source width and height
        self.width, self.height = res


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
        self.T=tk.Label(window, text='ELAPSED TIME: 00:00:00', font=('Helvetica', 18, 'bold'), bg='green')
        self.T.pack(fill=tk.BOTH, expand=1)
        self.elapsedTime=dt.datetime(1,1,1)
        self.running=0
        self.lastTime=''
        t = time.localtime()
        self.zeroTime = dt.timedelta(hours=t[3], minutes=t[4], seconds=t[5])

 
    def tick(self):
        # get the current local time from the PC
        self.now = dt.datetime(1, 1, 1).now()
        self.elapsedTime = self.now - self.zeroTime
        self.time2 = self.elapsedTime.strftime('%H:%M:%S')
        # if time string has changed, update it
        if self.time2 != self.lastTime:
            self.lastTime = self.time2
            self.T.config(text=self.time2)
        # calls itself every fps millisecondsto update the time display
        self.updwin=self.T.after(33, self.tick)

    def start(self):
            if not self.running:
                self.zeroTime=dt.datetime(1, 1, 1).now() - self.elapsedTime
                self.tick()
                self.running=1

    def stop(self):
            if self.running:
                self.T.after_cancel(self.updwin)
                self.elapsedTime=dt.datetime(1, 1, 1).now() - self.zeroTime
                self.time2=self.elapsedTime
                self.running=0

class CommandLineParser:  
    def __init__(self):

        # Create object of the Argument Parser
        parser=argparse.ArgumentParser(description='GUI for camera display')

        # Create a group for requirement 
        # for now no required arguments 
        # required_arguments=parser.add_argument_group('Required command line arguments')

        # Only values is supporting for the tag --type. So nargs will be '1' to get
        parser.add_argument('--type', nargs=1, default=['avi'], type=str, help='Type of the video output: for now we have only AVI or MP4')

        # Only one values are going to accept for the tag --res. So nargs will be '1'
        parser.add_argument('--res', nargs=1, default=['720'], type=str, help='Resolution of the video output: for now we have 720')

        # Only one values are going to accept for the tag --name. So nargs will be '1'
        parser.add_argument('--name', nargs=1, default=['UTEBOT'], type=str, help='Enter Output video title/name')

        # Only one values are going to accept for the tag --name. So nargs will be '1'
        parser.add_argument('--fps', nargs=1, default=['30'], type=str, help='Frame per Second rate of the video output: LOGITECH default setting 30 fps')

        # Parse the arguments and get all the values in the form of namespace.
        # Here args is of namespace and values will be accessed through tag names
        self.args = parser.parse_args()

def get_video_parameters(args):
    # 1. Video Type
    VIDEO_TYPE = {
        'avi': cv2.VideoWriter_fourcc(*'MPEG'),
        'mp4': cv2.VideoWriter_fourcc(*'MP4V'),
    }
    fourcc = VIDEO_TYPE[args.type[0]]

    # 2. Video Dimension
    STD_DIMENSIONS = {
        '720': (1280, 720),
        '1080': (1920, 1080),
    }
    res = STD_DIMENSIONS[args.res[0]]

    # 3. Video Frame Per Second
    FPS_RATE = {
        '15': 15,
        '30': 30,
    }
    fps = FPS_RATE[args.fps[0]]
    
    MS_RATE = {
    '15': 67,
    '30': 33,
    }
    ms = MS_RATE[args.fps[0]]

    return fourcc, res, fps, ms

def ssh_conn(host, user, passwd):
    try:

        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, password=passwd)
        print("SSH CONNECTION ESTABLISHED")
        
        # Command Line Parser
        args=CommandLineParser().args
        fourcc, res, fps, _ = get_video_parameters(args)

        # EXECUTE COMMAND FOR WEBCAM RECORDING
        command = '/usr/local/bin/mjpg_streamer -i "/usr/local/lib/mjpg-streamer/input_uvc.so -n -f 30 -r 1280x720" > -o "/usr/local/lib/mjpg-streamer/output_http.so -p 8085 -w /usr/local/share/mjpg-streamer/www"'
        stdin, stdout, stderr = ssh.exec_command(command)

        # CLOSE THE SSH CONNECTION
        ssh.close()
        print("SSH CONNECTION CLOSED")
    
    except Exception as err:
        print(str(err))

def main(host, user, passwd, folder):
    #Establish connection with Raspberry PI and execute the webcam order
    ssh_conn(host, user, passwd)
    # Create a window and pass it to the Application object
    App(tk.Tk(),'UTEBOT', 'http://10.20.1.1:8080/?action=stream', folder)

host = '10.20.1.1'
user = 'utebot'
passwd = 'ddm-utebot'

folder = os.getcwd()
print('Get current working directory : ', folder)

main(host, user, passwd, folder)
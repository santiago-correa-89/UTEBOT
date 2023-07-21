import cv2
import numpy as np
import tkinter as tk
import time
import datetime as dt
import argparse
from PIL import Image, ImageTk

class App:
    def __init__(self, window, window_title, rtsp_url):
        self.window = window
        self.window.title(window_title)

        # Create a video capture object to read from the RTSP source
        self.vid = cv2.VideoCapture(rtsp_url)

        # Create a canvas to display the video
        self.canvas = tk.Canvas(window)
        self.canvas.pack()

        # Create a button to start/stop recording
        self.record_button = tk.Button(window, text="Start Recording", width=20, command=self.toggle_record)
        self.record_button.pack(anchor=tk.CENTER, expand=True)

        # Command line arguments parser
        self.cmd_parser = CommandLineParser()

        # Initialize recording status
        self.is_recording = False

        # Start the video streaming
        self.stream()

        # Start the GUI main loop
        self.window.mainloop()

    def toggle_record(self):
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.record_button.config(text="Stop Recording")
            self.start_recording()
        else:
            # Stop recording
            self.is_recording = False
            self.record_button.config(text="Start Recording")
            self.stop_recording()

    def stream(self):
        try:
            # Read a frame from the video source
            ret, frame = self.vid.read()
            if ret:
                # Convert frame to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Resize frame to fit the canvas
                frame = self.resize(frame)

                # Convert frame to ImageTk format
                img = self.convert_image(frame)

                # Update the canvas with the new frame
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img)

            # Schedule the next frame update
            self.window.after(1, self.stream)

        except Exception as e:
            print("An error occurred while streaming:", str(e))

    def resize(self, frame):
        # Resize the frame to fit the canvas while maintaining aspect ratio
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        frame_width = frame.shape[1]
        frame_height = frame.shape[0]

        if frame_width > canvas_width or frame_height > canvas_height:
            scale_factor = min(canvas_width / frame_width, canvas_height / frame_height)
            new_width = int(frame_width * scale_factor)
            new_height = int(frame_height * scale_factor)
            frame = cv2.resize(frame, (new_width, new_height))

        return frame

    def convert_image(self, frame):
        # Convert the frame to ImageTk format
        img = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(image=img)

        return img

    def start_recording(self):
        try:
            # Get command line arguments
            args = self.cmd_parser.args

            # Define the codec for the output video
            VIDEO_TYPE = {
                'avi': cv2.VideoWriter_fourcc(*'XVID'),
                'mp4': cv2.VideoWriter_fourcc(*'mp4v'),
            }
            fourcc = VIDEO_TYPE[args.type[0]]

            # Define the video dimensions
            STD_DIMENSIONS = {
                '480p': (640, 480),
                '720p': (1280, 720),
                'HD': (1920, 1080),
                '4k': (3840, 2160),
            }
            res = STD_DIMENSIONS[args.res[0]]

            # Define the frames per second
            FRAME_PER_SECOND = {
                '10': 10,
                '20': 20,
                '30': 30,
                '40': 60,
            }
            fps = FRAME_PER_SECOND[args.fps[0]]

            # Create the output video writer
            output_filename = "Videos/" + args.name[0] + "_" + time.strftime("%Y-%m-%d_%H-%M-%S") + "." + args.type[0]
            self.out = cv2.VideoWriter(output_filename, fourcc, fps, res)

            # Set video source width and height
            self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
            self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])

            # Start recording frames
            while self.is_recording:
                ret, frame = self.vid.read()
                if ret:
                    # Convert frame to BGR
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    # Write frame to output video
                    self.out.write(frame)

                # Display the frame
                cv2.imshow('Recording', frame)

                # Check for 'q' key press to stop recording
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Release the video writer and video capture objects
            self.out.release()

            # Destroy the OpenCV windows
            cv2.destroyAllWindows()

        except Exception as e:
            print("An error occurred while recording:", str(e))

    def stop_recording(self):
        # Stop the recording loop
        cv2.waitKey(1)

class CommandLineParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Webcam Recorder")
        self.parser.add_argument('-n', '--name', nargs=1, type=str, default=[time.strftime("%Y-%m-%d_%H-%M-%S")],
                                 help='Specify the name of the output file (default is current date and time)')
        self.parser.add_argument('-t', '--type', nargs=1, type=str, default=['avi'], choices=['avi', 'mp4'],
                                 help='Specify the video file extension (default is avi)')
        self.parser.add_argument('-r', '--res', nargs=1, type=str, default=['480p'], choices=['480p', '720p', 'HD', '4k'],
                                 help='Specify the resolution (default is 480p)')
        self.parser.add_argument('-f', '--fps', nargs=1, type=str, default=['30'], choices=['10', '20', '30', '40'],
                                 help='Specify the frames per second (default is 30)')
        self.args = self.parser.parse_args()


# Create a window and pass it to the Application object
App(tk.Tk(), "Webcam Recorder", "rtsp://10.20.1.1:8080/unicast")
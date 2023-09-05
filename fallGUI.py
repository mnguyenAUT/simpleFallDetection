import cv2
import mediapipe as mp
import tkinter as tk
import numpy as np
from tkinter import ttk
from PIL import Image, ImageTk
import os

# Initialize
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
step = 1  # Resetting step

# Global variable to keep track of the after ID
after_id = None
cap = None

def stop_video():
    global after_id, cap
    if after_id is not None:
        lmain.after_cancel(after_id)
        after_id = None
    if cap is not None:
        cap.release()
        
def detect_fall(landmarks):
    nose = landmarks.landmark[mp_pose.PoseLandmark.NOSE.value].y
    left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value].y
    right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value].y
    #print(nose)
    #print(left_hip)
    #print(right_hip)
    #print("---")
    if abs(nose - left_hip) < 0.125 or abs(nose - right_hip) < 0.125:
        return True
    return False
    
def draw_connections(image, landmarks, connections, color=(255, 255, 255)):
    h, w, _ = image.shape
    for connection in connections:
        start_idx = connection[0]
        end_idx = connection[1]
        x1, y1 = int(landmarks[start_idx].x * w), int(landmarks[start_idx].y * h)
        x2, y2 = int(landmarks[end_idx].x * w), int(landmarks[end_idx].y * h)
        cv2.line(image, (x1, y1), (x2, y2), color, 3)
    
    

    
        
def play_video():
    global cap, frame_count, step, after_id
    ret, frame = cap.read()
    frame_count += 1
    blurry = 35
    if not ret:
        lmain.after_cancel(play_video)
        cap.release()
        return

    if frame_count % step == 0:
        h, w, c = frame.shape
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        
        frame = (frame * 0.5).astype(np.uint8)
        frame = cv2.blur(frame, (blurry, blurry))
        #if blurry < 100:
        #    blurry += 1
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            for landmark in landmarks:
                x, y = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(frame, (x, y), 5, (255, 255, 255), -1)
            # Draw skeleton with white lines
            pose_connections = mp_pose.POSE_CONNECTIONS
            
            if detect_fall(results.pose_landmarks):
                cv2.putText(frame, 'FALL DETECTED', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                draw_connections(frame, landmarks, pose_connections, (0, 0, 255))
                step = 0
            else:
                draw_connections(frame, landmarks, pose_connections)
            
        if step < 5:
            step = step + 1

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(frame)
        im = im.resize((1024, int(h * 1024 / w)))  # Resize proportionally
        imgtk = ImageTk.PhotoImage(image=im) 
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)

    after_id = lmain.after(1, play_video)  # Delayed by 1 second

def on_select(event=None):
    global cap, frame_count, step
    stop_video()  # Stop video if it is already playing
    frame_count = 0  # Resetting frame_count
    step = 1  # Resetting step
    selected_video = combo.get()
    video_path = os.path.join('dataset', selected_video)
    cap = cv2.VideoCapture(video_path)
    play_video()

# GUI
root = tk.Tk()
root.title("Fall Detection")

frame1 = tk.Frame(root)
frame1.pack(side=tk.LEFT, padx=20, pady=20)

frame2 = tk.Frame(root)
frame2.pack(side=tk.RIGHT, padx=20, pady=20)

# Drop-down to select video
video_files = os.listdir('dataset')
video_files.insert(0, '')  # Insert an empty string at the first position

combo = ttk.Combobox(frame1, values=video_files)
combo.pack(pady=20)

combo.current(0)  # Automatically select the empty string at index 0

combo.bind("<<ComboboxSelected>>", on_select)


# Label to display video
lmain = tk.Label(frame2)
lmain.pack(pady=20)

root.mainloop()

#!/usr/bin/env python3

"""
smart_crop.py
Smart cropping for converting landscape videos to 9:16 format
Uses face detection and movement analysis to keep important content in frame
"""

import cv2
import numpy as np
import sys
import os

def detect_faces_in_video(video_path, start_frame=0, end_frame=None):
    """Detect faces in video and return average position"""
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        return None
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if end_frame is None:
        end_frame = total_frames
    
    face_positions = []
    frame_count = 0
    
    # Sample every 30th frame for performance
    for frame_num in range(start_frame, min(end_frame, total_frames), 30):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            # Use the largest face
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            center_x = x + w // 2
            center_y = y + h // 2
            face_positions.append((center_x, center_y))
        
        frame_count += 1
    
    cap.release()
    
    if face_positions:
        # Return average face position
        avg_x = sum(pos[0] for pos in face_positions) // len(face_positions)
        avg_y = sum(pos[1] for pos in face_positions) // len(face_positions)
        return (avg_x, avg_y)
    
    return None

def calculate_smart_crop(video_path, target_width=1080, target_height=1920):
    """Calculate optimal crop position for 9:16 format"""
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        return "crop=1080:1920:420:0"  # Default center crop
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    print(f"Original video: {width}x{height}")
    
    # Try to detect faces
    face_center = detect_faces_in_video(video_path)
    
    if face_center:
        face_x, face_y = face_center
        print(f"Face detected at: ({face_x}, {face_y})")
        
        # Calculate crop position to center the face
        crop_x = max(0, min(width - target_width, face_x - target_width // 2))
        crop_y = max(0, min(height - target_height, face_y - target_height // 2))
    else:
        print("No face detected, using center crop")
        # Default center crop
        crop_x = max(0, (width - target_width) // 2)
        crop_y = max(0, (height - target_height) // 2)
    
    return f"crop={target_width}:{target_height}:{crop_x}:{crop_y}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python smart_crop.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        sys.exit(1)
    
    crop_filter = calculate_smart_crop(video_path)
    print(crop_filter)

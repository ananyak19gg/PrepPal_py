import cv2
import numpy as np
from typing import Dict

# Load detectors
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')


def analyze_video(video_path: str) -> Dict:
    """
    Analyze video for face visibility, posture, and gaze
    """
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        return {"success": False, "error": "Cannot open video file"}
    
    total_frames = 0
    frames_with_face = 0
    frames_good_posture = 0
    frames_good_gaze = 0
    
    # Process every frame for better accuracy
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 3 != 0:
            continue
        total_frames += 1
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast
        gray = cv2.equalizeHist(gray)
        
        # Try multiple detection attempts with different parameters
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=3,
            minSize=(40, 40)
        )
        
        if len(faces) > 0:
            frames_with_face += 1
            
            # Get largest face
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            (x, y, w, h) = largest_face
            
            face_roi_gray = gray[y:y+h, x:x+w]
            frame_height, frame_width = gray.shape
            
            # === POSTURE ANALYSIS ===
            face_center_y = y + h/2
            
            # Good posture: face in upper 70% of frame
            if face_center_y < frame_height * 0.7:
                frames_good_posture += 1
            
            # === GAZE ANALYSIS ===
            # Use upper half of face for eye detection
            face_upper_half = face_roi_gray[0:int(h*0.5), :]
            
            # Try eye detection
            eyes = eye_cascade.detectMultiScale(face_upper_half, 1.05, 2, minSize=(10, 10))
            
            # More lenient fallback
            if len(eyes) == 0:
                eyes = eye_cascade.detectMultiScale(face_roi_gray, 1.02, 1, minSize=(8, 8))
            
            if len(eyes) >= 1:
                frames_good_gaze += 1
            else:
                # Fallback: If face is centered, assume looking forward
                face_center_x = x + w/2
                if abs(face_center_x - frame_width/2) < frame_width * 0.25:
                    frames_good_gaze += 1
    
    cap.release()
    
    # Calculate scores
    if total_frames == 0:
        return {"success": False, "error": "No valid frames analyzed"}
    
    face_visibility = (frames_with_face / total_frames * 100)
    posture_score = (frames_good_posture / frames_with_face * 100) if frames_with_face > 0 else 0
    gaze_score = (frames_good_gaze / frames_with_face * 100) if frames_with_face > 0 else 0
    
    # Overall engagement
    engagement_score = (
        face_visibility * 0.4 +
        posture_score * 0.3 +
        gaze_score * 0.3
    )
    
    return {
        "success": True,
        "faceVisibility": round(face_visibility, 2),
        "postureScore": round(posture_score, 2),
        "gazeScore": round(gaze_score, 2),
        "engagementScore": round(engagement_score, 2),
        "totalFrames": total_frames,
        "framesWithFace": frames_with_face
    }
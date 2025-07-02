import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple, Dict, Optional

class PoseDetector:
    """姿态检测器，使用MediaPipe进行人体关键点检测"""
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
    def detect_pose(self, frame: np.ndarray) -> Optional[Dict]:
        """检测单帧的姿态关键点"""
        # 转换为RGB格式
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)
        
        if results.pose_landmarks:
            landmarks = []
            for landmark in results.pose_landmarks.landmark:
                landmarks.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
            return {
                'landmarks': landmarks,
                'pose_landmarks': results.pose_landmarks
            }
        return None
    
    def draw_pose(self, frame: np.ndarray, pose_data: Dict) -> np.ndarray:
        """在帧上绘制姿态关键点"""
        annotated_frame = frame.copy()
        self.mp_drawing.draw_landmarks(
            annotated_frame,
            pose_data['pose_landmarks'],
            self.mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
        )
        return annotated_frame
    
    def get_key_points(self, pose_data: Dict) -> Dict[str, Tuple[float, float]]:
        """提取关键点坐标"""
        landmarks = pose_data['landmarks']
        
        key_points = {
            'nose': (landmarks[0]['x'], landmarks[0]['y']),
            'left_shoulder': (landmarks[11]['x'], landmarks[11]['y']),
            'right_shoulder': (landmarks[12]['x'], landmarks[12]['y']),
            'left_elbow': (landmarks[13]['x'], landmarks[13]['y']),
            'right_elbow': (landmarks[14]['x'], landmarks[14]['y']),
            'left_wrist': (landmarks[15]['x'], landmarks[15]['y']),
            'right_wrist': (landmarks[16]['x'], landmarks[16]['y']),
            'left_hip': (landmarks[23]['x'], landmarks[23]['y']),
            'right_hip': (landmarks[24]['x'], landmarks[24]['y']),
            'left_knee': (landmarks[25]['x'], landmarks[25]['y']),
            'right_knee': (landmarks[26]['x'], landmarks[26]['y']),
            'left_ankle': (landmarks[27]['x'], landmarks[27]['y']),
            'right_ankle': (landmarks[28]['x'], landmarks[28]['y'])
        }
        
        return key_points
    
    def calculate_angle(self, point1: Tuple[float, float], 
                       point2: Tuple[float, float], 
                       point3: Tuple[float, float]) -> float:
        """计算三点之间的角度"""
        a = np.array(point1)
        b = np.array(point2)
        c = np.array(point3)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def calculate_distance(self, point1: Tuple[float, float], 
                          point2: Tuple[float, float]) -> float:
        """计算两点之间的距离"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2) 
import numpy as np
from typing import Dict, List, Tuple, Optional
from pose_detection import PoseDetector
import cv2

class BenchPressAnalyzer:
    """卧推姿势分析器"""
    
    def __init__(self):
        self.pose_detector = PoseDetector()
        
        # 卧推姿势的标准角度范围
        self.standard_angles = {
            'shoulder_angle': (80, 100),  # 肩部角度
            'elbow_angle_down': (70, 90),  # 下放时肘部角度
            'elbow_angle_up': (160, 180),  # 推起时肘部角度
            'hip_angle': (160, 180),  # 髋部角度
            'knee_angle': (80, 100)  # 膝盖角度
        }
        
        # 卧推动作状态
        self.states = {
            'IDLE': 0,
            'SETUP': 1,
            'DOWN': 2,
            'UP': 3,
            'COMPLETE': 4
        }
        
    def is_bench_press_pose(self, pose_data: Dict) -> bool:
        """判断是否为卧推姿势"""
        if not pose_data:
            return False
            
        key_points = self.pose_detector.get_key_points(pose_data)
        
        # 检查关键点是否可见
        if not self._check_visibility(key_points):
            return False
        
        # 计算关键角度
        angles = self._calculate_pose_angles(key_points)
        
        # 卧推姿势的基本判断条件
        conditions = [
            # 身体基本平躺（肩部到髋部的角度接近水平）
            angles['shoulder_hip_angle'] > 160,
            # 手臂弯曲（肘部角度在合理范围内）
            60 < angles['left_elbow_angle'] < 120 or 60 < angles['right_elbow_angle'] < 120,
            # 腿部弯曲（膝盖角度在合理范围内）
            70 < angles['left_knee_angle'] < 110 or 70 < angles['right_knee_angle'] < 110,
            # 手腕位置在肩部附近
            self._check_wrist_position(key_points)
        ]
        
        return all(conditions)
    
    def analyze_pose_quality(self, pose_data: Dict) -> Dict:
        """分析姿势标准性"""
        if not pose_data:
            return {'score': 0, 'feedback': '无法检测到姿态'}
        
        key_points = self.pose_detector.get_key_points(pose_data)
        angles = self._calculate_pose_angles(key_points)
        
        score = 100
        feedback = []
        
        # 检查肩部角度
        if angles['shoulder_hip_angle'] < 160:
            score -= 20
            feedback.append("身体没有保持平躺，请调整背部位置")
        
        # 检查肘部角度
        left_elbow = angles['left_elbow_angle']
        right_elbow = angles['right_elbow_angle']
        
        if left_elbow < 60 or left_elbow > 120:
            score -= 15
            feedback.append("左臂弯曲角度不当")
        if right_elbow < 60 or right_elbow > 120:
            score -= 15
            feedback.append("右臂弯曲角度不当")
        
        # 检查膝盖角度
        left_knee = angles['left_knee_angle']
        right_knee = angles['right_knee_angle']
        
        if left_knee < 70 or left_knee > 110:
            score -= 10
            feedback.append("左腿弯曲角度不当")
        if right_knee < 70 or right_knee > 110:
            score -= 10
            feedback.append("右腿弯曲角度不当")
        
        # 检查手腕位置
        if not self._check_wrist_position(key_points):
            score -= 20
            feedback.append("手腕位置不当，应保持在肩部正上方")
        
        # 检查身体对称性
        symmetry_score = self._check_symmetry(key_points)
        score += symmetry_score
        
        if symmetry_score < 0:
            feedback.append("身体姿势不对称，请调整")
        
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'feedback': feedback,
            'angles': angles
        }
    
    def detect_bench_press_phase(self, pose_data: Dict) -> str:
        """检测卧推动作阶段"""
        if not pose_data:
            return 'IDLE'
        
        key_points = self.pose_detector.get_key_points(pose_data)
        angles = self._calculate_pose_angles(key_points)
        
        # 使用肘部角度判断动作阶段
        avg_elbow_angle = (angles['left_elbow_angle'] + angles['right_elbow_angle']) / 2
        
        if avg_elbow_angle < 90:
            return 'DOWN'  # 下放阶段
        elif avg_elbow_angle > 160:
            return 'UP'    # 推起阶段
        else:
            return 'SETUP' # 准备阶段
    
    def _calculate_pose_angles(self, key_points: Dict) -> Dict:
        """计算姿态角度"""
        angles = {}
        
        # 肩部到髋部的角度（身体平躺程度）
        angles['shoulder_hip_angle'] = self.pose_detector.calculate_angle(
            key_points['left_shoulder'],
            key_points['left_hip'],
            key_points['right_hip']
        )
        
        # 左臂肘部角度
        angles['left_elbow_angle'] = self.pose_detector.calculate_angle(
            key_points['left_shoulder'],
            key_points['left_elbow'],
            key_points['left_wrist']
        )
        
        # 右臂肘部角度
        angles['right_elbow_angle'] = self.pose_detector.calculate_angle(
            key_points['right_shoulder'],
            key_points['right_elbow'],
            key_points['right_wrist']
        )
        
        # 左腿膝盖角度
        angles['left_knee_angle'] = self.pose_detector.calculate_angle(
            key_points['left_hip'],
            key_points['left_knee'],
            key_points['left_ankle']
        )
        
        # 右腿膝盖角度
        angles['right_knee_angle'] = self.pose_detector.calculate_angle(
            key_points['right_hip'],
            key_points['right_knee'],
            key_points['right_ankle']
        )
        
        return angles
    
    def _check_visibility(self, key_points: Dict) -> bool:
        """检查关键点可见性"""
        required_points = ['left_shoulder', 'right_shoulder', 'left_elbow', 
                          'right_elbow', 'left_wrist', 'right_wrist']
        
        for point in required_points:
            if point not in key_points:
                return False
        return True
    
    def _check_wrist_position(self, key_points: Dict) -> bool:
        """检查手腕位置是否在肩部正上方"""
        left_wrist = key_points['left_wrist']
        right_wrist = key_points['right_wrist']
        left_shoulder = key_points['left_shoulder']
        right_shoulder = key_points['right_shoulder']
        
        # 检查手腕是否在肩部上方
        left_vertical_diff = abs(left_wrist[0] - left_shoulder[0])
        right_vertical_diff = abs(right_wrist[0] - right_shoulder[0])
        
        # 允许一定的水平偏移
        max_horizontal_offset = 0.1
        
        return (left_vertical_diff < max_horizontal_offset and 
                right_vertical_diff < max_horizontal_offset)
    
    def _check_symmetry(self, key_points: Dict) -> float:
        """检查身体对称性"""
        # 计算左右两侧的肘部角度差异
        left_elbow_angle = self.pose_detector.calculate_angle(
            key_points['left_shoulder'],
            key_points['left_elbow'],
            key_points['left_wrist']
        )
        
        right_elbow_angle = self.pose_detector.calculate_angle(
            key_points['right_shoulder'],
            key_points['right_elbow'],
            key_points['right_wrist']
        )
        
        angle_diff = abs(left_elbow_angle - right_elbow_angle)
        
        # 角度差异越小，对称性越好
        if angle_diff < 10:
            return 10
        elif angle_diff < 20:
            return 5
        else:
            return -10 
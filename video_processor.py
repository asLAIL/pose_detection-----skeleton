import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple, Callable
from pose_detection import PoseDetector
from bench_press_analyzer import BenchPressAnalyzer
from workout_tracker import WorkoutTracker
import time
from datetime import datetime

class VideoProcessor:
    """视频处理器，用于分析卧推视频"""
    
    def __init__(self):
        self.pose_detector = PoseDetector()
        self.analyzer = BenchPressAnalyzer()
        self.tracker = WorkoutTracker()
        
        # 状态变量
        self.current_workout_id = None
        self.is_recording = False
        self.current_set_data = []
        self.rep_count = 0
        self.last_phase = 'IDLE'
        self.phase_transitions = []
        
    def process_video_file(self, video_path: str, output_path: Optional[str] = None,
                          callback: Optional[Callable] = None) -> Dict:
        """处理视频文件"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        # 获取视频信息
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 设置输出视频
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        else:
            out = None
        
        # 初始化分析结果
        analysis_results = {
            'total_frames': total_frames,
            'bench_press_frames': 0,
            'sets': [],
            'average_score': 0,
            'total_reps': 0,
            'duration': 0,
            'start_time': datetime.now().isoformat()
        }
        
        frame_count = 0
        bench_press_frames = 0
        current_set = []
        
        print(f"开始处理视频: {video_path}")
        print(f"视频信息: {width}x{height}, {fps}fps, {total_frames}帧")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 检测姿态
            pose_data = self.pose_detector.detect_pose(frame)
            
            if pose_data:
                # 判断是否为卧推姿势
                is_bench_press = self.analyzer.is_bench_press_pose(pose_data)
                
                if is_bench_press:
                    bench_press_frames += 1
                    
                    # 分析姿势质量
                    quality_analysis = self.analyzer.analyze_pose_quality(pose_data)
                    
                    # 检测动作阶段
                    current_phase = self.analyzer.detect_bench_press_phase(pose_data)
                    
                    # 记录当前帧数据
                    frame_data = {
                        'frame': frame_count,
                        'timestamp': frame_count / fps,
                        'phase': current_phase,
                        'score': quality_analysis['score'],
                        'angles': quality_analysis['angles'],
                        'feedback': quality_analysis['feedback']
                    }
                    
                    current_set.append(frame_data)
                    
                    # 在帧上绘制分析结果
                    annotated_frame = self._draw_analysis_on_frame(
                        frame, pose_data, quality_analysis, current_phase
                    )
                else:
                    # 如果不是卧推姿势，结束当前组
                    if current_set:
                        set_summary = self._analyze_set(current_set)
                        analysis_results['sets'].append(set_summary)
                        current_set = []
                    
                    annotated_frame = frame
            else:
                annotated_frame = frame
            
            # 写入输出视频
            if out:
                out.write(annotated_frame)
            
            # 调用回调函数
            if callback:
                progress = frame_count / total_frames
                callback(progress, frame_count, total_frames)
            
            # 显示进度
            if frame_count % 100 == 0:
                print(f"处理进度: {frame_count}/{total_frames} ({frame_count/total_frames*100:.1f}%)")
        
        # 处理最后一组
        if current_set:
            set_summary = self._analyze_set(current_set)
            analysis_results['sets'].append(set_summary)
        
        # 计算总体统计
        analysis_results['bench_press_frames'] = bench_press_frames
        analysis_results['total_reps'] = sum(set_data['reps'] for set_data in analysis_results['sets'])
        analysis_results['average_score'] = np.mean([set_data['average_score'] for set_data in analysis_results['sets']]) if analysis_results['sets'] else 0
        analysis_results['duration'] = total_frames / fps
        analysis_results['end_time'] = datetime.now().isoformat()
        
        # 清理资源
        cap.release()
        if out:
            out.release()
        
        print(f"视频处理完成: {analysis_results['total_reps']}次重复, 平均分数: {analysis_results['average_score']:.1f}")
        
        return analysis_results
    
    def start_realtime_analysis(self, camera_id: int = 0):
        """开始实时分析（摄像头）"""
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            raise ValueError(f"无法打开摄像头: {camera_id}")
        
        # 开始新的锻炼会话
        self.current_workout_id = self.tracker.start_workout()
        self.is_recording = True
        self.current_set_data = []
        self.rep_count = 0
        self.last_phase = 'IDLE'
        self.phase_transitions = []
        
        print("开始实时卧推分析...")
        print("按 'q' 退出, 's' 开始/停止记录, 'r' 重置计数")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 检测姿态
            pose_data = self.pose_detector.detect_pose(frame)
            
            if pose_data:
                # 判断是否为卧推姿势
                is_bench_press = self.analyzer.is_bench_press_pose(pose_data)
                
                if is_bench_press:
                    # 分析姿势质量
                    quality_analysis = self.analyzer.analyze_pose_quality(pose_data)
                    
                    # 检测动作阶段
                    current_phase = self.analyzer.detect_bench_press_phase(pose_data)
                    
                    # 检测重复次数
                    if self.last_phase == 'DOWN' and current_phase == 'UP':
                        self.rep_count += 1
                        print(f"重复次数: {self.rep_count}")
                    
                    self.last_phase = current_phase
                    
                    # 记录数据
                    if self.is_recording:
                        frame_data = {
                            'timestamp': time.time(),
                            'phase': current_phase,
                            'score': quality_analysis['score'],
                            'angles': quality_analysis['angles']
                        }
                        self.current_set_data.append(frame_data)
                    
                    # 在帧上绘制分析结果
                    annotated_frame = self._draw_realtime_analysis(
                        frame, pose_data, quality_analysis, current_phase
                    )
                else:
                    annotated_frame = frame
            else:
                annotated_frame = frame
            
            # 显示帧
            cv2.imshow('卧推姿势分析', annotated_frame)
            
            # 处理按键
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.is_recording = not self.is_recording
                print(f"记录状态: {'开启' if self.is_recording else '关闭'}")
            elif key == ord('r'):
                self._save_current_set()
                self.rep_count = 0
                self.current_set_data = []
                print("重置计数")
        
        # 保存最后一组数据
        if self.current_set_data:
            self._save_current_set()
        
        # 结束锻炼会话
        if self.current_workout_id:
            self.tracker.end_workout(self.current_workout_id)
        
        cap.release()
        cv2.destroyAllWindows()
    
    def _draw_analysis_on_frame(self, frame: np.ndarray, pose_data: Dict, 
                               quality_analysis: Dict, phase: str) -> np.ndarray:
        """在帧上绘制分析结果"""
        # 绘制姿态关键点
        annotated_frame = self.pose_detector.draw_pose(frame, pose_data)
        
        # 添加文本信息
        height, width = annotated_frame.shape[:2]
        
        # 姿势分数
        score = quality_analysis['score']
        score_color = (0, 255, 0) if score >= 80 else (0, 255, 255) if score >= 60 else (0, 0, 255)
        cv2.putText(annotated_frame, f'分数: {score:.1f}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, score_color, 2)
        
        # 动作阶段
        phase_text = f'阶段: {phase}'
        cv2.putText(annotated_frame, phase_text, (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 反馈信息
        feedback = quality_analysis['feedback']
        if feedback:
            for i, msg in enumerate(feedback[:3]):  # 只显示前3条反馈
                cv2.putText(annotated_frame, msg, (10, 110 + i * 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
        
        return annotated_frame
    
    def _draw_realtime_analysis(self, frame: np.ndarray, pose_data: Dict, 
                               quality_analysis: Dict, phase: str) -> np.ndarray:
        """在帧上绘制实时分析结果"""
        annotated_frame = self._draw_analysis_on_frame(frame, pose_data, quality_analysis, phase)
        
        # 添加实时信息
        height, width = annotated_frame.shape[:2]
        
        # 重复次数
        cv2.putText(annotated_frame, f'重复: {self.rep_count}', (width - 200, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 记录状态
        record_status = '记录中' if self.is_recording else '暂停'
        record_color = (0, 255, 0) if self.is_recording else (0, 0, 255)
        cv2.putText(annotated_frame, record_status, (width - 200, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, record_color, 2)
        
        return annotated_frame
    
    def _analyze_set(self, set_data: List[Dict]) -> Dict:
        """分析一组数据"""
        if not set_data:
            return {}
        
        # 计算重复次数
        phases = [frame['phase'] for frame in set_data]
        rep_count = 0
        for i in range(1, len(phases)):
            if phases[i-1] == 'DOWN' and phases[i] == 'UP':
                rep_count += 1
        
        # 计算平均分数
        scores = [frame['score'] for frame in set_data]
        average_score = np.mean(scores)
        
        return {
            'reps': rep_count,
            'average_score': average_score,
            'frames': len(set_data),
            'duration': set_data[-1]['timestamp'] - set_data[0]['timestamp'],
            'phase_data': set_data
        }
    
    def _save_current_set(self):
        """保存当前组数据"""
        if not self.current_set_data or not self.current_workout_id:
            return
        
        set_analysis = self._analyze_set(self.current_set_data)
        if set_analysis['reps'] > 0:
            self.tracker.add_set(
                self.current_workout_id,
                set_analysis['reps'],
                set_analysis['average_score'],
                self.current_set_data
            )
            print(f"保存组数据: {set_analysis['reps']}次重复, 平均分数: {set_analysis['average_score']:.1f}") 
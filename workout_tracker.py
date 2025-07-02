import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os

class WorkoutTracker:
    """锻炼数据跟踪器"""
    
    def __init__(self, data_file: str = "workout_data.json"):
        self.data_file = data_file
        self.workout_data = self._load_data()
        
    def _load_data(self) -> Dict:
        """加载历史锻炼数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._initialize_data()
        else:
            return self._initialize_data()
    
    def _initialize_data(self) -> Dict:
        """初始化数据结构"""
        return {
            'workouts': [],
            'statistics': {
                'total_workouts': 0,
                'total_reps': 0,
                'total_sets': 0,
                'best_score': 0,
                'average_score': 0,
                'total_duration': 0
            }
        }
    
    def _save_data(self):
        """保存数据到文件"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.workout_data, f, ensure_ascii=False, indent=2)
    
    def start_workout(self) -> str:
        """开始新的锻炼会话"""
        workout_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        workout = {
            'id': workout_id,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'sets': [],
            'total_reps': 0,
            'total_sets': 0,
            'average_score': 0,
            'best_score': 0,
            'duration': 0,
            'notes': ''
        }
        
        self.workout_data['workouts'].append(workout)
        self._save_data()
        return workout_id
    
    def end_workout(self, workout_id: str):
        """结束锻炼会话"""
        workout = self._find_workout(workout_id)
        if workout:
            workout['end_time'] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(workout['start_time'])
            end_time = datetime.fromisoformat(workout['end_time'])
            workout['duration'] = (end_time - start_time).total_seconds()
            
            # 计算统计数据
            if workout['sets']:
                scores = [set_data['score'] for set_data in workout['sets']]
                workout['average_score'] = np.mean(scores)
                workout['best_score'] = max(scores)
                workout['total_reps'] = sum(set_data['reps'] for set_data in workout['sets'])
                workout['total_sets'] = len(workout['sets'])
            
            self._update_statistics()
            self._save_data()
    
    def add_set(self, workout_id: str, reps: int, score: float, 
                phase_data: List[Dict], notes: str = "") -> bool:
        """添加一组卧推数据"""
        workout = self._find_workout(workout_id)
        if not workout:
            return False
        
        set_data = {
            'set_number': len(workout['sets']) + 1,
            'reps': reps,
            'score': score,
            'phase_data': phase_data,
            'timestamp': datetime.now().isoformat(),
            'notes': notes
        }
        
        workout['sets'].append(set_data)
        self._save_data()
        return True
    
    def get_workout_summary(self, workout_id: str) -> Optional[Dict]:
        """获取锻炼会话摘要"""
        workout = self._find_workout(workout_id)
        if not workout:
            return None
        
        return {
            'id': workout['id'],
            'date': workout['start_time'][:10],
            'duration': workout['duration'],
            'total_sets': workout['total_sets'],
            'total_reps': workout['total_reps'],
            'average_score': workout['average_score'],
            'best_score': workout['best_score'],
            'notes': workout['notes']
        }
    
    def get_statistics(self, days: int = 30) -> Dict:
        """获取统计数据"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_workouts = [
            w for w in self.workout_data['workouts']
            if datetime.fromisoformat(w['start_time']) > cutoff_date
        ]
        
        if not recent_workouts:
            return {
                'period': f'最近{days}天',
                'total_workouts': 0,
                'total_reps': 0,
                'total_sets': 0,
                'average_score': 0,
                'best_score': 0,
                'total_duration': 0,
                'average_duration': 0
            }
        
        total_reps = sum(w['total_reps'] for w in recent_workouts)
        total_sets = sum(w['total_sets'] for w in recent_workouts)
        scores = [w['average_score'] for w in recent_workouts if w['average_score'] > 0]
        durations = [w['duration'] for w in recent_workouts if w['duration'] > 0]
        
        return {
            'period': f'最近{days}天',
            'total_workouts': len(recent_workouts),
            'total_reps': total_reps,
            'total_sets': total_sets,
            'average_score': np.mean(scores) if scores else 0,
            'best_score': max(scores) if scores else 0,
            'total_duration': sum(durations),
            'average_duration': np.mean(durations) if durations else 0
        }
    
    def get_progress_data(self, days: int = 30) -> Dict:
        """获取进度数据用于图表显示"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_workouts = [
            w for w in self.workout_data['workouts']
            if datetime.fromisoformat(w['start_time']) > cutoff_date
        ]
        
        dates = []
        scores = []
        reps = []
        sets = []
        
        for workout in recent_workouts:
            date = workout['start_time'][:10]
            dates.append(date)
            scores.append(workout['average_score'])
            reps.append(workout['total_reps'])
            sets.append(workout['total_sets'])
        
        return {
            'dates': dates,
            'scores': scores,
            'reps': reps,
            'sets': sets
        }
    
    def get_recommendations(self) -> List[str]:
        """获取锻炼建议"""
        stats = self.get_statistics(7)  # 最近7天
        recommendations = []
        
        if stats['total_workouts'] == 0:
            recommendations.append("开始你的第一次卧推锻炼吧！")
            return recommendations
        
        if stats['average_score'] < 70:
            recommendations.append("建议多关注姿势标准性，可以降低重量专注于动作质量")
        
        if stats['total_workouts'] < 3:
            recommendations.append("建议每周进行3-4次卧推训练以保持进步")
        
        if stats['average_duration'] < 1800:  # 30分钟
            recommendations.append("建议延长训练时间，确保充分热身和放松")
        
        if stats['total_reps'] < 20:
            recommendations.append("建议增加训练量，每组8-12次重复")
        
        return recommendations
    
    def _find_workout(self, workout_id: str) -> Optional[Dict]:
        """查找锻炼会话"""
        for workout in self.workout_data['workouts']:
            if workout['id'] == workout_id:
                return workout
        return None
    
    def _update_statistics(self):
        """更新总体统计数据"""
        workouts = self.workout_data['workouts']
        
        if not workouts:
            return
        
        total_workouts = len(workouts)
        total_reps = sum(w['total_reps'] for w in workouts)
        total_sets = sum(w['total_sets'] for w in workouts)
        scores = [w['average_score'] for w in workouts if w['average_score'] > 0]
        durations = [w['duration'] for w in workouts if w['duration'] > 0]
        
        self.workout_data['statistics'] = {
            'total_workouts': total_workouts,
            'total_reps': total_reps,
            'total_sets': total_sets,
            'best_score': max(scores) if scores else 0,
            'average_score': np.mean(scores) if scores else 0,
            'total_duration': sum(durations)
        }
    
    def export_to_csv(self, filename: str = "workout_data.csv"):
        """导出数据到CSV文件"""
        data = []
        
        for workout in self.workout_data['workouts']:
            for set_data in workout['sets']:
                row = {
                    'workout_id': workout['id'],
                    'date': workout['start_time'][:10],
                    'set_number': set_data['set_number'],
                    'reps': set_data['reps'],
                    'score': set_data['score'],
                    'duration': workout['duration'],
                    'notes': set_data['notes']
                }
                data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        return filename 
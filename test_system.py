#!/usr/bin/env python3
"""
卧推姿势分析系统测试脚本
测试各个模块的基本功能
"""

import sys
import os
import numpy as np
from datetime import datetime

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        import cv2
        print("✅ OpenCV 导入成功")
    except ImportError as e:
        print(f"❌ OpenCV 导入失败: {e}")
        return False
    
    try:
        import mediapipe as mp
        print("✅ MediaPipe 导入成功")
    except ImportError as e:
        print(f"❌ MediaPipe 导入失败: {e}")
        return False
    
    try:
        import streamlit as st
        print("✅ Streamlit 导入成功")
    except ImportError as e:
        print(f"❌ Streamlit 导入失败: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ Plotly 导入成功")
    except ImportError as e:
        print(f"❌ Plotly 导入失败: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas 导入成功")
    except ImportError as e:
        print(f"❌ Pandas 导入失败: {e}")
        return False
    
    return True

def test_pose_detection():
    """测试姿态检测模块"""
    print("\n🔍 测试姿态检测模块...")
    
    try:
        from pose_detection import PoseDetector
        detector = PoseDetector()
        print("✅ PoseDetector 初始化成功")
        
        # 创建一个测试图像
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        pose_data = detector.detect_pose(test_image)
        print("✅ 姿态检测功能正常")
        
        return True
    except Exception as e:
        print(f"❌ 姿态检测测试失败: {e}")
        return False

def test_bench_press_analyzer():
    """测试卧推分析器"""
    print("\n🔍 测试卧推分析器...")
    
    try:
        from bench_press_analyzer import BenchPressAnalyzer
        analyzer = BenchPressAnalyzer()
        print("✅ BenchPressAnalyzer 初始化成功")
        
        # 测试角度计算
        point1 = (0, 0)
        point2 = (1, 0)
        point3 = (1, 1)
        angle = analyzer.pose_detector.calculate_angle(point1, point2, point3)
        print(f"✅ 角度计算功能正常: {angle:.1f}°")
        
        return True
    except Exception as e:
        print(f"❌ 卧推分析器测试失败: {e}")
        return False

def test_workout_tracker():
    """测试锻炼跟踪器"""
    print("\n🔍 测试锻炼跟踪器...")
    
    try:
        from workout_tracker import WorkoutTracker
        tracker = WorkoutTracker("test_data.json")
        print("✅ WorkoutTracker 初始化成功")
        
        # 测试开始锻炼会话
        workout_id = tracker.start_workout()
        print(f"✅ 开始锻炼会话成功: {workout_id}")
        
        # 测试添加数据
        test_data = [
            {'timestamp': 0, 'phase': 'SETUP', 'score': 85},
            {'timestamp': 1, 'phase': 'DOWN', 'score': 80},
            {'timestamp': 2, 'phase': 'UP', 'score': 90}
        ]
        success = tracker.add_set(workout_id, 1, 85.0, test_data, "测试组")
        print(f"✅ 添加数据成功: {success}")
        
        # 测试结束锻炼会话
        tracker.end_workout(workout_id)
        print("✅ 结束锻炼会话成功")
        
        # 测试获取统计
        stats = tracker.get_statistics(7)
        print(f"✅ 获取统计数据成功: {stats['total_workouts']} 次锻炼")
        
        # 清理测试文件
        if os.path.exists("test_data.json"):
            os.remove("test_data.json")
        
        return True
    except Exception as e:
        print(f"❌ 锻炼跟踪器测试失败: {e}")
        return False

def test_video_processor():
    """测试视频处理器"""
    print("\n🔍 测试视频处理器...")
    
    try:
        from video_processor import VideoProcessor
        processor = VideoProcessor()
        print("✅ VideoProcessor 初始化成功")
        
        # 测试创建处理器
        print("✅ 视频处理器创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 视频处理器测试失败: {e}")
        return False

def test_web_app():
    """测试Web应用模块"""
    print("\n🔍 测试Web应用模块...")
    
    try:
        import app
        print("✅ Web应用模块导入成功")
        
        return True
    except Exception as e:
        print(f"❌ Web应用模块测试失败: {e}")
        return False

def test_camera():
    """测试摄像头"""
    print("\n🔍 测试摄像头...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            print("✅ 摄像头可用")
            ret, frame = cap.read()
            if ret:
                print(f"✅ 摄像头读取成功，图像尺寸: {frame.shape}")
            else:
                print("⚠️  摄像头读取失败")
            cap.release()
        else:
            print("⚠️  摄像头不可用")
        
        return True
    except Exception as e:
        print(f"❌ 摄像头测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 卧推姿势分析系统测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("姿态检测", test_pose_detection),
        ("卧推分析器", test_bench_press_analyzer),
        ("锻炼跟踪器", test_workout_tracker),
        ("视频处理器", test_video_processor),
        ("Web应用", test_web_app),
        ("摄像头", test_camera)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以正常使用")
        print("\n🚀 启动建议:")
        print("  - Web界面: python run.py web")
        print("  - 演示脚本: python run.py demo")
        print("  - 实时分析: python run.py realtime")
    else:
        print("⚠️  部分测试失败，请检查依赖安装")
        print("\n💡 解决建议:")
        print("  - 安装依赖: pip install -r requirements.txt")
        print("  - 检查Python版本: 需要Python 3.8+")
        print("  - 检查摄像头权限")

if __name__ == "__main__":
    main() 
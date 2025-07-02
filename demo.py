#!/usr/bin/env python3
"""
卧推姿势分析系统演示脚本
演示如何使用系统进行视频分析和实时分析
"""

import os
import sys
from video_processor import VideoProcessor
from workout_tracker import WorkoutTracker

def demo_video_analysis():
    """演示视频文件分析"""
    print("=" * 50)
    print("🎬 视频文件分析演示")
    print("=" * 50)
    
    # 检查是否有示例视频文件
    video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.avi', '.mov'))]
    
    if not video_files:
        print("❌ 未找到视频文件")
        print("请将卧推视频文件放在当前目录下，支持格式: .mp4, .avi, .mov")
        return
    
    print(f"📹 找到视频文件: {video_files[0]}")
    
    # 创建处理器
    processor = VideoProcessor()
    
    try:
        # 分析视频
        print("🔄 开始分析视频...")
        results = processor.process_video_file(video_files[0])
        
        # 显示结果
        print("\n✅ 分析完成!")
        print(f"📊 总重复次数: {results['total_reps']}")
        print(f"📈 平均分数: {results['average_score']:.1f}")
        print(f"⏱️  训练时长: {results['duration']:.1f}秒")
        print(f"🎯 卧推帧数: {results['bench_press_frames']}")
        
        # 显示各组详情
        if results['sets']:
            print("\n📋 各组详情:")
            for i, set_data in enumerate(results['sets']):
                print(f"  第{i+1}组: {set_data['reps']}次重复, 平均分数: {set_data['average_score']:.1f}")
        
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")

def demo_realtime_analysis():
    """演示实时分析"""
    print("=" * 50)
    print("⚡ 实时分析演示")
    print("=" * 50)
    
    print("📹 准备启动摄像头...")
    print("💡 使用说明:")
    print("  - 确保摄像头正常工作")
    print("  - 调整位置，确保全身在视野内")
    print("  - 开始卧推动作")
    print("  - 按 'q' 退出, 's' 暂停/继续, 'r' 重置")
    
    input("按回车键开始实时分析...")
    
    processor = VideoProcessor()
    
    try:
        processor.start_realtime_analysis()
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        print("💡 请检查摄像头是否可用")

def demo_data_statistics():
    """演示数据统计功能"""
    print("=" * 50)
    print("📊 数据统计演示")
    print("=" * 50)
    
    tracker = WorkoutTracker()
    
    # 显示统计数据
    stats_7d = tracker.get_statistics(7)
    stats_30d = tracker.get_statistics(30)
    
    print("📈 最近7天统计:")
    print(f"  锻炼次数: {stats_7d['total_workouts']}")
    print(f"  重复次数: {stats_7d['total_reps']}")
    print(f"  平均分数: {stats_7d['average_score']:.1f}")
    print(f"  训练时长: {stats_7d['total_duration']/60:.1f}分钟")
    
    print("\n📈 最近30天统计:")
    print(f"  锻炼次数: {stats_30d['total_workouts']}")
    print(f"  重复次数: {stats_30d['total_reps']}")
    print(f"  平均分数: {stats_30d['average_score']:.1f}")
    print(f"  训练时长: {stats_30d['total_duration']/60:.1f}分钟")
    
    # 显示建议
    recommendations = tracker.get_recommendations()
    if recommendations:
        print("\n💡 锻炼建议:")
        for rec in recommendations:
            print(f"  - {rec}")

def demo_workout_tracking():
    """演示锻炼跟踪功能"""
    print("=" * 50)
    print("🎯 锻炼跟踪演示")
    print("=" * 50)
    
    tracker = WorkoutTracker()
    
    # 开始新的锻炼会话
    workout_id = tracker.start_workout()
    print(f"🏁 开始新的锻炼会话: {workout_id}")
    
    # 模拟添加一些数据
    print("📝 模拟添加锻炼数据...")
    
    # 模拟第一组数据
    set1_data = [
        {'timestamp': 0, 'phase': 'SETUP', 'score': 85, 'angles': {}},
        {'timestamp': 1, 'phase': 'DOWN', 'score': 80, 'angles': {}},
        {'timestamp': 2, 'phase': 'UP', 'score': 90, 'angles': {}},
        {'timestamp': 3, 'phase': 'DOWN', 'score': 82, 'angles': {}},
        {'timestamp': 4, 'phase': 'UP', 'score': 88, 'angles': {}}
    ]
    
    tracker.add_set(workout_id, 2, 85.0, set1_data, "第一组热身")
    print("✅ 添加第一组: 2次重复, 平均分数85.0")
    
    # 模拟第二组数据
    set2_data = [
        {'timestamp': 10, 'phase': 'SETUP', 'score': 88, 'angles': {}},
        {'timestamp': 11, 'phase': 'DOWN', 'score': 85, 'angles': {}},
        {'timestamp': 12, 'phase': 'UP', 'score': 92, 'angles': {}},
        {'timestamp': 13, 'phase': 'DOWN', 'score': 87, 'angles': {}},
        {'timestamp': 14, 'phase': 'UP', 'score': 90, 'angles': {}}
    ]
    
    tracker.add_set(workout_id, 2, 88.5, set2_data, "第二组正式训练")
    print("✅ 添加第二组: 2次重复, 平均分数88.5")
    
    # 结束锻炼会话
    tracker.end_workout(workout_id)
    print("🏁 结束锻炼会话")
    
    # 显示锻炼摘要
    summary = tracker.get_workout_summary(workout_id)
    if summary:
        print("\n📊 锻炼摘要:")
        print(f"  日期: {summary['date']}")
        print(f"  总组数: {summary['total_sets']}")
        print(f"  总重复: {summary['total_reps']}")
        print(f"  平均分数: {summary['average_score']:.1f}")
        print(f"  最佳分数: {summary['best_score']:.1f}")

def main():
    """主函数"""
    print("💪 卧推姿势分析系统演示")
    print("=" * 50)
    
    while True:
        print("\n请选择演示功能:")
        print("1. 🎬 视频文件分析")
        print("2. ⚡ 实时分析")
        print("3. 📊 数据统计")
        print("4. 🎯 锻炼跟踪")
        print("5. 🌐 启动Web界面")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-5): ").strip()
        
        if choice == '1':
            demo_video_analysis()
        elif choice == '2':
            demo_realtime_analysis()
        elif choice == '3':
            demo_data_statistics()
        elif choice == '4':
            demo_workout_tracking()
        elif choice == '5':
            print("🌐 启动Web界面...")
            print("请在浏览器中访问: http://localhost:8501")
            os.system("streamlit run app.py")
        elif choice == '0':
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请重新输入")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main() 
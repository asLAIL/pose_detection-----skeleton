#!/usr/bin/env python3
"""
卧推姿势分析系统启动脚本
提供多种启动方式：Web界面、命令行演示、实时分析等
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = [
        'opencv-python',
        'mediapipe',
        'streamlit',
        'plotly',
        'pandas',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def start_web_app():
    """启动Web应用"""
    print("🌐 启动Web应用...")
    print("请在浏览器中访问: http://localhost:8501")
    print("按 Ctrl+C 停止服务")
    
    try:
        subprocess.run(["streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Web应用已停止")
    except FileNotFoundError:
        print("❌ 未找到streamlit，请先安装: pip install streamlit")
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")

def start_demo():
    """启动演示脚本"""
    print("🎬 启动演示脚本...")
    try:
        subprocess.run([sys.executable, "demo.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 演示已停止")
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")

def start_realtime():
    """启动实时分析"""
    print("⚡ 启动实时分析...")
    try:
        from video_processor import VideoProcessor
        processor = VideoProcessor()
        processor.start_realtime_analysis()
    except KeyboardInterrupt:
        print("\n👋 实时分析已停止")
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")

def analyze_video(video_path):
    """分析指定视频文件"""
    print(f"📹 分析视频文件: {video_path}")
    
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return
    
    try:
        from video_processor import VideoProcessor
        processor = VideoProcessor()
        results = processor.process_video_file(video_path)
        
        print("\n✅ 分析完成!")
        print(f"📊 总重复次数: {results['total_reps']}")
        print(f"📈 平均分数: {results['average_score']:.1f}")
        print(f"⏱️  训练时长: {results['duration']:.1f}秒")
        
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")

def show_help():
    """显示帮助信息"""
    print("💪 卧推姿势分析系统")
    print("=" * 50)
    print("使用方法:")
    print("  python run.py web          # 启动Web界面")
    print("  python run.py demo         # 启动演示脚本")
    print("  python run.py realtime     # 启动实时分析")
    print("  python run.py video <file> # 分析指定视频文件")
    print("  python run.py install      # 安装依赖")
    print("  python run.py help         # 显示帮助")
    print("\n示例:")
    print("  python run.py web")
    print("  python run.py video my_workout.mp4")

def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖包...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ 依赖安装完成")
    except Exception as e:
        print(f"❌ 安装失败: {str(e)}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="卧推姿势分析系统")
    parser.add_argument("command", nargs="?", default="help", 
                       choices=["web", "demo", "realtime", "video", "install", "help"],
                       help="要执行的命令")
    parser.add_argument("video_file", nargs="?", help="要分析的视频文件路径")
    
    args = parser.parse_args()
    
    # 检查依赖
    if args.command != "install" and not check_dependencies():
        return
    
    # 执行命令
    if args.command == "web":
        start_web_app()
    elif args.command == "demo":
        start_demo()
    elif args.command == "realtime":
        start_realtime()
    elif args.command == "video":
        if not args.video_file:
            print("❌ 请指定视频文件路径")
            print("示例: python run.py video my_workout.mp4")
            return
        analyze_video(args.video_file)
    elif args.command == "install":
        install_dependencies()
    elif args.command == "help":
        show_help()

if __name__ == "__main__":
    main() 
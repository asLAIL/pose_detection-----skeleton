import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import tempfile
from video_processor import VideoProcessor
from workout_tracker import WorkoutTracker
import cv2
from PIL import Image
import io

# 页面配置
st.set_page_config(
    page_title="卧推姿势分析系统",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .score-high { color: #28a745; }
    .score-medium { color: #ffc107; }
    .score-low { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# 初始化组件
@st.cache_resource
def init_components():
    return VideoProcessor(), WorkoutTracker()

processor, tracker = init_components()

# 主标题
st.markdown('<h1 class="main-header">💪 卧推姿势分析系统</h1>', unsafe_allow_html=True)

# 侧边栏
st.sidebar.title("功能菜单")
page = st.sidebar.selectbox(
    "选择功能",
    ["🏠 主页", "📹 视频分析", "📊 数据统计", "⚡ 实时分析", "📈 进度追踪", "⚙️ 设置"]
)

if page == "🏠 主页":
    st.header("欢迎使用卧推姿势分析系统")
    
    # 快速统计
    col1, col2, col3, col4 = st.columns(4)
    
    stats = tracker.get_statistics(30)
    
    with col1:
        st.metric("总锻炼次数", stats['total_workouts'])
    
    with col2:
        st.metric("总重复次数", stats['total_reps'])
    
    with col3:
        st.metric("平均分数", f"{stats['average_score']:.1f}")
    
    with col4:
        st.metric("最佳分数", f"{stats['best_score']:.1f}")
    
    # 最近建议
    st.subheader("💡 锻炼建议")
    recommendations = tracker.get_recommendations()
    for rec in recommendations:
        st.info(rec)
    
    # 快速开始
    st.subheader("🚀 快速开始")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("开始实时分析", type="primary"):
            st.session_state.start_realtime = True
            st.rerun()
    
    with col2:
        uploaded_file = st.file_uploader("上传视频文件", type=['mp4', 'avi', 'mov'])
        if uploaded_file is not None:
            st.session_state.uploaded_video = uploaded_file

elif page == "📹 视频分析":
    st.header("视频文件分析")
    
    uploaded_file = st.file_uploader(
        "选择卧推视频文件",
        type=['mp4', 'avi', 'mov', 'mkv'],
        help="支持常见的视频格式"
    )
    
    if uploaded_file is not None:
        # 保存上传的文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            video_path = tmp_file.name
        
        # 分析选项
        col1, col2 = st.columns(2)
        with col1:
            save_output = st.checkbox("保存分析结果视频", value=True)
        with col2:
            show_progress = st.checkbox("显示处理进度", value=True)
        
        if st.button("开始分析", type="primary"):
            with st.spinner("正在分析视频..."):
                # 进度条
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(progress, current, total):
                    progress_bar.progress(progress)
                    status_text.text(f"处理进度: {current}/{total} 帧 ({progress*100:.1f}%)")
                
                try:
                    # 处理视频
                    output_path = None
                    if save_output:
                        output_path = "output_analysis.mp4"
                    
                    results = processor.process_video_file(
                        video_path, 
                        output_path,
                        progress_callback if show_progress else None
                    )
                    
                    # 显示结果
                    st.success("分析完成！")
                    
                    # 结果统计
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("总重复次数", results['total_reps'])
                    with col2:
                        st.metric("平均分数", f"{results['average_score']:.1f}")
                    with col3:
                        st.metric("训练时长", f"{results['duration']:.1f}秒")
                    
                    # 详细结果
                    st.subheader("详细分析结果")
                    if results['sets']:
                        sets_data = []
                        for i, set_data in enumerate(results['sets']):
                            sets_data.append({
                                '组数': i + 1,
                                '重复次数': set_data['reps'],
                                '平均分数': f"{set_data['average_score']:.1f}",
                                '时长(秒)': f"{set_data['duration']:.1f}"
                            })
                        
                        df = pd.DataFrame(sets_data)
                        st.dataframe(df, use_container_width=True)
                        
                        # 分数分布图
                        scores = [set_data['average_score'] for set_data in results['sets']]
                        fig = px.histogram(
                            x=scores,
                            title="分数分布",
                            labels={'x': '分数', 'y': '频次'},
                            nbins=10
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # 下载结果视频
                    if save_output and os.path.exists(output_path):
                        with open(output_path, 'rb') as f:
                            st.download_button(
                                label="下载分析结果视频",
                                data=f.read(),
                                file_name="bench_press_analysis.mp4",
                                mime="video/mp4"
                            )
                
                except Exception as e:
                    st.error(f"分析过程中出现错误: {str(e)}")
                finally:
                    # 清理临时文件
                    if os.path.exists(video_path):
                        os.unlink(video_path)
                    if save_output and os.path.exists(output_path):
                        os.unlink(output_path)

elif page == "📊 数据统计":
    st.header("锻炼数据统计")
    
    # 时间范围选择
    col1, col2 = st.columns(2)
    with col1:
        days = st.selectbox("统计时间范围", [7, 30, 90, 365], index=1)
    with col2:
        if st.button("刷新数据"):
            st.rerun()
    
    # 获取统计数据
    stats = tracker.get_statistics(days)
    progress_data = tracker.get_progress_data(days)
    
    # 统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>锻炼次数</h3>
            <h2>{stats['total_workouts']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>总重复次数</h3>
            <h2>{stats['total_reps']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        score_class = "score-high" if stats['average_score'] >= 80 else "score-medium" if stats['average_score'] >= 60 else "score-low"
        st.markdown(f"""
        <div class="metric-card">
            <h3>平均分数</h3>
            <h2 class="{score_class}">{stats['average_score']:.1f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>总训练时长</h3>
            <h2>{stats['total_duration']/60:.1f}分钟</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # 进度图表
    if progress_data['dates']:
        st.subheader("进度趋势")
        
        # 分数趋势
        fig_score = px.line(
            x=progress_data['dates'],
            y=progress_data['scores'],
            title="平均分数趋势",
            labels={'x': '日期', 'y': '分数'}
        )
        st.plotly_chart(fig_score, use_container_width=True)
        
        # 重复次数趋势
        fig_reps = px.bar(
            x=progress_data['dates'],
            y=progress_data['reps'],
            title="每日重复次数",
            labels={'x': '日期', 'y': '重复次数'}
        )
        st.plotly_chart(fig_reps, use_container_width=True)
    
    # 导出数据
    st.subheader("数据导出")
    if st.button("导出CSV数据"):
        csv_file = tracker.export_to_csv()
        with open(csv_file, 'r', encoding='utf-8') as f:
            st.download_button(
                label="下载CSV文件",
                data=f.read(),
                file_name="workout_data.csv",
                mime="text/csv"
            )

elif page == "⚡ 实时分析":
    st.header("实时卧推分析")
    
    st.info("""
    **使用说明：**
    1. 点击"开始实时分析"启动摄像头
    2. 调整位置，确保全身在摄像头视野内
    3. 开始卧推动作，系统会自动识别和计数
    4. 按 'q' 退出，'s' 暂停/继续记录，'r' 重置计数
    """)
    
    if st.button("开始实时分析", type="primary"):
        st.warning("正在启动摄像头...")
        try:
            processor.start_realtime_analysis()
        except Exception as e:
            st.error(f"启动失败: {str(e)}")

elif page == "📈 进度追踪":
    st.header("个人进度追踪")
    
    # 目标设置
    st.subheader("目标设置")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        weekly_goal = st.number_input("每周锻炼次数目标", min_value=1, value=3)
    with col2:
        score_goal = st.number_input("目标平均分数", min_value=0, max_value=100, value=80)
    with col3:
        reps_goal = st.number_input("每周重复次数目标", min_value=10, value=50)
    
    # 目标完成情况
    stats = tracker.get_statistics(7)
    
    st.subheader("本周目标完成情况")
    
    # 锻炼次数目标
    workout_progress = min(stats['total_workouts'] / weekly_goal, 1.0)
    st.progress(workout_progress)
    st.write(f"锻炼次数: {stats['total_workouts']}/{weekly_goal} ({workout_progress*100:.1f}%)")
    
    # 分数目标
    score_progress = min(stats['average_score'] / score_goal, 1.0) if score_goal > 0 else 0
    st.progress(score_progress)
    st.write(f"平均分数: {stats['average_score']:.1f}/{score_goal} ({score_progress*100:.1f}%)")
    
    # 重复次数目标
    reps_progress = min(stats['total_reps'] / reps_goal, 1.0)
    st.progress(reps_progress)
    st.write(f"重复次数: {stats['total_reps']}/{reps_goal} ({reps_progress*100:.1f}%)")

elif page == "⚙️ 设置":
    st.header("系统设置")
    
    st.subheader("数据管理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("清除所有数据", type="secondary"):
            if st.checkbox("确认清除所有数据"):
                # 这里可以添加清除数据的逻辑
                st.success("数据已清除")
    
    with col2:
        if st.button("备份数据"):
            # 这里可以添加备份数据的逻辑
            st.success("数据备份完成")
    
    st.subheader("分析参数")
    
    # 可以添加一些可配置的参数
    confidence_threshold = st.slider("检测置信度阈值", 0.1, 1.0, 0.5, 0.1)
    min_rep_duration = st.number_input("最小重复时长(秒)", 0.5, 5.0, 1.0, 0.1)
    
    if st.button("保存设置"):
        st.success("设置已保存")

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>💪 卧推姿势分析系统 | 基于MediaPipe和OpenCV构建</p>
        <p>帮助您提升卧推技巧，获得更好的训练效果</p>
    </div>
    """,
    unsafe_allow_html=True
) 
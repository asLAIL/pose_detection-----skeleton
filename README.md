# 💪 卧推姿势分析系统

一个基于计算机视觉的智能卧推姿势分析系统，能够自动识别卧推动作、分析姿势标准性，并提供详细的锻炼数据统计。

## ✨ 功能特点

- **🎯 智能识别**: 使用MediaPipe实时检测人体关键点，准确识别卧推姿势
- **📊 姿势分析**: 分析卧推动作的标准性，提供详细的反馈建议
- **📈 数据统计**: 自动统计锻炼数据，包括重复次数、平均分数、训练时长等
- **⚡ 实时分析**: 支持摄像头实时分析，即时反馈
- **📹 视频处理**: 支持上传视频文件进行离线分析
- **🌐 Web界面**: 提供友好的Web界面，方便查看数据和分析结果
- **📊 进度追踪**: 可视化展示训练进度和趋势

## 🛠️ 技术栈

- **Python 3.8+**
- **OpenCV**: 视频处理和图像处理
- **MediaPipe**: 人体姿态检测
- **Streamlit**: Web应用界面
- **Plotly**: 数据可视化
- **NumPy & Pandas**: 数据处理和分析

## 📦 安装指南

### 1. 克隆项目

```bash
git clone <repository-url>
cd 骨骼识别
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 🚀 使用方法

### 启动Web应用

```bash
streamlit run app.py
```

应用将在 `http://localhost:8501` 启动。

### 命令行使用

#### 1. 视频文件分析

```python
from video_processor import VideoProcessor

processor = VideoProcessor()
results = processor.process_video_file("your_video.mp4", "output.mp4")
print(f"分析完成: {results['total_reps']}次重复, 平均分数: {results['average_score']:.1f}")
```

#### 2. 实时分析

```python
from video_processor import VideoProcessor

processor = VideoProcessor()
processor.start_realtime_analysis()  # 启动摄像头实时分析
```

## 📱 功能模块

### 1. 主页
- 快速统计概览
- 锻炼建议
- 快速开始选项

### 2. 视频分析
- 上传视频文件
- 自动分析卧推动作
- 生成分析报告
- 下载分析结果视频

### 3. 数据统计
- 训练数据可视化
- 进度趋势图表
- 数据导出功能

### 4. 实时分析
- 摄像头实时分析
- 即时姿势反馈
- 自动重复计数

### 5. 进度追踪
- 目标设置
- 完成情况跟踪
- 个性化建议

## 🎯 卧推姿势标准

系统基于以下标准分析卧推姿势：

### 身体姿势
- **平躺**: 身体保持平躺，肩部到髋部角度 > 160°
- **对称性**: 左右两侧动作对称
- **稳定性**: 身体保持稳定，避免晃动

### 手臂动作
- **肘部角度**: 下放时70-90°，推起时160-180°
- **手腕位置**: 保持在肩部正上方
- **动作轨迹**: 垂直上下运动

### 腿部姿势
- **膝盖角度**: 70-110°，保持稳定
- **脚部位置**: 平放在地面，提供支撑

## 📊 评分系统

系统根据以下维度进行评分（满分100分）：

- **身体平躺度** (20分): 检查身体是否保持平躺
- **肘部角度** (30分): 左右手臂弯曲角度
- **膝盖角度** (20分): 腿部弯曲角度
- **手腕位置** (20分): 手腕是否在正确位置
- **对称性** (10分): 身体动作对称性

## 🔧 配置说明

### 检测参数
- `min_detection_confidence`: 姿态检测置信度阈值 (默认: 0.5)
- `min_tracking_confidence`: 姿态跟踪置信度阈值 (默认: 0.5)

### 分析参数
- `shoulder_hip_angle`: 肩部到髋部角度阈值 (默认: > 160°)
- `elbow_angle_range`: 肘部角度范围 (默认: 60-120°)
- `knee_angle_range`: 膝盖角度范围 (默认: 70-110°)

## 📁 项目结构

```
骨骼识别/
├── app.py                 # Streamlit Web应用
├── pose_detection.py      # 姿态检测模块
├── bench_press_analyzer.py # 卧推分析器
├── video_processor.py     # 视频处理器
├── workout_tracker.py     # 锻炼数据跟踪器
├── requirements.txt       # 依赖包列表
├── README.md             # 项目说明
└── data/                 # 数据存储目录
    ├── workout_data.json # 锻炼数据
    └── videos/           # 视频文件
```

## 🎨 界面预览

### 主页
- 统计卡片显示关键指标
- 锻炼建议和快速开始选项

### 视频分析
- 文件上传界面
- 分析进度显示
- 结果统计和图表

### 数据统计
- 进度趋势图表
- 数据导出功能
- 个性化建议

## 🔍 使用技巧

### 最佳拍摄角度
- 侧面拍摄，确保能看到完整的卧推动作
- 保持适当距离，确保全身在画面中
- 光线充足，避免阴影干扰

### 提高识别准确率
- 穿着紧身运动服，便于关键点检测
- 保持动作标准，避免快速晃动
- 确保摄像头稳定，避免抖动

### 数据管理
- 定期导出数据备份
- 设置合理的训练目标
- 关注分数趋势，及时调整训练计划

## 🐛 常见问题

### Q: 系统无法检测到姿态？
A: 检查摄像头是否正常工作，确保光线充足，人物在画面中清晰可见。

### Q: 识别准确率不高？
A: 调整拍摄角度，确保侧面拍摄，穿着紧身运动服，保持动作标准。

### Q: 视频处理速度慢？
A: 可以降低视频分辨率或帧率，或者使用更快的硬件设备。

### Q: 数据丢失怎么办？
A: 定期导出CSV数据备份，系统会自动保存到JSON文件中。

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🙏 致谢

- [MediaPipe](https://mediapipe.dev/) - 人体姿态检测
- [OpenCV](https://opencv.org/) - 计算机视觉库
- [Streamlit](https://streamlit.io/) - Web应用框架
- [Plotly](https://plotly.com/) - 数据可视化

---

�� **开始你的智能卧推训练之旅吧！** 
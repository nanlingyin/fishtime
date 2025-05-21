# Ciallo～(∠・ω< )⌒☆
# README.md
- en [English](README.en.md)
- zh_CN [简体中文](README.zh_CN.md)
# 摸鱼时间追踪器 (Fish Time)

<div align="center">
  <img src="icon/text.png" alt="Fish Time Logo" width="120">
  <br>
  <p>记录你的时间，提升你的效率</p>
</div>

## 📝 项目简介

摸鱼时间追踪器是一款桌面应用程序，用于自动记录用户在不同应用程序上花费的时间。通过详细的统计和直观的可视化报告，帮助用户了解自己的时间分配情况，从而提高工作效率和时间管理能力。

## ✨ 主要功能

- **实时监控追踪**：自动检测并记录当前正在使用的应用程序，精确统计使用时长
- **进程白名单管理**：支持添加不需要监控的应用到白名单，灵活控制监控范围
- **多样化报告生成**：生成当天使用时间的详细报表，包含应用名称、图标和使用时长
- **数据导出功能**：支持将使用数据导出为XLSX、CSV和PDF格式，方便存档和分析
- **多语言界面**：支持中文和英文界面切换，满足不同用户需求
- **主题定制**：提供暗黑、白色和灰色三种主题风格，个性化视觉体验
- **字体设置**：自定义界面字体和颜色，打造舒适的使用环境
- **系统托盘运行**：可最小化到系统托盘，保持记录的同时不占用桌面空间

## 🔧 技术栈

- **编程语言**: Python
- **图形界面**: PyQt5
- **数据存储**: SQLite
- **数据可视化**: Matplotlib
- **辅助库**: psutil, openpyxl, fpdf, pywin32

## 📦 安装使用

### 1. 环境要求

- Python 3.6或更高版本
- Windows操作系统

### 2. 获取代码

```bash
git clone https://github.com/yourusername/fishtime.git
cd fishtime
```

### 3. 安装依赖

```bash
# 创建并激活虚拟环境(可选)
python -m venv .venv
.venv\Scripts\activate

# 安装依赖包
pip install -r requirements.txt
```

### 4. 运行应用

```bash
python app.py
```

## 🚀 使用指南

1. **启动应用**：运行程序后，应用会自动开始记录当前活动窗口的使用情况
2. **查看当前追踪**：主界面显示当前活动的应用名称及其图标
3. **管理白名单**：通过"进程白名单"功能，添加或移除不需要监控的应用
   - 手动输入应用名称添加白名单
   - 从已跟踪过的应用列表中选择添加
4. **查看报告**：点击"生成报告"查看当天的应用使用统计
5. **导出数据**：在报告界面，选择喜欢的格式(XLSX/CSV/PDF)导出数据
6. **清除记录**：如需清除历史数据，点击"清除记录"按钮
7. **个性化设置**：
   - 更改界面语言(中文/英文)
   - 切换主题风格(暗黑/白色/灰色)
   - 自定义字体样式和颜色

## ⚙️ 配置说明

应用配置信息保存在`config.json`文件中，包括以下设置：

```json
{
    "font_family": "Microsoft YaHei",
    "font_color": "#2E3440",
    "language": "zh_CN",
    "theme": "灰色",
    "Process Whitelist": []
}
```

- **font_family**: 界面字体
- **font_color**: 字体颜色
- **language**: 语言设置("zh_CN"或"en_US")
- **theme**: 界面主题("暗黑"、"白色"或"灰色")
- **Process Whitelist**: 进程白名单列表

## 📷 截图展示

![应用主界面](https://placeholder.com/image1) 
![报告界面](https://placeholder.com/image2)

## 📄 许可证

本项目采用MIT许可证。详情请参阅[LICENSE](LICENSE)文件。

## 🤝 贡献

欢迎对项目提出建议和改进！如有任何问题或建议，请提交issue或pull request。

---

<div align="center">
  <p>Made with ❤️ by LynngNAN</p>
</div>

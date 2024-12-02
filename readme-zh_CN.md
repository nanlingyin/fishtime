# 摸鱼时间追踪器 (Fish Time)

## 描述

摸鱼时间追踪器是一款桌面应用，旨在记录用户每天在不同应用程序和网站上的使用时间。通过自动统计和可视化报告，帮助用户了解时间分配，提升工作效率。

## 功能

- **自动统计使用时长**：实时跟踪当前活动应用的使用时间。
- **进程白名单管理**：添加或移除不需要监控的进程。
- **生成可视化报告**：生成当天的使用时间分布图。
- **数据导出**：支持将数据导出为 CSV、XLSX 和 PDF 格式。
- **多语言支持**：支持中英文界面切换。
- **主题选择**：提供暗黑、白色和灰色主题。
- **字体设置**：自定义字体样式和颜色。
- **系统托盘最小化**：应用可最小化到系统托盘，保持桌面整洁。

## 技术栈

- **编程语言**: Python
- **GUI框架**: PyQt5
- **数据库**: SQLite
- **数据可视化**: Matplotlib
- **其他库**: psutil, openpyxl, fpdf, pywin32

## 安装

1. **克隆仓库**

    ```bash
    git clone https://github.com/yourusername/fish_time_tracker.git
    cd fish_time_tracker
    ```

2. **创建虚拟环境并激活**

    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```

3. **安装依赖**

    ```bash
    pip install -r requirements.txt
    ```

4. **运行应用**

    ```bash
    python main.py
    ```

## 配置

应用的配置文件为 

config.json

，包含以下设置：

- **font_family**: 字体名称（默认: "Microsoft YaHei"）
- **font_color**: 字体颜色（默认: "#2E3440"）
- **language**: 界面语言（"zh_CN" 或 "en_US"）
- **theme**: 主题样式（"灰色"、"白色"、"暗黑"）
- **Process Whitelist**: 白名单中的进程列表，不会被监控

示例 

config.json

：

```json
{
    "font_family": "Microsoft YaHei",
    "font_color": "#2E3440",
    "language": "zh_CN",
    "theme": "灰色",
    "Process Whitelist": []
}
```

## 使用

- **启动应用**：运行 

main.py

 启动应用程序，自动开始跟踪当前活动应用的使用时间。
- **生成报告**：点击“生成报告”按钮查看当天的使用时间分布图。
- **管理白名单**：在进程白名单中添加或移除不需要监控的应用程序。
- **导出数据**：选择导出为 CSV、XLSX 或 PDF 格式，以便进一步分析或存档。
- **设置**：
    - **字体设置**：自定义应用的字体样式和颜色。
    - **语言切换**：在语言选项中选择中文或英文界面。
    - **主题切换**：选择喜欢的主题样式（暗黑、白色、灰色）。

## 许可证

本项目采用 MIT 许可证。详情见 LICENSE。

---

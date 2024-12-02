
# Fish Time

## Description

Fish Time Tracker is a desktop application designed to record the daily usage time of different applications and websites. By automatically tracking and generating visual reports, it helps users understand their time distribution and improve productivity.

## Features

- **Automatic Time Tracking**: Real-time tracking of active application usage.
- **Process Whitelist Management**: Add or remove processes that do not need to be monitored.
- **Generate Visual Reports**: Create usage distribution charts for the day.
- **Data Export**: Export data to CSV, XLSX, and PDF formats.
- **Multi-language Support**: Interface available in both Chinese and English.
- **Theme Selection**: Choose between dark, white, and gray themes.
- **Font Settings**: Customize font styles and colors.
- **System Tray Minimization**: Minimize the application to the system tray for a clutter-free desktop.

## Tech Stack

- **Programming Language**: Python
- **GUI Framework**: PyQt5
- **Database**: SQLite
- **Data Visualization**: Matplotlib
- **Other Libraries**: psutil, openpyxl, fpdf, pywin32

## Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yourusername/fish_time_tracker.git
    cd fish_time_tracker
    ```

2. **Create and Activate Virtual Environment**

    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Application**

    ```bash
    python main.py
    ```

## Configuration

The application's configuration file is 

config.json

, which includes the following settings:

- **font_family**: Font name (default: "Microsoft YaHei")
- **font_color**: Font color (default: "#2E3440")
- **language**: Interface language ("zh_CN" or "en_US")
- **theme**: Theme style ("灰色", "白色", "暗黑")
- **Process Whitelist**: List of processes to exclude from monitoring

Example 

config.json

:

```json
{
    "font_family": "Microsoft YaHei",
    "font_color": "#2E3440",
    "language": "zh_CN",
    "theme": "灰色",
    "Process Whitelist": []
}
```

## Usage

- **Start the Application**: Run 

main.py

 to launch the application, which will automatically begin tracking the usage time of the active application.
- **Generate Reports**: Click the "Generate Report" button to view the usage time distribution for the day.
- **Manage Whitelist**: Add or remove applications from the process whitelist to exclude them from tracking.
- **Export Data**: Choose to export data in CSV, XLSX, or PDF formats for further analysis or archiving.
- **Settings**:
    - **Font Settings**: Customize the application's font style and color.
    - **Language Switching**: Select Chinese or English from the language options.
    - **Theme Switching**: Choose your preferred theme style (dark, white, gray).

## License

This project is licensed under the MIT License. See the LICENSE file for details.

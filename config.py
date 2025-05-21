# config.py
import json
import os
from constants import CONFIG_FILE, DEFAULT_CONFIG

def load_config():
    """加载配置文件，如果不存在则创建默认配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            try:
                config = json.load(f)
                # 确保所有默认键存在
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
            except json.JSONDecodeError:
                return DEFAULT_CONFIG.copy()
    else:
        config = DEFAULT_CONFIG.copy()
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value
    return config

def save_config(config):
    """保存配置到文件"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
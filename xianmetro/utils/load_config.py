"""
配置文件加载模块

提供从config.yaml读取配置信息的功能。
"""

import os
import yaml
from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    """
    加载配置文件
    
    Returns:
        dict: 配置信息字典
    """
    config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_file = os.path.join(config_dir, "config.yaml")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"Warning: Config file {config_file} not found. Using default values.")
        config = {
            "defaults": {
                "city": "西安",
                "lang": "zh_cn"
            },
            "update_link": {}
        }
    except yaml.YAMLError as e:
        print(f"Warning: Error parsing {config_file}: {e}. Using default values.")
        config = {
            "defaults": {
                "city": "西安",
                "lang": "zh_cn"
            },
            "update_link": {}
        }
    
    return config


def get_default_city() -> str:
    """
    获取默认城市
    
    Returns:
        str: 默认城市名称
    """
    config = load_config()
    return config.get("defaults", {}).get("city", "西安")


def get_default_lang() -> str:
    """
    获取默认语言
    
    Returns:
        str: 默认语言代码
    """
    config = load_config()
    return config.get("defaults", {}).get("lang", "zh_cn")


def get_update_links() -> Dict[str, str]:
    """
    获取城市地铁数据更新链接
    
    Returns:
        dict: 城市名称到更新链接的映射
    """
    config = load_config()
    return config.get("update_link", {})


def get_update_link(city: str) -> str:
    """
    获取指定城市的地铁数据更新链接
    
    Args:
        city: 城市名称
        
    Returns:
        str: 更新链接，如果城市不存在则返回西安的链接
    """
    links = get_update_links()
    return links.get(city, links.get("西安", ""))

"""
国际化(i18n)模块

提供多语言支持功能，加载和管理本地化文本资源。
"""

import os
import yaml
from typing import Dict, Any

__name__ = "i18n"
__version__ = "0.1.0"
__author__ = "imoscarz"
__description__ = "Internationalization support for the Xi'an Metro Route Planner application."


class I18n:
    """国际化文本管理类"""

    def __init__(self, language: str = 'zh_cn'):
        """
        初始化国际化管理器

        Args:
            language: 语言代码，默认为 'zh_cn'
        """
        self._language = language
        self._texts: Dict[str, Any] = {}
        self._load_language(language)

    def _load_language(self, language: str):
        """
        加载指定语言的文本资源

        Args:
            language: 语言代码
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        yaml_file = os.path.join(current_dir, f"{language}.yaml")

        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                self._texts = yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(
                f"Warning: Language file {yaml_file} not found. Using empty strings.")
            self._texts = {}
        except yaml.YAMLError as e:
            print(
                f"Warning: Error parsing {yaml_file}: {e}. Using empty strings.")
            self._texts = {}

    def get(self, key: str, default: str = "", **kwargs) -> str:
        """
        获取文本资源

        Args:
            key: 文本键，支持点号分隔的嵌套路径，如 'ui.title_label'
            default: 默认值，当键不存在时返回
            **kwargs: 格式化参数，用于文本中的占位符替换

        Returns:
            本地化的文本字符串
        """
        keys = key.split('.')
        value = self._texts

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        if value is None:
            return default

        # 如果value是字符串，进行格式化
        if isinstance(value, str) and kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, ValueError):
                return value

        return str(value) if not isinstance(value, dict) else default

    def __call__(self, key: str, default: str = "", **kwargs) -> str:
        """
        获取文本资源的快捷方式

        Args:
            key: 文本键
            default: 默认值
            **kwargs: 格式化参数

        Returns:
            本地化的文本字符串
        """
        return self.get(key, default, **kwargs)


# 创建全局i18n实例
_i18n_instance = I18n()


def get_text(key: str, default: str = "", **kwargs) -> str:
    """
    获取文本资源的全局函数

    Args:
        key: 文本键
        default: 默认值
        **kwargs: 格式化参数

    Returns:
        本地化的文本字符串
    """
    return _i18n_instance.get(key, default, **kwargs)


# 导出常用别名
t = get_text
_ = get_text

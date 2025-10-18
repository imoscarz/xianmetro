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
__description__ = "国际化支持模块，为西安地铁路线规划器应用程序提供多语言功能。"


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
    
    def get_nested(self, key: str, default=None):
        """
        获取嵌套的数据结构（如列表、字典）
        
        与 get() 方法不同，此方法返回原始的数据结构（dict、list等），
        而不会将其转换为字符串或进行格式化处理。
        
        Args:
            key: 文本键，支持点号分隔的嵌套路径
            default: 默认值，当键不存在时返回
            
        Returns:
            原始的数据结构（可能是dict、list等），未进行任何转换
        """
        keys = key.split('.')
        value = self._texts

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

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

def load_language(language: str):
    """
    加载指定语言的文本资源

    Args:
        language: 语言代码
    """
    _i18n_instance._load_language(language)

def get_language_list():
    """
    获取可用语言列表（返回locale和文件名的映射）

    Returns:
        dict: 语言locale到文件名的映射，例如 {"中文(简体)": "zh_cn", "English(US)": "en_us"}
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    languages = {}
    for file in os.listdir(current_dir):
        if file.endswith('.yaml'):
            lang_code = file[:-5]  # 去掉 .yaml 后缀
            yaml_file = os.path.join(current_dir, file)
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    locale = data.get('locale', lang_code)
                    languages[locale] = lang_code
            except Exception as e:
                print(f"Warning: Error reading locale from {yaml_file}: {e}")
                languages[lang_code] = lang_code
    return languages

# 导出常用别名
t = get_text
_ = get_text

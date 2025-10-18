"""
UI辅助工具模块

提供UI相关的工具函数，包括消息对话框、路线格式化等功能。
"""

from qfluentwidgets import MessageBox
from xianmetro.i18n import get_text, _i18n_instance
from xianmetro.utils.load_config import get_default_city


def show_message(window, msg: str):
    """
    显示消息对话框

    Args:
        window: 父窗口对象
        msg: 要显示的消息内容
    """
    dlg = MessageBox(
        title=get_text("messages.dialog_title", "提示"),
        content=msg,
        parent=window
    )
    dlg.exec_()


def _build_card_items_from_format(format_template, values, get_line_color_func):
    """
    根据格式模板构建卡片项列表
    
    Args:
        format_template: 格式模板列表，每个元素包含 type 和可选的 key
        values: 值字典，包含 station, line, next_line 等
        get_line_color_func: 获取线路颜色的函数
    
    Returns:
        list: 卡片项列表，每个元素是一个包含 text, text_color, background_color 的字典
    """
    card_items = []
    
    for item in format_template:
        item_type = item.get('type')
        
        if item_type == 'text':
            # 普通文本
            key = item.get('key', '')
            text = get_text(f"route.{key}", "")
            card_items.append({
                "text": text,
                "text_color": "#000000",
                "background_color": "#FFFFFF"
            })
        elif item_type == 'station':
            # 站点
            station = values.get('station', '')
            line = values.get('line', '')
            line_color = get_line_color_func(line)
            card_items.append({
                "text": station,
                "text_color": "#FFFFFF",
                "background_color": line_color
            })
        elif item_type == 'line':
            # 线路
            line = values.get('line', '')
            line_color = get_line_color_func(line)
            card_items.append({
                "text": line,
                "text_color": "#FFFFFF",
                "background_color": line_color
            })
        elif item_type == 'next_line':
            # 下一条线路
            next_line = values.get('next_line', '')
            next_line_color = get_line_color_func(next_line)
            card_items.append({
                "text": next_line,
                "text_color": "#FFFFFF",
                "background_color": next_line_color
            })
    
    return card_items


def format_route_output_verbose(route, stations, get_line_color_func):
    """
    格式化路线输出：每行为一个站点，包含上车、换乘和下车提示
    返回item字典列表和icons列表，每个卡片包含多个不同颜色的文本片段

    Args:
        route: 路线段列表，每段包含线路名称和站点ID列表
        stations: 站点字典，用于ID到站点名称的转换
        get_line_color_func: 获取线路颜色的函数

    Returns:
        tuple: (items_list, icons_list)
            - items_list: 每个元素是一个字典列表，代表一个卡片中的多个文本片段
            - icons_list: 每个元素是一个图标，对应每个卡片
    """
    from xianmetro.core import id_to_name
    from xianmetro.assets import UP, DOWN, TRANSFER, INFO

    items_list = []
    icons_list = []
    
    # 获取格式模板，使用公共接口
    board_format = _i18n_instance.get_nested('route.board_format', [])
    transfer_format = _i18n_instance.get_nested('route.transfer_format', [])
    alight_format = _i18n_instance.get_nested('route.alight_format', [])
    
    # 如果没有格式模板，使用默认格式（中文格式）
    if not board_format:
        board_format = [
            {'type': 'text', 'key': 'board_at'},
            {'type': 'station'},
            {'type': 'text', 'key': 'take_line'},
            {'type': 'line'}
        ]
    if not transfer_format:
        transfer_format = [
            {'type': 'text', 'key': 'transfer_at'},
            {'type': 'station'},
            {'type': 'text', 'key': 'from_line'},
            {'type': 'line'},
            {'type': 'text', 'key': 'transfer_to'},
            {'type': 'next_line'}
        ]
    if not alight_format:
        alight_format = [
            {'type': 'text', 'key': 'alight_at'},
            {'type': 'station'},
            {'type': 'text', 'key': 'alight'}
        ]

    for i, segment in enumerate(route):
        line = segment["line"]
        station_ids = segment["stations"]
        n = len(station_ids)

        # 上车提示卡片
        if i == 0 and n > 0:
            start_station = id_to_name(stations, station_ids[0])
            values = {'station': start_station, 'line': line}
            card_items = _build_card_items_from_format(board_format, values, get_line_color_func)
            items_list.append(card_items)
            icons_list.append(UP)

        # 中间站点卡片
        for j, sid in enumerate(station_ids):
            station_name = id_to_name(stations, sid)
            if i == 0 and j == 0:  # 跳过起点站（已在乘车提示中显示）
                continue

            # 普通站点卡片
            line_color = get_line_color_func(line)
            card_items = [
                {
                    "text": station_name,
                    "text_color": "#FFFFFF",
                    "background_color": line_color
                }
            ]
            items_list.append(card_items)
            icons_list.append(INFO)

            # 换乘提示卡片
            if j == n - 1 and i < len(route) - 1:
                next_line = route[i + 1]["line"]
                values = {'station': station_name, 'line': line, 'next_line': next_line}
                card_items = _build_card_items_from_format(transfer_format, values, get_line_color_func)
                items_list.append(card_items)
                icons_list.append(TRANSFER)

        # 终点提示卡片
        if i == len(route) - 1 and n > 0:
            end_station = id_to_name(stations, station_ids[-1])
            values = {'station': end_station, 'line': line}
            card_items = _build_card_items_from_format(alight_format, values, get_line_color_func)
            items_list.append(card_items)
            icons_list.append(DOWN)

    return items_list, icons_list


def get_price_text(distance: float, city: str, calc_price_func) -> str:
    """
    获取票价信息文本

    Args:
        distance: 距离（公里）
        city: 城市名称
        calc_price_func: 计算票价的函数

    Returns:
        str: 格式化的票价信息文本
    """
    if city != get_default_city():
        return get_text("info.price_not_supported", "暂不支持当前城市的票价计算")

    price = calc_price_func(int(distance + 0.5))
    price_card = calc_price_func(int(distance + 0.5), discount=1)
    price_student = calc_price_func(int(distance + 0.5), discount=2)

    return get_text(
        "info.price_format",
        "票价: 普通{normal}元 | 地铁卡{card:.1f}元 | 学生卡{student:.1f}元 | 老年卡/爱心卡/拥军卡免费",
        normal=price,
        card=price_card,
        student=price_student
    )

"""
UI辅助工具模块

提供UI相关的工具函数，包括消息对话框、路线格式化等功能。
"""

from qfluentwidgets import MessageBox
from xianmetro.i18n import get_text
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

    for i, segment in enumerate(route):
        line = segment["line"]
        station_ids = segment["stations"]
        n = len(station_ids)
        line_color = get_line_color_func(line)

        # 上车提示卡片
        if i == 0 and n > 0:
            start_station = id_to_name(stations, station_ids[0])
            card_items = [
                {
                    "text": get_text("route.board_at", "在"),
                    "text_color": "#000000",
                    "background_color": "#FFFFFF"
                },
                {
                    "text": start_station,
                    "text_color": "#FFFFFF",
                    "background_color": line_color
                },
                {
                    "text": get_text("route.take_line", "乘坐"),
                    "text_color": "#000000",
                    "background_color": "#FFFFFF"
                },
                {
                    "text": line,
                    "text_color": "#FFFFFF",
                    "background_color": line_color
                }
            ]
            items_list.append(card_items)
            icons_list.append(UP)

        # 中间站点卡片
        for j, sid in enumerate(station_ids):
            station_name = id_to_name(stations, sid)
            if i == 0 and j == 0:  # 跳过起点站（已在乘车提示中显示）
                continue

            # 普通站点卡片
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
                next_line_color = get_line_color_func(next_line)
                card_items = [
                    {
                        "text": get_text("route.transfer_at", "在"),
                        "text_color": "#000000",
                        "background_color": "#FFFFFF"
                    },
                    {
                        "text": station_name,
                        "text_color": "#FFFFFF",
                        "background_color": line_color
                    },
                    {
                        "text": get_text("route.from_line", "由"),
                        "text_color": "#000000",
                        "background_color": "#FFFFFF"
                    },
                    {
                        "text": line,
                        "text_color": "#FFFFFF",
                        "background_color": line_color
                    },
                    {
                        "text": get_text("route.transfer_to", "换乘"),
                        "text_color": "#000000",
                        "background_color": "#FFFFFF"
                    },
                    {
                        "text": next_line,
                        "text_color": "#FFFFFF",
                        "background_color": next_line_color
                    }
                ]
                items_list.append(card_items)
                icons_list.append(TRANSFER)

        # 终点提示卡片
        if i == len(route) - 1 and n > 0:
            end_station = id_to_name(stations, station_ids[-1])
            card_items = [
                {
                    "text": get_text("route.alight_at", "在"),
                    "text_color": "#000000",
                    "background_color": "#FFFFFF"
                },
                {
                    "text": end_station,
                    "text_color": "#FFFFFF",
                    "background_color": line_color
                },
                {
                    "text": get_text("route.alight", "下车"),
                    "text_color": "#000000",
                    "background_color": "#FFFFFF"
                }
            ]
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

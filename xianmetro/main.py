import sys
from PyQt5.QtWidgets import QApplication
from xianmetro.ui.main_window import MetroPlannerUI
from xianmetro.core import plan_route, parse_stations, id_to_name, name_to_id
from xianmetro.fetch import get_metro_info, parse_metro_info, save_to_file, get_line_color
from xianmetro.utils import calc_price
from xianmetro.assets import *

from qfluentwidgets import MessageBox, InfoBarIcon


def format_route_output_verbose(route, stations):
    """
    格式化路线输出：每行为一个站点，包含上车、换乘和下车提示
    返回item字典列表和icons列表，每个卡片包含多个不同颜色的文本片段
    """
    items_list = []  # 每个元素是一个字典列表，代表一个卡片中的多个文本片段
    icons_list = []  # 每个元素是一个图标，对应每个卡片

    for i, segment in enumerate(route):
        line = segment["line"]
        station_ids = segment["stations"]
        n = len(station_ids)
        line_color = get_line_color(line)

        # 上车提示卡片
        if i == 0 and n > 0:
            start_station = id_to_name(stations, station_ids[0])
            card_items = [
                {"text": "在", "text_color": "#000000", "background_color": "#FFFFFF"},
                {"text": start_station, "text_color": "#FFFFFF", "background_color": line_color},
                {"text": "乘坐", "text_color": "#000000", "background_color": "#FFFFFF"},
                {"text": line, "text_color": "#FFFFFF", "background_color": line_color}
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
                {"text": station_name, "text_color": "#FFFFFF", "background_color": line_color}
            ]
            items_list.append(card_items)
            icons_list.append(INFO)

            # 换乘提示卡片
            if j == n - 1 and i < len(route) - 1:
                next_line = route[i + 1]["line"]
                next_line_color = get_line_color(next_line)
                card_items = [
                    {"text": "在", "text_color": "#000000", "background_color": "#FFFFFF"},
                    {"text": station_name, "text_color": "#FFFFFF", "background_color": line_color},
                    {"text": "由", "text_color": "#000000", "background_color": "#FFFFFF"},
                    {"text": line, "text_color": "#FFFFFF", "background_color": line_color},
                    {"text": "换乘", "text_color": "#000000", "background_color": "#FFFFFF"},
                    {"text": next_line, "text_color": "#FFFFFF", "background_color": next_line_color}
                ]
                items_list.append(card_items)
                icons_list.append(TRANSFER)

        # 终点提示卡片
        if i == len(route) - 1 and n > 0:
            end_station = id_to_name(stations, station_ids[-1])
            card_items = [
                {"text": "在", "text_color": "#000000", "background_color": "#FFFFFF"},
                {"text": end_station, "text_color": "#FFFFFF", "background_color": line_color},
                {"text": "下车", "text_color": "#000000", "background_color": "#FFFFFF"}
            ]
            items_list.append(card_items)
            icons_list.append(DOWN)

    return items_list, icons_list

def show_message(window, msg):
    # 使用 qfluentwidgets 的 MessageDialog
    dlg = MessageBox(
        title="提示",
        content=msg,
        parent=window
    )
    dlg.exec_()


def get_price_text(distance, city):
    price = calc_price(int(distance + 0.5))
    price_card = calc_price(int(distance + 0.5), discount=1)
    price_student = calc_price(int(distance + 0.5), discount=2)
    price_free = calc_price(int(distance + 0.5), discount=3)
    # 票价信息
    return (
        f"票价: 普通{price}元 | 地铁卡{price_card:.1f}元 | 学生卡{price_student:.1f}元 | 老年卡/爱心卡/拥军卡免费"
        if city == "西安" else "暂不支持当前城市的票价计算"
    )


def main():
    save_to_file(parse_metro_info(get_metro_info("西安")))
    app = QApplication(sys.argv)
    window = MetroPlannerUI()
    stations = parse_stations()
    # 设置默认城市
    current_city = window.get_city() or "西安"

    def load_city_data(city):
        metro_json = get_metro_info(city)
        metro_info = parse_metro_info(metro_json)
        save_to_file(metro_info)
        return parse_stations()

    stations = load_city_data(current_city)

    def refresh_station_inputs(city):
        # 更新下拉选项
        from xianmetro.fetch import get_id_list, get_station_list
        station_names = get_station_list()
        station_ids = []#get_id_list()
        start_options = list(dict.fromkeys(station_names + station_ids))
        window.start_input.clear()
        window.end_input.clear()
        window.start_input.addItems(start_options)
        window.end_input.addItems(start_options)

    def update_routes():
        """
        更新并显示三种策略的路线规划结果
        1. 最少换乘
        2. 最少站点
        3. 最短距离
        允许输入站名或ID，优先ID
        结果显示每个站点一行，包含上车、换乘和下车提示
        结果显示总站点数、总距离、换乘次数和票价信息
        处理无效输入和相同起终点的情况
        """
        start_input = window.get_start_station().strip()
        end_input = window.get_end_station().strip()
        if start_input == "imoscarz":
            show_message(window,
                         "You Found The Easter egg\n欢迎使用西安地铁线路规划器！\n"
                         "作者: imoscarz\nGitHub:https://github.com/imoscarz/xianmetro")
            return
        if end_input == "imoscarz":
            show_message(window, "You Found The Easter egg\n缪尔塞斯真的很可爱！！！！！")
            return
        # 允许输入站名或ID，优先ID
        start_id = stations.get(start_input) and start_input
        end_id = stations.get(end_input) and end_input

        if not start_id:
            start_id = name_to_id(stations, start_input)
        if not end_id:
            end_id = name_to_id(stations, end_input)

        if not start_id or not end_id:
            show_message(window, "请输入有效的起点和终点（支持站名或ID）！")
            for idx in range(3):
                window.store_route_result(idx, message="请输入有效的起点和终点")
            window.on_route_selector_changed()
            return
        if start_id == end_id:
            show_message(window, "你搁这原地TP呢？起点和终点不能相同！")
            for idx in range(3):
                window.store_route_result(idx, message="起点和终点不能相同")
            window.on_route_selector_changed()
            return
        # 路径规划
        results = []
        for strategy in [1, 2, 3]:
            result = plan_route(start_id, end_id, strategy=strategy)
            results.append(result)

        # Build line colors dictionary
        line_colors = {}
        for result in results:
            if result:
                for segment in result["route"]:
                    line_name = segment["line"]
                    if line_name not in line_colors:
                        line_colors[line_name] = get_line_color(line_name)

        # 输出各方案
        for idx, result in enumerate(results):
            if result:
                item_list, icon_list = format_route_output_verbose(result["route"], stations)
                info_text = (
                    f"总站点数: {result['total_stops']}\n"
                    f"总距离: {result['total_distance']} km\n"
                    f"换乘次数: {result['transfers']}\n"
                    f"{get_price_text(result['total_distance'], window.get_city())}"
                )
                window.store_route_result(
                    idx, 
                    item_list=item_list,
                    icon_list=icon_list,
                    info_text=info_text,
                    route_data=result["route"],
                    stations_dict=stations,
                    line_colors=line_colors
                )
            else:
                window.store_route_result(idx, message="未找到方案")
        
        # Trigger display update for current selected tab
        window.on_route_selector_changed()

    def on_plan_clicked():
        """
        规划路线按钮点击事件
        """
        update_routes()

    def on_refresh_clicked():
        nonlocal stations
        city = window.get_city() or "西安"
        try:
            stations = load_city_data(city)
            refresh_station_inputs(city)
            show_message(window, f"{city}地铁数据已刷新成功！")
        except Exception as e:
            show_message(window, f"{city}地铁数据刷新失败: {e}")

    def on_city_changed():
        nonlocal stations
        city = window.get_city() or "西安"
        stations = load_city_data(city)
        refresh_station_inputs(city)
        show_message(window, f"已切换至{city}，地铁数据已更新！")

    window.plan_btn.clicked.connect(on_plan_clicked)
    window.refresh_btn.clicked.connect(on_refresh_clicked)
    window.city_input.currentTextChanged.connect(on_city_changed)
    window.route_selector.currentItemChanged.connect(window.on_route_selector_changed)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

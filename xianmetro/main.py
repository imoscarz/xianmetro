"""
西安地铁路线规划器 - 主程序

本程序提供地铁路线规划功能，支持多种策略（最少换乘、最少站点、最短距离）。
用户可以选择不同城市，输入起点和终点站，获得最优路线规划方案。
"""

import sys
from PyQt5.QtWidgets import QApplication

from xianmetro.ui.main_window import MetroPlannerUI
from xianmetro.core import plan_route, parse_stations, name_to_id
from xianmetro.fetch import (
    get_metro_info,
    parse_metro_info,
    save_to_file,
    get_line_color
)
from xianmetro.utils import (
    calc_price,
    show_message,
    format_route_output_verbose,
    get_price_text,
    get_default_city,
    get_default_lang
)
from xianmetro.i18n import get_text, load_language


def main():
    """
    主函数：初始化应用程序并设置事件处理
    """
    # 获取默认城市
    default_city = get_default_city()
    
    # 初始化默认城市数据
    save_to_file(parse_metro_info(get_metro_info(default_city)))
    
    # 创建应用程序和主窗口
    app = QApplication(sys.argv)
    window = MetroPlannerUI()
    stations = parse_stations()
    
    # 设置默认城市
    current_city = window.get_city() or default_city

    def load_city_data(city):
        """
        加载指定城市的地铁数据
        
        Args:
            city: 城市名称
            
        Returns:
            dict: 站点字典
        """
        metro_json = get_metro_info(city)
        metro_info = parse_metro_info(metro_json)
        save_to_file(metro_info)
        return parse_stations()

    # 加载当前城市数据
    stations = load_city_data(current_city)

    def refresh_station_inputs(city):
        """
        刷新站点输入下拉框的选项
        
        Args:
            city: 城市名称
        """
        from xianmetro.fetch import get_station_list
        station_names = get_station_list()
        station_ids = []
        start_options = list(dict.fromkeys(station_names + station_ids))
        window.start_input.clear()
        window.end_input.clear()
        window.start_input.addItems(start_options)
        window.end_input.addItems(start_options)

    def update_routes():
        """
        更新并显示三种策略的路线规划结果：
        1. 最少换乘
        2. 最少站点
        3. 最短距离
        
        支持输入站名或ID，优先ID。
        结果显示每个站点一行，包含上车、换乘和下车提示。
        结果显示总站点数、总距离、换乘次数和票价信息。
        处理无效输入和相同起终点的情况。
        """
        start_input = window.get_start_station().strip()
        end_input = window.get_end_station().strip()
        
        # 彩蛋处理
        if start_input == "imoscarz":
            show_message(window, get_text("messages.easter_egg_found"))
            return
        if end_input == "imoscarz":
            show_message(window, get_text("messages.easter_egg_secret"))
            return
        
        # 允许输入站名或ID，优先ID
        start_id = stations.get(start_input) and start_input
        end_id = stations.get(end_input) and end_input

        if not start_id:
            start_id = name_to_id(stations, start_input)
        if not end_id:
            end_id = name_to_id(stations, end_input)

        # 验证输入
        if not start_id or not end_id:
            show_message(window, get_text("messages.invalid_input"))
            for idx in range(3):
                window.store_route_result(
                    idx,
                    message=get_text("messages.invalid_input")
                )
            window.on_route_selector_changed()
            return
            
        if start_id == end_id:
            show_message(window, get_text("messages.same_station"))
            for idx in range(3):
                window.store_route_result(
                    idx,
                    message=get_text("messages.same_station")
                )
            window.on_route_selector_changed()
            return
            
        # 路径规划 - 三种策略
        results = []
        for strategy in [1, 2, 3]:
            result = plan_route(start_id, end_id, strategy=strategy)
            results.append(result)

        # 构建线路颜色字典
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
                item_list, icon_list = format_route_output_verbose(
                    result["route"],
                    stations,
                    get_line_color
                )
                info_text = (
                    f"{get_text('info.total_stops', '总站点数: {stops}').format(stops=result['total_stops'])}\n"
                    f"{get_text('info.total_distance', '总距离: {distance} km').format(distance=result['total_distance'])}\n"
                    f"{get_text('info.transfer_times', '换乘次数: {times}').format(times=result['transfers'])}\n"
                    f"{get_price_text(result['total_distance'], window.get_city(), calc_price)}"
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
                window.store_route_result(
                    idx,
                    message=get_text("messages.no_route_found")
                )
        
        # 触发显示更新
        window.on_route_selector_changed()

    def on_plan_clicked():
        """
        规划路线按钮点击事件处理函数
        """
        update_routes()

    def on_refresh_clicked():
        """
        刷新按钮点击事件处理函数
        """
        nonlocal stations
        city = window.get_city() or default_city
        try:
            stations = load_city_data(city)
            refresh_station_inputs(city)
            show_message(
                window,
                get_text("messages.data_refreshed", city=city)
            )
        except Exception as e:
            show_message(
                window,
                get_text("messages.data_refresh_failed", city=city, error=str(e))
            )

    def on_city_changed():
        """
        城市切换事件处理函数
        """
        nonlocal stations
        city = window.get_city() or default_city
        stations = load_city_data(city)
        refresh_station_inputs(city)
        show_message(window, get_text("messages.city_switched", city=city))

    def on_lang_changed():
        """
        语言切换事件处理函数
        """
        lang = window.get_lang()
        load_language(lang)
        show_message(window, get_text("messages.language_switched", language=lang))
        window.reload_ui()

    # 连接信号和槽
    window.plan_btn.clicked.connect(on_plan_clicked)
    window.refresh_btn.clicked.connect(on_refresh_clicked)
    window.city_input.currentTextChanged.connect(on_city_changed)
    window.lang_input.currentTextChanged.connect(on_lang_changed)
    window.route_selector.currentItemChanged.connect(window.on_route_selector_changed)

    # 显示窗口并启动应用程序
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

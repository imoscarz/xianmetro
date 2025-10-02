import sys
from PyQt5.QtWidgets import QApplication
from xianmetro.ui.main_window import MetroPlannerUI
from xianmetro.core import plan_route, parse_stations, id_to_name, name_to_id
from xianmetro.fetch import get_metro_info, parse_metro_info, save_to_file
from xianmetro.utils.calc_price import calc_price

from qfluentwidgets import MessageBox , InfoBarIcon

def format_route_output_verbose(route, stations):
    """
    格式化路线输出：每行为一个站点，包含上车、换乘和下车提示
    """
    output = []
    icon_list = []
    for i, segment in enumerate(route):
        line = segment["line"]
        station_ids = segment["stations"]
        n = len(station_ids)
        # 上车提示
        if i == 0 and n > 0:
            start_station = id_to_name(stations, station_ids[0])
            output.append(f"在【{start_station}】乘坐【{line}】")
            icon_list.append("xianmetro/assets/icon_start.png")
        for j, sid in enumerate(station_ids):
            station_name = id_to_name(stations, sid)
            if i == 0 and j == 0:
                continue
            output.append(f"{station_name}")
            # 普通站点
            icon_list.append("xianmetro/assets/icon_station.png")
            # 换乘提示
            if j == n - 1 and i < len(route) - 1:
                next_line = route[i + 1]["line"]
                output.append(f"在【{station_name}】由【{line}】换乘【{next_line}】")
                icon_list.append("xianmetro/assets/icon_transfer.png")
        # 终点提示
        if i == len(route) - 1 and n > 0:
            end_station = id_to_name(stations, station_ids[-1])
            output.append(f"在【{end_station}】下车")
            icon_list.append("xianmetro/assets/icon_end.png")
    return output, icon_list

def show_message(window, msg):
    # 使用 qfluentwidgets 的 MessageDialog
    dlg = MessageBox (
        title="提示",
        content=msg,
        parent=window
    )
    dlg.exec_()

def get_price_text(distance):
    price = calc_price(int(distance + 0.5))
    price_card = calc_price(int(distance + 0.5), discount=1)
    price_student = calc_price(int(distance + 0.5), discount=2)
    price_free = calc_price(int(distance + 0.5), discount=3)
    # 票价信息
    return (f"票价: 普通{price}元 | 地铁卡{price_card:.1f}元 | 学生卡{price_student:.1f}元 | 老年卡/爱心卡/拥军卡免费")

def main():
    app = QApplication(sys.argv)
    window = MetroPlannerUI()
    stations = parse_stations()

    def update_routes():
        """
        路径规划并输出到界面（新版：竖直滚动+按钮item支持icon）
        """
        start_input = window.get_start_station().strip()
        end_input = window.get_end_station().strip()
        if start_input == "imoscarz":
            show_message(window, "You Found The Easter egg\n欢迎使用西安地铁线路规划器！\n作者: imoscarz\nGitHub:https://github.com/imoscarz/xianmetro")
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
                window.clear_result_area(idx)
                window.result_info_labels[idx].setText("")
            return
        if start_id == end_id:
            show_message(window, "你搁这原地TP呢？起点和终点不能相同！")
            for idx in range(3):
                window.clear_result_area(idx)
                window.result_info_labels[idx].setText("")
            return
        # 路径规划
        results = []
        for strategy in [1, 2, 3]:
            result = plan_route(start_id, end_id, strategy=strategy)
            results.append(result)

        # 输出各方案
        for idx, result in enumerate(results):
            if result:
                route_lines, icon_list = format_route_output_verbose(result["route"], stations)
                info_text = (
                    f"总站点数: {result['total_stops']}\n"
                    f"总距离: {result['total_distance']} km\n"
                    f"换乘次数: {result['transfers']}\n"
                    f"{get_price_text(result['total_distance'])}"
                )
                window.clear_result_area(idx)
                for item, icon in zip(route_lines, icon_list):
                    window.add_result_item(idx, item, icon)
                window.result_info_labels[idx].setText(info_text)
            else:
                window.clear_result_area(idx)
                window.add_result_item(idx, "未找到方案")
                window.result_info_labels[idx].setText("")

    def on_plan_clicked():
        update_routes()

    def on_refresh_clicked():
        try:
            metro_json = get_metro_info()
            metro_info = parse_metro_info(metro_json)
            save_to_file(metro_info)
            nonlocal stations
            stations = parse_stations()
            show_message(window, "地铁数据已刷新成功！")
            # update_routes()
        except Exception as e:
            show_message(window, f"地铁数据刷新失败: {e}")

    window.plan_btn.clicked.connect(on_plan_clicked)
    window.refresh_btn.clicked.connect(on_refresh_clicked)

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
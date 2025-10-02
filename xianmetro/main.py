import sys
from PyQt5.QtWidgets import QApplication
from xianmetro.ui.main_window import MetroPlannerUI
from xianmetro.core import plan_route, parse_stations, id_to_name, name_to_id

def format_route_output_verbose(route, stations):
    """
    格式化路线输出，每行为一个站点，包含上车、换乘和下车提示
    """
    output = []
    for i, segment in enumerate(route):
        line = segment["line"]
        station_ids = segment["stations"]
        n = len(station_ids)
        # 上车提示
        if i == 0 and n > 0:
            start_station = id_to_name(stations, station_ids[0])
            output.append(f"在【{start_station}】乘坐【{line}】")
        for j, sid in enumerate(station_ids):
            station_name = id_to_name(stations, sid)
            if i == 0 and j == 0:
                # 已有上车提示，不重复
                continue
            output.append(f"{station_name}")
            # 换乘提示
            # 如果不是最后一段且到达该段终点，则提示换乘
            if j == n - 1 and i < len(route) - 1:
                next_line = route[i + 1]["line"]
                output.append(f"在【{station_name}】由【{line}】换乘【{next_line}】")
        # 终点提示
        if i == len(route) - 1 and n > 0:
            end_station = id_to_name(stations, station_ids[-1])
            output.append(f"在【{end_station}】下车")
    return output

def main():
    app = QApplication(sys.argv)
    window = MetroPlannerUI()

    stations = parse_stations()

    def on_plan_clicked():
        start_input = window.get_start_station().strip()
        end_input = window.get_end_station().strip()

        # 允许输入站名或ID，优先ID
        start_id = stations.get(start_input) and start_input
        end_id = stations.get(end_input) and end_input

        if not start_id:
            start_id = name_to_id(stations, start_input)
        if not end_id:
            end_id = name_to_id(stations, end_input)

        if not start_id or not end_id:
            window.set_least_transfer_result(["无效的起点或终点"])
            window.set_least_stops_result(["无效的起点或终点"])
            window.set_shortest_distance_result(["无效的起点或终点"])
            return

        # 最少换乘
        result1 = plan_route(start_id, end_id, strategy=1)
        least_transfer_lines = format_route_output_verbose(result1["route"], stations) if result1 else ["未找到方案"]
        least_transfer_lines.append(f"总站点数: {result1['total_stops']}, 总距离: {result1['total_distance']} km, 换乘次数: {result1['transfers']}" if result1 else "")

        # 最少站点
        result2 = plan_route(start_id, end_id, strategy=2)
        least_stops_lines = format_route_output_verbose(result2["route"], stations) if result2 else ["未找到方案"]
        least_stops_lines.append(f"总站点数: {result2['total_stops']}, 总距离: {result2['total_distance']} km, 换乘次数: {result2['transfers']}" if result2 else "")

        # 最短距离
        result3 = plan_route(start_id, end_id, strategy=3)
        shortest_distance_lines = format_route_output_verbose(result3["route"], stations) if result3 else ["未找到方案"]
        shortest_distance_lines.append(f"总站点数: {result3['total_stops']}, 总距离: {result3['total_distance']} km, 换乘次数: {result3['transfers']}" if result3 else "")

        window.set_least_transfer_result(least_transfer_lines)
        window.set_least_stops_result(least_stops_lines)
        window.set_shortest_distance_result(shortest_distance_lines)

    window.plan_btn.clicked.connect(on_plan_clicked)

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
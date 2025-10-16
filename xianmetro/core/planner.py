"""
路径规划模块

提供地铁路线规划功能，支持三种策略：最少换乘、最少站点、最短距离。
使用基于优先队列的搜索算法来找到最优路径。
"""

from collections import defaultdict
from heapq import heappush, heappop

from xianmetro.core import parse_stations, id_to_name, name_to_id
from xianmetro.utils import haversine


def plan_route(start_station, end_station, strategy):
    """
    规划地铁路线

    根据指定策略计算从起点到终点的最优路线。算法使用优先队列搜索，
    根据不同策略优化不同的目标（换乘次数、站点数或距离）。

    Args:
        start_station: 起始站ID
        end_station: 目标站ID
        strategy: 选择策略
            1 - 最少换乘优先
            2 - 最少站点优先
            3 - 最短距离优先

    Returns:
        dict: 包含路线信息的字典，格式为：
        {
            "route": [
                {"line": "1号线", "stations": ["ID1", "ID2", ...]},
                {"line": "2号线", "stations": ["ID3", "ID4", ...]}
            ],
            "total_stops": 总站点数,
            "total_distance": 总距离（公里）,
            "transfers": 换乘次数
        }
        如果未找到路径则返回None
    """
    stations = parse_stations()

    # 构建邻接表，站点ID为节点，边为相邻站
    adj = defaultdict(list)
    line_map = defaultdict(list)  # 站点ID到其所有线路的映射

    for station_id, station_obj in stations.items():
        for st_line in station_obj.line:
            line_map[station_id].append(st_line.line_name)
            if st_line.prev_station_id:
                adj[station_id].append(
                    (st_line.prev_station_id, st_line.line_name)
                )
            if st_line.next_station_id:
                adj[station_id].append(
                    (st_line.next_station_id, st_line.line_name)
                )

    # 状态：(权重, 当前站ID, 当前线路, 路径列表, 已走距离, 换乘次数, 经过站点数)
    queue = []
    visited = dict()  # (station_id, line_name): 权重，防止回头/环线死循环

    # 初始化起点入队 - 为每条可能的线路创建初始状态
    for line_name in line_map[start_station]:
        heappush(
            queue,
            (0, start_station, line_name, [(start_station, line_name)],
             0.0, 0, 1)
        )

    while queue:
        # 根据策略排序
        if strategy == 1:
            # 换乘优先：首先按换乘次数，其次按站点数
            queue.sort(key=lambda x: (x[5], x[6]))
        elif strategy == 2:
            # 站点数优先：首先按站点数，其次按换乘次数
            queue.sort(key=lambda x: (x[6], x[5]))
        elif strategy == 3:
            # 距离优先：首先按距离，其次按换乘次数
            queue.sort(key=lambda x: (x[4], x[5]))

        item = queue.pop(0)
        (_, curr_id, curr_line, path, curr_dist,
         curr_transfer, curr_stops) = item

        # 到达终点
        if curr_id == end_station:
            # 整理路线分段
            route = []
            temp = []
            last_line = path[0][1]
            for sid, lname in path:
                if lname != last_line:
                    route.append({"line": last_line, "stations": temp})
                    temp = [sid]
                    last_line = lname
                else:
                    temp.append(sid)
            if temp:
                route.append({"line": last_line, "stations": temp})

            transfers = max(0, len(route) - 1)  # 换乘次数为分段数减一

            return {
                "route": route,
                "total_stops": curr_stops,
                "total_distance": round(curr_dist, 5),
                "transfers": transfers
            }

        # 防止回头/死循环，记录最优权重
        state_key = (curr_id, curr_line)
        weight = (curr_transfer, curr_stops, curr_dist)
        if state_key in visited:
            # 如果已访问且当前权重不优则跳过
            if visited[state_key] <= weight:
                continue
        visited[state_key] = weight

        # 扩展邻居站点
        for neighbor_id, neighbor_line in adj[curr_id]:
            # 判断是否需要换乘
            next_transfer = curr_transfer
            if neighbor_line != curr_line:
                next_transfer += 1

            # 计算距离增量
            lat1, lon1 = stations[curr_id].coords
            lat2, lon2 = stations[neighbor_id].coords
            d = haversine(lat1, lon1, lat2, lon2)

            # 将新状态加入队列
            heappush(
                queue,
                (0, neighbor_id, neighbor_line,
                 path + [(neighbor_id, neighbor_line)],
                 curr_dist + d,
                 next_transfer,
                 curr_stops + 1)
            )

    return None  # 未找到路径


if __name__ == '__main__':
    stations = parse_stations()
    start = name_to_id(stations, "咸阳西站")
    end = name_to_id(stations, "雁鸣湖")

    print("最少换乘".center(50, "-"))
    result = plan_route(start, end, strategy=1)
    for segment in result["route"]:
        line = segment["line"]
        station_names = [id_to_name(stations, sid)
                         for sid in segment["stations"]]
        print(f"乘坐{line}：{' -> '.join(station_names)}")
    print(
        f"总站点数: {result['total_stops']}, "
        f"总距离: {result['total_distance']} km, "
        f"换乘次数: {result['transfers']}"
    )

    print("最少站点".center(50, "-"))
    result = plan_route(start, end, strategy=2)
    for segment in result["route"]:
        line = segment["line"]
        station_names = [id_to_name(stations, sid)
                         for sid in segment["stations"]]
        print(f"乘坐{line}：{' -> '.join(station_names)}")
    print(
        f"总站点数: {result['total_stops']}, "
        f"总距离: {result['total_distance']} km, "
        f"换乘次数: {result['transfers']}"
    )

    print("最短距离".center(50, "-"))
    result = plan_route(start, end, strategy=3)
    for segment in result["route"]:
        line = segment["line"]
        station_names = [id_to_name(stations, sid)
                         for sid in segment["stations"]]
        print(f"乘坐{line}：{' -> '.join(station_names)}")
    print(
        f"总站点数: {result['total_stops']}, "
        f"总距离: {result['total_distance']} km, "
        f"换乘次数: {result['transfers']}"
    )

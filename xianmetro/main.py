import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from xianmetro.ui import MetroPlannerUI
from xianmetro.core import parse_stations, plan_route, id_to_name, name_to_id


class MetroPlannerApp(MetroPlannerUI):
    """
    西安地铁路线规划应用程序主类
    """
    def __init__(self):
        super().__init__()
        self.stations = None
        self.load_stations()
        
        # 连接按钮点击事件
        self.plan_button.clicked.connect(self.on_plan_clicked)
    
    def load_stations(self):
        """加载站点数据"""
        try:
            self.stations = parse_stations()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载站点数据失败：{str(e)}")
    
    def validate_station(self, input_text):
        """
        验证并获取站点ID
        支持输入站名或站点ID
        :param input_text: 用户输入的文本
        :return: 站点ID，如果不存在返回None
        """
        if not input_text or not input_text.strip():
            return None
        
        input_text = input_text.strip()
        
        # 检查是否为站点ID（存在于stations字典中）
        if input_text in self.stations:
            return input_text
        
        # 尝试作为站名查找
        station_id = name_to_id(self.stations, input_text)
        return station_id
    
    def format_route_result(self, result):
        """
        格式化路线规划结果
        :param result: plan_route返回的结果字典
        :return: 格式化后的文本列表
        """
        if not result:
            return ["未找到路线"]
        
        lines = []
        
        # 显示每段路线
        for segment in result["route"]:
            line_name = segment["line"]
            station_ids = segment["stations"]
            station_names = [id_to_name(self.stations, sid) for sid in station_ids]
            route_text = f"{line_name}：{' -> '.join(station_names)}"
            lines.append(route_text)
        
        # 添加统计信息
        lines.append("")
        lines.append(f"总站点数: {result['total_stops']}")
        lines.append(f"总距离: {result['total_distance']:.2f} km")
        lines.append(f"换乘次数: {result['transfers']}")
        
        return lines
    
    def on_plan_clicked(self):
        """处理规划按钮点击事件"""
        # 清空之前的结果
        self.transfer_list.clear()
        self.stops_list.clear()
        self.distance_list.clear()
        
        # 获取并验证输入
        start_text = self.start_input.text()
        end_text = self.end_input.text()
        
        start_id = self.validate_station(start_text)
        end_id = self.validate_station(end_text)
        
        # 验证输入
        if not start_id:
            QMessageBox.warning(self, "输入错误", f"起点站名或站点ID不存在：{start_text}")
            return
        
        if not end_id:
            QMessageBox.warning(self, "输入错误", f"终点站名或站点ID不存在：{end_text}")
            return
        
        # 规划三种策略的路线
        try:
            # 策略1：最少换乘
            result1 = plan_route(start_id, end_id, strategy=1)
            if result1:
                for line in self.format_route_result(result1):
                    self.transfer_list.addItem(line)
            else:
                self.transfer_list.addItem("未找到路线")
            
            # 策略2：最少站点
            result2 = plan_route(start_id, end_id, strategy=2)
            if result2:
                for line in self.format_route_result(result2):
                    self.stops_list.addItem(line)
            else:
                self.stops_list.addItem("未找到路线")
            
            # 策略3：最短距离
            result3 = plan_route(start_id, end_id, strategy=3)
            if result3:
                for line in self.format_route_result(result3):
                    self.distance_list.addItem(line)
            else:
                self.distance_list.addItem("未找到路线")
        
        except Exception as e:
            QMessageBox.critical(self, "规划错误", f"路线规划失败：{str(e)}")


def main():
    """主程序入口"""
    app = QApplication(sys.argv)
    window = MetroPlannerApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

"""
地图显示组件模块

提供地铁路线的可视化地图显示功能，支持缩放、平移等交互操作。
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import (
    QPainter, QPen, QColor, QFont, QBrush, QPainterPath, QPixmap
)

from xianmetro.assets.icon import UP, DOWN, TRANSFER
from xianmetro.i18n import get_text


class MapWidget(QWidget):
    """
    地铁路线地图显示组件
    
    使用经纬度坐标显示地铁路线，支持缩放和平移交互。
    """
    
    def __init__(self, parent=None):
        """
        初始化地图组件
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        self.setMinimumSize(400, 600)
        self.route_data = None  # 存储路线信息
        self.stations_dict = None  # 存储所有站点信息
        self.scale_factor = 1.0  # 缩放系数
        self.pan_offset_x = 0.0  # X方向平移偏移
        self.pan_offset_y = 0.0  # Y方向平移偏移
        self.last_mouse_pos = None  # 用于跟踪鼠标拖动
        
        # 初始化时加载图标，带错误处理
        try:
            self.up_icon = QPixmap(UP)
            if self.up_icon.isNull():
                print(f"Warning: Failed to load UP icon from {UP}")
        except Exception as e:
            print(f"Warning: Error loading UP icon: {e}")
            self.up_icon = QPixmap()
            
        try:
            self.down_icon = QPixmap(DOWN)
            if self.down_icon.isNull():
                print(f"Warning: Failed to load DOWN icon from {DOWN}")
        except Exception as e:
            print(f"Warning: Error loading DOWN icon: {e}")
            self.down_icon = QPixmap()
            
        try:
            self.transfer_icon = QPixmap(TRANSFER)
            if self.transfer_icon.isNull():
                print(f"Warning: Failed to load TRANSFER icon from {TRANSFER}")
        except Exception as e:
            print(f"Warning: Error loading TRANSFER icon: {e}")
            self.transfer_icon = QPixmap()
        
    def set_route(self, route, stations_dict, line_colors):
        """
        设置要显示的路线
        
        Args:
            route: 路线段列表，每段包含线路名称和站点ID列表
            stations_dict: 所有站点字典（id -> Station对象）
            line_colors: 线路名称到颜色的映射字典
        """
        self.route_data = route
        self.stations_dict = stations_dict
        self.line_colors = line_colors
        self.update()
        
    def clear_route(self):
        """清除当前路线显示"""
        self.route_data = None
        self.update()
    
    def zoom_in(self):
        """放大地图"""
        self.scale_factor = min(self.scale_factor * 1.2, 5.0)
        self.update()
    
    def zoom_out(self):
        """缩小地图"""
        self.scale_factor = max(self.scale_factor / 1.2, 0.5)
        self.update()
    
    def reset_zoom(self):
        """重置缩放到默认值"""
        self.scale_factor = 1.0
        self.pan_offset_x = 0.0
        self.pan_offset_y = 0.0
        self.update()
    
    def mousePressEvent(self, event):
        """处理鼠标按下事件以支持平移"""
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件以支持平移"""
        if event.buttons() & Qt.LeftButton and self.last_mouse_pos is not None:
            delta = event.pos() - self.last_mouse_pos
            self.pan_offset_x += delta.x()
            self.pan_offset_y += delta.y()
            self.last_mouse_pos = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None
            self.setCursor(Qt.ArrowCursor)
        
    def paintEvent(self, event):
        """
        绘制地图和路线
        
        Args:
            event: 绘制事件
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆角背景
        painter.fillRect(self.rect(), Qt.transparent)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10)
        painter.setClipPath(path)
        painter.fillRect(self.rect(), QColor("#f4f7fa"))
        
        if not self.route_data or not self.stations_dict:
            # 绘制占位符文本
            painter.setPen(QColor("#999"))
            painter.setFont(QFont("Microsoft YaHei", 14))
            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                get_text("ui.default_map_text")
            )
            return
            
        # 收集路线中的所有坐标
        all_coords = []
        for segment in self.route_data:
            for station_id in segment["stations"]:
                station = self.stations_dict.get(station_id)
                if (station and station.coords and isinstance(station.coords, tuple)
                        and len(station.coords) >= 2):
                    all_coords.append(station.coords)
                    
        if not all_coords:
            return
            
        # 计算边界和缩放
        lats = [c[0] for c in all_coords]
        lons = [c[1] for c in all_coords]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # 添加内边距
        padding = 40
        base_width = self.width() - 2 * padding
        base_height = self.height() - 2 * padding
        
        # 应用缩放 - 缩放绘图区域
        width = base_width * self.scale_factor
        height = base_height * self.scale_factor
        
        # 计算缩放的中心偏移
        center_x = self.width() / 2
        center_y = self.height() / 2
        offset_x = center_x - (center_x * self.scale_factor) + self.pan_offset_x
        offset_y = center_y - (center_y * self.scale_factor) + self.pan_offset_y
        
        # 处理所有坐标相同的边缘情况
        lat_range = max_lat - min_lat if max_lat != min_lat else 0.01
        lon_range = max_lon - min_lon if max_lon != min_lon else 0.01
        
        def coord_to_point(lat, lon):
            """
            将经纬度转换为组件坐标（带缩放）
            
            Args:
                lat: 纬度
                lon: 经度
                
            Returns:
                QPointF: 组件坐标点
            """
            x = ((padding + (lon - min_lon) / lon_range * base_width) *
                 self.scale_factor + offset_x)
            y = ((padding + (max_lat - lat) / lat_range * base_height) *
                 self.scale_factor + offset_y)
            return QPointF(x, y)
        
        # 识别特殊站点（上车、下车、换乘）
        boarding_station = None  # 第一段的第一个站点
        alighting_station = None  # 最后一段的最后一个站点
        transfer_stations = []  # 换乘站点
        
        if self.route_data:
            # 上车站点
            if self.route_data[0]["stations"]:
                boarding_station = self.route_data[0]["stations"][0]
            
            # 下车站点
            if self.route_data[-1]["stations"]:
                alighting_station = self.route_data[-1]["stations"][-1]
            
            # 换乘站点 - 除最后一段外，每段的最后一个站点
            for i in range(len(self.route_data) - 1):
                if self.route_data[i]["stations"]:
                    transfer_station = self.route_data[i]["stations"][-1]
                    transfer_stations.append((i, transfer_station))
        
        def is_special_station(station_id):
            """
            检查站点是否为特殊站点（上车、下车或换乘）
            
            Args:
                station_id: 站点ID
                
            Returns:
                bool: 是否为特殊站点
            """
            return (station_id == boarding_station or 
                    station_id == alighting_station or
                    any(station_id == ts_id for _, ts_id in transfer_stations))
        
        # Draw route segments
        for i, segment in enumerate(self.route_data):
            line_name = segment["line"]
            station_ids = segment["stations"]
            color = self.line_colors.get(line_name, "#000000")
            
            # Draw lines between stations within this segment
            pen = QPen(QColor(color))
            pen.setWidth(4)  # Keep line width constant
            painter.setPen(pen)
            
            for j in range(len(station_ids) - 1):
                station1 = self.stations_dict.get(station_ids[j])
                station2 = self.stations_dict.get(station_ids[j + 1])
                if (station1 and station1.coords and isinstance(station1.coords, tuple) and len(station1.coords) >= 2 and
                    station2 and station2.coords and isinstance(station2.coords, tuple) and len(station2.coords) >= 2):
                    p1 = coord_to_point(station1.coords[0], station1.coords[1])
                    p2 = coord_to_point(station2.coords[0], station2.coords[1])
                    painter.drawLine(p1, p2)
        
        # Draw transfer connections (from transfer station to first station of next line)
        for i, transfer_station_id in transfer_stations:
            if i + 1 < len(self.route_data):
                next_segment = self.route_data[i + 1]
                if next_segment["stations"]:
                    next_station_id = next_segment["stations"][0]
                    next_color = self.line_colors.get(next_segment["line"], "#000000")
                    
                    transfer_station = self.stations_dict.get(transfer_station_id)
                    next_station = self.stations_dict.get(next_station_id)
                    
                    if (transfer_station and transfer_station.coords and isinstance(transfer_station.coords, tuple) and len(transfer_station.coords) >= 2 and
                        next_station and next_station.coords and isinstance(next_station.coords, tuple) and len(next_station.coords) >= 2):
                        p1 = coord_to_point(transfer_station.coords[0], transfer_station.coords[1])
                        p2 = coord_to_point(next_station.coords[0], next_station.coords[1])
                        
                        # Draw connection with next line's color
                        pen = QPen(QColor(next_color))
                        pen.setWidth(4)
                        #pen.setStyle(Qt.DashLine)  # Use dashed line to distinguish transfer connection
                        painter.setPen(pen)
                        painter.drawLine(p1, p2)
        
        # Draw station markers, labels, and icons
        for seg_idx, segment in enumerate(self.route_data):
            line_name = segment["line"]
            station_ids = segment["stations"]
            color = self.line_colors.get(line_name, "#000000")
            
            for station_id in station_ids:
                station = self.stations_dict.get(station_id)
                if station and station.coords and isinstance(station.coords, tuple) and len(station.coords) >= 2:
                    point = coord_to_point(station.coords[0], station.coords[1])
                    
                    # Determine if this is a special station
                    is_boarding = (station_id == boarding_station)
                    is_alighting = (station_id == alighting_station)
                    is_transfer = any(station_id == ts_id for _, ts_id in transfer_stations)
                    
                    # Draw station circle only for non-special stations
                    if not is_special_station(station_id):
                        painter.setBrush(QBrush(QColor(color)))
                        painter.setPen(QPen(QColor("#ffffff"), 2))
                        painter.drawEllipse(point, 6, 6)
                    
                    # Draw icon for special stations
                    icon_size = 24  # Keep icon size constant
                    if is_boarding and not self.up_icon.isNull():
                        icon_rect = QRectF(point.x() - icon_size/2, point.y() - icon_size*1/2 , icon_size, icon_size)
                        painter.drawPixmap(icon_rect.toRect(), self.up_icon)
                    elif is_alighting and not self.down_icon.isNull():
                        icon_rect = QRectF(point.x() - icon_size/2, point.y() - icon_size*1/2 , icon_size, icon_size)
                        painter.drawPixmap(icon_rect.toRect(), self.down_icon)
                    elif is_transfer and not self.transfer_icon.isNull():
                        icon_rect = QRectF(point.x() - icon_size/2, point.y() - icon_size*1/2 , icon_size, icon_size)
                        painter.drawPixmap(icon_rect.toRect(), self.transfer_icon)
                    
                    # Draw station name with constant font size
                    painter.setPen(QColor("#333"))
                    painter.setFont(QFont("Microsoft YaHei", 9))  # Keep font size constant
                    text_rect = painter.boundingRect(0, 0, 200, 50, Qt.AlignLeft, station.name)
                    text_rect.moveCenter(point.toPoint())
                    
                    # Offset text down if icon is present
                    if is_boarding or is_alighting or is_transfer:
                        text_rect.translate(0, 20)
                    else:
                        text_rect.translate(0, 15)
                    
                    # Draw text background
                    painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
                    painter.setPen(Qt.NoPen)
                    painter.drawRoundedRect(text_rect.adjusted(-3, -1, 3, 1), 3, 3)
                    
                    # Draw text
                    painter.setPen(QColor("#333"))
                    painter.drawText(text_rect, Qt.AlignCenter, station.name)


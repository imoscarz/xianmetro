"""
Map widget for displaying metro route on a canvas
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QBrush, QPainterPath, QPixmap
from xianmetro.assets.icon import UP, DOWN, TRANSFER


class MapWidget(QWidget):
    """
    A simple map widget that displays metro routes using latitude/longitude coordinates
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 600)
        self.route_data = None  # Will store route information
        self.stations_dict = None  # Will store all stations information
        self.scale_factor = 1.0  # Zoom scale factor
        
        # Load icons once during initialization with error handling
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
        Set the route to display
        :param route: List of route segments, each containing line name and station IDs
        :param stations_dict: Dictionary of all stations (id -> Station object)
        :param line_colors: Dictionary mapping line names to colors
        """
        self.route_data = route
        self.stations_dict = stations_dict
        self.line_colors = line_colors
        self.update()
        
    def clear_route(self):
        """Clear the current route display"""
        self.route_data = None
        self.update()
    
    def zoom_in(self):
        """Zoom in the map"""
        self.scale_factor = min(self.scale_factor * 1.2, 5.0)
        self.update()
    
    def zoom_out(self):
        """Zoom out the map"""
        self.scale_factor = max(self.scale_factor / 1.2, 0.5)
        self.update()
    
    def reset_zoom(self):
        """Reset zoom to default"""
        self.scale_factor = 1.0
        self.update()
        
    def paintEvent(self, event):
        """Paint the map with route"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw rounded background
        painter.fillRect(self.rect(), Qt.transparent)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10)
        painter.setClipPath(path)
        painter.fillRect(self.rect(), QColor("#f4f7fa"))
        
        if not self.route_data or not self.stations_dict:
            # Draw placeholder text
            painter.setPen(QColor("#999"))
            painter.setFont(QFont("Microsoft YaHei", 14))
            painter.drawText(self.rect(), Qt.AlignCenter, "请先规划路线")
            return
            
        # Collect all coordinates from the route
        all_coords = []
        for segment in self.route_data:
            for station_id in segment["stations"]:
                station = self.stations_dict.get(station_id)
                if station and station.coords and isinstance(station.coords, tuple) and len(station.coords) >= 2:
                    all_coords.append(station.coords)
                    
        if not all_coords:
            return
            
        # Calculate bounds and scaling
        lats = [c[0] for c in all_coords]
        lons = [c[1] for c in all_coords]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Add padding
        padding = 40
        base_width = self.width() - 2 * padding
        base_height = self.height() - 2 * padding
        
        # Apply zoom - scale the drawing area
        width = base_width * self.scale_factor
        height = base_height * self.scale_factor
        
        # Calculate center offset for zoom
        center_x = self.width() / 2
        center_y = self.height() / 2
        offset_x = center_x - (center_x * self.scale_factor)
        offset_y = center_y - (center_y * self.scale_factor)
        
        # Handle edge case where all coordinates are the same
        lat_range = max_lat - min_lat if max_lat != min_lat else 0.01
        lon_range = max_lon - min_lon if max_lon != min_lon else 0.01
        
        def coord_to_point(lat, lon):
            """Convert latitude/longitude to widget coordinates with zoom"""
            x = (padding + (lon - min_lon) / lon_range * base_width) * self.scale_factor + offset_x
            y = (padding + (max_lat - lat) / lat_range * base_height) * self.scale_factor + offset_y
            return QPointF(x, y)
        
        # Identify special stations (boarding, alighting, transfer)
        boarding_station = None  # First station of first segment
        alighting_station = None  # Last station of last segment
        transfer_stations = []  # Stations where transfer occurs
        
        if self.route_data:
            # Boarding station
            if self.route_data[0]["stations"]:
                boarding_station = self.route_data[0]["stations"][0]
            
            # Alighting station
            if self.route_data[-1]["stations"]:
                alighting_station = self.route_data[-1]["stations"][-1]
            
            # Transfer stations - last station of each segment except the last
            for i in range(len(self.route_data) - 1):
                if self.route_data[i]["stations"]:
                    transfer_station = self.route_data[i]["stations"][-1]
                    transfer_stations.append((i, transfer_station))
        
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
                        pen.setStyle(Qt.DashLine)  # Use dashed line to distinguish transfer connection
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
                    
                    # Draw station circle
                    painter.setBrush(QBrush(QColor(color)))
                    painter.setPen(QPen(QColor("#ffffff"), 2))
                    painter.drawEllipse(point, 6, 6)
                    
                    # Draw icon for special stations
                    icon_size = 24  # Keep icon size constant
                    if is_boarding and not self.up_icon.isNull():
                        icon_rect = QRectF(point.x() - icon_size/2, point.y() - icon_size - 10, icon_size, icon_size)
                        painter.drawPixmap(icon_rect.toRect(), self.up_icon)
                    elif is_alighting and not self.down_icon.isNull():
                        icon_rect = QRectF(point.x() - icon_size/2, point.y() - icon_size - 10, icon_size, icon_size)
                        painter.drawPixmap(icon_rect.toRect(), self.down_icon)
                    elif is_transfer and not self.transfer_icon.isNull():
                        icon_rect = QRectF(point.x() - icon_size/2, point.y() - icon_size - 10, icon_size, icon_size)
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


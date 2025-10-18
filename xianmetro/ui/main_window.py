"""
主窗口UI模块

提供地铁路线规划器的图形用户界面，包括输入、显示和交互组件。
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy,
    QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap, QIcon
from PyQt5.QtWidgets import QGraphicsBlurEffect

from qfluentwidgets import (
    TitleLabel, EditableComboBox, PrimaryPushButton, PushButton,
    TextEdit, SmoothScrollArea, ComboBox, SegmentedWidget,
    CommandBar, Action, FluentIcon, CardWidget
)

from xianmetro.fetch import get_station_list
from xianmetro.utils.load_config import get_update_links, get_default_city, get_default_lang
from xianmetro.ui.map_widget import MapWidget
from xianmetro.i18n import get_text, get_language_list


class MetroPlannerUI(QWidget):
    """
    地铁路线规划器主窗口类

    提供完整的用户界面，包括输入控件、结果显示和地图可视化。
    """

    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle(get_text("ui.window_title"))
        self.resize(1920, 1080)
        self.setMinimumSize(1920, 1080)
        self.setWindowIcon(QIcon("./xianmetro/assets/icon.ico"))
        self._set_background()
        self._init_ui()

    def _set_background(self):
        """设置窗口背景图片和模糊效果"""
        palette = self.palette()
        pixmap = QPixmap("xianmetro/assets/bg.jpg")
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(pixmap)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.lower()

        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(10)
        self.bg_label.setGraphicsEffect(blur_effect)

        self.bg_label.setScaledContents(True)
        self.resizeEvent = self._resize_event_with_bg

    def _resize_event_with_bg(self, event):
        """窗口大小改变时调整背景图片大小"""
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        event.accept()

    def _init_ui(self):
        """初始化用户界面组件"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 左侧面板
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(60, 48, 40, 48)
        left_layout.setSpacing(32)

        # 标题
        title = TitleLabel(get_text("ui.title_label"))
        title.setFont(QFont("Microsoft YaHei", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)

        # 输入区域
        input_layout = QVBoxLayout()
        input_layout.setSpacing(18)

        # 语言选择
        self.lang_label = QLabel(get_text("ui.current_lang"))
        self.lang_label.setFont(QFont("Microsoft YaHei", 13))
        self.lang_input = ComboBox()
        self.lang_input.setPlaceholderText(get_text("ui.lang_placeholder"))
        self.lang_input.setMaximumWidth(140)
        self.lang_input.setFixedHeight(50)
        self.lang_input.setFont(QFont("Microsoft YaHei", 12))

        # 城市选择
        self.city_label = QLabel(get_text("ui.current_city"))
        self.city_label.setFont(QFont("Microsoft YaHei", 13))
        self.city_input = ComboBox()
        self.city_input.setPlaceholderText(get_text("ui.city_placeholder"))
        self.city_input.setMaximumWidth(140)
        self.city_input.setFixedHeight(50)
        self.city_input.setFont(QFont("Microsoft YaHei", 12))

        lang_layout = QVBoxLayout()
        lang_layout.addWidget(self.lang_label)
        lang_layout.addWidget(self.lang_input)

        city_layout = QVBoxLayout()
        city_layout.addWidget(self.city_label)
        city_layout.addWidget(self.city_input)

        settings_layout = QHBoxLayout()
        settings_layout.setSpacing(12)
        settings_layout.addLayout(lang_layout)
        settings_layout.addLayout(city_layout)

        left_layout.addLayout(settings_layout)

        # 起点站选择
        self.start_label = QLabel(get_text("ui.start_station"))
        self.start_label.setFont(QFont("Microsoft YaHei", 13))
        self.start_input = EditableComboBox()
        self.start_input.setPlaceholderText(get_text("ui.start_placeholder"))
        self.start_input.setMaximumWidth(320)
        self.start_input.setFixedHeight(50)
        self.start_input.setFont(QFont("Microsoft YaHei", 12))

        # 终点站选择
        self.end_label = QLabel(get_text("ui.end_station"))
        self.end_label.setFont(QFont("Microsoft YaHei", 13))
        self.end_input = EditableComboBox()
        self.end_input.setPlaceholderText(get_text("ui.end_placeholder"))
        self.end_input.setMaximumWidth(320)
        self.end_input.setFixedHeight(50)
        self.end_input.setFont(QFont("Microsoft YaHei", 12))

        # 填充下拉内容（语言、站名和ID）
        language_names = get_language_list()
        city_names = get_update_links().keys()
        station_names = get_station_list()
        station_ids = []
        start_options = list(dict.fromkeys(station_names + station_ids))
        end_options = start_options.copy()
        self.lang_input.addItems(language_names)
        self.city_input.addItems(city_names)
        self.start_input.addItems(start_options)
        self.end_input.addItems(end_options)

        # 设置语言和城市的默认值
        default_lang = get_default_lang()
        default_city = get_default_city()
        self.lang_input.setCurrentText(default_lang)
        self.city_input.setCurrentText(default_city)

        input_layout.addWidget(self.start_label)
        input_layout.addWidget(self.start_input)
        input_layout.addWidget(self.end_label)
        input_layout.addWidget(self.end_input)
        input_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        left_layout.addLayout(input_layout)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(18)
        btn_layout.setAlignment(Qt.AlignCenter)

        self.plan_btn = PrimaryPushButton(get_text("ui.plan_button"))
        self.plan_btn.setFont(QFont("Microsoft YaHei", 13))
        self.plan_btn.setMinimumWidth(180)
        self.plan_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.refresh_btn = PrimaryPushButton(get_text("ui.refresh_button"))
        self.refresh_btn.setFont(QFont("Microsoft YaHei", 13))
        self.refresh_btn.setMinimumWidth(180)
        self.refresh_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        btn_layout.addWidget(self.plan_btn)
        btn_layout.addWidget(self.refresh_btn)
        left_layout.addLayout(btn_layout)

        left_layout.addStretch()
        left_widget.setFixedWidth(int(self.width() * 0.37))
        main_layout.addWidget(left_widget, 30)

        # 右侧面板
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 48, 40, 48)
        right_layout.setSpacing(22)

        # 路线策略选择器
        self.route_selector = SegmentedWidget()
        self.route_selector.addItem(
            "transfer", get_text("strategy.least_transfer"))
        self.route_selector.addItem("stops", get_text("strategy.least_stops"))
        self.route_selector.addItem(
            "distance", get_text("strategy.shortest_distance"))
        self.route_selector.setCurrentItem("transfer")
        self.route_selector.setMinimumHeight(50)
        self.route_selector.setFont(QFont("Microsoft YaHei", 13))
        right_layout.addWidget(self.route_selector)

        # 内容布局（结果显示和地图）
        content_layout = QHBoxLayout()
        content_layout.setSpacing(22)

        # 结果显示区域
        result_container = QWidget()
        result_layout = QVBoxLayout(result_container)
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.setSpacing(10)

        self.info_label = TextEdit()
        self.info_label.setFont(QFont("Microsoft YaHei", 11))
        self.info_label.setReadOnly(True)
        self.info_label.setMaximumHeight(150)
        self.info_label.setMinimumHeight(32)
        self.info_label.setStyleSheet(
            "background: #f7fafd; border:none; color:#444; border-radius: 10px;"
        )
        result_layout.addWidget(self.info_label)

        scroll_area = SmoothScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            "background: #f4f7fa; border-radius: 10px; border:1px solid #dbeaf5;"
        )
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll_content = QWidget()
        self.result_vlayout = QVBoxLayout(scroll_content)
        self.result_vlayout.setSpacing(8)
        self.result_vlayout.setContentsMargins(10, 10, 10, 10)
        scroll_area.setWidget(scroll_content)
        result_layout.addWidget(scroll_area, stretch=1)

        content_layout.addWidget(result_container, 1)

        # 地图容器和控制栏
        map_container = QWidget()
        map_layout = QVBoxLayout(map_container)
        map_layout.setContentsMargins(0, 0, 0, 0)
        map_layout.setSpacing(10)

        # 地图缩放控制栏
        self.map_command_bar = CommandBar()
        self.zoom_in_action = Action(
            FluentIcon.ZOOM_IN,
            get_text("ui.zoom_in"),
            triggered=self._on_zoom_in
        )
        self.zoom_out_action = Action(
            FluentIcon.ZOOM_OUT,
            get_text("ui.zoom_out"),
            triggered=self._on_zoom_out
        )
        self.reset_zoom_action = Action(
            FluentIcon.SYNC,
            get_text("ui.reset_zoom"),
            triggered=self._on_reset_zoom
        )
        self.map_command_bar.addAction(self.zoom_in_action)
        self.map_command_bar.addAction(self.zoom_out_action)
        self.map_command_bar.addAction(self.reset_zoom_action)
        map_layout.addWidget(self.map_command_bar)

        # 地图滚动区域
        self.map_scroll_area = SmoothScrollArea()
        self.map_scroll_area.setWidgetResizable(True)
        self.map_scroll_area.setStyleSheet(
            "background: #f4f7fa; border-radius: 10px; border:1px solid #dbeaf5;"
        )
        self.map_scroll_area.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.map_widget = MapWidget()
        self.map_widget.setMinimumSize(400, 600)
        self.map_scroll_area.setWidget(self.map_widget)
        map_layout.addWidget(self.map_scroll_area, 1)

        content_layout.addWidget(map_container, 1)

        right_layout.addLayout(content_layout, 1)

        main_layout.addWidget(right_widget, 70)

        # 存储路线结果用于切换标签页
        self.route_results = [None, None, None]  # 三种策略的结果

    def clear_result_area(self, idx=None):
        """
        清空结果显示区域

        Args:
            idx: 保留用于向后兼容，但会被忽略
        """
        layout = self.result_vlayout
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def add_result_item(self, items, icon=None):
        """
        添加结果项到当前显示区域，支持多个彩色文本片段

        Args:
            items: 文本字典列表，每个字典包含text、text_color和background_color
            icon: 要显示的图标（PNG路径或FluentIcon）
        """
        # 统一处理输入格式
        if isinstance(items, str):
            items = [{
                'text': items,
                'text_color': '#333333',
                'background_color': '#FFFFFF'
            }]
        elif isinstance(items, dict):
            items = [items]
        elif not isinstance(items, list):
            raise ValueError("items must be a string, dict, or list of dicts")

        card = CardWidget(self)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 8, 16, 8)
        card_layout.setSpacing(18)

        # 左侧图标
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        if icon:
            if isinstance(icon, str) and icon.endswith('.png'):
                pixmap = QPixmap(icon)
                icon_label.setPixmap(
                    pixmap.scaled(
                        32,
                        32,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation))
            else:
                try:
                    icon_label.setPixmap(
                        QPixmap(QIcon.fromTheme(icon).pixmap(QSize(32, 32)))
                    )
                except Exception:
                    icon_label.setText("🛈")
        else:
            icon_label.setText("🛈")
        icon_label.setAlignment(Qt.AlignCenter)

        # 右侧文本区域
        text_container = QWidget()
        text_layout = QHBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(8)

        for item in items:
            text = item.get('text', '')
            text_color = item.get('text_color', '#333333')
            background_color = item.get('background_color', '#FFFFFF')

            text_label = QLabel(text)
            text_label.setFont(QFont("Microsoft YaHei", 13))
            text_label.setStyleSheet(f"""
                background-color: {background_color};
                border-radius: 8px;
                padding: 10px 18px;
                color: {text_color};
            """)
            text_label.setWordWrap(True)
            text_layout.addWidget(text_label)

        text_layout.addStretch()

        card_layout.addWidget(icon_label)
        card_layout.addWidget(text_container)

        self.result_vlayout.addWidget(card)

    def update_map_display(self):
        """根据当前选择更新地图显示"""
        current_tab = self.route_selector.currentRouteKey()
        idx_map = {"transfer": 0, "stops": 1, "distance": 2}
        idx = idx_map.get(current_tab, 0)

        result = self.route_results[idx]
        if result and result.get("route_data"):
            route = result["route_data"]
            stations = result["stations_dict"]
            line_colors = result["line_colors"]
            self.map_widget.set_route(route, stations, line_colors)
        else:
            self.map_widget.clear_route()

    def on_route_selector_changed(self):
        """处理路线选择器标签页切换事件"""
        current_tab = self.route_selector.currentRouteKey()
        idx_map = {"transfer": 0, "stops": 1, "distance": 2}
        idx = idx_map.get(current_tab, 0)

        # 清空并显示选择的路线结果
        self.clear_result_area()
        result = self.route_results[idx]

        if result:
            # 显示路线行
            if result.get("item_list"):
                for item, icon in zip(
                        result["item_list"], result["icon_list"]):
                    self.add_result_item(item, icon)
            else:
                self.add_result_item(
                    result.get("message", get_text("messages.no_route_found"))
                )

            # 更新信息标签
            self.info_label.setText(result.get("info_text", ""))
        else:
            self.info_label.setText("")

        # 更新地图
        self.update_map_display()

    def store_route_result(self, idx, item_list=None, icon_list=None,
                           info_text="", route_data=None, stations_dict=None,
                           line_colors=None, message=None):
        """
        存储路线结果用于稍后切换标签页时显示

        Args:
            idx: 策略索引（0-2）
            item_list: 结果项列表
            icon_list: 图标列表
            info_text: 信息文本
            route_data: 路线数据
            stations_dict: 站点字典
            line_colors: 线路颜色字典
            message: 错误或提示消息
        """
        self.route_results[idx] = {
            "item_list": item_list,
            "icon_list": icon_list,
            "info_text": info_text,
            "route_data": route_data,
            "stations_dict": stations_dict,
            "line_colors": line_colors,
            "message": message
        }

    def get_start_station(self):
        """获取起点站输入"""
        return self.start_input.currentText()

    def get_end_station(self):
        """获取终点站输入"""
        return self.end_input.currentText()

    def get_city(self):
        """获取当前选择的城市"""
        return self.city_input.currentText()

    def get_lang(self):
        """获取当前选择的语言"""
        return self.lang_input.currentText()

    def _on_zoom_in(self):
        """处理地图放大操作"""
        self.map_widget.zoom_in()

    def _on_zoom_out(self):
        """处理地图缩小操作"""
        self.map_widget.zoom_out()

    def _on_reset_zoom(self):
        """处理地图重置缩放操作"""
        self.map_widget.reset_zoom()

    def reload_ui(self):
        """重新加载UI文本以支持语言切换"""
        self.setWindowTitle(get_text("ui.window_title"))
        self.lang_label.setText(get_text("ui.current_lang"))
        self.city_label.setText(get_text("ui.current_city"))
        self.start_label.setText(get_text("ui.start_station"))
        self.start_input.setPlaceholderText(get_text("ui.start_placeholder"))
        self.end_label.setText(get_text("ui.end_station"))
        self.end_input.setPlaceholderText(get_text("ui.end_placeholder"))
        self.plan_btn.setText(get_text("ui.plan_button"))
        self.refresh_btn.setText(get_text("ui.refresh_button"))
        self.route_selector.setItemText(
            "transfer", get_text("strategy.least_transfer"))
        self.route_selector.setItemText(
            "stops", get_text("strategy.least_stops"))
        self.route_selector.setItemText(
            "distance", get_text("strategy.shortest_distance"))
        self.zoom_in_action.setText(get_text("ui.zoom_in"))
        self.zoom_out_action.setText(get_text("ui.zoom_out"))
        self.reset_zoom_action.setText(get_text("ui.reset_zoom"))

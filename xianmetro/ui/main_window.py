from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QSpacerItem,
    QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap, QIcon

from qfluentwidgets import TitleLabel, EditableComboBox, PrimaryPushButton, PushButton, TextEdit, SmoothScrollArea, \
    ComboBox

from PyQt5.QtWidgets import QGraphicsBlurEffect

from qfluentwidgets import CardWidget

from xianmetro.fetch import get_id_list, get_station_list
from xianmetro.assets import UPDATE_LINK



class MetroPlannerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("地铁路线规划 BY imoscarz")
        # self.resize(1920, 1080)
        self.setFixedSize(1920, 1080)
        # self.setMinimumSize(1200, 700)
        self._set_background()
        self._init_ui()

    def _set_background(self):
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
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        event.accept()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(60, 48, 40, 48)
        left_layout.setSpacing(32)

        title = TitleLabel("地铁路线规划")
        title.setFont(QFont("Microsoft YaHei", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)

        input_layout = QVBoxLayout()
        input_layout.setSpacing(18)

        self.city_label = QLabel("当前城市")
        self.city_label.setFont(QFont("Microsoft YaHei", 13))
        self.city_input = ComboBox()
        self.city_input.setPlaceholderText("请选择城市")
        self.city_input.setMaximumWidth(320)
        self.city_input.setFixedHeight(50)
        self.city_input.setFont(QFont("Microsoft YaHei", 12))

        self.start_label = QLabel("起点站:")
        self.start_label.setFont(QFont("Microsoft YaHei", 13))
        self.start_input = EditableComboBox()
        self.start_input.setPlaceholderText("请输入或选择起点站名/站点ID")
        self.start_input.setMaximumWidth(320)
        self.start_input.setFixedHeight(50)
        self.start_input.setFont(QFont("Microsoft YaHei", 12))

        self.end_label = QLabel("终点站:")
        self.end_label.setFont(QFont("Microsoft YaHei", 13))
        self.end_input = EditableComboBox()
        self.end_input.setPlaceholderText("请输入或选择终点站名/站点ID")
        self.end_input.setMaximumWidth(320)
        self.end_input.setFixedHeight(50)
        self.end_input.setFont(QFont("Microsoft YaHei", 12))

        # 填充下拉内容（站名和ID）
        city_names = UPDATE_LINK.keys()
        station_names = get_station_list()
        station_ids = get_id_list()
        # 合并并去重
        start_options = list(dict.fromkeys(station_names + station_ids))
        end_options = start_options.copy()
        self.city_input.addItems(city_names)
        self.start_input.addItems(start_options)
        self.end_input.addItems(end_options)

        input_layout.addWidget(self.city_label)
        input_layout.addWidget(self.city_input)
        input_layout.addWidget(self.start_label)
        input_layout.addWidget(self.start_input)
        input_layout.addWidget(self.end_label)
        input_layout.addWidget(self.end_input)
        input_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        left_layout.addLayout(input_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(18)
        btn_layout.setAlignment(Qt.AlignCenter)

        self.plan_btn = PrimaryPushButton("开始规划")
        self.plan_btn.setFont(QFont("Microsoft YaHei", 13))
        self.plan_btn.setFixedWidth(180)
        self.plan_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.refresh_btn = PrimaryPushButton("刷新路线")
        self.refresh_btn.setFont(QFont("Microsoft YaHei", 13))
        self.refresh_btn.setFixedWidth(180)
        self.refresh_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        btn_layout.addWidget(self.plan_btn)
        btn_layout.addWidget(self.refresh_btn)
        left_layout.addLayout(btn_layout)

        left_layout.addStretch()
        left_widget.setFixedWidth(int(self.width() * 0.37))
        main_layout.addWidget(left_widget, 30)

        right_widget = QWidget()
        right_layout = QHBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 48, 40, 48)
        right_layout.setSpacing(22)

        self.result_areas = []
        self.result_info_labels = []
        self.result_scrolls = []
        self.result_vlayouts = []

        for title_text in ["最少换乘方案", "最少站点方案", "最短距离方案"]:
            area_widget = QWidget()
            area_layout = QVBoxLayout(area_widget)
            area_layout.setContentsMargins(0, 0, 0, 0)
            area_layout.setSpacing(10)

            info_label = TextEdit()
            info_label.setFont(QFont("Microsoft YaHei", 11))
            info_label.setReadOnly(True)
            info_label.setMaximumHeight(150)
            info_label.setMinimumHeight(32)
            info_label.setStyleSheet("background: #f7fafd; border:none; color:#444; border-radius: 10px;")
            scheme_label = QLabel(title_text)
            scheme_label.setFont(QFont("Microsoft YaHei", 13, QFont.Bold))
            scheme_label.setStyleSheet("color: #0078d7; margin-bottom: 2px;")
            area_layout.addWidget(scheme_label)
            area_layout.addWidget(info_label)
            self.result_info_labels.append(info_label)

            scroll_area = SmoothScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet("background: #f4f7fa; border-radius: 10px; border:1px solid #dbeaf5;")
            scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            scroll_content = QWidget()
            vlayout = QVBoxLayout(scroll_content)
            vlayout.setSpacing(8)
            vlayout.setContentsMargins(10, 10, 10, 10)
            scroll_area.setWidget(scroll_content)
            area_layout.addWidget(scroll_area, stretch=1)

            self.result_scrolls.append(scroll_area)
            self.result_vlayouts.append(vlayout)
            self.result_areas.append(area_widget)
            right_layout.addWidget(area_widget, 1)

        main_layout.addWidget(right_widget, 70)

    # 新增清空与添加方法
    def clear_result_area(self, idx):
        layout = self.result_vlayouts[idx]
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def add_result_item(self, idx, text, icon=None, color = '#FFFFFF'):
        card = CardWidget(self)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 8, 16, 8)
        card_layout.setSpacing(18)
        # 左侧icon
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        if icon:
            # 支持assets路径（png）和 FluentIcon
            if isinstance(icon, str) and icon.endswith('.png'):
                pixmap = QPixmap(icon)
                icon_label.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                # 尝试用FluentIcon
                try:
                    icon_label.setPixmap(QPixmap(QIcon.fromTheme(icon).pixmap(QSize(32, 32))))
                except Exception:
                    icon_label.setText("🛈")
        else:
            icon_label.setText("🛈")
        # 右侧文本
        text_label = QLabel(text)
        text_label.setFont(QFont("Microsoft YaHei", 13))
        # print(color)
        text_label.setStyleSheet(f"""
            background-color: {color};
            border-radius: 8px;
            padding: 10px 18px;
            color: #333;
        """)
        text_label.setWordWrap(True)
        # 加入布局
        card_layout.addWidget(icon_label)
        card_layout.addWidget(text_label)
        card_layout.addStretch()
        # 添加到结果区
        self.result_vlayouts[idx].addWidget(card)

    def set_least_transfer_result(self, lines: list, info_text: str = "", icon_list=None, color_list=None):
        self.clear_result_area(0)
        icon_list = icon_list or [None] * len(lines)
        # print(color_list)
        color_list = color_list or ['#FFFFFF'] * len(lines)
        # print(color_list)
        for text, icon, color in zip(lines, icon_list, color_list):
            self.add_result_item(0, text, icon, color)
        self.result_info_labels[0].setText(info_text)

    def set_least_stops_result(self, lines: list, info_text: str = "", icon_list=None, color_list=None):
        self.clear_result_area(1)
        icon_list = icon_list or [None] * len(lines)
        color_list = color_list or ['#FFFFFF'] * len(lines)
        for text, icon, color in zip(lines, icon_list, color_list):
            self.add_result_item(1, text, icon, color)
        self.result_info_labels[1].setText(info_text)

    def set_shortest_distance_result(self, lines: list, info_text: str = "", icon_list=None, color_list=None):
        self.clear_result_area(2)
        icon_list = icon_list or [None] * len(lines)
        color_list = color_list or ['#FFFFFF'] * len(lines)
        for text, icon, color in zip(lines, icon_list, color_list):
            self.add_result_item(2, text, icon, color)
        self.result_info_labels[2].setText(info_text)

    def get_start_station(self):
        return self.start_input.currentText()

    def get_end_station(self):
        return self.end_input.currentText()

    def get_city(self):
        return self.city_input.currentText()
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap

from qfluentwidgets import TitleLabel, LineEdit, PrimaryPushButton, ListWidget, TextEdit

# 新增：导入 QGraphicsBlurEffect
from PyQt5.QtWidgets import QGraphicsBlurEffect

class MetroPlannerUI(QWidget):
    def __init__(self):
        super().__init__()
        # 高DPI自适应
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("西安地铁路线规划")
        self.resize(1600, 900)
        self.setMinimumSize(1200, 700)
        self._set_background()
        self._init_ui()

    def _set_background(self):
        # 设置背景图片
        palette = self.palette()
        pixmap = QPixmap("xianmetro/assets/bg.jpg")
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # 新增：创建一个覆盖整个窗口的 QLabel 用于模糊背景
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(pixmap)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.lower()  # 确保在最底层

        # 应用模糊效果
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(30)  # 模糊半径可调整
        self.bg_label.setGraphicsEffect(blur_effect)

        # 保证窗口大小变化时背景也自适应
        self.bg_label.setScaledContents(True)
        self.resizeEvent = self._resize_event_with_bg

    def _resize_event_with_bg(self, event):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        event.accept()

    def _init_ui(self):
        # Parallel Layout: 左侧输入区，右侧结果区
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 左侧：标题、输入框、按钮
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(60, 48, 40, 48)
        left_layout.setSpacing(32)

        # 标题（字号减小）
        title = TitleLabel("西安地铁路线规划")
        title.setFont(QFont("Microsoft YaHei", 22, QFont.Bold))
        title.setAlignment(Qt.AlignLeft)
        left_layout.addWidget(title)

        # 输入区
        input_layout = QVBoxLayout()
        input_layout.setSpacing(18)

        self.start_label = QLabel("起点站:")
        self.start_label.setFont(QFont("Microsoft YaHei", 13))
        self.start_input = LineEdit()
        self.start_input.setPlaceholderText("请输入起点站名或站点ID")
        self.start_input.setMaximumWidth(320)
        self.start_input.setFixedHeight(50)
        self.start_input.setFont(QFont("Microsoft YaHei", 12))

        self.end_label = QLabel("终点站:")
        self.end_label.setFont(QFont("Microsoft YaHei", 13))
        self.end_input = LineEdit()
        self.end_input.setPlaceholderText("请输入终点站名或站点ID")
        self.end_input.setMaximumWidth(320)
        self.end_input.setFixedHeight(50)
        self.end_input.setFont(QFont("Microsoft YaHei", 12))

        input_layout.addWidget(self.start_label)
        input_layout.addWidget(self.start_input)
        input_layout.addWidget(self.end_label)
        input_layout.addWidget(self.end_input)

        # --- 新增中心对齐 ---
        input_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        left_layout.addLayout(input_layout)

        # 按钮区域（水平布局，包含“开始规划”和“刷新路线”按钮）
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

        # 左侧占据约30%
        left_layout.addStretch()
        left_widget.setFixedWidth(int(self.width() * 0.37))
        main_layout.addWidget(left_widget, 30)

        # 右侧：三种方案列
        right_widget = QWidget()
        right_layout = QHBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 48, 40, 48)
        right_layout.setSpacing(22)

        # 方案区布局
        self.result_areas = []
        self.result_info_labels = []
        self.result_lists = []

        for title_text in ["最少换乘方案", "最少站点方案", "最短距离方案"]:
            area_widget = QWidget()
            area_layout = QVBoxLayout(area_widget)
            area_layout.setContentsMargins(0, 0, 0, 0)
            area_layout.setSpacing(10)

            # 路径信息显示（如距离、换乘数等）
            info_label = TextEdit()
            info_label.setFont(QFont("Microsoft YaHei", 11))
            info_label.setReadOnly(True)
            info_label.setMaximumHeight(90)
            info_label.setMinimumHeight(32)
            info_label.setStyleSheet("background: #f7fafd; border:none; color:#444;")

            # 标题
            scheme_label = QLabel(title_text)
            scheme_label.setFont(QFont("Microsoft YaHei", 13, QFont.Bold))
            scheme_label.setStyleSheet("color: #0078d7; margin-bottom: 2px;")
            area_layout.addWidget(scheme_label)
            area_layout.addWidget(info_label)
            self.result_info_labels.append(info_label)

            # 路径列表
            result_list = ListWidget()
            result_list.setFont(QFont("Microsoft YaHei", 14))
            result_list.setStyleSheet(
                "background-color: #f4f7fa; border-radius: 10px; border:1px solid #dbeaf5;"
            )
            result_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            area_layout.addWidget(result_list, stretch=1)
            self.result_lists.append(result_list)

            right_layout.addWidget(area_widget, 1)
            self.result_areas.append(area_widget)

        main_layout.addWidget(right_widget, 70)

    # UI getter methods for controller connection
    def get_start_station(self):
        return self.start_input.text()

    def get_end_station(self):
        return self.end_input.text()

    def set_least_transfer_result(self, lines: list, info_text: str = ""):
        self.result_lists[0].clear()
        for item in lines:
            self.result_lists[0].addItem(item)
        self.result_info_labels[0].setText(info_text)

    def set_least_stops_result(self, lines: list, info_text: str = ""):
        self.result_lists[1].clear()
        for item in lines:
            self.result_lists[1].addItem(item)
        self.result_info_labels[1].setText(info_text)

    def set_shortest_distance_result(self, lines: list, info_text: str = ""):
        self.result_lists[2].clear()
        for item in lines:
            self.result_lists[2].addItem(item)
        self.result_info_labels[2].setText(info_text)
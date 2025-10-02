from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QSpacerItem,
    QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QBrush, QPixmap, QIcon

from qfluentwidgets import TitleLabel, LineEdit, PrimaryPushButton, PushButton, TextEdit

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

        # 新增：存储滚动区和布局
        self.result_areas = []
        self.result_info_labels = []
        self.result_scrolls = []  # 替换原 result_lists
        self.result_vlayouts = []  # 竖直布局

        for title_text in ["最少换乘方案", "最少站点方案", "最短距离方案"]:
            area_widget = QWidget()
            area_layout = QVBoxLayout(area_widget)
            area_layout.setContentsMargins(0, 0, 0, 0)
            area_layout.setSpacing(10)

            info_label = TextEdit()
            info_label.setFont(QFont("Microsoft YaHei", 11))
            info_label.setReadOnly(True)
            info_label.setMaximumHeight(130)
            info_label.setMinimumHeight(32)
            info_label.setStyleSheet("background: #f7fafd; border:none; color:#444;")
            scheme_label = QLabel(title_text)
            scheme_label.setFont(QFont("Microsoft YaHei", 13, QFont.Bold))
            scheme_label.setStyleSheet("color: #0078d7; margin-bottom: 2px;")
            area_layout.addWidget(scheme_label)
            area_layout.addWidget(info_label)
            self.result_info_labels.append(info_label)

            # 新增：竖直滚动区域
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet("background: #f4f7fa; border-radius: 10px; border:1px solid #dbeaf5;")
            scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            # 内容区
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

    def add_result_item(self, idx, text, icon=None):
        btn = PushButton(text)
        btn.setFont(QFont("Microsoft YaHei", 17))
        btn.setEnabled(False)  # 禁用点击
        btn.setStyleSheet("""
                QPushButton {
                    background-color: #f3f8fb;
                    border-radius: 8px;
                    margin-bottom: 2px;
                    padding: 10px 18px;
                    font-size: 17px;
                    color: #333;
                    border: 1px solid #c8e0f0;
                }
                QPushButton:disabled {
                    color: #666;
                }
            """)
        if icon:
            btn.setIcon(QIcon(icon))
            btn.setIconSize(btn.sizeHint())
        self.result_vlayouts[idx].addWidget(btn)

    # 接口兼容原 ListWidget 批量添加
    def set_least_transfer_result(self, lines: list, info_text: str = "", icon_list=None):
        self.clear_result_area(0)
        icon_list = icon_list or [None] * len(lines)
        for text, icon in zip(lines, icon_list):
            self.add_result_item(0, text, icon)
        self.result_info_labels[0].setText(info_text)

    def set_least_stops_result(self, lines: list, info_text: str = "", icon_list=None):
        self.clear_result_area(1)
        icon_list = icon_list or [None] * len(lines)
        for text, icon in zip(lines, icon_list):
            self.add_result_item(1, text, icon)
        self.result_info_labels[1].setText(info_text)

    def set_shortest_distance_result(self, lines: list, info_text: str = "", icon_list=None):
        self.clear_result_area(2)
        icon_list = icon_list or [None] * len(lines)
        for text, icon in zip(lines, icon_list):
            self.add_result_item(2, text, icon)
        self.result_info_labels[2].setText(info_text)

    # 兼容原 getter
    def get_start_station(self):
        return self.start_input.text()

    def get_end_station(self):
        return self.end_input.text()
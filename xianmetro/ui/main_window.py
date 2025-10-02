from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from qfluentwidgets import FluentWindow, TitleLabel, LineEdit, PrimaryPushButton, ListWidget

class MetroPlannerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("西安地铁路线规划")
        self.setMinimumSize(900, 700)
        self._init_ui()

    def _init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setSpacing(25)
        outer_layout.setContentsMargins(32, 32, 32, 32)

        # Title
        title = TitleLabel("西安地铁路线规划")
        title.setFont(QFont("Microsoft YaHei", 26, QFont.Bold))
        outer_layout.addWidget(title, alignment=Qt.AlignCenter)

        # Input section
        input_layout = QHBoxLayout()
        input_layout.setSpacing(16)

        self.start_label = QLabel("起点站:")
        self.start_label.setFont(QFont("Microsoft YaHei", 14))
        self.start_input = LineEdit()
        self.start_input.setPlaceholderText("请输入起点站名或站点ID")
        self.start_input.setMaximumWidth(220)

        self.end_label = QLabel("终点站:")
        self.end_label.setFont(QFont("Microsoft YaHei", 14))
        self.end_input = LineEdit()
        self.end_input.setPlaceholderText("请输入终点站名或站点ID")
        self.end_input.setMaximumWidth(220)

        self.plan_btn = PrimaryPushButton("开始规划")
        self.plan_btn.setFont(QFont("Microsoft YaHei", 14))
        self.plan_btn.setFixedWidth(160)
        self.plan_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        input_layout.addWidget(self.start_label)
        input_layout.addWidget(self.start_input)
        input_layout.addWidget(self.end_label)
        input_layout.addWidget(self.end_input)
        input_layout.addWidget(self.plan_btn)
        input_layout.addStretch()
        outer_layout.addLayout(input_layout)

        # Result section: 3 Lists for 3 strategy results
        result_layout = QHBoxLayout()
        result_layout.setSpacing(24)

        # List for least transfer
        self.list_least_transfer = ListWidget()
        self.list_least_transfer.setMinimumWidth(250)
        self.list_least_transfer.setMaximumWidth(380)
        self.list_least_transfer.setFont(QFont("Microsoft YaHei", 12))
        self.label_least_transfer = QLabel("最少换乘方案")
        self.label_least_transfer.setFont(QFont("Microsoft YaHei", 15, QFont.Bold))
        least_transfer_layout = QVBoxLayout()
        least_transfer_layout.addWidget(self.label_least_transfer)
        least_transfer_layout.addWidget(self.list_least_transfer)
        result_layout.addLayout(least_transfer_layout)

        # List for least stops
        self.list_least_stops = ListWidget()
        self.list_least_stops.setMinimumWidth(250)
        self.list_least_stops.setMaximumWidth(380)
        self.list_least_stops.setFont(QFont("Microsoft YaHei", 12))
        self.label_least_stops = QLabel("最少站点方案")
        self.label_least_stops.setFont(QFont("Microsoft YaHei", 15, QFont.Bold))
        least_stops_layout = QVBoxLayout()
        least_stops_layout.addWidget(self.label_least_stops)
        least_stops_layout.addWidget(self.list_least_stops)
        result_layout.addLayout(least_stops_layout)

        # List for shortest distance
        self.list_shortest_distance = ListWidget()
        self.list_shortest_distance.setMinimumWidth(250)
        self.list_shortest_distance.setMaximumWidth(380)
        self.list_shortest_distance.setFont(QFont("Microsoft YaHei", 12))
        self.label_shortest_distance = QLabel("最短距离方案")
        self.label_shortest_distance.setFont(QFont("Microsoft YaHei", 15, QFont.Bold))
        shortest_distance_layout = QVBoxLayout()
        shortest_distance_layout.addWidget(self.label_shortest_distance)
        shortest_distance_layout.addWidget(self.list_shortest_distance)
        result_layout.addLayout(shortest_distance_layout)

        outer_layout.addLayout(result_layout)
        outer_layout.addStretch()

    # UI getter methods for controller connection
    def get_start_station(self):
        return self.start_input.text()

    def get_end_station(self):
        return self.end_input.text()

    def set_least_transfer_result(self, lines: list):
        self.list_least_transfer.clear()
        for item in lines:
            self.list_least_transfer.addItem(item)

    def set_least_stops_result(self, lines: list):
        self.list_least_stops.clear()
        for item in lines:
            self.list_least_stops.addItem(item)

    def set_shortest_distance_result(self, lines: list):
        self.list_shortest_distance.clear()
        for item in lines:
            self.list_shortest_distance.addItem(item)
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from qfluentwidgets import LineEdit, PushButton, ListWidget, FluentWindow


class MetroPlannerUI(FluentWindow):
    """
    西安地铁路线规划主界面，基于 PyQt-Fluent-Widgets
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("西安地铁路线规划")
        self.resize(1000, 700)
        
        # 创建主窗口部件
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 输入区域
        self.input_layout = self._create_input_section()
        self.main_layout.addLayout(self.input_layout)
        
        # 结果显示区域
        self.result_layout = self._create_result_section()
        self.main_layout.addLayout(self.result_layout)
        
        # 将主窗口部件添加到 FluentWindow
        self.addSubInterface(self.main_widget, "home", "路线规划")
    
    def _create_input_section(self):
        """创建输入区域"""
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("请输入起点和终点（支持站名或站点ID）")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 起点输入框
        start_layout = QHBoxLayout()
        start_label = QLabel("起点：")
        start_label.setFixedWidth(60)
        self.start_input = LineEdit()
        self.start_input.setPlaceholderText("请输入起点站名或站点ID")
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_input)
        layout.addLayout(start_layout)
        
        # 终点输入框
        end_layout = QHBoxLayout()
        end_label = QLabel("终点：")
        end_label.setFixedWidth(60)
        self.end_input = LineEdit()
        self.end_input.setPlaceholderText("请输入终点站名或站点ID")
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.end_input)
        layout.addLayout(end_layout)
        
        # 规划按钮
        self.plan_button = PushButton("开始规划")
        self.plan_button.setFixedSize(150, 40)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.plan_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return layout
    
    def _create_result_section(self):
        """创建结果显示区域"""
        layout = QHBoxLayout()
        
        # 最少换乘结果
        transfer_layout = QVBoxLayout()
        transfer_label = QLabel("最少换乘")
        transfer_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        transfer_label.setAlignment(Qt.AlignCenter)
        self.transfer_list = ListWidget()
        transfer_layout.addWidget(transfer_label)
        transfer_layout.addWidget(self.transfer_list)
        layout.addLayout(transfer_layout)
        
        # 最少站点结果
        stops_layout = QVBoxLayout()
        stops_label = QLabel("最少站点")
        stops_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        stops_label.setAlignment(Qt.AlignCenter)
        self.stops_list = ListWidget()
        stops_layout.addWidget(stops_label)
        stops_layout.addWidget(self.stops_list)
        layout.addLayout(stops_layout)
        
        # 最短距离结果
        distance_layout = QVBoxLayout()
        distance_label = QLabel("最短距离")
        distance_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        distance_label.setAlignment(Qt.AlignCenter)
        self.distance_list = ListWidget()
        distance_layout.addWidget(distance_label)
        distance_layout.addWidget(self.distance_list)
        layout.addLayout(distance_layout)
        
        return layout

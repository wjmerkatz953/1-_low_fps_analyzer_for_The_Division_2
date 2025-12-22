"""
FPS Analyzer GUI - GPU Load Analysis Tool
PySide6 기반 GPU 로드율 분석 GUI 애플리케이션
"""

import sys
import numpy as np
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QFileDialog, QGroupBox, QMessageBox,
    QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False


class FPSBarChart(FigureCanvas):
    """하위 1% FPS 성능 막대 그래프를 표시하는 Matplotlib 캔버스"""
    
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(12, 2.5), dpi=100)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # 초기 빈 그래프 설정
        self._setup_empty_chart()
    
    def wheelEvent(self, event):
        """휠 이벤트를 부모로 전달"""
        event.ignore()
    
    def _setup_empty_chart(self):
        """빈 그래프 초기 설정"""
        self.axes.set_title('FPS Performance Metrics', fontsize=12, fontweight='bold')
        self.axes.text(0.5, 0.5, 'CSV 파일을 불러와주세요\n(Please load a CSV file)', 
                      transform=self.axes.transAxes, ha='center', va='center',
                      fontsize=11, color='gray')
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.fig.tight_layout()
    
    def plot_data(self, avg_fps: float, low_1_percent: float, low_01_percent: float):
        """FPS 성능 데이터를 막대 그래프로 표시"""
        self.axes.clear()
        
        labels = ['Avg FPS', '1% Low', '0.1% Low']
        values = [avg_fps, low_1_percent, low_01_percent]
        colors = ['#3498db', '#e74c3c', '#9b59b6']
        
        x = np.arange(len(labels))
        bars = self.axes.bar(x, values, color=colors, alpha=0.85, width=0.5)
        
        # 막대 위에 값 표시
        for bar, val in zip(bars, values):
            height = bar.get_height()
            self.axes.annotate(f'{val:.1f}',
                             xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3),
                             textcoords="offset points",
                             ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        self.axes.set_ylabel('FPS')
        self.axes.set_title('FPS Performance Metrics', fontsize=12, fontweight='bold')
        self.axes.set_xticks(x)
        self.axes.set_xticklabels(labels)
        self.axes.grid(axis='y', alpha=0.3)
        self.axes.set_ylim(0, max(values) * 1.15)
        
        self.fig.tight_layout()
        self.draw()


class GPULoadChart(FigureCanvas):
    """GPU 로드율 그래프를 표시하는 Matplotlib 캔버스"""
    
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(12, 4), dpi=100)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # 초기 빈 그래프 설정
        self._setup_empty_chart()
    
    def wheelEvent(self, event):
        """휠 이벤트를 부모로 전달"""
        event.ignore()
    
    def _setup_empty_chart(self):
        """빈 그래프 초기 설정"""
        self.axes.set_title('GPU Load Analysis', fontsize=12, fontweight='bold')
        self.axes.set_xlabel('Frame')
        self.axes.set_ylabel('GPU Load (%)')
        self.axes.set_ylim(0, 100)
        self.axes.grid(True, alpha=0.3)
        self.axes.text(0.5, 0.5, 'CSV 파일을 불러와주세요\n(Please load a CSV file)', 
                      transform=self.axes.transAxes, ha='center', va='center',
                      fontsize=11, color='gray')
        self.fig.tight_layout()
    
    def plot_data(self, df: pd.DataFrame, avg_gpu: float, title: str = "GPU Load Analysis"):
        """데이터를 그래프로 표시"""
        self.axes.clear()
        
        # GPU 로드율 플롯
        self.axes.plot(df['Frame'], df['GPU%'], 
                      color='teal', linewidth=0.5, alpha=0.8, label='GPU Load')
        
        # 평균선 표시
        self.axes.axhline(avg_gpu, color='red', linestyle='--', 
                         label=f'Average ({avg_gpu:.1f}%)')
        
        # 그래프 스타일 설정
        self.axes.set_title(title, fontsize=12, fontweight='bold')
        self.axes.set_xlabel('Frame')
        self.axes.set_ylabel('GPU Load (%)')
        self.axes.set_ylim(0, 100)
        self.axes.legend(loc='upper right')
        self.axes.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        self.draw()


class CPULoadChart(FigureCanvas):
    """CPU 로드율 그래프를 표시하는 Matplotlib 캔버스"""
    
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(12, 4), dpi=100)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # 초기 빈 그래프 설정
        self._setup_empty_chart()
    
    def wheelEvent(self, event):
        """휠 이벤트를 부모로 전달"""
        event.ignore()
    
    
    def _setup_empty_chart(self):
        """빈 그래프 초기 설정"""
        self.axes.set_title('CPU Load Analysis', fontsize=12, fontweight='bold')
        self.axes.set_xlabel('Frame')
        self.axes.set_ylabel('CPU Load (%)')
        self.axes.set_ylim(0, 100)
        self.axes.grid(True, alpha=0.3)
        self.axes.text(0.5, 0.5, 'CSV 파일을 불러와주세요\n(Please load a CSV file)', 
                      transform=self.axes.transAxes, ha='center', va='center',
                      fontsize=11, color='gray')
        self.fig.tight_layout()
    
    def plot_data(self, df: pd.DataFrame, avg_cpu: float, title: str = "CPU Load Analysis"):
        """데이터를 그래프로 표시"""
        self.axes.clear()
        
        # CPU 로드율 플롯
        self.axes.plot(df['Frame'], df['CPU%'], 
                      color='#e67e22', linewidth=0.5, alpha=0.8, label='CPU Load')
        
        # 평균선 표시
        self.axes.axhline(avg_cpu, color='blue', linestyle='--', 
                         label=f'Average ({avg_cpu:.1f}%)')
        
        # 그래프 스타일 설정
        self.axes.set_title(title, fontsize=12, fontweight='bold')
        self.axes.set_xlabel('Frame')
        self.axes.set_ylabel('CPU Load (%)')
        self.axes.set_ylim(0, 100)
        self.axes.legend(loc='upper right')
        self.axes.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        self.draw()


class FPSAnalyzerWindow(QMainWindow):
    """FPS 분석기 메인 윈도우"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("1% Low FPS Analyzer for The Division 2 by InnovaNex")
        self.setMinimumSize(1000, 1000)
        
        # 스크롤 영역 설정
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll_area)
        
        # 메인 컨테이너 위젯
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        scroll_area.setWidget(container)
        
        # UI 구성 요소 생성
        self._create_file_section(main_layout)
        self._create_fps_chart_section(main_layout)  # 하위 1% FPS 차트 (위쪽)
        self._create_gpu_chart_section(main_layout)  # GPU 로드 차트
        self._create_gpu_stats_section(main_layout)   # GPU 통계
        self._create_cpu_chart_section(main_layout)  # CPU 로드 차트
        self._create_cpu_stats_section(main_layout)   # CPU 통계
        
        # 스타일 적용
        self._apply_styles()
    
    def _create_file_section(self, parent_layout):
        """파일 선택 영역 생성"""
        file_group = QGroupBox("📁 파일 불러오기 (Load File)")
        file_layout = QHBoxLayout(file_group)
        
        # 파일 경로 입력 필드
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("CSV 파일 경로를 선택하세요 (Select CSV file path)...")
        self.file_path_edit.setReadOnly(True)
        
        # 파일 선택 버튼
        self.browse_btn = QPushButton("파일 선택\n(Select File)")
        self.browse_btn.setFixedWidth(120)
        self.browse_btn.clicked.connect(self._on_browse_clicked)
        
        # 분석 시작 버튼
        self.analyze_btn = QPushButton("분석 시작\n(Start Analysis)")
        self.analyze_btn.setFixedWidth(120)
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self._on_analyze_clicked)
        
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.browse_btn)
        file_layout.addWidget(self.analyze_btn)
        
        parent_layout.addWidget(file_group)
    
    def _create_fps_chart_section(self, parent_layout):
        """하위 1% FPS 막대 그래프 영역 생성"""
        fps_group = QGroupBox("📊 FPS 성능 지표 (FPS Performance Metrics) - Avg / 1% Low / 0.1% Low")
        fps_layout = QVBoxLayout(fps_group)
        
        self.fps_chart = FPSBarChart()
        self.fps_chart.setMinimumHeight(250)
        fps_layout.addWidget(self.fps_chart)
        
        parent_layout.addWidget(fps_group)
    
    def _create_gpu_chart_section(self, parent_layout):
        """GPU 로드 그래프 영역 생성"""
        chart_group = QGroupBox("📈 GPU Load 그래프 (GPU Load Chart)")
        chart_layout = QVBoxLayout(chart_group)
        
        self.gpu_chart = GPULoadChart()
        self.gpu_chart.setMinimumHeight(300)
        chart_layout.addWidget(self.gpu_chart)
        
        parent_layout.addWidget(chart_group)
    
    def _create_cpu_chart_section(self, parent_layout):
        """CPU 로드 그래프 영역 생성"""
        chart_group = QGroupBox("📉 CPU Load 그래프 (CPU Load Chart)")
        chart_layout = QVBoxLayout(chart_group)
        
        self.cpu_chart = CPULoadChart()
        self.cpu_chart.setMinimumHeight(300)
        chart_layout.addWidget(self.cpu_chart)
        
        parent_layout.addWidget(chart_group)
    
    def _create_gpu_stats_section(self, parent_layout):
        """통계 데이터 표시 영역 생성"""
        stats_group = QGroupBox("🔢 GPU 분석 결과 (GPU Analysis Results)")
        stats_layout = QHBoxLayout(stats_group)
        stats_layout.setSpacing(20)
        
        # 통계 라벨들
        self.gpu_avg_label = self._create_stat_widget("평균 GPU 로드율\n(Avg GPU Load)", "- %", "#3498db")
        self.gpu_stressed_label = self._create_stat_widget("풀로드 구간 (90%↑)\n(Stressed >90%)", "- %", "#e74c3c")
        self.gpu_chilling_label = self._create_stat_widget("저부하 구간 (50%↓)\n(Chilling <50%)", "- %", "#2ecc71")
        self.total_frames_label = self._create_stat_widget("총 프레임 수\n(Total Frames)", "-", "#9b59b6")
        
        stats_layout.addWidget(self.gpu_avg_label)
        stats_layout.addWidget(self.gpu_stressed_label)
        stats_layout.addWidget(self.gpu_chilling_label)
        stats_layout.addWidget(self.total_frames_label)
        
        parent_layout.addWidget(stats_group)
    
    def _create_cpu_stats_section(self, parent_layout):
        """CPU 통계 데이터 표시 영역 생성"""
        stats_group = QGroupBox("🔢 CPU 분석 결과 (CPU Analysis Results)")
        stats_layout = QHBoxLayout(stats_group)
        stats_layout.setSpacing(20)
        
        # CPU 통계 라벨들
        self.cpu_avg_label = self._create_stat_widget("평균 CPU 로드율\n(Avg CPU Load)", "- %", "#e67e22")
        self.cpu_stressed_label = self._create_stat_widget("고부하 구간 (70%↑)\n(High Load >70%)", "- %", "#e74c3c")
        self.cpu_chilling_label = self._create_stat_widget("저부하 구간 (30%↓)\n(Low Load <30%)", "- %", "#2ecc71")
        self.cpu_max_label = self._create_stat_widget("최대 CPU 로드율\n(Max CPU Load)", "- %", "#9b59b6")
        
        stats_layout.addWidget(self.cpu_avg_label)
        stats_layout.addWidget(self.cpu_stressed_label)
        stats_layout.addWidget(self.cpu_chilling_label)
        stats_layout.addWidget(self.cpu_max_label)
        
        parent_layout.addWidget(stats_group)
    
    def _create_stat_widget(self, title: str, value: str, color: str) -> QWidget:
        """개별 통계 위젯 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 12px; color: #666;")
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        value_label.setObjectName("value_label")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return widget
    
    def _apply_styles(self):
        """전역 스타일 적용"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #ffffff;
                color: #000000;
            }
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #ffffff;
            }
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                top: 3px;
                padding: 0 8px;
                background-color: white;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
                background-color: #fafafa;
            }
        """)
    
    def _on_browse_clicked(self):
        """파일 선택 버튼 클릭 핸들러"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "CSV 파일 선택 (Select CSV File)",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
            self.analyze_btn.setEnabled(True)
    
    def _on_analyze_clicked(self):
        """분석 시작 버튼 클릭 핸들러"""
        file_path = self.file_path_edit.text()
        
        if not file_path:
            QMessageBox.warning(self, "경고 (Warning)", "먼저 CSV 파일을 선택해주세요.\n(Please select a CSV file first.)")
            return
        
        try:
            # 데이터 로드 (헤더 2줄 스킵)
            df = pd.read_csv(file_path, skiprows=2)
            df.columns = [c.strip() for c in df.columns]
            
            # 필수 컬럼 확인
            if 'GPU%' not in df.columns or 'Time 0.1mS' not in df.columns:
                QMessageBox.critical(self, "오류 (Error)", "CSV 파일에 'GPU%' 또는 'Time 0.1mS' 컬럼이 없습니다.\n(Missing 'GPU%' or 'Time 0.1mS' columns in CSV.)")
                return
            
            # FPS 계산
            df['frametime_ms'] = df['Time 0.1mS'] * 0.1
            df['fps'] = 1000 / df['frametime_ms']
            
            # FPS 지표 계산
            avg_fps = df['fps'].mean()
            low_1_percent = df['fps'].quantile(0.01)
            low_01_percent = df['fps'].quantile(0.001)
            
            # GPU 분석 수행
            avg_gpu = df['GPU%'].mean()
            stressed_percent = (len(df[df['GPU%'] > 90]) / len(df)) * 100
            chilling_percent = (len(df[df['GPU%'] < 50]) / len(df)) * 100
            total_frames = len(df)
            
            # FPS 막대 그래프 업데이트
            self.fps_chart.plot_data(avg_fps, low_1_percent, low_01_percent)
            
            # GPU 로드 그래프 업데이트
            self.gpu_chart.plot_data(df, avg_gpu)
            
            # CPU 분석 및 그래프 업데이트
            if 'CPU%' in df.columns:
                avg_cpu = df['CPU%'].mean()
                self.cpu_chart.plot_data(df, avg_cpu)
            
            # GPU 통계 라벨 업데이트
            self._update_stat_value(self.gpu_avg_label, f"{avg_gpu:.1f}%")
            self._update_stat_value(self.gpu_stressed_label, f"{stressed_percent:.1f}%")
            self._update_stat_value(self.gpu_chilling_label, f"{chilling_percent:.1f}%")
            self._update_stat_value(self.total_frames_label, f"{total_frames:,}")
            
            # CPU 통계 라벨 업데이트
            if 'CPU%' in df.columns:
                cpu_stressed = (len(df[df['CPU%'] > 70]) / len(df)) * 100
                cpu_chilling = (len(df[df['CPU%'] < 30]) / len(df)) * 100
                cpu_max = df['CPU%'].max()
                self._update_stat_value(self.cpu_avg_label, f"{avg_cpu:.1f}%")
                self._update_stat_value(self.cpu_stressed_label, f"{cpu_stressed:.1f}%")
                self._update_stat_value(self.cpu_chilling_label, f"{cpu_chilling:.1f}%")
                self._update_stat_value(self.cpu_max_label, f"{cpu_max:.1f}%")
            
        except Exception as e:
            QMessageBox.critical(self, "오류 (Error)", f"파일 분석 중 오류가 발생했습니다 (Error during analysis):\n{str(e)}")
    
    def _update_stat_value(self, widget: QWidget, value: str):
        """통계 위젯의 값 업데이트"""
        value_label = widget.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(value)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    
    window = FPSAnalyzerWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

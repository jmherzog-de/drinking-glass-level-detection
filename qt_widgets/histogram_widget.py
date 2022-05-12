from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtWidgets import QWidget, QVBoxLayout
import numpy as np
import cv2


class HistogramWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.central_layout = QVBoxLayout(self)
        self.central_layout.setObjectName(u"central_layout")

        self.hist_chart = QChart()
        self.hist_chart.setObjectName(u"hist_chart")
        self.hist_chart.setAnimationOptions(QChart.NoAnimation)

        self.cum_hist_chart = QChart()
        self.cum_hist_chart.setObjectName(u"cum_hist_chart")
        self.cum_hist_chart.setAnimationOptions(QChart.NoAnimation)

        # Setting X-Axis for Histogram Chart
        self.hist_x_axis = QValueAxis()
        self.hist_x_axis.setMin(0)
        self.hist_x_axis.setMax(65535)
        self.hist_x_axis.setTitleText(u"Pixel Value")
        self.hist_chart.addAxis(self.hist_x_axis, Qt.AlignBottom)

        # Setting Y-Axis for Histogram Chart
        self.hist_y_axis = QValueAxis()
        self.hist_y_axis.setTickCount(10)
        self.hist_y_axis.setMin(0.0)
        self.hist_y_axis.setTitleText(u"N Pixels")
        self.hist_chart.addAxis(self.hist_y_axis, Qt.AlignLeft)

        # Add ChartView to Histogram Chart
        self.histogram = QChartView(self.hist_chart)
        self.histogram.setRenderHint(QPainter.Antialiasing)
        self.central_layout.addWidget(self.histogram)

        # Setting X-Axis for Cumulative Histogram Chart
        self.cum_hist_x_axis = QValueAxis()
        self.cum_hist_x_axis.setMin(0)
        self.cum_hist_x_axis.setMin(65535)
        self.cum_hist_x_axis.setTitleText(u"Pixel Value")
        self.cum_hist_chart.addAxis(self.cum_hist_x_axis, Qt.AlignBottom)

        # Setting Y-Axis for Cumulative Histogram Chart
        self.cum_hist_y_axis = QValueAxis()
        self.cum_hist_y_axis.setMin(0.0)
        self.cum_hist_y_axis.setMax(1.0)
        self.hist_y_axis.setTitleText(u"p")
        self.cum_hist_chart.addAxis(self.cum_hist_y_axis, Qt.AlignLeft)

        # Add ChartView to Cumulative Histogram Chart
        self.cum_histogram = QChartView(self.cum_hist_chart)
        self.cum_histogram.setRenderHint(QPainter.Antialiasing)
        self.central_layout.addWidget(self.cum_histogram)

    def add_histogram(self, name: str, image: np.ndarray):

        series = QLineSeries()
        series.setName(name)

        cum_series = QLineSeries()
        cum_series.setName(name)

        n_pixel = (image.shape[0] * image.shape[1])
        m = 64 if str(image.dtype) == "uint16" else 1
        bins = 65536 if str(image.dtype) == "uint16" else 256

        self.hist_x_axis.setMax(bins - 1)
        self.cum_hist_x_axis.setMax(bins - 1)

        hist = cv2.calcHist([image], [0], None, [bins // m], [0, bins])
        cum_hist = hist / n_pixel
        cum_hist = cum_hist.cumsum()

        for p, n in enumerate(hist):
            series.append(QPointF(p*m, n))

        for p, n in enumerate(cum_hist):
            cum_series.append(QPointF(p*m, n))

        self.hist_chart.addSeries(series)
        series.attachAxis(self.hist_x_axis)
        series.attachAxis(self.hist_y_axis)

        self.cum_hist_chart.addSeries(cum_series)
        cum_series.attachAxis(self.cum_hist_x_axis)
        cum_series.attachAxis(self.cum_hist_y_axis)

        y_max = self.hist_y_axis.max() if self.hist_y_axis.max() > hist.max() else hist.max()
        self.hist_y_axis.setMax(y_max)

    def update_histogram(self, name: str, image: np.ndarray):
        for series in self.hist_chart.series():
            if series.name() == name:
                self.hist_chart.removeSeries(series)
                break
        for series in self.cum_hist_chart.series():
            if series.name() == name:
                self.cum_hist_chart.removeSeries(series)
                break
        self.add_histogram(name, image)

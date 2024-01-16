import utils
from PySide6.QtWidgets import (QWidget, QSlider, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel)
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
import PySide6

class ClickSlider(QSlider):
    userInvokedValueChanged = Signal(int)

    def __init__(self):
        super().__init__()



    def mousePressEvent(self, event):
        super(ClickSlider, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            val = self.pixelPosToRangeValue(event.pos())
            self.setValue(val)
            self.userInvokedValueChanged.emit(val)

    # def mouseMoveEvent(self, event):
    #     x = event.pos().x()
    #     value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
    #     self.setValue(value)
    #     self.userInvokedValueChanged.emit(value)


    def pixelPosToRangeValue(self, pos):
        opt = PySide6.QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(PySide6.QtWidgets.QStyle.CC_Slider, opt, PySide6.QtWidgets.QStyle.SC_SliderGroove, self)
        sr = self.style().subControlRect(PySide6.QtWidgets.QStyle.CC_Slider, opt, PySide6.QtWidgets.QStyle.SC_SliderHandle, self)

        if self.orientation() == Qt.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1;
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == Qt.Horizontal else pr.y()
        return PySide6.QtWidgets.QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - sliderMin,
                                               sliderMax - sliderMin, opt.upsideDown)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            e.accept()
            x = e.pos().x()
            value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
            self.setValue(value)
            self.userInvokedValueChanged.emit(value)
        else:
            return super().mouseReleaseEvent(self, e)


class SeekBarWidget(QWidget):
    userInvokedValueChanged = Signal(int)

    def __init__(self):
        super().__init__()


        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.setSizePolicy(sizePolicy)


        self.layout = QHBoxLayout(self)

        self.seek_bar = ClickSlider()
        self.layout.addWidget(self.seek_bar)

        self.seek_bar.setOrientation(Qt.Horizontal)

        self.seek_bar.userInvokedValueChanged.connect(self.userInvokedValueChanged.emit)

        self.current_time_label = QLabel("0:00:00")
        self.total_time_label = QLabel("/ 0:00:00")
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.layout.addWidget(self.current_time_label)
        self.layout.addWidget(self.total_time_label)

    def set_offset(self, timeInMilliseconds):
        # self.seek_bar.setMinimum(timeInMilliseconds)
        # durationTime = self.seek_bar.maximum() - timeInMilliseconds
        # self.total_time_label.setText("/ " + utils.milliseconds_to_time_string(durationTime))
        pass

    def set_duration(self, timeInMilliseconds):
        self.seek_bar.setMaximum(timeInMilliseconds)
        self.total_time_label.setText("/ " + utils.milliseconds_to_time_string(timeInMilliseconds - self.seek_bar.minimum()))

    def set_current_time(self, timeInMilliseconds):
        self.seek_bar.setValue(timeInMilliseconds)
        self.current_time_label.setText(utils.milliseconds_to_time_string(timeInMilliseconds))


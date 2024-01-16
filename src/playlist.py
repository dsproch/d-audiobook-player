from PySide6.QtWidgets import (QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QLabel)

from PySide6.QtCore import Signal

from PySide6 import QtGui

import subprocess
import json

import utils

import os


def probe_file(filename):
    cmnd = ['ffprobe', '-show_entries', 'format', '-show_entries', 'chapters', '-print_format', 'json', '-v', 'quiet', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()

    myJson = json.loads(out)
    return myJson


class PlaylistWidget(QWidget):
	playingItemChanged = Signal()

	def __init__(self):
		super().__init__()

		self.layout = QVBoxLayout(self)
		self.treeWidget = QTreeWidget()
		self.layout.addWidget(self.treeWidget)

		self.playingIndex = -1

		self.treeWidget.setColumnCount(2)
		self.treeWidget.setHeaderLabels(["Name", "Duration"])


		self.current_time_label = QLabel("0:00:00")
		self.total_time_label = QLabel("/ 0:00:00")



		self.treeWidget.itemDoubleClicked.connect(self._change_current_item)

	def _change_current_item(self, treeItem, colNum):
		topLevelIndexValue = self.treeWidget.indexOfTopLevelItem(treeItem)

		self._set_playing_index(topLevelIndexValue)

	def add_file(self, path, duration):
		probeJson = probe_file(path.toString())
		timeInSeconds = float(probeJson["format"]["duration"])
		h = int(timeInSeconds // 3600)
		m = int(timeInSeconds % 3600 // 60)
		s = int(timeInSeconds % 3600 % 60)


		treeItem = QTreeWidgetItem(self.treeWidget, [os.path.basename(path.toString()), '{:d}:{:02d}:{:02d}'.format(h,m,s)])
		treeItem.filePath = path.toString()

		self.treeWidget.addTopLevelItem(treeItem)


	def _set_playing_index(self, newIndexValue, emit=True):

		treeItem = self.treeWidget.topLevelItem(self.playingIndex)
		self._clear_formatting_on_item(treeItem)

		self.playingIndex = newIndexValue

		treeItem = self.treeWidget.topLevelItem(self.playingIndex)
		self._mark_formatting_on_item(treeItem)

		if emit:
			self.playingItemChanged.emit()

	def _clear_formatting_on_item(self, treeItem):
		if treeItem:
			# treeItem.setBackground(0, QtGui.QBrush())
			treeItem.setFont(0, QtGui.QFont())
	def _mark_formatting_on_item(self, treeItem):
		if treeItem:
			# treeItem.setBackground(0, QtGui.QBrush(QtGui.QColor("red")))
			font = QtGui.QFont()
			font.setBold(True)
			treeItem.setFont(0, font)

	def get_current(self):
		if self.playingIndex < 0:
			print("PlaylistWidget::_set_playing_index():: NO CURRENT INDEX")
			return None
		url =  self.treeWidget.topLevelItem(self.playingIndex).filePath
		return url


	def select_next(self):
		if self.playingIndex + 1 < self.treeWidget.topLevelItemCount():
			self._set_playing_index(self.playingIndex + 1)





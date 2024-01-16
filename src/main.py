import sys
import PySide6
from PySide6.QtCore import QStandardPaths, Qt, Slot, QUrl
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (QWidget, QApplication, QDialog, QFileDialog,
    QMainWindow, QSlider, QStyle, QToolBar, QSplitter, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy)
from PySide6.QtMultimedia import (QAudioOutput, QMediaFormat,
                                  QMediaPlayer)
from PySide6.QtMultimediaWidgets import QVideoWidget


from playlist import PlaylistWidget
from PySide6.QtCore import Signal
import time

from seekBarWidget import SeekBarWidget





class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self._audio_output = QAudioOutput()
        self._player = QMediaPlayer()
        self._player.setAudioOutput(self._audio_output)

        # ToolBar
        self._tool_bar = QToolBar("Quick Action Toolbar")
        self.addToolBar(self._tool_bar)

        # MenuBar >> File
        file_menu = self.menuBar().addMenu("&File")

        # MenuBar >> File >> Open
        icon = QIcon.fromTheme("document-open")
        open_action = QAction(icon, "&Open...", self, shortcut=QKeySequence.Open, triggered=self.open)
        file_menu.addAction(open_action)
        self._tool_bar.addAction(open_action)

        # MenuBar >> File >> Exit
        icon = QIcon.fromTheme("application-exit")
        exit_action = QAction(icon, "E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        file_menu.addAction(exit_action)

        # MenuBar >> Play
        play_menu = self.menuBar().addMenu("&Play")

        # MenuBar >> Play >> Play
        icon = QIcon.fromTheme("media-playback-start")
        # icon = QIcon.fromTheme("media-playback-start.png", style.standardIcon(QStyle.SP_MediaPlay))
        play_action = self._tool_bar.addAction(icon, "Play")
        play_action.triggered.connect(self.play)
        play_menu.addAction(play_action)

        # MenuBar >> Play >> Pause
        icon = QIcon.fromTheme("media-playback-pause.png", self.style().standardIcon(QStyle.SP_MediaPause))
        pause_action = self._tool_bar.addAction(icon, "Pause")
        pause_action.triggered.connect(self._player.pause)
        play_menu.addAction(pause_action)


        # Central Widget
        self._centralWidget = QWidget()
        self.setCentralWidget(self._centralWidget)
        self._central_vertical_box_layout = QVBoxLayout(self._centralWidget)

        main_splitter = QSplitter(self._centralWidget)
        main_splitter.setOrientation(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(True)
        self._central_vertical_box_layout.addWidget(main_splitter)

        # Left Frame
        left_frame = QFrame(main_splitter)
        left_frame.setFrameShape(QFrame.Box)
        left_frame_layout = QVBoxLayout(left_frame)

        # Right Frame
        right_frame = QFrame(main_splitter)
        right_frame_layout = QVBoxLayout(right_frame)

        main_splitter.addWidget(left_frame)
        main_splitter.addWidget(right_frame)




        # Primary Tools
        self.primary_seek_slider = SeekBarWidget()
        self._central_vertical_box_layout.addWidget(self.primary_seek_slider)

        self._playlist = PlaylistWidget()
        right_frame_layout.addWidget(self._playlist)




        # MISC, Possibly misplaced items, find a better home for them
        self._player.durationChanged.connect(self._update_duration)
        self._player.positionChanged.connect(self.update_seekbar)

        self.primary_seek_slider.userInvokedValueChanged.connect(self.seekValueHandler)

        self._playlist.playingItemChanged.connect(self._handle_playing_item_change)
        self._player.mediaStatusChanged.connect(self._handle_media_status_change)
        self._play_queued = False
        self._player.errorOccurred.connect(self._player_error)

    @Slot("QMediaPlayer::Error", str)
    def _player_error(self, error, error_string):
        print(error_string, file=sys.stderr)


    def seekValueHandler(self, value):
        # if abs(value - self._player.position()) >= 1000:
        #     print("seekValueHandler:: value = ", value)
        self._player.setPosition(value)

    def update_seekbar(self, seekPos):
        self.primary_seek_slider.set_current_time(seekPos)


    def _handle_media_status_change(self, mediaStatus):

        print(mediaStatus)

        if mediaStatus == QMediaPlayer.EndOfMedia:
            self.play()

        # if self._play_queued and mediaStatus == QMediaPlayer.LoadingMedia:
        #     print("Media is being loaded, and so cannot be played yet...")

        if self._play_queued and mediaStatus == QMediaPlayer.LoadedMedia:
            # print("loadedMedia and play_queued, so play current...")
            self.play_current()

        # # if self._play_queued and (mediaStatus == QMediaPlayer.BufferedMedia or mediaStatus == QMediaPlayer.LoadedMedia):
        #     pass
    @Slot()
    def _handle_playing_item_change(self):
        # print("_handle_playing_item_change():: aa ", self._player.mediaStatus(), self._player.playbackState())
        if self._player.playbackState() != QMediaPlayer.StoppedState:
            self._ensure_stopped()
        url = self._playlist.get_current()
        if url:
            time.sleep(.1)  # Sleep before seting source, to ensure that QMediaPlayer has processed everything it needs to
            self._player.setSource(url)
            self.play()




    @Slot()
    def _ensure_stopped(self):
        if self._player.playbackState() != QMediaPlayer.StoppedState:
            self._player.stop()



    def _update_duration(self, value):
        self._update_primary_duration(value)

    def _update_primary_duration(self, value):
        self.primary_seek_slider.set_duration(value)


    def play_current(self):
        self._play_queued = True
        if self._player.playbackState() == QMediaPlayer.StoppedState:
            if self._player.mediaStatus() == QMediaPlayer.LoadingMedia:
                return
            elif self._player.mediaStatus() == QMediaPlayer.LoadedMedia:
                self._player.play()
                self._play_queued = False

        elif self._player.playbackState() == QMediaPlayer.PlayingState:
            self._play_queued = False
        elif self._player.playbackState() == QMediaPlayer.PausedState:
            self._player.play()
            self._play_queued = False



    @Slot()
    def play(self):
        if self._player.mediaStatus() == QMediaPlayer.NoMedia or self._player.mediaStatus() == QMediaPlayer.EndOfMedia:
            self._ensure_stopped()
            self._playlist.select_next()
        else:
            self.play_current()


    @Slot()
    def open(self):

        file_dialog = QFileDialog(self)
        if file_dialog.exec() == QDialog.Accepted:

            url = file_dialog.selectedUrls()[0]

            self._playlist.add_file(url, self._player.duration())



    def play_next_file(self):
        self._playlist.select_next()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    available_geometry = main_win.screen().availableGeometry()
    main_win.resize(available_geometry.width() / 3,
                    available_geometry.height() / 2)
    main_win.show()
    sys.exit(app.exec())

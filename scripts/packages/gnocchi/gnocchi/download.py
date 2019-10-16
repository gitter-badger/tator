from PyQt5.QtCore import QObject, pyqtSignal,pyqtSlot
import os
import os.path
import pathlib

import logging
import time

class Download(QObject):
    """ Background thread to handle copying directories """

    progress = pyqtSignal(str, int)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)
    _trigger = pyqtSignal()

    def __init__(self, tator, mediaList, outputDirectory):
        super(Download, self).__init__()
        self.tator = tator
        self.output_dir = outputDirectory
        self.mediaList = mediaList
        self._trigger.connect(self._process)
        self._terminated=True

    def start(self):
        self._terminated=False
        self._trigger.emit()

    def stop(self):
        self._terminated=True

    @pyqtSlot()
    def _process(self):
        idx = 0
        for media in self.mediaList:
            self.progress.emit(media['name'], idx)
            time.sleep(0.1)
            idx += 1
            if self._terminated:
                return
        self.finished.emit(len(self.mediaList))

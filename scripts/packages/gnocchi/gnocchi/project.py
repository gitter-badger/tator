import argparse
import sys
import logging

import pytator
import os

# QT Imports
from PyQt5 import Qt,QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSlot
from gnocchi.ui_project import Ui_Project
from gnocchi.ui_projectDetail import Ui_ProjectDetail
from gnocchi.download import Download
import qdarkstyle

DIRNAME = os.path.dirname(os.path.abspath(__file__))
QT_ICON_PATH = os.path.join(DIRNAME, 'assets', 'cvision_no_text.ico')
QT_DOWNLOAD_PATH = os.path.join(DIRNAME, 'assets', 'download.svg')
QT_UPLOAD_PATH = os.path.join(DIRNAME, 'assets', 'upload.svg')

class ProjectDetail(QtWidgets.QWidget):
    def __init__(self, parent, backgroundThread, url, token, projectId):
        super(ProjectDetail, self).__init__(parent)
        self.background_thread = backgroundThread
        self.ui = Ui_ProjectDetail()
        self.ui.setupUi(self)
        self.project_id = projectId
        self.tator = pytator.Tator(url,
                                   token,
                                   self.project_id)
        self.ui.sectionTree.setHeaderLabel("Media Files")
        # Enable multiple selections
        self.ui.sectionTree.setSelectionMode(QtWidgets.QTreeWidget.MultiSelection)

        self.ui.downloadBtn.setIcon(QtGui.QIcon(QT_DOWNLOAD_PATH))
        self.ui.uploadBtn.setIcon(QtGui.QIcon(QT_UPLOAD_PATH))

        #Disable upload button for now
        self.ui.uploadBtn.setEnabled(False)
        self.ui.downloadBtn.setEnabled(False)

        self.ui.sectionTree.itemSelectionChanged.connect(self.onSelectionChanged)
    @pyqtSlot()
    def onSelectionChanged(self):
        selected_items = self.ui.sectionTree.selectedItems()
        if len(selected_items):
            self.ui.downloadBtn.setEnabled(True)
        else:
            self.ui.downloadBtn.setEnabled(False)

    @pyqtSlot()
    def on_downloadBtn_clicked(self):
        selected_items = self.ui.sectionTree.selectedItems()
        download_list = []
        def addSelfAndChildren(obj):
            if obj.data(0,0x100):
                download_list.append(obj.data(0,0x100))
            for child_idx in range(obj.childCount()):
                addSelfAndChildren(obj.child(child_idx))

        for item in selected_items:
            addSelfAndChildren(item)

        file_count = len(download_list)
        logging.info(f"Selected {file_count} for download.")

        my_documents=Qt.QStandardPaths.writableLocation(
            Qt.QStandardPaths.DocumentsLocation)
        output_directory=QtWidgets.QFileDialog.getExistingDirectory(
            self,
            f"Save {file_count} Files to...",
            my_documents)

        if output_directory:
            logging.info(f"Saving to {output_directory}")
            self.download = Download(self.tator,
                                     download_list,
                                     output_directory)
            self.download.progress.connect(self.download_progress)
            self.download.finished.connect(self.download_finished)
            self.download.moveToThread(self.background_thread)
            self.download_dialog = QtWidgets.QProgressDialog(
                "Downloading project...",
                "Cancel",
                0,
                file_count,
                self)
            self.download.start()
            self.download_dialog.setMinimumDuration(0)
            self.download_dialog.setValue(0)
            self.download_dialog.canceled.connect(self.download_stopped)

    @pyqtSlot()
    def download_stopped(self):
        logging.info("Stopping download")
        self.download.stop()
        self.download_dialog.reset()

    @pyqtSlot(str, int)
    def download_progress(self, filename, idx):
        logging.info(f"Got download progress @ {idx}")
        self.download_dialog.setValue(idx)
        self.download_dialog.setLabelText(filename)

    @pyqtSlot(int)
    def download_finished(self, idx):
        logging.info("Download complete")
        self.download_dialog.reset()

    def refreshProjectData(self):
        project_data=self.tator.Project.get(self.project_id)
        self.ui.sectionTree.clear()
        self.sections = {}
        for section in project_data['section_order']:
            section_tree = QtWidgets.QTreeWidgetItem(self.ui.sectionTree)
            section_tree.setText(0,section)
            self.sections.update({section: {'widget': section_tree}})
            self.ui.sectionTree.addTopLevelItem(section_tree)

        self.parentWidget().repaint()
        number_of_sections = len(project_data['section_order'])
        progress_dialog = QtWidgets.QProgressDialog("Loading project...",
                                                    "Cancel",
                                                    0,
                                                    number_of_sections,
                                                    self)

        progress_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        idx = 1
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)
        for section in project_data['section_order']:
            medias = self.tator.Media.filter({"attribute":
                                              f"tator_user_sections::{section}"})
            section_tree = self.sections[section]['widget']
            self.sections[section]['medias'] = []
            if medias is None:
                continue
            for media in medias:
                media_item = QtWidgets.QTreeWidgetItem(section_tree)
                media_item.setData(0,0x100,media)
                self.sections[section]['medias'].append(media_item)
                media_item.setText(0,media['name'])
            section_tree.addChildren(self.sections[section]['medias'])

            # Handle progress dialog
            progress_dialog.setValue(idx)
            idx += 1
            self.parentWidget().repaint()
            progress_dialog.repaint()



    def showEvent(self, evt):
        super(ProjectDetail, self).showEvent(evt)
        QtCore.QTimer.singleShot(50,self.refreshProjectData)

class Project(QtWidgets.QMainWindow):
    def __init__(self):
        super(Project, self).__init__()
        self.ui = Ui_Project()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(QT_ICON_PATH))

        # hide tab stuff at first
        self.ui.tabWidget.setVisible(False)
        self.adjustSize()
        self.background_thread=QtCore.QThread(self)
        self.background_thread.start()


    @pyqtSlot()
    def on_actionExit_triggered(self):
        self.close()

    @pyqtSlot()
    def on_connectBtn_clicked(self):
        token=pytator.Auth.getToken('https://cvision.tatorapp.com/rest',
                                    self.ui.username_field.text(),
                                    self.ui.password_field.text())
        if token is None:
            logging.warning("Bad user credentials")
        else:
            self.ui.login_widget.setVisible(False)

            tator=pytator.Tator('https://cvision.tatorapp.com/rest',
                                token,
                                None)
            projects=tator.Project.all()
            # TODO landing page
            self.ui.tabWidget.addTab(QtWidgets.QWidget(self), "Welcome")
            for project in projects:
                self.ui.tabWidget.addTab(
                    ProjectDetail(self,
                                  self.background_thread,
                                  'https://cvision.tatorapp.com/rest',
                                  token,
                                  project['id']),
                    project['name'])
            self.ui.tabWidget.setVisible(True)
            self.adjustSize()
            screenGeometry = QtWidgets.QApplication.desktop().screenGeometry()
            marginLeft = (screenGeometry.width() - self.width()) / 2
            marginRight = (screenGeometry.height() - self.height()) / 2
            self.move(marginLeft, marginRight)

def start():
    parser = argparse.ArgumentParser(description='Gnocchi --- The PyTator GUI')
    parser.add_argument('--theme', default='dark',
                        choices=['dark', 'light'])
    args = parser.parse_args()
    """ Starts the camera control UI """
    app = QtWidgets.QApplication(sys.argv)
    if args.theme == 'dark':
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = Project()
    screenGeometry = QtWidgets.QApplication.desktop().screenGeometry()
    marginLeft = (screenGeometry.width() - window.width()) / 2
    marginRight = (screenGeometry.height() - window.height()) / 2
    window.move(marginLeft, marginRight)
    window.show()
    sys.exit(app.exec())

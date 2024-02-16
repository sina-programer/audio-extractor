from PyQt5 import QtGui, QtWidgets, QtCore
from moviepy import editor
import configparser
import webbrowser
import sys
import os


class AboutDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setup_Ui()

    def setup_Ui(self):
        self.setWindowTitle("About us")
        self.setWindowIcon(QtGui.QIcon(ICON_PATH))
        self.setFixedSize(300, 100)

        description = QtWidgets.QLabel(self)
        description.setGeometry(75, 10, 150, 30)
        description.setText("This program made by Sina.F")


        horizontal_frame = QtWidgets.QWidget(self)
        horizontal_frame.setGeometry(50, 50, 200, 40)

        horizontal_layout = QtWidgets.QHBoxLayout(horizontal_frame)
        horizontal_layout.setContentsMargins(0, 0, 0, 0)
        horizontal_layout.setSpacing(15)

        btn_github = QtWidgets.QPushButton(horizontal_frame)
        btn_github.clicked.connect(lambda: webbrowser.open('https://github.com/sina-programer'))
        btn_github.setText("GitHub")
        horizontal_layout.addWidget(btn_github)

        btn_telegram = QtWidgets.QPushButton(horizontal_frame)
        btn_telegram.clicked.connect(lambda: webbrowser.open('https://t.me/sina_programer'))
        btn_telegram.setText("Telegram")
        horizontal_layout.addWidget(btn_telegram)


class SettingDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Setting")
        self.setFixedSize(250, 170)

        self.centralwidget = QtWidgets.QWidget(self)


        self.gridWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridWidget.setGeometry(QtCore.QRect(20, 10, 200, 150))

        self.gridLayout = QtWidgets.QGridLayout(self.gridWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)


        self.label_fps = QtWidgets.QLabel(self.gridWidget)
        self.label_fps.setText('FPS: ')
        self.gridLayout.addWidget(self.label_fps, 1, 0, 1, 1)

        self.lineEdit_fps = QtWidgets.QLineEdit(self.gridWidget)
        self.gridLayout.addWidget(self.lineEdit_fps, 1, 1, 1, 1)


        self.label_bitrate = QtWidgets.QLabel(self.gridWidget)
        self.label_bitrate.setText('Bitrate: ')
        self.gridLayout.addWidget(self.label_bitrate, 2, 0, 1, 1)

        self.lineEdit_bitrate = QtWidgets.QLineEdit(self.gridWidget)
        self.gridLayout.addWidget(self.lineEdit_bitrate, 2, 1, 1, 1)


        self.pushButton_reload = QtWidgets.QPushButton(self.gridWidget)
        self.pushButton_reload.setText('Reload')
        self.pushButton_reload.clicked.connect(self.reload)
        self.gridLayout.addWidget(self.pushButton_reload, 3, 0, 1, 1)

        self.pushButton_submit = QtWidgets.QPushButton(self.gridWidget)
        self.pushButton_submit.setText('Submit')
        self.pushButton_submit.clicked.connect(self.submit)
        self.gridLayout.addWidget(self.pushButton_submit, 3, 1, 1, 1)


        self.reload()

    def get_dict(self):
        return {
            'fps': self.lineEdit_fps.text(),
            'bitrate': self.lineEdit_bitrate.text()
        }

    def reload(self):
        parser = configparser.ConfigParser()
        parser.read(CONFIGS_PATH)
        configs = dict(parser['Audio'])

        self.lineEdit_fps.setText(configs['fps'])
        self.lineEdit_bitrate.setText(configs['bitrate'])

    def submit(self):
        if QtWidgets.QMessageBox.question(self, 'Submit', 'Are sure to save new configs?') == 16384:  # No=65536, Yes=16384
            parser = configparser.ConfigParser()
            parser.read_dict({'Audio': self.get_dict()})
            with open(CONFIGS_PATH, 'w') as handler:
                parser.write(handler)

            QtWidgets.QMessageBox.information(self, 'Submit', 'The new settings have set')


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.aboutDialog = AboutDialog()
        self.setup_Ui()
        self.show()

    def setup_Ui(self):
        self.setWindowTitle("Audio Extractor")
        self.setWindowIcon(QtGui.QIcon(ICON_PATH))
        self.setFixedSize(550, 90)

        browse_btn = QtWidgets.QPushButton(self)
        browse_btn.setGeometry(20, 40, 80, 30)
        browse_btn.setText("Browse")
        browse_btn.clicked.connect(self.browse)

        self.video_path = QtWidgets.QLineEdit(self)
        self.video_path.setGeometry(110, 45, 300, 20)
        self.video_path.setReadOnly(True)
        self.video_path.setPlaceholderText("Video path")

        extract_btn = QtWidgets.QPushButton(self)
        extract_btn.setGeometry(430, 40, 100, 30)
        extract_btn.setText("Extract Audio")
        extract_btn.clicked.connect(self.extract_audio)

        self.init_menu()

    def extract_audio(self):
        parser = configparser.ConfigParser()
        parser.read(CONFIGS_PATH)
        options = dict(parser['Audio'])
        options['fps'] = int(options['fps'])

        path = self.video_path.text()
        if path:
            save_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Audio File', '', "Audio Files (*.mp3)")
            if save_path:
                video = editor.VideoFileClip(path)
                video.audio.write_audiofile(save_path, **options)
                video.close()

                QtWidgets.QMessageBox.information(self, 'Audio Extracted', '\nAudio of your file successfully exported!\t\n')

        else:
            QtWidgets.QMessageBox.critical(self, 'ERROR', '\nPlease first load a video!\t\n')

    def browse(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Video File', '', "Video Files (*.mp4)")
        if path:
            path = os.path.normpath(path)
            self.video_path.setText(path)

    def init_menu(self):
        settingAction = QtWidgets.QAction('Setting', self)
        settingAction.triggered.connect(lambda: SettingDialog(self).exec_())

        aboutAction = QtWidgets.QAction('About us', self)
        aboutAction.triggered.connect(lambda: self.aboutDialog.exec_())

        menu = self.menuBar()
        menu.addAction(settingAction)
        menu.addAction(aboutAction)



ICON_PATH = 'icon.ico'
CONFIGS_PATH = os.path.expanduser(r'~\audio-extractor-configs.ini')
DEFAULT_CONFIGS = {
    'fps': '44100',
    'bitrate': '160K',
}

if not os.path.exists(CONFIGS_PATH):
    parser = configparser.ConfigParser()
    parser.read_dict({'Audio': DEFAULT_CONFIGS})
    with open(CONFIGS_PATH, 'w') as handler:
        parser.write(handler)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()

    sys.exit(app.exec_())

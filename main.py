import sys
import time
from threading import Thread
import multiprocessing as mp
from assistant import Assistant
from uiapp import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMenu, QWidget, QApplication, QMessageBox
from PyQt6.QtGui import QPen, QPainter, QColor, QIcon, QPalette, QShortcut, QKeySequence


class AssistantApplication(QMainWindow):
    MAX_PHRASES_QUANTITY = 3

    def __init__(self):
        super(AssistantApplication, self).__init__(parent=None)
        self.assist_condition = False
        self.assistant = Assistant()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._button_checker()

    def __setattr__(self, key, value):
        print("app set attr")
        if key == 'phrases':
            print("phr", value)
            # self.show_messages(value)

        object.__setattr__(self, key, value)

    def _button_checker(self):
        keyboard_event_button = QShortcut(QKeySequence('Enter'), self)
        keyboard_event_button.activated.connect(self.exec_assist)
        self.ui.pushButton.clicked.connect(self.exec_assist)

    def exec_assist(self):
        print(228, self.phrases)
        self.assist_condition = not self.assist_condition
        if self.assist_condition:
            self.process_assist = mp.Process(target=self.assistant.execute)
            self.process_assist.start()
            self.ui.pushButton.setText("Stop")
        else:
            self.process_assist.terminate()
            self.ui.pushButton.setText("Start")

    def show_messages(self, message):
        print(123)
        # if len(self.phrases) > self.MAX_PHRASES_QUANTITY:
        #     self.phrases = self.phrases[1:-0]
        # self.ui.__dict__['label_1'].setText('Test')
        # if not self.phrases:
        #     for i, phrase in enumerate(self.phrases):
        #         print(i)
        #         self.ui.__dict__[f"label_{i + 1}"].setText(phrase)
        print(1233)
        return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    assistantAppGUI = AssistantApplication()
    assistantAppGUI.show()
    sys.exit(app.exec())

    # assistant = assist.Assistant()
    # assistant.execute()
    # time.sleep(4)
    # assistant.change_breakout()
    # print(123)
    # assistant.recognize('посоветуй фильмы')   # если не работает микрофон, можно проверить другой функционал'''


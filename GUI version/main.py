from Draw_GUI import GUIApp
from PyQt5.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)
    GUI = GUIApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

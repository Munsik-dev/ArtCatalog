import sys, os
import sqlite3
from PyQt5  import QtCore, QtGui, QtWidgets
from beta3 import *
from AddWindow import *
from validator import Validator


class AddWindowWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.ui = Ui_Adding()
        self.ui.setupUi(self)
        self.setup_connection()
        self.Error_style = "background-color: #FFB3B3; color: black;"
        self.True_style = "background-color: #B3FFB3; color: black;"

    def setup_connection(self):
        """
        Функция с хранением всех подключений
        """
        self.ui.cancel_button.clicked.connect(self.cancel_windowAW)
        self.ui.clear_button.clicked.connect(self.clear_allAW)
        self.ui.add_button.clicked.connect(self.check_all)

    def cancel_windowAW(self):
        """
        Функция закрывает виджет и очищает все значения строк
        """
        self.close()
        self.clear_allAW()

    def clear_allAW(self):
        """
        Функция через цикл очищает весь текст и стили всех lineedit и label
        """
        a = [self.ui.name_lineedit, self.ui.data_lineedit, self.ui.comment_lineedit, 
             self.ui.path_lineedit, self.ui.data_label, self.ui.comment_label, 
             self.ui.name_label, self.ui.path_label, self.ui.label_finish]
        for line_edit in a:
            line_edit.clear()
            line_edit.setStyleSheet(None)

    def check_all(self):
        """
        Функция вызывает 3 функции, которые проверяют правильность ввода данных
        Дальше от результата обратывает это и изменяет стили и выводит ошибки
        """
        name_va, name_err = Validator.check_name(self.ui.name_lineedit.text())
        data_va, data_err = Validator.check_data(self.ui.data_lineedit.text())
        path_va, path_err = Validator.check_path(self.ui.path_lineedit.text())
        self.ui.comment_lineedit.setStyleSheet(self.True_style)

        if name_va:
            self.ui.name_lineedit.setStyleSheet(self.True_style)
            self.ui.name_label.setText(None)
        else:
            self.ui.name_lineedit.setStyleSheet(self.Error_style)
            self.ui.name_label.setText(name_err)

        if data_va:
            self.ui.data_lineedit.setStyleSheet(self.True_style)
            self.ui.data_label.setText(None)
        else:
            self.ui.data_lineedit.setStyleSheet(self.Error_style)
            self.ui.data_label.setText(data_err)

        if path_va:
            self.ui.path_lineedit.setStyleSheet(self.True_style)
            self.ui.path_label.setText(None)
        else:
            self.ui.path_lineedit.setStyleSheet(self.Error_style)
            self.ui.path_label.setText(path_err)

        if name_va and data_va and path_va:
            self.ui.label_finish.setStyleSheet(self.True_style)
            self.ui.label_finish.setText("  Запись успешно добавлена")
            return True
        else:
            self.ui.label_finish.setStyleSheet(self.Error_style)
            self.ui.label_finish.setText("  Не удалось добавить запись") 
            return False
    
class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self,parent)
        self.ui = Ui_ArtCatalog()
        self.ui.setupUi(self)
        self.add_window = None
        self.ui.pushButton.clicked.connect(self.open_add_window)
    
    def open_add_window(self):
        """
        Функция открывает виджет добавления записи.
        Если виджет уже открыт, то просто активирует его и выводит пользователю.
        """
        if self.add_window is None:
            self.add_window = AddWindowWidget()
            self.add_window.show()
        else:
            self.add_window.show()
        self.add_window.raise_()
        self.add_window.activateWindow()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
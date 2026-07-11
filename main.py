import sys, os, shutil
import sqlite3
import logging
from datetime import datetime
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PIL import Image
import io
from MainWindow import *
from AddWindow import *
from WatchWindow import *
from validator import Validator


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("ArtCatalog")

class AddWindowWidget(QtWidgets.QWidget):
    art_added = pyqtSignal()

    def __init__(self, db, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Adding()
        self.ui.setupUi(self)
        self.db = db
        self.setup_connection()
        self.Error_style = "background-color: #FFB3B3; color: black;"
        self.True_style = "background-color: #B3FFB3; color: black;"
        logger.info("Запущенно окно создания записей")

    def setup_connection(self):
        """
        Функция с хранением всех подключений
        """
        self.ui.cancel_button.clicked.connect(self.cancel_windowAW)
        self.ui.clear_button.clicked.connect(self.clear_allAW)
        self.ui.add_button.clicked.connect(self.add_entry)

    def add_entry(self):
        """
        Функция, проверяя правильность значений, копирует картинку 
        А так же отправляет запрос на создание записи в бд
        """
        if self.check_all():
            name = self.ui.name_lineedit.text()
            data = self.ui.data_lineedit.text()
            path = self.ui.path_lineedit.text()
            comment = self.ui.comment_lineedit.text()

            new_path, file_size = self.copy_image_to_storage(path, name)

            if new_path is None:
                return

            self.ui.add_button.setEnabled(False)
            self.db.add_art(name, comment, data, file_size, new_path)
            self.art_added.emit()
            logger.info(f"Добавлена запись: {name}")

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
        self.ui.add_button.setEnabled(True)

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
    
    def copy_image_to_storage(self, path, name):
        """
        Получает путь и имя, потом копирует фотографию в внутреннию папку
        И возвращает путь и размер
        """
        storage = "images"

        try:
            os.makedirs(storage, exist_ok=True)

            ext = os.path.splitext(path)[1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}{ext}"
            new_path = os.path.join(storage, filename)

            shutil.copy2(path, new_path)
            size = os.path.getsize(new_path)
            logger.info(f"Изображение скопированно")

            return new_path, size
        
        except  PermissionError:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Нет прав доступа к файлу или папке.")
            logger.error("Ошибка прав доступа")
            return None, 0

    
class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = Ui_ArtCatalog()
        self.ui.setupUi(self)
        self.setup_connection()
        self.db = ArtCatalogBD()
        self.add_window = None
        self.watch_window = None
        self.load_list()
        logger.info("Приложение запущено")

    def setup_connection(self):
        """
        Функция с хранением всех подключений
        """
        self.ui.pushButton.clicked.connect(self.open_add_window)
        self.ui.listWidget.itemDoubleClicked.connect(self.open_watch_window)
    
    def open_add_window(self):
        """
        Функция открывает виджет добавления записи.
        Если виджет уже открыт, то просто активирует его и выводит пользователю.
        """
        if self.add_window is None:
            self.add_window = AddWindowWidget(self.db)
            self.add_window.art_added.connect(self.load_list)
            self.add_window.show()
        else:
            self.add_window.show()
        self.add_window.raise_()
        self.add_window.activateWindow()

    def open_watch_window(self, item):
        """
        Функция открывает окно предосмотра.
        Если виджет уже открыт, то просто активирует его и выводит пользователю.
        """
        text = item.text()
        art_id = int(text[1:text.index("]")])

        if self.watch_window is not None:
            self.watch_window.close()

        self.watch_window = WatchWindowWidget(self.db, art_id)
        self.watch_window.art_updated.connect(self.load_list)
        self.watch_window.destroyed.connect(self.load_list)
        self.watch_window.show()
        self.watch_window.raise_()
        self.watch_window.activateWindow()

    def closeEvent(self, event):
        """
        Подтверждение завершения работы
        """
        reply = QtWidgets.QMessageBox.question(
        self, "Выход", "Вы уверены, что хотите выйти?",
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.db.close()
            logger.info("Приложение закрыто")
            event.accept()
        else:
            event.ignore()

    def load_list(self):
        """
        Функция очищает и обновляет лист с записями из бд,
        после чего автоматически заполняет его новыми записями
        """
        self.ui.listWidget.clear()
        arts = self.db.get_all_names()
        for art_id, name in arts:
            self.ui.listWidget.addItem(f"[{art_id}] {name}")
        logger.info("Перезагружен лист с записями")


class WatchWindowWidget(QtWidgets.QWidget):
    art_updated = pyqtSignal()

    def __init__(self, db, art_id, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.db = db
        self.art_id = art_id
        self.ui = Ui_WatchWindow()
        self.ui.setupUi(self)
        self.setup_connection()
        self.load_art()
        self.Error_style = "background-color: #FFB3B3; color: black;"
        self.True_style = "background-color: #B3FFB3; color: black;"
        logger.info("Запущено окно предосмотра")

    def setup_connection(self):
        """
        Функция с хранением всех подключений на будущее
        """
        self.ui.edit_pushbutton.clicked.connect(self.enable_edit)
        self.ui.save_pushButton.clicked.connect(self.save_changes)
        self.ui.delete_pushbutton.clicked.connect(self.delete_art)

    def load_art(self):
        """
        Загружает данные в поля ввода в окне предосмотр
        """
        art = self.db.get_art_by_id(self.art_id)
        if not art:
            QtWidgets.QMessageBox.warning(self, "Не найдено", f"Запись с ID {self.art_id} не найдена.")
            self.close()
            return  

        self.ui.name_lineedit.setText(art[1])
        self.ui.comment_lineedit.setText(art[2])
        self.ui.data_lineedit.setText(art[3])
        self.ui.path_lineedit.setText(art[5])
            
        try:
            pil_image = Image.open(art[5])
            
            label_size = self.ui.art_label.size()
            pil_image.thumbnail(
                (label_size.width(), label_size.height()), 
                Image.Resampling.LANCZOS)
            
            buffer = io.BytesIO()
            pil_image.save(buffer, format="PNG")
            buffer.seek(0)
            
            image = QtGui.QImage()
            image.loadFromData(buffer.read())
            buffer.close()
            pixmap = QtGui.QPixmap.fromImage(image)

            self.ui.art_label.setPixmap(pixmap)

        except FileNotFoundError:
            QtWidgets.QMessageBox.warning(self, "Ошибка", f"Файл изображения не найден:\n{art[5]}")
            logger.error("Изображения не обнаружено")
            self.ui.art_label.setText("Изображение не найдено")

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить изображение:\n{e}")
            logger.error("Ошибка загрузки изображения")
            self.ui.art_label.setText("Ошибка загрузки")
    
    def enable_edit(self):
        """
        Изменяет состояние полей для редакции названия, даты и тд.
        """
        self.ui.name_lineedit.setReadOnly(False)
        self.ui.comment_lineedit.setReadOnly(False)
        self.ui.data_lineedit.setReadOnly(False)

        self.ui.save_pushButton.setEnabled(True)
        self.ui.edit_pushbutton.setEnabled(False)

    def save_changes(self):
        """
        Проводит проверку введеных значений и сохраняет их в бд.
        Так же добавляет кнопкам стили
        """
        name = self.ui.name_lineedit.text()
        data = self.ui.data_lineedit.text()
        comment = self.ui.comment_lineedit.text()

        self.ui.comment_lineedit.setStyleSheet(self.True_style)
        self.ui.path_lineedit.setStyleSheet(self.True_style)

        name_va, name_err = Validator.check_name(name)
        data_va, data_err = Validator.check_data(data)

        if name_va:
            self.ui.name_lineedit.setStyleSheet(self.True_style)
            self.ui.name_label.setText(None)
        else:
            self.ui.name_lineedit.setStyleSheet(self.Error_style)
            self.ui.name_label.setText(name_err)
        
        if data_va:
            self.ui.data_lineedit.setStyleSheet(self.True_style)
            self.ui.data_window.setText(None)
        else:
            self.ui.data_lineedit.setStyleSheet(self.Error_style)
            self.ui.data_window.setText(data_err)

        if name_va and data_va:
            self.db.update_art(self.art_id, name, data, comment)
            self.art_updated.emit()
            self.ui.save_pushButton.setStyleSheet(self.True_style)
            self.ui.save_pushButton.setEnabled(False)
            logger.info(f"изменена запись с ID - {self.art_id}")

    def delete_art(self):
        """
        Функция для удаления записи
        """
        reply = QtWidgets.QMessageBox.question(
            self, "Удаление", "Вы уверены, что хотите удалить эту запись?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if reply != QtWidgets.QMessageBox.Yes:
            return
        
        try:
            art = self.db.get_art_by_id(self.art_id)
            if art and art[5]:
                file_path = art[5]
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info("Фотография удаленна")

        except OSError as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка", f"Не удалось удалить файл:\n{e}")
            logger.error("Ошибка удаления файла")

        try:
            self.db.delete_art(self.art_id)
            self.art_updated.emit()
            logger.info(f"запись с ID - {self.art_id} удаленна")
            self.close()

        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка БД", f"Не удалось удалить запись:\n{e}")
            logger.error(f"Ошибка удаленния записи")


class ArtCatalogBD:
    def __init__(self, db_name="database.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ArtCatalog (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                Comment TEXT,
                Data TEXT NOT NULL,
                Size INTEGER NOT NULL,
                Path TEXT NOT NULL
            )
        """)
        self.conn.commit()
    
    def add_art(self, name, comment, data, size, path):
        """
        Получает данные в строковом формате, добавляет о них информацию в бд 
        """
        self.cursor.execute("""
            INSERT INTO ArtCatalog (Name, Comment, Data, Size, Path)
            VALUES (?, ?, ?, ?, ?)
            """, (name, comment, data, size, path))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_names(self):
        """
        Запрос в бд для получения всех имен
        """
        self.cursor.execute("SELECT ID, Name FROM ArtCatalog")
        return self.cursor.fetchall()
    
    def get_art_by_id(self, art_id):
        """ 
        Запрос в бд по айди. Возвращает полную запись
        """
        self.cursor.execute("SELECT * FROM ArtCatalog WHERE ID = ?", (art_id,))
        return self.cursor.fetchone()
    
    def update_art(self, art_id, name, data, comment):
        """
        Обновляет запись в БД по ID.
        """
        self.cursor.execute("""
            UPDATE ArtCatalog
            SET Name = ?, Data = ?, Comment = ?
            WHERE ID = ?
        """, (name, data, comment, art_id))
        self.conn.commit()

    def close(self):
        """
        Функция закрытия
        """
        self.conn.close()

    def delete_art(self, art_id):
        """
        Функция отправляет запрос на удаление обьекта в бд
        """
        self.cursor.execute("DELETE FROM ArtCatalog WHERE ID = ?", (art_id,))
        self.conn.commit()
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())


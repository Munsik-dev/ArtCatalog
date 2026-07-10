import os

from PyQt5  import QtCore


class Validator:
    @staticmethod
    def check_data(data):
        """
        Получает date в формате str, проверяет на наличие и корректность
        Возвращает True или False, а так же текст ошибки в формте str/None
        """
        date = QtCore.QDate.fromString(data, "dd.MM.yyyy")
        if not date.isValid():
            return False, "Используйте формат: ДД.ММ.ГГГГ"
        
        if date > QtCore.QDate.currentDate():
            return False, "Дата не может быть в будущем"
        
        return True, None

    @staticmethod 
    def check_name(name):
        """
        Получает name в формте str. Проверяет на наличие
        Возвращает True/False, а так же текст ошибки в формате str/None
        """
        if not name:
            return False, "Введите название"
        
        return True, None

    @staticmethod    
    def check_path(path):
        """
        Получает path в str.
        Проверяет правильность ввода пути к файлу, наличия файла, правильность формата. 
        Возвращает True/False, а так же текст ошибки в форме str/None
        """
        path = path.strip()
    
        if not path:
            return False, "Введите путь к файлу"
        
        if not os.path.exists(path):
            return False, "Файл не найден"
        
        if not os.path.isfile(path):
            return False, "Укажите файл, а не папку"
        
        ext = os.path.splitext(path)[1].lower()
        allowed_ext = ['.jpg', '.jpeg', '.png', '.webp']
        if ext not in allowed_ext:
            return False, f"Разрешенные форматы: {', '.join(allowed_ext)}"
        
        return True, None   
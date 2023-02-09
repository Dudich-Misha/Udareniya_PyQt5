import sys
from random import sample
from pymorphy2 import MorphAnalyzer
from list_words import get_list_words
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QPushButton, QMessageBox, \
    QTableWidgetItem
from MainMenu_style import Ui_MainWindow
from TrainingDialog_style import Ui_Dialog as Ui_TrainingDialog
from CountWordsDialog_style import Ui_Dialog as Ui_CountWordsDialog
from ResultTrainigDialog_style import Ui_Dialog as Ui_ResultTrainingDialog
from MyDictionaryDialog_style import Ui_Dialog as Ui_MyDictionaryDialog
from AddWordDialog_style import Ui_Dialog as Ui_AddWordDialog
from PyQt5 import QtCore, QtWidgets

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class MainMenu(QMainWindow, Ui_MainWindow):
    """Основное меню приложения"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUi()

    def initUi(self):
        self.list_word = get_list_words()
        # при нажатии на кнопку создастся тренировка
        self.training_btn.clicked.connect(self.create_training)
        # при нажатии на кнопку откроется меню работы со словарём
        self.my_dictionary_btn.clicked.connect(self.show_dictionary)

    def create_training(self):
        """Создание тренировки"""
        dialog = CountWordsDialog(self)
        COUNT_WORDS = dialog.words_count  # получаем количество слов, в которых будет проверяться
        # правильность выбора букв, на которые падает ударение. Если пользователь закрыл окно, то
        # возвращается count_words равняется None
        if COUNT_WORDS is None:  # если количество слов не выбрано, то тренировка отменяется
            return
        # случайным образом получаем слова, кол-во которых задал пользователь
        WORDS = sample(self.list_word, k=COUNT_WORDS)
        errors = 0
        for i, word in enumerate(WORDS):
            # преобразуем слово в итератор, где элементами будут кортежи. В кажлм кортеже будет 2
            # элемента: порядковый номер буквы и сама буква. Чтобы получить номер буквы, на
            # которое падает ударение, нужно найти букву, выделенную капсом
            NUMBER_RIGHT_LETTER = [j for j, letter in enumerate(word, 1) if letter.isupper()][0]
            # для каждого слова создается диалог, в котором пользователю нужно выбрать букву
            dialog = TrainingDialog(self, word.lower(), NUMBER_RIGHT_LETTER)
            # пока пользователь жмет на Cancel в QMessageBox, будет создаваться тот же диалог
            while dialog.flag_stop_training is None:
                dialog = TrainingDialog(self, word.lower(), NUMBER_RIGHT_LETTER)
            # если флаг окончания тренировки активен, то завершаем тренировку, иначе продолжаем
            # тренировку
            if dialog.flag_stop_training:
                return
            if dialog.flag_error:
                errors += 1
        # находим процент правильных ответов и создаём диалог, где показываем результат пользователю
        percents = 100 - int(errors / COUNT_WORDS * 100)
        dialog = ResultTrainingDialog(self, percents)

    def show_dictionary(self):
        """Показываем словарь пользователю"""
        dialog = MyDictionaryDialog(self)


class TrainingDialog(QDialog, Ui_TrainingDialog):
    """Диалог-тренировка"""

    def __init__(self, parent, word, number_right_letter):
        super().__init__(parent)
        self.word = word
        self.number_right_letter = number_right_letter
        self.setupUi(self)
        self.initUi()
        self.exec_()

    def initUi(self):
        self.flag_stop_training = False
        self.flag_error = False
        self.next_word_btn.setEnabled(False)
        self.next_word_btn.clicked.connect(self.next_word)
        self.back_to_main_menu_button.clicked.connect(self.back_to_main_menu)
        # словарь, где ключ - порядковый номер буквы, а значение - кнопка с этой буквой
        self.buttons_numbers = {}
        # список гласных
        self.VOWElS = 'А, Е, И, О, У, Ы, Э, Ю, Я'.split(', ')
        x = y = 10
        for i, letter in enumerate(self.word, 1):
            # создаем в цикле кнопки
            letter_btn = QPushButton(letter.upper(), self)
            letter_btn.resize(25, 25)
            letter_btn.move(x, y)
            letter_btn.setStyleSheet('''background-color: black; color: white;''')
            # добавляем в словарь
            self.buttons_numbers[i] = letter_btn
            # связываем нажатие со слотом
            letter_btn.clicked.connect(self.click_handler)
            # меняем координаты
            x += 40
            # это нужно, чтобы кнопки не выходили за края. Если следующая кнопка в ряду выйдет за
            # края, то мы опускаем кнопку ниже на ряд ниже и возвращаем 'x' в начала ряда
            if x >= 375:
                x = 10
                y += 40

    def click_handler(self):
        # осуществляем проверку. Если у хоть у одной кнопки есть задний фон зелёного цвета, значит
        # пользователь уже нажал на кнопку и на последующие нажатия в этом окне приложение никак
        # реагировать не должно
        if any(map(lambda btn_numb: 'background-color: rgb(22, 222, 22);'
                                    in self.buttons_numbers[btn_numb].styleSheet(),
                   self.buttons_numbers)):
            return
        # Если нажатая кнопка была с согласной буквой, то никак не реагируем
        if self.sender().text() not in self.VOWElS:
            return
        # Если кнопка была с гласной буквой, делаем ей красный задний фон
        if self.sender().text() in self.VOWElS:
            self.sender().setStyleSheet('background-color: red; color: white')
        # Ставим зеленый задний фон кнопке с правильной гласной. Если нажатая кнопка была с ударной
        # гласной, то выделена фоном будет только 1 кнопка - та, которая нажата. Если с безударной
        # гласной, то будет выделено фоном 2 кнопки - красным, та которая нажата, зелёным -
        # кнопка с ударной гласной
        self.buttons_numbers[self.number_right_letter].setStyleSheet(
            'background-color: rgb(22, 222, 22); color: white')
        if self.sender() != self.buttons_numbers[self.number_right_letter]:
            self.flag_error = True
        self.next_word_btn.setEnabled(True)

    def next_word(self):
        self.hide()

    def back_to_main_menu(self):
        self.close()

    def closeEvent(self, event):
        # В случае попытки выйти, не завершив тренировку, предупреждаем пользователя
        # о потере прогресса
        STR_ = 'В случае выхода прогресс по тренировке будет утерян. Вы действительно хотите выйти?'
        valid = QMessageBox.question(self, 'Запрос подтверждения', STR_, QMessageBox.Ok,
                                     QMessageBox.Cancel)
        # Если пользователь подтвердит выход, то завершаем активируем флаг завершения тернировки
        if valid == QMessageBox.Ok:
            self.flag_stop_training = True
        else:
            self.flag_stop_training = None


class CountWordsDialog(QDialog, Ui_CountWordsDialog):
    """Диалог, появляющийся перед тренировкой,
    в котором пользователь задает количество слов тренировки"""

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.initUi()
        self.exec_()

    def initUi(self):
        self.words_count = None  # изначально количество не задано. Если пользователь закроет диалог,
        # не нажав на кнопку "готово", words_count останется None
        self.ready_btn.clicked.connect(self.ready)

    def ready(self):
        self.words_count = int(self.words_count_spinBox.text())  # получаем количество слов из
        # спинбокса
        self.close()


class ResultTrainingDialog(QDialog, Ui_ResultTrainingDialog):
    """Диалог, в котором пользователь узнаёт результат тренировки"""

    def __init__(self, parent, percents):
        super().__init__(parent)
        self.percents = percents
        self.setupUi(self)
        self.initUi()
        self.exec_()

    def initUi(self):
        self.result_in_procents_label.setText(f'{self.percents}% правильных ответов')
        self.ok_button.clicked.connect(self.close_dialog)

    def close_dialog(self):
        self.close()


class MyDictionaryDialog(QDialog, Ui_MyDictionaryDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.initUi()
        self.exec_()

    def initUi(self):
        self.show_table()
        # Выделенное пользователем слово, которое, возможно, будет удалено
        self.deleted_word = None
        # При нажатии на кнопку происходит возвращение в главное меню
        self.back_to_main_menu_button.clicked.connect(self.back_to_main_menu)
        # Вовремя поиска слов через строку поиска выдаются результаты, соответствующие
        # введённому тексту
        self.search_word_Edit.textChanged.connect(self.search_word)
        # При нажатии на кнопку в список слов добавляется ещё одно
        self.add_word_button.clicked.connect(self.add_word)
        # При выделении элемента таблицы появляется возможность его удалить
        self.tableWidget.itemClicked.connect(self.activate_delete_button)
        # При нажатии на кнопку выделенные слова удаляются
        self.delete_word_button.clicked.connect(self.delete_word)

    def back_to_main_menu(self):
        self.close()

    def search_word(self):
        # При обновлении таблицы во время поиска сбрасывается выделение элемента, поэтому
        # деактивируем кнопку "удалить"
        self.delete_word_button.setEnabled(False)
        text = self.search_word_Edit.text()
        # если строка пустая, показываем всю таблицу
        if not text:
            self.show_table()
            return
        new_table = [word for word in self.parent().list_word
                     if word.lower().startswith(text.lower())]
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnWidth(0, 270)
        self.tableWidget.setHorizontalHeaderLabels(['Слово'])
        for i, elem in enumerate(new_table):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            self.tableWidget.setItem(i, 0, QTableWidgetItem(str(elem)))

    def show_table(self):
        """Метод, который показывает таблицу слов, отсортированных по алфавиту"""
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnWidth(0, 270)
        self.tableWidget.setHorizontalHeaderLabels(['Слово'])
        for i, elem in enumerate(self.parent().list_word):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            self.tableWidget.setItem(i, 0, QTableWidgetItem(str(elem)))

    def add_word(self):
        # Если пользователь кликнул на элемент, то при добавлении нового элемента, выделение элемента
        # сбрасывается, поэтому деактивируем кнопку "удалить"
        self.delete_word_button.setEnabled(False)
        # Для добавления слова в список вызываем диалог
        dialog = AddWordDialog(self)
        self.search_word()

    def activate_delete_button(self, item):
        # Запоминаем выделенное слово, которое, возможно, будет удалено
        self.deleted_word = item.text()
        # Активируем кнопку "удалить"
        self.delete_word_button.setEnabled(True)

    def delete_word(self):
        # деактивируем кнопку удалить
        self.delete_word_button.setEnabled(False)
        # Чтобы пользователь не удалил все слова из словаря, вводим ограничение.
        # Должно остаться минимум 30 слов. Если пользователь захочет удалить 30 слово,
        # то программа не позволит это сделать
        if len(self.parent().list_word) == 30:
            valid = QMessageBox.question(
                self, 'Оповещение', 'В словаре не может быть меньше 30 слов', QMessageBox.Ok)
            return
        # удаляем из выделенное слово из списка
        self.parent().list_word.remove(self.deleted_word)
        # Показываем изменённую таблицу
        self.search_word()


class AddWordDialog(QDialog, Ui_AddWordDialog):
    """Диалог для добавления слова в список"""

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.initUI()
        self.exec_()

    def initUI(self):
        # При нажатии на кнопку производится проверка введённого слова. Если слово проходит проверку,
        # то оно добавляется в список, иначе выводится сообщение в QMessageBox, где написано
        # что именно нужно исправить
        self.add_button.clicked.connect(self.add_word)
        self.word = None

    def add_word(self):
        # получаем введённое пользователем слово
        word = self.new_wordEdit.text()
        RUSSIAN_ALPHABET = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        VOWELS = 'А, Е, И, О, У, Ы, Э, Ю, Я'.split(', ')
        # если слово уже есть в списке
        if word in self.parent().parent().list_word:
            STR_ = 'Это слово уже естьв списке, попробуйте другое'
            valid = QMessageBox.information(self, 'Некорректный ввод', STR_, QMessageBox.Ok)
        # если в слове встречаются символы не из русского алфавита
        elif not all(map(lambda let: let in RUSSIAN_ALPHABET, word.lower())):
            STR_ = '''Необходимо написать слово только буквами русского алфавита без 
дополнительных знаков и разделителей'''
            valid = QMessageBox.information(self, 'Некорректный ввод', STR_, QMessageBox.Ok)
        # если в слове нет букв, выделенных капсом
        elif word.lower() == word:
            STR_ = 'Необходимо выделить капсом букву, на которую падает ударение.'
            valid = QMessageBox.information(self, 'Некорректный ввод', STR_, QMessageBox.Ok)
        # если в слове больше одной буквы, выделенной капсом
        elif len([letter for letter in word if letter.isupper()]) > 1:
            STR_ = 'Необходимо выделить капсом ОДНУ букву, на которую падает ударение.'
            valid = QMessageBox.information(self, 'Некорректный ввод', STR_, QMessageBox.Ok)
        elif [letter for letter in word if letter.isupper()][0] not in VOWELS:
            STR_ = 'Необходимо выделить капсом ГЛАСНУЮ букву, на которую падает ударение.'
            valid = QMessageBox.information(self, 'Некорректный ввод', STR_, QMessageBox.Ok)
        # если есть "ё" в слове и оно не выделено как ударное
        elif 'ё' in word:
            STR_ = 'Ошибка. Буква "ё" всегда ударная'
            valid = QMessageBox.information(self, 'Некорректный ввод', STR_, QMessageBox.Ok)
        elif str(MorphAnalyzer().parse(word)[0].methods_stack[0][0]) == 'FakeDictionary()':
            STR_ = 'Скорее всего такого слова не существует. Попробуйте другое'
            valid = QMessageBox.information(self, 'Некорректный ввод', STR_, QMessageBox.Ok)
        else:
            # добавляем слово в список. Если в слове есть буква "Ё", меняем её на "Е"
            self.parent().parent().list_word.append(word.replace('Ё', 'Е'))
            # сортируем полученный список по алфавиту
            self.parent().parent().list_word = sorted(self.parent().parent().list_word,
                                                      key=lambda elem: elem.lower())
            self.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainMenu()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())

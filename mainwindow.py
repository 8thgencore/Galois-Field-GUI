# -*- coding: utf-8 -*-
import sys
import numpy as np
import xlsxwriter
import xlwt
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import galois
import mult_add

class GaliosApp(QtWidgets.QMainWindow, galois.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Для инициализации дизайна
        self.setWindowTitle("Построение поле Галлуа")

        # вставляем изображение
        # pixmap = QPixmap("img.bmp")
        # self.label_for_image.setPixmap(pixmap)

        # connect
        self.pb_Create_Table.clicked.connect(self.createGaloisTable)
        self.pb_ShowPolynom.clicked.connect(self.showPolynom)
        self.lw_SelectPolynom.itemDoubleClicked.connect(self.createGaloisTable)
        self.pb_ExportToExcel.clicked.connect(self.exportToExcel)

        # разрешаем вводить только цифры
        #self.le_MultAddNum_1.setValidator(QRegExpValidator(QRegExp("-?[0-9]{1,3}"), self))
        #self.le_Exponent.setValidator(QRegExpValidator(QRegExp("-?[0-9]{1,2}"), self))
        #self.le_MultAddNum_2.setValidator(QRegExpValidator(QRegExp("-?[0-9]{1,3}"), self))

    def showPolynom(self):
        # считываем степень полинома
        self.exponent = int(self.le_Exponent.text())

        # для хранение размера поля
        self.field_size = pow(2, self.exponent)

        # соездаем массив всех возможных полиномов
        find_polynomial_simple = []
        find_polynomial_bin = []
        find_polynomial_bool = []

        # генерируем полиномы поля
        for i in range(self.field_size):
            format_str = '0b{0:0>' +str(self.exponent) + 'b}'
            find_polynomial_bin.append(format_str.format(self.field_size + i)[2:])
            find_polynomial_simple.append(format_str.format(i)[2:])
            find_polynomial_bool.append(0)



        # перемножаем между собой полиномы, тем самым ищем неприводимые полиномы
        for k in range(len(find_polynomial_simple)):
            for l in range(len(find_polynomial_simple)):
                if l < k:
                    continue

                bin_mult_add_num_1 = []
                bin_mult_add_num_2 = []

                # перевод вида: 10001101 -> '7','3','2','0'
                for i in range(0, self.exponent):
                    if (find_polynomial_simple[k][i] == "1"):
                        bin_mult_add_num_1 += str(self.exponent - 1 - i)
                    if (find_polynomial_simple[l][i] == "1"):
                        bin_mult_add_num_2 += str(self.exponent - 1 - i)

                # перевод элементов массива в int '7','3','2','0' -> 7,3,2,0
                for i, elem in enumerate(bin_mult_add_num_1):
                    bin_mult_add_num_1[i] = int(elem)
                for i, elem in enumerate(bin_mult_add_num_2):
                    bin_mult_add_num_2[i] = int(elem)

                ##############################################################################

                # умножение по модулю
                mult_add.setGF2(self.exponent*2, mult_add.i2P(0b10000000000000000))
                bin_mult_result_in_int = mult_add.int2Poly(mult_add.hdMultGF2(bin_mult_add_num_1, bin_mult_add_num_2))
                if not bin_mult_result_in_int:
                    continue
                ##############################################################################

                # переводим в 2-ый вид
                bin_mult_result = ""  # для результата
                item = 0  # индекс элементов массива
                bin_bool = 0  # для проверки
                bin_len = len(bin_mult_result_in_int)
                for i in range(0, self.exponent*2+1):
                    if (item == bin_len):
                        item = 0
                        bin_bool = 1
                    if ((self.exponent*2 - i == int(bin_mult_result_in_int[item])) and (bin_bool == 0)):
                        item += 1
                        bin_mult_result += "1"
                    else:
                        bin_mult_result += "0"

                # проверка результата перемножение на его принадлежность полю
                for i in range(self.field_size):
                    if (bin_mult_result == (self.exponent * '0' + find_polynomial_bin[i])):
                        find_polynomial_bool[i] = 1

        # создаем массив из полиномов
        self.newfind_polynomial_bin = []
        self.newfind_polynomial = []
        for i in range(self.field_size):
            if find_polynomial_bool[i] == 0:
                self.newfind_polynomial_bin.append(find_polynomial_bin[i])

        # переводим в "красивый" вид
        self.exponent = self.exponent + 1
        for i in range(len(self.newfind_polynomial_bin)):
             self.bin_to_polynom(self.newfind_polynomial_bin[i])
             self.newfind_polynomial.append(self.result_polynom)
        self.exponent = self.exponent - 1

        self.lw_SelectPolynom.clear()
        self.lw_SelectPolynom.addItems(self.newfind_polynomial)



    def createGaloisTable(self):
        # считываем выбранный нами полином
        self.main_polynom = self.lw_SelectPolynom.item(self.lw_SelectPolynom.currentRow()).text()
        self.label_MainPolynomial.setText(self.main_polynom)
        for i in range(len(self.newfind_polynomial_bin)):
            if self.main_polynom == self.newfind_polynomial[i]:
                self.main_polynom = self.newfind_polynomial_bin[i]

        # объявление массиво
        self.bin_array = []
        self.dec_array = np.array(range(self.field_size*2), int)
        hex_array = np.array(range(self.field_size*2), str)
        nop_array = np.array(range(self.field_size*2), int)
        self.polynomial = []

        self.dec_array += int(1);

        for i in range(0, self.field_size):
            # создаем список элементов поля в 10-ой системе
            self.dec_array[i + 1] = self.dec_array[i] * 2
            self.dec_array[i + 1] ^= self.dec_array[i]
            if self.dec_array[i + 1] & self.field_size: #int("0x100", 0):
                self.dec_array[i + 1] ^= int(self.main_polynom, 2) #int("0x11b", 0)

            # создаем список элементов поля в 16-ой системе
            hex_array[i] = hex(self.dec_array[i])[2:4]
            if self.dec_array[i] < 16:
                hex_array[i] = "0" + hex_array[i][:1]

            # создаем список элементов поля в 2-ой системе
            format_str = '0b{0:0>' + str(self.exponent) + 'b}'
            self.bin_array.append(format_str.format(self.dec_array[i])[2:])

            # создаем полиномы
            self.bin_to_polynom(self.bin_array[i])
            self.polynomial.append(self.result_polynom)


        # построение столбцы nop
        for i in range(1, self.field_size, 15):
            nop_array[i] = "255"
            nop_array[i+1] = "255"
            nop_array[i+2] = "85"
            nop_array[i+3] = "255"
            nop_array[i+4] = "51"
            nop_array[i+5] = "85"
            nop_array[i+6] = "255"
            nop_array[i+7] = "255"
            nop_array[i+8] = "85"
            nop_array[i+9] = "51"
            nop_array[i+10] = "255"
            nop_array[i+11] = "85"
            nop_array[i+12] = "255"
            nop_array[i+13] = "255"
            nop_array[i+14] = "17"
        nop_array[0] = "1"
        nop_array[self.field_size] = "1"

        # объявляем таблицу
        self.twig_Galios_Table.setColumnCount(9)  # Устанавливаем колонки
        self.twig_Galios_Table.setRowCount(self.field_size)  # и строки в таблице
        # Устанавливаем заголовки таблицы
        self.twig_Galios_Table.setHorizontalHeaderLabels(["Степень", "bin", "dec", "hex", "nop", "inv(bin)", "inv(dec)", "inv(hex)", "Полином"])
        # Устанавливаем всплывающие подсказки на заголовки
        self.twig_Galios_Table.horizontalHeaderItem(0).setToolTip("Степень")
        self.twig_Galios_Table.horizontalHeaderItem(1).setToolTip("Binary")
        self.twig_Galios_Table.horizontalHeaderItem(2).setToolTip("10-x")
        self.twig_Galios_Table.horizontalHeaderItem(3).setToolTip("16-x")

        # заполняем таблицу
        for item in range(0,self.field_size):
            self.twig_Galios_Table.setItem(item, 0, QtWidgets.QTableWidgetItem("a^"+str(item)))
            self.twig_Galios_Table.setItem(item, 1, QtWidgets.QTableWidgetItem(str(self.bin_array[item])))
            self.twig_Galios_Table.setItem(item, 2, QtWidgets.QTableWidgetItem(str(self.dec_array[item])))
            self.twig_Galios_Table.setItem(item, 3, QtWidgets.QTableWidgetItem(str(hex_array[item])))
            self.twig_Galios_Table.setItem(item, 4, QtWidgets.QTableWidgetItem(str(nop_array[item])))
            self.twig_Galios_Table.setItem(item, 5, QtWidgets.QTableWidgetItem(str(self.bin_array[self.field_size-1-item])))
            self.twig_Galios_Table.setItem(item, 6, QtWidgets.QTableWidgetItem(str(self.dec_array[self.field_size-1-item])))
            self.twig_Galios_Table.setItem(item, 7, QtWidgets.QTableWidgetItem(str(hex_array[self.field_size-1-item])))
            self.twig_Galios_Table.setItem(item, 8, QtWidgets.QTableWidgetItem(str(self.polynomial[item])))

        # Расскрашивание поля
        for color in range(0, self.field_size):
            self.twig_Galios_Table.item(color, 0).setBackground(QtGui.QColor(224, 224, 224))
            self.twig_Galios_Table.item(color, 1).setBackground(QtGui.QColor(224, 255, 255))
            self.twig_Galios_Table.item(color, 2).setBackground(QtGui.QColor(224, 255, 255))
            self.twig_Galios_Table.item(color, 3).setBackground(QtGui.QColor(224, 255, 255))
            self.twig_Galios_Table.item(color, 5).setBackground(QtGui.QColor(255, 255, 224))
            self.twig_Galios_Table.item(color, 6).setBackground(QtGui.QColor(255, 255, 224))
            self.twig_Galios_Table.item(color, 7).setBackground(QtGui.QColor(255, 255, 224))
            self.twig_Galios_Table.item(color, 8).setBackground(QtGui.QColor(255, 224, 224))

        # делаем ресайз колонок по содержимому
        self.twig_Galios_Table.resizeColumnsToContents()
        self.twig_Galios_Table.resizeRowsToContents()

    def bin_to_polynom(self, bin_temp_array):
        # перевод двоичного числа в полином
        temp_polynomial = ""
        temp_bool = 0
        for i in range(self.exponent):
            if (bin_temp_array[i] == "1"):
                if (temp_bool == 1):
                    temp_polynomial += "+"
                if (i == self.exponent - 1):
                    temp_polynomial += "1"
                else:
                    temp_polynomial += "x^" + str(self.exponent - 1 - i)
                    temp_bool = 1
        self.result_polynom = temp_polynomial



    def exportToExcel(self):
        filename = QFileDialog.getSaveFileName(self, 'Save File', '', ".xls(*.xls)")
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet("sheet", cell_overwrite_ok=True)
        self.add2(sheet)
        wbk.save(filename[0])

    def add2(self, sheet):
        for currentColumn in range(self.twig_Galios_Table.columnCount()):
            for currentRow in range(self.twig_Galios_Table.rowCount()):
                try:
                    teext = str(self.twig_Galios_Table.item(currentRow, currentColumn).text())
                    sheet.write(currentRow, currentColumn, teext)
                except AttributeError:
                    pass

def main():
    app = QtWidgets.QApplication(sys.argv) # Новый экземпляр QApplication
    window = GaliosApp() # Создаем объект класса ExampleApp
    window.show() # Показать окно
    app.exec() # Запускаем приложение

if __name__ == '__main__': # Если мы запусаем файл напрямую, а не импортируем
    main()
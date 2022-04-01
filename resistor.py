# from quantiphy import Quantity as quan
import numpy as np
# from numpy import sin, cos, sqrt, deg2rad, zeros, linspace

from PyQt5.QtGui import QColor, QStandardItem
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from functools import partial
import sys

# eng_form = mpl.
color_ls = ['black', 'brown', 'red', 'orange', 'yellow', 'green', 'blue', 'violet', 'grey', 'white']
toler_ls = [0.01, 0.02, 0.005, 0.0025, 0.001, 0.0005, 0.05, 0.10]
exp_ls = ['silver', 'gold']
tol_col = ['brown', 'red', 'green', 'blue', 'violet', 'grey', 'gold', 'silver']


class Band(QComboBox):
    def __init__(self, par, pos, tol=''):
        super().__init__()
        self.tol = tol
        self.par = par
        self.poss = pos
        if tol == 'ex':
            self.ls = exp_ls + color_ls
        elif tol == 'tol':
            self.ls = tol_col
        else:
            self.ls = color_ls
        # self.setItemDelegate()
        idx = self.model()
        for n, i in enumerate(self.ls):
            it = QStandardItem(i)
            it.setBackground(QColor(i))
            # self.addItem(it)  # todo value from index

            idx.appendRow(it)
        self.setStyleSheet("background-color: " + self.currentText() + "; }")

        self.currentTextChanged.connect(self.current_changed)

    def current_changed(self):
        v = self.currentText()
        va = self.ls.index(v)
        if self.tol == 'ex':
            va -= 2
        elif self.tol == 'tol':
            va = toler_ls[va]
        # elif self.bands[pos].tol == 'tol':
        self.setStyleSheet("background-color: " + v + "; }")
        self.par.col_swap(va, self.poss)


class bandNum(QSpinBox):
    def __init__(self, par, pos, tol=''):
        super().__init__()
        self.tol = tol
        self.poss = pos
        # todo solve type self.
        self.par = par
        if tol == 'ex':
            r = (-2, 9)
        else:
            r = (0, 9)
        self.setRange(*r)
        self.setSingleStep(1)
        self.valueChanged.connect(self.current_changed)

    def current_changed(self):
        v = self.value()
        if self.tol == 'ex':
            v += 2
        self.par.num_swap(v,self.poss)

    def set_v(self, v):
        self.setValue(v)


class TolBox(QComboBox):
    def __init__(self, par, pos):
        super().__init__()
        self.poss = pos
        self.par = par
        for n, i in enumerate(toler_ls):
            self.addItem(str(i))  # todo value from index
            self.currentTextChanged.connect(self.current_changed)

    def current_changed(self):
        v = self.currentText()
        va = toler_ls.index(float(v))
        print('hi')
        # elif self.bands[pos].tol == 'tol':
        self.par.num_swap(va, self.poss)
    # def singleStep(self):

    def set_v(self, v):
        self.setCurrentText(str(v))


# def step_by(self):
#     pass
#  {
#  int
#  const
#  index = std::max(0, (acceptedValues.indexOf(value()) + steps) % acceptedValues.length()); // Bounds
#  the
#  index
#  between
#  0 and length
#  setValue(acceptedValues.value(index));


class Window(QMainWindow):
    # noinspection PyArgumentList
    def __init__(self):
        super().__init__()
        self.wig = QWidget()
        self.setCentralWidget(self.wig)
        self.lay = QGridLayout()

        self.res_type = QSpinBox()
        self.res_type.setRange(3, 5)
        self.res_type.setSingleStep(1)
        self.res_type.setValue(3)

        self.res_type.valueChanged.connect(self.set_resistor)
        self.lay.addWidget(self.res_type, 0, 0)
        self.lay.addWidget(QLabel('Band Count'), 0, 1)

        self.main_disp = QLineEdit()
        self.main_disp.editingFinished.connect(self.solve_resistor)
        self.lay.addWidget(self.main_disp, 1, 0)
        self.lay.addWidget(QLabel('Value'), 1, 1)
        self.wig.setLayout(self.lay)
        self.bands = []
        self.band_num = []

        self._set_const()
        self.set_resistor()

    def _set_const(self):
        self.conver = ['n', 'mc', 'm', '', 'k', 'M', 'G']

    def set_resistor(self):
        # band = self.res_type.value()
        band = max(2, self.res_type.value() - 2)
        delta = len(self.bands)
        if delta > 2:
            self.bands = self.bands[:band]
            self.band_num = self.band_num[:band]
        # if num > 3:
        else:
            for i in range(delta, band):
                j = Band(self, i)
                sp = bandNum(self, i)
                self.lay.addWidget(j, i + 2, 0)
                self.lay.addWidget(sp, i + 2, 1)
                self.bands.append(j)
                self.band_num.append(sp)

        j = Band(self, band, 'ex')
        sp = bandNum(self, band, 'ex')
        self.lay.addWidget(j, band + 2, 0)
        self.lay.addWidget(sp, band + 2, 1)
        self.bands.append(j)
        self.band_num.append(sp)

        if band + 1 < self.res_type.value():
            print('tol')
            j = Band(self, band + 1, 'tol')
            sp = TolBox(self, band + 1)
            print('set tol')
            self.lay.addWidget(j, band + 3, 0)
            self.lay.addWidget(sp, band + 3, 1)
            self.bands.append(j)
            self.band_num.append(sp)
        self.solve_resistor()

    def col_swap(self, v, pos):
        # elif self.bands[pos].tol == 'tol':
        #
        self.band_num[pos].set_v(v)  # todo add ex
        self.solve_resistor()

    def num_swap(self, v, pos):
        va = self.bands[pos].ls[v]
        self.bands[pos].setCurrentText(va)  # todo add ex
        self.solve_resistor()

    def solve_resistor(self):
        # for reverse
        num = ''
        ex_in = 1
        lb = len(self.bands)
        if len(self.bands) > 3:
            # tol = self.band_num[-1].currentText()
            ex_in += 1
            tol_v = '+-' + self.band_num[-1].currentText()
        else:
            tol_v = ''
        print('ex: ', ex_in)
        ex = self.band_num[-ex_in].value()
        for col in range(lb - ex_in):  # only first

            col_val = self.band_num[col].value()
            # col_f = color_ls[col_val]# find prefix
            num += str(col_val)
            # print(f'col: {col}, val: {col_val}')

        # without exponet len
        po = ex + lb - ex_in - 1
        print(f'pow: {po}, exp: {ex}, dec: {(po - 1) % 2}')
        num = str(int(num) * 10 ** (po % 3 - 1))
        # if dec != 0:
        #     num = num[:-dec] + '.' + num[-dec:]
        pre = int(np.floor(po / 3)) + 3  # decimal
        if len(num) == 0:
            num = '1'
        num += f'{self.conver[pre]} Ω'  # add exponent
        print(num)

        # get exp of coler then the corresp in toler
        text_out = num + tol_v  # todo render
        print('R =: ', text_out)
        self.main_disp.setText(text_out)

    def set_val(self):
        user_input = self.main_disp.text()
        user_input = user_input.replace('ohm', '').replace('Ω', '').replace(' ', '')
        # todo in place?, tolerance

        po = 0
        for n, i in enumerate(self.conver):
            if user_input.endswith(i):
                user_input.replace(i, '')
                po = (n - 3) * 3

        res_sig = max(2, self.res_type.value() - 2) - 1

        # band = user_num.render(form='eng', prec=res_sig)
        # print(band)
        ui = float(user_input) * 10 ** po
        log_band = np.floor(np.log10(ui))  # get ten ^x  # todo error code

        dif_exp = res_sig - log_band
        norm_band = str(int(ui * 10 ** dif_exp))  # todo -1?
        # pre -= res_sig  # creates corect indexing

        for n, i in enumerate(norm_band):
            ii = int(i)
            self.band_num[n].setValue(ii)
            self.bands[n].setCurrentText(color_ls[ii])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    audio_app = Window()
    audio_app.show()
    sys.exit(app.exec_())

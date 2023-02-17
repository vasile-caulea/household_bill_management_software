import logging
from datetime import datetime
from functools import partial
from multiprocessing import Queue

from PyQt6.QtCore import QSize, Qt, QStringListModel
from PyQt6.QtWidgets import QLineEdit, QDateEdit, QSpinBox, QDoubleSpinBox, QComboBox, QCompleter, QPushButton

from DBConnenction import DBConn

with open('app.log', 'w') as f:
    f.write('')

logging.basicConfig(filename='app.log', encoding='utf-8', level=logging.INFO, format='%(levelname)s : %(message)s')


def log_err(e):
    logging.error(e)


def log_info(e):
    logging.info(e)


msgQueue = Queue()


def get_elem(data_type: tuple, parent=None, size=None, value=None):
    if data_type[0] == 'VARCHAR':
        res = QLineEdit(parent)
        res.setMaxLength(data_type[1])
        if isinstance(value, str):
            res.setText(value)
            res.setStyleSheet('QLineEdit{border:none;}')
    elif data_type[0] == 'DATE':
        res = QLineEdit(parent)
        res.setObjectName('DATE')
        res.setPlaceholderText('DD.MM.YYYY')
        if isinstance(value, datetime):
            res.setText(value.strftime('%d.%m.%Y'))
            res.setStyleSheet('QLineEdit{border:none;}')
        elif isinstance(value, str):
            res.setText(value)
            res.setStyleSheet('QLineEdit{border:none;}')
        else:
            res.setText(datetime.today().strftime('%d.%m.%Y'))
    else:
        if data_type[3] > 0:
            res = QDoubleSpinBox(parent)
            max_value = float('9' * (data_type[2] - data_type[3]) + '.' + '9' * data_type[3])
            res.setMaximum(max_value)
        else:
            res = QSpinBox(parent)
            if data_type[2] != 0:
                max_value = int('9' * data_type[2])
            else:
                max_value = 999_999
            res.setMaximum(max_value)
        res.setMinimum(0)
        if value:
            res.setValue(value)
    if size:
        res.setFixedSize(size)

    if isinstance(res, QLineEdit) and value:
        res.setCursorPosition(0)
        res.setMinimumWidth(res.font().pointSize() * len(res.text()))
    return res


def set_call_back(widget, function, args):
    widget.editingFinished.connect(partial(function, *args))


def set_invisible(elem):
    if isinstance(elem, tuple):
        elem[0].setVisible(False)
        elem[1].setVisible(False)
    else:
        elem.setVisible(False)


def get_data_from_elem(elem):
    if isinstance(elem, QLineEdit):
        if elem.objectName() != 'DATE':
            data = f"'{elem.text()}'"
        else:
            data = datetime.strptime(elem.text(), '%d.%m.%Y')
            data = f"'{data.strftime('%d-%b-%Y').upper()}'"
    else:
        data = elem.value()
    return data


def get_table_details(tab, indx=0):
    c = DBConn()
    return get_cursor_details(c.execute(f'select * from {tab}'), indx)


def get_cursor_details(cursor, index=0):
    headers = []
    for record in cursor.description:
        headers.append(record[index])
    return headers


def get_data_types(tab):
    c = DBConn()
    cr = c.execute(f'select * from {tab}')
    data_info = []
    for record in cr.description:
        aux = str(record[1])
        aux = aux[aux.rfind('_') + 1:-1]
        data_info.append((aux, record[3], record[4], record[5]))
    return data_info


def add_unique(m_list, elem):
    if elem not in m_list:
        m_list.append(elem)


def get_combobox(parent, name, size, editable, items, with_completer):
    elem = QComboBox(parent)
    elem.setPlaceholderText('Select value...')
    if name:
        elem.setObjectName(name)
    if size:
        elem.setMinimumSize(size)
    if editable:
        elem.setEditable(editable)

    elem.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
    elem.addItems(items)
    elem.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

    if with_completer:
        completer = QCompleter()
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setModel(QStringListModel(items))
        elem.setCompleter(completer)
    return elem


def get_button(parent, text, size, fun=None, args=None):
    button = QPushButton(parent)
    if text:
        button.setText(text)
    button.setFixedSize(size)
    if fun and args:
        button.clicked.connect(partial(fun, *args))
    return button


def set_dedit_dimmed(btn: QPushButton, elem: QDateEdit):
    if btn.isChecked():
        elem.setEnabled(True)
    else:
        elem.setEnabled(False)


# operations
VIEW = 'VIEW'
ADD = 'ADD'
DELETE = 'DELETE'
UPDATE = 'UPDATE'

# objects sizes
obj_h = 30
obj_size1 = QSize(200, obj_h)
obj_size2 = QSize(300, obj_h)

# main window size
WIN_WIDTH = 898
WIN_HEIGHT = 654

errs = {
    'TARIFFTYPE_NAME_CK': 'NAME length should be > 1',
    'TARIFFS_TYPES_NAME_UK': 'NAME must be unique',
    'TARIFFS_TYPES_NAME_CK': 'Description should have a length > 1',
    'SERVICES_NAME_CK': 'Service name should have a length > 1',
    'SERVICES_NAME_UK': 'Service name should be unique',
    'PROVIDERS_NAME_CK': 'Provider name should have a length > 1',
    'PROVIDERS_NAME_UK': 'Provider name should be unique',
    'PERSONS_ADDRESS_CK': 'Person\'s address should have a length > 1',
    'PERSONS_EMAIL_CK': 'Email is invalid',
    'PERSONS_EMAIL_UK': 'Email should be unique',
    'PERSONS_FULLNAME_CK': 'Invalid full name',
    'PERSONS_PHONENO_CK': 'Invalid phone number',
    'PERSONS_PHONE_NO_UK': 'Phone number should be unique',
    'INVOICES_CONSUMPTION_CK': 'Consumption cannot be 0',
    'INVOICES_PAYMENT_CK': 'Payment cannot be 0',
    'PROVSERV_PRICE_CK': 'Price must be greater than 0',
    'PROVIDER_SERVICE_UK': 'The services offered must be unique'
}


def decode_err(e):
    e = str(e)
    if 'NULL' in e:
        e.replace('"', '')
        field_name = e[e.rfind('.') + 1: e.rfind('"')]
        return f'Field {field_name} cannot be empty'

    for er in errs:
        if er in e:
            return errs[er]
    indx_err = e.find('ORA-', e.find('ORA-') + 1)
    e = e[0:indx_err]
    substr = e[0:e.find(':') + 1]
    e = e.replace(substr, '')
    return e

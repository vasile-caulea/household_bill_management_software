# pyuic6 xyz.ui > xyz.py
import json
import re
from copy import deepcopy

import cx_Oracle
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, \
    QTableWidget, QTableWidgetItem, QLabel, QAbstractScrollArea, QGridLayout, QMessageBox

from gu import *
from login import LogInDialog

c = DBConn()


class Tables:
    def __init__(self, tabs: list):
        self.tables = tabs
        self.fk_ref: list[tuple] = c.execute(
            f"""SELECT UC.TABLE_NAME tbl,
                       UCC2.COLUMN_NAME,
                       UCC.TABLE_NAME ref_table
                   FROM (SELECT TABLE_NAME, CONSTRAINT_NAME, R_CONSTRAINT_NAME, CONSTRAINT_TYPE FROM USER_CONSTRAINTS) 
                        UC,
                        (SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME FROM USER_CONS_COLUMNS) UCC,
                        (SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME FROM USER_CONS_COLUMNS) UCC2
                   WHERE UC.R_CONSTRAINT_NAME = UCC.CONSTRAINT_NAME
                     AND UC.CONSTRAINT_NAME = UCC2.CONSTRAINT_NAME
                     AND uc.constraint_type = 'R' 
                     and lower(uc.table_name) in ({",".join(map(lambda x: str("'" + x + "'").lower(), self.tables))}
                     )"""
        ).fetchall()

        self.acronyms: dict[str, str] = {}
        self.fk: dict[str, list[tuple]] = {}
        self.data_types: dict[str, list] = {}
        self.headers: dict[str, list[str]] = {}

        for tbl_name in self.tables:
            self.fk[tbl_name] = list()
            for y in self.fk_ref:
                if tbl_name == y[0] and y[1:]:
                    self.fk[tbl_name].append(y[1:])
            self.data_types[tbl_name] = get_data_types(tbl_name)
            self.headers[tbl_name] = get_table_details(tbl_name)
        self.set_acronyms()

    def get_fk_cols(self, tab: str):
        return list(x[0] for x in self.fk[tab])

    def set_acronyms(self):
        for name in self.tables:
            self.acronyms[name] = name[0] + name[len(name) // 2 - 1] + name[-1]

    def get_tab_fk(self, tab, fk):
        for key in self.fk[tab]:
            if key[0] == fk:
                return key[1]
        return ''

    def get_add_fk_query(self, table, fk_col):
        ref_tab = self.get_tab_fk(table, fk_col)
        name_col = list(filter(lambda x: re.search('.*NAME.*', x), self.headers[ref_tab]))
        if name_col:
            query = f"SELECT {self.headers[ref_tab][0]}, {name_col[0]} FROM {ref_tab} ORDER BY {self.headers[ref_tab][0]}"
        else:
            query = f"SELECT {self.acronyms[ref_tab]}.{self.headers[ref_tab][0]}"
            tables_to_select_from = [f'{ref_tab} {self.acronyms[ref_tab]}']
            where_cond_list = []
            flag = True
            tab = ref_tab
            while flag:
                val = False
                for key in self.get_fk_cols(tab):
                    ref_tab2 = self.get_tab_fk(tab, key)
                    tables_to_select_from.append(f'{ref_tab2} {self.acronyms[ref_tab2]}')
                    where_cond_list.append(
                        f"{self.acronyms[tab]}.{self.headers[ref_tab2][0]}={self.acronyms[ref_tab2]}.{self.headers[ref_tab2][0]}")
                    name_col = list(filter(lambda x: re.search('.*NAME.*', x), self.headers[ref_tab2]))
                    if name_col:
                        query += f", {self.acronyms[ref_tab2]}.{name_col[0]}"
                    else:
                        tab = ref_tab2
                        val = True
                flag = val

            query += '\nFROM ' + ', '.join(tables_to_select_from)
            query += '\nWHERE ' + ' AND '.join(where_cond_list)
            if table == 'INVOICES':
                query += f' AND ({self.acronyms[ref_tab]}.END_DATE > SYSDATE OR {self.acronyms[ref_tab]}.END_DATE is NULL)'
            query += f'\nORDER BY {self.acronyms[ref_tab]}.{self.headers[ref_tab][0]}'
        return query

    def get_view_fk_query(self, tab, fk_col):
        where_cond_list = []
        select_col_list = []
        tables_to_select_from = []

        def rec(tb):
            for h_name in self.headers[tb]:
                for key in self.fk[tb]:
                    if (tab == tb and h_name == fk_col) or (tab != tb):
                        if h_name == key[0]:
                            where_cond_list.append(f'{self.acronyms[tb]}.{h_name}={self.acronyms[key[1]]}.{h_name}')
                            t_name = f'{key[1]} {self.acronyms[key[1]]}'
                            if t_name not in tables_to_select_from:
                                tables_to_select_from.append(t_name)

                            col = list(filter(lambda x: re.search('.*NAME.*', x), get_table_details(key[1])))
                            if bool(col):
                                add_unique(select_col_list, f'{self.acronyms[key[1]]}.{self.headers[key[1]][0]}')
                                add_unique(select_col_list, f'{self.acronyms[key[1]]}.{col[0]}')
                            else:
                                rec(key[1])

        ref_tab = self.get_tab_fk(tab, fk_col)

        select_col_list.append(f'{self.acronyms[ref_tab]}.{self.headers[ref_tab][0]}')
        rec(tab)

        tables_to_select_from.append(f'{tab} {self.acronyms[tab]}')
        if 'ID' not in select_col_list[0]:
            query = 'SELECT ' + ', '.join(select_col_list) + '\nFROM ' + ', '.join(tables_to_select_from)
        else:
            query = 'SELECT DISTINCT ' + ', '.join(select_col_list) + '\nFROM ' + ', '.join(tables_to_select_from)
        query += '\nWHERE ' + ' AND '.join(where_cond_list)
        query += f'\nORDER BY {select_col_list[0]}'

        return query

    def get_view_query(self, tab: str, condition: str):
        if not bool(self.fk[tab]):
            query = f'SELECT * FROM {tab}' + (f' WHERE {condition}' if condition else condition)
            query += f' ORDER BY {self.headers[tab][0]}'
        else:
            where_cond_list = []
            select_col_list = []
            tables_to_select_from = []
            fk_cols = self.get_fk_cols(tab)

            def rec(tb):
                for h_name in self.headers[tb]:
                    if tb == tab and h_name not in fk_cols:
                        select_col_list.append(f'{self.acronyms[tab]}.{h_name}')
                    else:
                        for elem in self.fk[tb]:
                            if h_name == elem[0]:
                                where_cond_list.append(
                                    f'{self.acronyms[tb]}.{h_name}={self.acronyms[elem[1]]}.{h_name}')
                                t_name = f'{elem[1]} {self.acronyms[elem[1]]}'
                                if t_name not in tables_to_select_from:
                                    tables_to_select_from.append(t_name)

                                if tb == 'SERVICES_DESCRIPTIONS':
                                    select_col_list.append(f'{self.acronyms[elem[1]]}.ID_SERVICE')

                                col = list(filter(lambda x: re.search('.*NAME.*', x), self.headers[elem[1]]))
                                if bool(col):
                                    col_name = elem[1].split('_')[0][:-1].lower()
                                    select_col_list.append(f'{self.acronyms[elem[1]]}.{col[0]} {col_name}')
                                else:
                                    rec(elem[1])

            rec(tab)

            tables_to_select_from.append(f'{tab} {self.acronyms[tab]}')

            query = 'SELECT ' + ', '.join(select_col_list) + '\nFROM ' + ', '.join(tables_to_select_from)
            query += '\nWHERE ' + ' AND '.join(where_cond_list)
            query += (f' AND {condition}' if condition else condition)
            query += f' ORDER BY {self.acronyms[tab]}.{self.headers[tab][0]}'

        return query

    def get_header(self, tab):
        return self.headers[tab]

    def get_data_type(self, tab):
        return self.data_types[tab]


class UiMainwindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.sql_tables: Tables = None
        self.tables: dict[str, QTableWidget] = {}
        self.tabs_widgets: dict[str, QWidget] = {}
        self.table_operations: dict[str, list[str]] = {}
        self.option_widgets: dict[str, QTabWidget] = {}
        self.ui_elements: dict[str, dict[str, list]] = {}
        self.table_buttons: dict[str, list[QPushButton]] = {}
        self.unlocked_rows: dict[str, list[int]] = {}
        self.changed_items_rows: dict[str, dict[int, set[int]]] = {}
        self.tables_headers: dict[str, list[str]] = {}
        self.result_label: dict[str, QLabel] = {}
        self.last_view_condition: dict[str, str] = {}

        self.resize(WIN_WIDTH, WIN_HEIGHT)
        self.setWindowTitle("BD App")

        self.tabWidget = QTabWidget(self)
        self.tabWidget.setMinimumHeight(WIN_HEIGHT)

        self.get_op_tables()
        self.tab_list = list(map(lambda y: y.upper(), self.table_operations.keys()))

        flag = True
        while flag:
            log = LogInDialog()
            if log.exec():
                if type(msgQueue.get()) == bool:
                    try:
                        self.sql_tables: Tables = Tables(self.tab_list)
                        self.setup()
                        flag = False
                    except cx_Oracle.DatabaseError:
                        question = QMessageBox.question(self, 'Confirm', 'The account is invalid... Try again?',
                                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                                        QMessageBox.StandardButton.Yes)
                        if not question:
                            exit(0)
            else:
                exit(0)

    def setup(self):
        for tab in self.tab_list:
            self.tabs_widgets[tab] = QWidget()
            self.tabWidget.addTab(self.tabs_widgets[tab], tab)
            self.tabWidget.currentChanged.connect(partial(self.set_view, tab))
            # add operations
            operations = QTabWidget(self.tabs_widgets[tab])
            operations.setMinimumHeight(WIN_HEIGHT)
            operations.adjustSize()

            for index in range(2):
                item_name = self.table_operations[tab][index]
                wid = QWidget(operations)
                operations.addTab(wid, item_name)
                operations.setMinimumWidth(WIN_WIDTH)
                self.option_widgets[tab] = operations

                self.result_label[tab + ADD] = QLabel('', operations)
                self.result_label[tab + ADD].setWordWrap(True)
                self.result_label[tab + VIEW] = QLabel('')
                self.result_label[tab + VIEW].setWordWrap(True)

            operations.setCurrentIndex(1)
            operations.currentChanged.connect(partial(self.do_operation, tab, operations))

            self.table_buttons[tab] = list()
            self.unlocked_rows[tab] = list()
            self.changed_items_rows[tab] = {}
            self.tables_headers[tab] = list()

        for tab in self.tab_list:
            self.create_elements(tab, self.table_operations[tab][0:2])

        self.tabWidget.setCurrentIndex(0)
        self.set_view(self.tab_list[0])

        self.show()

    def create_elements(self, tab, args: list):
        self.ui_elements[tab] = {}
        for name in args:
            self.ui_elements[tab][name] = list()

    def do_operation(self, tab: str, operations: QTabWidget):
        current_op = operations.tabText(operations.currentIndex())
        if current_op == ADD:
            self.set_add(tab)
        else:
            self.set_view(tab)
        self.set_visible(tab, current_op)

    def set_visible(self, tab, current_op):
        elements = self.ui_elements[tab][current_op]
        value_to_set = True
        for widget in elements:
            if isinstance(widget, tuple):
                widget[0].setVisible(value_to_set)
                widget[1].setVisible(value_to_set)
            else:
                widget.setVisible(value_to_set)

    def set_in_position(self, tab, name):

        wid = self.option_widgets[tab].widget(self.table_operations[tab].index(name))

        layout = wid.layout()
        row = 0
        row2 = 0
        if not layout:
            layout = QGridLayout(wid)
            layout.setVerticalSpacing(10)
            layout.setHorizontalSpacing(20)
            layout.setContentsMargins(20, 30, 30, 30)
            layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            layout.setColumnMinimumWidth(0, 100)
            wid.setLayout(layout)
        else:
            while layout.count():
                item = layout.takeAt(0)
                item.widget().setVisible(False)
                layout.removeItem(item)
            layout.update()

        for elem in self.ui_elements[tab][name]:
            layout.setRowMinimumHeight(row, obj_h)
            if isinstance(elem, tuple):
                layout.addWidget(elem[0], row, 0)
                layout.addWidget(elem[1], row, 1)
                row += 1
            elif name == VIEW and isinstance(elem, QPushButton):
                layout.addWidget(elem, row2, 2)
                row2 += 1
            elif isinstance(elem, QTableWidget):
                layout.addWidget(elem, row, 0, 1, 0)
                # layout.setRowMinimumHeight(row, self.height())
                row += 1
            else:
                layout.addWidget(elem, row, 0)
                row += 1

        layout.setRowStretch(row + 1, 1)
        layout.setColumnStretch(3, 1)

        self.set_visible(tab, name)
        layout.update()

    def set_add(self, tab):
        parent = self.option_widgets[tab].widget(self.table_operations[tab].index(ADD))

        fk_cols = self.sql_tables.get_fk_cols(tab)
        data_types = self.sql_tables.get_data_type(tab)
        tab_header = self.sql_tables.get_header(tab)

        if self.ui_elements[tab][ADD]:
            self.ui_elements[tab][ADD].clear()

        for index in range(len(tab_header)):
            col_name = tab_header[index]
            if col_name != 'PAYMENT':
                if col_name in fk_cols:
                    if tab != 'SERVICES_DESCRIPTIONS':
                        query = self.sql_tables.get_add_fk_query(tab, tab_header[index])
                    else:
                        query = f"SELECT id_service || '. ' || name from services " \
                                f"where id_service not in (select id_service from services_descriptions)"

                    fk_data = []

                    cr = c.execute(query)
                    for val in cr:
                        lst = map(str, val)
                        fk_data.append('. '.join(lst))
                    elem = get_combobox(parent, col_name, obj_size1, True, fk_data, True)

                    self.ui_elements[tab][ADD].append((QLabel(col_name, parent), elem))

                elif 'ID' in col_name:
                    pass
                else:
                    elem = get_elem(data_types[index], parent, obj_size2)
                    if isinstance(elem, QLineEdit) and elem.objectName() != 'DATE':
                        elem.setPlaceholderText(col_name)

                    if col_name == 'END_DATE':
                        btn = get_button(parent, col_name, obj_size1)
                        btn.setCheckable(True)
                        btn.clicked.connect(partial(set_dedit_dimmed, btn, elem))
                        elem.setEnabled(False)
                        self.ui_elements[tab][ADD].append((btn, elem))
                    else:
                        self.ui_elements[tab][ADD].append((QLabel(col_name, parent), elem))

        add_btn = get_button(parent, 'Insert', obj_size1, self.do_add_op, [tab])
        self.ui_elements[tab][ADD].append(add_btn)

        self.ui_elements[tab][ADD].append(self.result_label[tab + ADD])
        self.set_in_position(tab, ADD)

    def set_view(self, tab):
        self.option_widgets[tab].setCurrentIndex(1)
        parent = self.option_widgets[tab].widget(self.table_operations[tab].index(VIEW))
        self.result_label[tab + VIEW].setText('')
        self.result_label[tab + ADD].setText('')

        if self.ui_elements[tab][VIEW]:
            self.ui_elements[tab][VIEW].clear()

        tab_header = ['ALL']
        tab_header.extend(self.sql_tables.get_header(tab))

        elem = get_combobox(parent, None, obj_size1, False, tab_header, False)
        elem.activated.connect(partial(self.do_view_op, tab, elem))

        label = QLabel('Filter by', parent)
        label.setFixedWidth(obj_size1.width())
        self.ui_elements[tab][VIEW].append((label, elem))

        self.ui_elements[tab][VIEW].append(self.result_label[tab + VIEW])

        if 'UPDATE' in self.table_operations[tab]:
            btn = get_button(parent, 'UPDATE', obj_size1, self.do_update_op, [tab, VIEW])
            self.ui_elements[tab][VIEW].append(btn)
        if 'DELETE' in self.table_operations[tab]:
            btn = get_button(parent, 'DELETE', obj_size1, self.do_delete_op, [tab, VIEW])
            self.ui_elements[tab][VIEW].append(btn)

        self.tables[tab] = QTableWidget(parent)
        self.tables[tab].setVisible(False)
        self.tables[tab].setMinimumWidth(self.width())
        self.tables[tab].setFixedWidth(self.width() - 50)

        # self.tables[tab].horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Custom)
        self.tables[tab].setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.tables[tab].setStyleSheet('QTableWidget { gridline-color: black }')
        self.ui_elements[tab][VIEW].append(self.tables[tab])

        self.set_in_position(tab, VIEW)

    def do_add_op(self, tab):
        self.result_label[tab + ADD].setText('')
        tab_header = self.sql_tables.get_header(tab)
        values = []
        valid = True
        element = self.result_label[tab + ADD]
        if tab == 'SERVICES_DESCRIPTIONS':
            cols = deepcopy(tab_header)
        else:
            cols = deepcopy(tab_header[1:])

        for elem in self.ui_elements[tab][ADD]:
            if isinstance(elem, tuple):
                if isinstance(elem[1], QPushButton):
                    break
                elif isinstance(elem[1], QComboBox):
                    col_name = elem[0].text()

                    combobox_items = [elem[1].itemText(i) for i in range(elem[1].count())]
                    if elem[1].currentText() in combobox_items:
                        index = elem[1].currentIndex()

                        ref_tab = self.sql_tables.get_tab_fk(tab, col_name)
                        if tab != 'INVOICES':
                            tab_query = f'SELECT {col_name} FROM {ref_tab} ORDER BY {col_name}'
                        else:
                            tab_query = f'SELECT {col_name} FROM {ref_tab} WHERE END_DATE > SYSDATE OR END_DATE is NULL ' \
                                        f'ORDER BY {col_name}'
                        cr = c.execute(tab_query)
                        data = [x[0] for x in cr]

                        values.append(str(data[index]))
                    else:
                        valid = False
                        element.setText('Select values for fields...')
                        break
                else:
                    if isinstance(elem[0], QPushButton):
                        if elem[0].isChecked():
                            try:
                                values.append(str(get_data_from_elem(elem[1])))
                            except:
                                valid = False
                                element.setText('Insert valid data for ' + elem[0].text())
                                break
                        else:
                            cols.remove(elem[0].text())
                    else:
                        try:
                            values.append(str(get_data_from_elem(elem[1])))
                        except:
                            valid = False
                            element.setText('Insert valid data for ' + elem[0].text())
                            break
        if valid:
            if 'PAYMENT' in cols:
                cols.remove('PAYMENT')
            if 'EMAIL' in cols:
                indx = cols.index('EMAIL')
                values[indx] = f'lower({values[indx]})'

            query = f'INSERT INTO {tab}({", ".join(cols)}) VALUES (' + ", ".join(values) + ')'
            try:
                c.execute(query)
                c.commit()
                element.setText('Operation succeeded!')
                self.set_add(tab)
            except cx_Oracle.DatabaseError as e:
                log_err(e)
                element.setText('Operation failed! ' + decode_err(e))

    def do_update_op(self, tab, name):
        elem = self.result_label[tab + name]
        elem.setText('')
        table_header = self.tables_headers[tab]
        header = self.sql_tables.get_header(tab)
        data_types = self.sql_tables.get_data_type(tab)

        valid = False
        invalid_fields = False
        col_name = ''
        aux_unlck_rows = deepcopy(self.unlocked_rows[tab])
        row = None
        for row in aux_unlck_rows:
            lst = []
            aux_chgd_rows = deepcopy(self.changed_items_rows[tab])
            if row in aux_chgd_rows:
                id_value = self.tables[tab].item(row, 1).text()
                for col in aux_chgd_rows[row]:
                    col_name = self.tables_headers[tab][col]
                    try:
                        txt = str(get_data_from_elem(self.tables[tab].cellWidget(row, col)))
                    except:
                        invalid_fields = True
                        break
                    index = header.index(col_name)
                    if txt != "''":
                        if col_name == 'EMAIL':
                            if not re.fullmatch(r'[a-z0-9._%-]+@[a-z0-9._%-]+\.[a-z]{2,4}', txt[1:-1]):
                                invalid_fields = True
                                break
                        if data_types[index][0] == 'DATE':
                            txt = f"TO_DATE({txt}, 'dd.mm.yyyy')"
                    else:
                        txt = f"NULL"
                    lst.append(f'{table_header[col]}={txt}')
                query = f"UPDATE {tab} SET {', '.join(lst)} WHERE {header[0]}={id_value}"
                try:
                    c.execute(query)
                    c.commit()
                    elem.setText('Row updated successfully...')
                    self.unlocked_rows[tab].remove(row)
                    self.changed_items_rows[tab].pop(row)
                    valid = True
                except cx_Oracle.DatabaseError as e:
                    log_err(e)
                    elem.setText('Row could not be updated...' + decode_err(e))
        if invalid_fields:
            elem.setText('Invalid field: ' + col_name + ', row: ' + str(row + 1))
        if valid:
            self.set_table(tab, self.last_view_condition[tab])

    def do_delete_op(self, tab, name):
        self.result_label[tab + VIEW].setText('')
        header = self.sql_tables.get_header(tab)
        refresh = False
        aux_unlck_rows = deepcopy(self.unlocked_rows[tab])
        for row in aux_unlck_rows:
            id_value = self.tables[tab].item(row, 1).text()
            query = f"DELETE FROM {tab} WHERE {header[0]}={id_value}"
            elem = self.result_label[tab + name]
            try:
                c.execute(query)
                c.commit()
                elem.setText('Row deleted successfully...')
                refresh = True
            except cx_Oracle.DatabaseError:
                elem.setText('Row could not be deleted...')
            elem.setVisible(True)

        if refresh:
            self.set_table(tab, self.last_view_condition[tab])

    def do_view_op(self, tab, elem):
        self.result_label[tab + VIEW].setText('')
        parent = self.option_widgets[tab].widget(self.table_operations[tab].index(VIEW))
        selected_col = elem.currentText()

        index = elem.currentIndex()
        self.eliminate_second_element(tab, VIEW)

        if index == 0:
            self.view(tab)
        else:
            index -= 1

            fk_cols = self.sql_tables.get_fk_cols(tab)
            data_types = self.sql_tables.get_data_type(tab)
            tab_header = self.sql_tables.get_header(tab)

            if selected_col not in fk_cols:
                elem = get_elem(data_types[index], parent, obj_size1)
                set_call_back(elem, self.view, [tab, tab_header[index], elem])

            else:
                query = f'SELECT DISTINCT {tab_header[index]} FROM {tab} ORDER BY {tab_header[index]}'
                cr = c.execute(query)
                data = [x[0] for x in cr]

                query = self.sql_tables.get_view_fk_query(tab, tab_header[index])
                cr = c.execute(query)
                fk_data = []
                for inf in cr:
                    lst = map(str, inf)
                    fk_data.append('. '.join(lst))

                elem = get_combobox(parent, None, obj_size1, True, fk_data, True)
                elem.activated.connect(partial(self.view_by_fk, tab, tab_header[index], data, elem))

            label = QLabel('Search data', parent)
            self.ui_elements[tab][VIEW].insert(1, (label, elem))

            self.set_in_position(tab, VIEW)

    def view_by_fk(self, tab: str, col: str, data: list, elem: QComboBox):
        self.result_label[tab + VIEW].setText('')
        try:
            indx = elem.currentIndex()
            cond = f'{self.sql_tables.acronyms[tab]}.{col}={data[indx]}'
            self.set_table(tab, cond)
        except IndexError:
            pass

    def view(self, tab, col=None, elem=None):
        cond = ''
        self.result_label[tab + VIEW].setText('')
        valid = True
        if col and elem:

            has_fk = bool(self.sql_tables.fk[tab])
            value = self.sql_tables.acronyms[tab] + '.' if has_fk else ''

            col_index = self.sql_tables.get_header(tab).index(col)
            d_types = get_data_types(tab)[col_index]
            if d_types[0] == 'VARCHAR':
                data = elem.text().lower()
                if data:
                    data = f"'%{data}%'"
                    cond = f'LOWER({value}{col}) LIKE {data}'
                else:
                    cond = f'{value}{col} IS NULL'
            else:
                try:
                    if d_types[0] == 'DATE':
                        if elem.text():
                            cond = f"{value}{col}={get_data_from_elem(elem)}"
                        else:
                            cond = f'{value}{col} is NULL'
                    else:
                        cond = f'{value}{col}={get_data_from_elem(elem)}'
                except:
                    self.result_label[tab + VIEW].setText('Insert valid data...')
                    valid = False
        if valid:
            self.set_table(tab, cond)

    def set_table(self, tab: str, condition: str = ''):
        parent = self.option_widgets[tab].widget(self.table_operations[tab].index(VIEW))
        query = self.sql_tables.get_view_query(tab, condition)
        table_cr = c.execute(query)
        self.last_view_condition[tab] = condition

        if table_cr:
            data_types = self.sql_tables.get_data_type(tab)
            tab_header = get_cursor_details(table_cr)
            col_count = len(tab_header)
            self.tables[tab].clear()
            self.tables[tab].setColumnCount(col_count + 1)
            tab_header.insert(0, 'Locked')
            self.tables[tab].setHorizontalHeaderLabels(tab_header)
            self.tables_headers[tab] = tab_header

            self.table_buttons[tab].clear()
            self.unlocked_rows[tab].clear()
            self.changed_items_rows[tab].clear()

            query_data: list[tuple] = table_cr.fetchall()
            row_count = len(query_data)
            self.tables[tab].setRowCount(row_count)

            sql_header = self.sql_tables.get_header(tab)

            for c_index in range(col_count + 1):
                for r_index in range(row_count):
                    if c_index == 0:
                        btn = QPushButton(parent)
                        btn.setIcon(locked_icon)
                        btn.setCheckable(True)
                        btn.clicked.connect(partial(self.toggle_lock, btn, tab, r_index))
                        self.table_buttons[tab].append(btn)
                        self.tables[tab].setCellWidget(r_index, c_index, btn)
                    else:
                        if 'ID' not in tab_header[c_index] and tab_header[c_index] in sql_header:
                            dtype_index = sql_header.index(tab_header[c_index])
                            val = query_data[r_index][c_index - 1]
                            elem = get_elem(data_types[dtype_index], value=val if val else '')
                            elem.setEnabled(False)
                            elem.editingFinished.connect(partial(self.value_changed, tab))
                            self.tables[tab].setCellWidget(r_index, c_index, elem)
                        else:
                            item = QTableWidgetItem("%s" % (query_data[r_index][c_index - 1]))
                            self.tables[tab].setItem(r_index, c_index, item)
                            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                            item.setBackground(QColor('lightGray'))
            self.tables[tab].resizeColumnsToContents()

    def toggle_lock(self, btn: QPushButton, tab: str, r_index: int):
        header = self.sql_tables.get_header(tab)
        tab_header = self.tables_headers[tab]
        if btn.isChecked():
            self.unlocked_rows[tab].append(r_index)
            btn.setIcon(unlocked_icon)

            for index in range(1, len(tab_header)):
                if 'ID' not in tab_header[index] and tab_header[index] in header:
                    itm = self.tables[tab].cellWidget(r_index, index)
                    itm.setEnabled(True)
        else:
            try:
                self.unlocked_rows[tab].remove(r_index)
            except ValueError:
                pass
            btn.setIcon(locked_icon)
            for index in range(1, len(tab_header)):
                if 'ID' not in tab_header[index] and tab_header[index] in header:
                    itm = self.tables[tab].cellWidget(r_index, index)
                    itm.setEnabled(False)

    def value_changed(self, tab: str):
        index = self.tables[tab].currentIndex()
        row = index.row()
        col = index.column()
        if row != -1 and col not in [0, 1]:
            if row not in self.changed_items_rows[tab].keys():
                self.changed_items_rows[tab][row] = set()
            self.changed_items_rows[tab][row].add(col)

    def eliminate_second_element(self, tab, name):
        view_elements = self.ui_elements[tab][name]
        if len(view_elements) > 5:
            elem = view_elements.pop(1)
            set_invisible(elem)

    def get_op_tables(self):
        op_file = open('operations.json')
        data: dict[str, dict] = json.load(op_file)
        self.table_operations = {key.upper(): value for key, value in data['tables_operations'].items()}

    def resizeEvent(self, event):
        if self.width() >= WIN_WIDTH:
            for tab in self.tab_list:
                if tab in self.tables:
                    self.tables[tab].setFixedWidth(self.width() - 50)
                    self.option_widgets[tab].setFixedWidth(self.width())
                    self.option_widgets[tab].setFixedHeight(self.height())
        self.tabWidget.setMinimumWidth(self.width())
        if self.height() >= WIN_HEIGHT:
            self.tabWidget.setFixedHeight(self.height())


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    app.setStyleSheet("QLineEdit:disabled{background-color: lightGray; color: black;}"
                      "QSpinBox:disabled{background-color: lightGray; color: black;}"
                      "QDoubleSpinBox:disabled{background-color: lightGray; color: black;}")
    # icons
    locked_icon = QIcon('icons/locked.png')
    unlocked_icon = QIcon('icons/unlocked.png')

    main_win = UiMainwindow()

    sys.exit(app.exec())

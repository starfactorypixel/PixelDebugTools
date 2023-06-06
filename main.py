import datetime
import sys

from PyQt5.QtCore import QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QMessageBox, QWidget, \
    QPushButton, QComboBox, QLabel, QTextEdit, QHBoxLayout, QCheckBox

baudRate = 115200  # НЕ ЗАБУДЬ УСТАНОВИТЬ СКОРОСТЬ ПОРТА !
prefixes = ['+INFO', '+POUT', '+Warning', '+PXL']  # ПРЕФИКСЫ ДОБАВЛЯТЬ СЮДА


class MainWindow(QMainWindow):
    global prefixes, baudRate

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PixelDebugTools (by @ItMan7145)")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.port_layout = QHBoxLayout()
        self.layout.addLayout(self.port_layout)

        self.port_label = QLabel("Выберите порт:", self)
        self.port_layout.addWidget(self.port_label)

        self.port_combo_box = QComboBox(self)
        self.port_layout.addWidget(self.port_combo_box)

        self.refresh_button = QPushButton("Обновить порты", self)
        self.port_layout.addWidget(self.refresh_button)

        self.refresh_button.clicked.connect(self.refresh_ports)

        self.connect_button = QPushButton("Подключиться", self)
        self.port_layout.addWidget(self.connect_button)

        self.connect_button.clicked.connect(self.connect_button_clicked)

        self.disconnect_button = QPushButton("Отключиться", self)
        self.port_layout.addWidget(self.disconnect_button)

        self.disconnect_button.clicked.connect(self.disconnect_button_clicked)

        self.filter_layout = QHBoxLayout()
        self.layout.addLayout(self.filter_layout)

        self.filter_label = QLabel("Фильтр префиксов:", self)
        self.filter_layout.addWidget(self.filter_label)

        self.prefixes = prefixes
        self.prefix_checkboxes = []

        for prefix in self.prefixes:
            checkbox = QCheckBox(prefix, self)
            checkbox.setChecked(False)
            self.filter_layout.addWidget(checkbox)
            self.prefix_checkboxes.append(checkbox)

        self.all_checkbox = QCheckBox("ALL", self)
        self.filter_layout.addWidget(self.all_checkbox)

        self.log_label = QLabel("Логи:", self)
        self.layout.addWidget(self.log_label)

        self.log_text_edit = QTextEdit(self)
        self.layout.addWidget(self.log_text_edit)

        self.clear_button = QPushButton("Очистить", self)
        self.layout.addWidget(self.clear_button)

        self.clear_button.clicked.connect(self.clear_log)

        self.serial = None

    def refresh_ports(self):
        self.port_combo_box.clear()

        ports = QSerialPortInfo.availablePorts()
        for port in ports:
            self.port_combo_box.addItem(port.portName())

    def connect_button_clicked(self):
        port_name = self.port_combo_box.currentText()
        QMessageBox.critical(self, "Ошибка скорости порта", "Установите правильную скорость порта") \
            if baudRate == 0 or type(baudRate) != int else 0
        if port_name:
            try:
                self.serial = QSerialPort()
                self.serial.setPortName(port_name)
                self.serial.setBaudRate(baudRate)
                self.serial.readyRead.connect(self.read_from_serial)

                if self.serial.open(QIODevice.ReadWrite):
                    self.connect_button.setEnabled(False)
                    self.disconnect_button.setEnabled(True)
                    self.refresh_button.setEnabled(False)
                    self.port_combo_box.setEnabled(False)
                    self.port_label.setText(f"Подключен к порту: {port_name}")
                    self.log_text_edit.append(f"[INFO] Подключен к порту: {port_name}\n")
                    self.read_from_serial()
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к порту.")
            except:
                QMessageBox.critical(self, "Ошибка подключения к COM порту", "Ошибка подключения к COM порту")
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите порт для подключения.")

    def disconnect_button_clicked(self):
        if self.serial is not None and self.serial.isOpen():
            self.serial.close()
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.refresh_button.setEnabled(True)
            self.port_combo_box.setEnabled(True)
            self.port_label.setText("Выберите порт:")
            self.log_text_edit.append(f"[INFO] Отключено\n")

    def read_from_serial(self):
        if self.serial is not None and self.serial.isOpen():
            # далее есть костыли (!)
            if self.serial.canReadLine():
                data = self.serial.readLine()
                if data:
                    text = data.data().decode('ascii', errors='ignore').strip()  # или использовать это
                    # text = str(data, 'ascii).strip()  # или это
                    # print(text)
                    self.process_data(text)

    def process_data(self, data):
        if not self.all_checkbox.isChecked():
            for checkbox in self.prefix_checkboxes:
                prefix = checkbox.text()
                if checkbox.isChecked() and data.startswith(prefix):
                    text = f'{datetime.datetime.now()}:    {data}\n'
                    self.log_text_edit.append(text)
                    break
        else:
            text = f'{datetime.datetime.now()}:    {data}\n'
            self.log_text_edit.append(text)

    def clear_log(self):
        self.log_text_edit.clear()

    def showEvent(self, event):
        if event.type() == event.Show:
            self.refresh_ports()

        super(MainWindow, self).showEvent(event)

    def closeEvent(self, event):
        if self.serial is not None and self.serial.isOpen():
            self.serial.close()

        super(MainWindow, self).closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

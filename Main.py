import sys

from PySide6.QtGui import QFont
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, \
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QFileDialog, QDialog
from datetime import datetime


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход")
        self.setFixedSize(400, 200)  # Увеличиваем размер окна

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("Войти")
        login_button.clicked.connect(self.login)

        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)

        # Устанавливаем размер и шрифт для полей ввода
        font = QFont("Arial Black", 12)
        self.username_input.setFont(font)
        self.password_input.setFont(font)

        # Устанавливаем размер и шрифт для кнопки
        login_button.setFont(font)
        login_button.setStyleSheet("font-size: 18px;")  # Изменяем размер кнопки

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Добавьте здесь логику проверки логина и пароля
        if username == "admin" and password == "admin":
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")


class PayrollApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Приложение по учету ЗП")
        self.setFixedSize(1280, 720)  # Установка размера окна

        # Создаем главный виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Создаем вертикальный layout для главного виджета
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Поля для ввода данных о сотруднике
        self.name_input = QLineEdit()
        self.hours_input = QLineEdit()
        self.rate_input = QLineEdit()
        self.calculate_button = QPushButton("Рассчитать и сохранить")

        # Стилизация кнопок и полей ввода
        self.calculate_button.setStyleSheet("background-color: #4CAF50; color: white; border: none; padding: 10px 24px; text-align: center; font-size: 18px; border-radius: 8px;")
        self.name_input.setStyleSheet("font-size: 18px;")
        self.hours_input.setStyleSheet("font-size: 18px;")
        self.rate_input.setStyleSheet("font-size: 18px;")

        # Таблица для отображения списка сотрудников
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Отработано часов", "Заработная плата"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Растягиваем столбцы

        # Кнопка удаления записи
        self.delete_button = QPushButton("Удалить запись")

        # Стилизация кнопки удаления
        self.delete_button.setStyleSheet("background-color: #f44336; color: white; border: none; padding: 10px 24px; text-align: center; font-size: 18px; border-radius: 8px;")

        # Кнопка создания отчета
        self.report_button = QPushButton("Создать отчет")

        # Стилизация кнопки отчета
        self.report_button.setStyleSheet("background-color: #800080; color: white; border: none; padding: 10px 24px; text-align: center; font-size: 18px; border-radius: 8px;")

        # Кнопка для отображения общей зарплаты
        self.total_payroll_button = QPushButton("Общая зарплата")
        self.total_payroll_button.setStyleSheet("background-color: #008080; color: white; border: none; padding: 10px 24px; text-align: center; font-size: 18px; border-radius: 8px;")

        # Добавляем элементы на layout
        layout.addWidget(QLabel("ФИО:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Отработано часов:"))
        layout.addWidget(self.hours_input)
        layout.addWidget(QLabel("Почасовая ставка:"))
        layout.addWidget(self.rate_input)
        layout.addWidget(self.calculate_button)
        layout.addWidget(QLabel("Список сотрудников:"))
        layout.addWidget(self.table)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.report_button)
        layout.addWidget(self.total_payroll_button)

        # Подключение к базе данных SQLite и создание таблицы сотрудников
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("payroll.db")
        if not self.db.open():
            QMessageBox.critical(None, "Ошибка", "Не удалось подключиться к базе данных")
            sys.exit(1)
        self.create_table()

        # Загрузка списка сотрудников
        self.load_employees()

        # Связываем кнопку с обработчиком события
        self.calculate_button.clicked.connect(self.calculate_and_save)
        self.delete_button.clicked.connect(self.delete_employee)
        self.report_button.clicked.connect(self.create_report)
        self.total_payroll_button.clicked.connect(self.show_total_payroll)

        # Обновляем ID при каждом запуске программы
        self.update_ids()


    def create_table(self):
        query = QSqlQuery()
        query.exec("CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT, hours INTEGER, rate REAL)")


    def load_employees(self):
        query = QSqlQuery("SELECT * FROM employees")
        self.table.setRowCount(0)
        while query.next():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(query.value(0))))
            self.table.setItem(row, 1, QTableWidgetItem(query.value(1)))
            self.table.setItem(row, 2, QTableWidgetItem(str(query.value(2))))
            rate = float(query.value(3)) * 0.8  # 20% налога
            total_payroll = float(query.value(2)) * rate
            self.table.setItem(row, 3, QTableWidgetItem(f"{total_payroll:.2f} руб."))


    def calculate_and_save(self):
        name = self.name_input.text()
        hours = self.hours_input.text()
        rate = self.rate_input.text()

        try:
            hours = int(hours)
            rate = float(rate)
        except ValueError:
            QMessageBox.warning(self, "Предупреждение", "Введите корректные данные в поля отработанных часов и почасовой ставки.")
            return

        if not name:
            QMessageBox.warning(self, "Предупреждение", "Заполните поле ФИО.")
            return

        total = hours * rate * 0.8  # 20% налога

        query = QSqlQuery()
        query.prepare("INSERT INTO employees (name, hours, rate) VALUES (:name, :hours, :rate)")
        query.bindValue(":name", name)
        query.bindValue(":hours", hours)
        query.bindValue(":rate", rate)
        if not query.exec():
            QMessageBox.critical(None, "Ошибка", "Не удалось сохранить данные в базе данных")
            return

        self.load_employees()
        QMessageBox.information(None, "Успех", f"Сотрудник {name} успешно добавлен. Заработная плата: {total} руб.")

        # Обновляем ID
        self.update_ids()


    def delete_employee(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(None, "Предупреждение", "Выберите запись для удаления.")
            return

        employee_id = int(self.table.item(selected_row, 0).text())
        query = QSqlQuery(f"DELETE FROM employees WHERE id = {employee_id}")
        if not query.exec():
            QMessageBox.critical(None, "Ошибка", "Не удалось удалить запись из базы данных")
            return

        self.table.removeRow(selected_row)
        self.update_ids()
        self.db.commit()  # Сохраняем изменения в базе данных
        QMessageBox.information(None, "Успех", "Запись успешно удалена.")


    def update_ids(self):
        for row in range(self.table.rowCount()):
            self.table.item(row, 0).setText(str(row + 1))
        # Сохраняем обновленные ID в базе данных
        query = QSqlQuery()
        for row in range(self.table.rowCount()):
            new_id = row + 1
            old_id = int(self.table.item(row, 0).text())
            if old_id != new_id:
                query.exec(f"UPDATE employees SET id = {new_id} WHERE id = {old_id}")
        self.db.commit()


    def create_report(self):
        file_name = f"Отчет_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", file_name, "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w") as file:
                file.write("Отчет о сотрудниках:\n\n")
                total_payroll = 0
                for row in range(self.table.rowCount()):
                    employee_id = row + 1
                    name = self.table.item(row, 1).text()
                    hours = self.table.item(row, 2).text()
                    rate = self.table.item(row, 3).text()
                    file.write(f"ID: {employee_id}, ФИО: {name}, Отработано часов: {hours}, Заработная плата: {rate}\n")
                    total_payroll += float(rate.split()[0])
                file.write(f"\nОбщая зарплата всех сотрудников: {total_payroll} руб.")


    def show_total_payroll(self):
        total_payroll = sum(float(self.table.item(row, 3).text().split()[0]) for row in range(self.table.rowCount()))
        total_payroll -= total_payroll * 0  # Учитываем налог в 20%
        QMessageBox.information(self, "Общая зарплата", f"Общая зарплата всех сотрудников: {total_payroll:.2f} руб.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial Black", 14))  # Установка шрифта для всего приложения

    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.Accepted:
        window = PayrollApp()
        window.show()
        sys.exit(app.exec())

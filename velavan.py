import sys
import sqlite3
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QFormLayout, QStackedWidget, QMessageBox
)
from PySide6.QtCore import Qt

def init_db():
    conn = sqlite3.connect("goods.db")
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goods_receiving (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            production_details TEXT,
            supplier_details TEXT,
            quantity INTEGER,
            unit_of_measurement TEXT,
            rate_per_unit REAL,
            total_rate REAL,
            tax REAL
        )
    ''')

    # Insert default users
    users = [("goods_receiver", "gr@123"), ("viewer", "view@123")]
    for user in users:
        try:
            cursor.execute("INSERT INTO users VALUES (?, ?)", user)
        except sqlite3.IntegrityError:
            pass  # Already exists

    conn.commit()
    conn.close()

class LoginPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QFormLayout()
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login")

        layout.addRow("Username:", self.user_input)
        layout.addRow("Password:", self.pass_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)
        self.login_button.clicked.connect(self.try_login)

    def try_login(self):
        username = self.user_input.text()
        password = self.pass_input.text()

        conn = sqlite3.connect("goods.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            if username == "goods_receiver":
                self.stacked_widget.setCurrentIndex(1)
            else:
                QMessageBox.information(self, "Access Limited", "You are logged in as 'viewer'. No data entry allowed.")
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")

class GoodsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QFormLayout()

        self.production = QLineEdit()
        self.supplier = QLineEdit()
        self.quantity = QLineEdit()
        self.uom = QLineEdit()
        self.rate = QLineEdit()
        self.tax = QLineEdit()

        self.submit_btn = QPushButton("Submit Entry")
        self.submit_btn.clicked.connect(self.save_entry)

        self.layout.addRow("Production Details:", self.production)
        self.layout.addRow("Supplier Details:", self.supplier)
        self.layout.addRow("Quantity:", self.quantity)
        self.layout.addRow("Unit of Measurement:", self.uom)
        self.layout.addRow("Rate per Unit:", self.rate)
        self.layout.addRow("Tax (%):", self.tax)
        self.layout.addWidget(self.submit_btn)

        self.setLayout(self.layout)

    def save_entry(self):
        try:
            qty = int(self.quantity.text())
            rate = float(self.rate.text())
            tax = float(self.tax.text())
            total = qty * rate

            conn = sqlite3.connect("goods.db")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO goods_receiving (
                    production_details, supplier_details, quantity,
                    unit_of_measurement, rate_per_unit, total_rate, tax
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.production.text(),
                self.supplier.text(),
                qty,
                self.uom.text(),
                rate,
                total,
                tax
            ))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Goods entry recorded.")
            self.clear_fields()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numbers for quantity, rate, and tax.")

    def clear_fields(self):
        for widget in [self.production, self.supplier, self.quantity, self.uom, self.rate, self.tax]:
            widget.clear()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Goods Receiving System")
        self.setFixedSize(400, 300)

        self.stack = QStackedWidget()
        self.login_page = LoginPage(self.stack)
        self.goods_page = GoodsPage()

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.goods_page)

        self.setCentralWidget(self.stack)

if __name__ == "__main__":
    init_db()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

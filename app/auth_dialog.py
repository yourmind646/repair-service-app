# QT
from PyQt5.QtWidgets import (
	QVBoxLayout, QHBoxLayout,
	QLabel, QLineEdit, QPushButton, QMessageBox, QDialog
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt

# Models
from models.user import SQLiteUserRepository, User

# Utils
from utils.path_tools import resource_path
from utils.icon_paths import *

# Another
import os, json, base64


class AuthDialog(QDialog):
	def __init__(self, user_repo: SQLiteUserRepository, auth_cache_path = '.auth'):
		super().__init__()
		self.user_repo = user_repo
		self.auth_cache_path = auth_cache_path
		self.user = None
		self.configure_window()
		self.init_ui()
		self.apply_styles()

	def configure_window(self):
		screen = self.screen().availableGeometry()  # Получаем доступное разрешение экрана
		screen_width = screen.width()
		screen_height = screen.height()

		# Пропорциональный расчет размеров окна авторизации
		window_width = int(screen_width * 0.2083)  # 400 / 1920
		window_height = int(screen_height * 0.2314)  # 250 / 1080

		# Применяем настройки
		self.setWindowTitle("RepairService - Auth")
		self.setWindowIcon(QIcon(KEY_ICO))
		self.setFixedSize(window_width, window_height)

	def init_ui(self):
		layout = QVBoxLayout()

		#* Горизонтальная компоновка для текста приветствия
		header_layout = QHBoxLayout()
		
		# Иконка
		icon_label = QLabel()
		pixmap = QPixmap(REPAIR_SHOP_ICO)
		if pixmap.isNull():
			print("Не удалось загрузить иконку. Проверьте путь к файлу.")
		else:
			# Масштабируем иконку до 32x32
			pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
			icon_label.setPixmap(pixmap)
		
		icon_label.setFixedSize(32, 32)  # Устанавливаем размер 32x32 пикселя
		icon_label.setScaledContents(True)  # Масштабирование содержимого по размеру QLabel

		# Текст
		header = QLabel("Добро пожаловать!")
		header.setFont(QFont('Ubuntu', 14, QFont.Bold))
		
		# Добавляем иконку и текст в горизонтальную компоновку
		header_layout.addWidget(icon_label)
		header_layout.addSpacing(5)  # Отступ между иконкой и текстом
		header_layout.addWidget(header)
		header_layout.setAlignment(Qt.AlignCenter)

		# Добавляем горизонтальную компоновку в основную вертикальную компоновку
		layout.addLayout(header_layout)
		#*

		#* Поля для ввода данных
		form_layout = QVBoxLayout()
		
		# Имя пользователя
		user_layout = QHBoxLayout()
		self.label_login = QLabel("Имя пользователя:")
		self.entry_login = QLineEdit()
		user_layout.addWidget(self.label_login)
		user_layout.addWidget(self.entry_login)
		form_layout.addLayout(user_layout)

		# Пароль
		password_layout = QHBoxLayout()
		self.label_password = QLabel("Пароль:")
		self.entry_password = QLineEdit()
		self.entry_password.setEchoMode(QLineEdit.Password)
		password_layout.addWidget(self.label_password)
		password_layout.addWidget(self.entry_password)
		form_layout.addLayout(password_layout)

		# Подтверждение пароля (только для регистрации)
		confirm_layout = QHBoxLayout()
		self.label_confirm = QLabel("Подтвердите пароль:")
		self.entry_confirm = QLineEdit()
		self.entry_confirm.setEchoMode(QLineEdit.Password)
		confirm_layout.addWidget(self.label_confirm)
		confirm_layout.addWidget(self.entry_confirm)
		form_layout.addLayout(confirm_layout)

		layout.addLayout(form_layout)
		layout.addSpacing(20)
		#*

		#* Кнопки Войти и Зарегистрироваться
		buttons_layout = QHBoxLayout()
		self.button_login = QPushButton("Войти")
		self.button_register = QPushButton("Зарегистрироваться")
		buttons_layout.addWidget(self.button_login)
		buttons_layout.addWidget(self.button_register)
		layout.addLayout(buttons_layout)

		self.setLayout(layout)
		#*

		#* Подключение сигналов
		self.button_login.clicked.connect(self.login)
		self.button_register.clicked.connect(self.register)

	def apply_styles(self):
		styles_path = resource_path("resources/styles/dark_theme.css")
		with open(styles_path, "r", encoding = "utf-8") as fp:
			self.setStyleSheet(fp.read())

	def login(self):
		login = self.entry_login.text().strip()
		password = self.entry_password.text().strip()

		if not login or not password:
			QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля!")
			return
		if self.user_repo.verify_user(login, password):
			user_data = self.user_repo.get_user(login)
			print(user_data)
			self.user = User(*user_data, self.user_repo)
			self.save_auth_cache(password)
			QMessageBox.information(self, "Вход выполнен", f"Добро пожаловать, {self.user.login}!")
			self.accept()
		else:
			QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль!")

	def register(self):
		login = self.entry_login.text().strip()
		password = self.entry_password.text().strip()
		confirm_password = self.entry_confirm.text().strip()
		if not login or not password or not confirm_password:
			QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля!")
			return
		if password != confirm_password:
			QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
			return
		if self.user_repo.add_user(login, password):
			user_data = self.user_repo.get_user(login)
			self.user = User(*user_data, user_repo = self.user_repo)
			self.save_auth_cache(password)
			QMessageBox.information(self, "Регистрация", f"Пользователь {self.user.login} успешно зарегистрирован!")
			self.accept()
		else:
			QMessageBox.warning(self, "Ошибка", "Пользователь уже существует!")

	def save_auth_cache(self, password: str):
		"""Сохранение данных авторизации"""
		data = f"{self.user.login}:{password}"
		encoded_data = base64.b64encode(data.encode('utf-8')).decode('utf-8')  # Преобразуем bytes в str

		try:
			with open(self.auth_cache_path, "w") as f:
				f.write(encoded_data)
			print("Данные авторизации успешно сохранены.")
		except OSError as e:
			print(f"Ошибка при сохранении кэша авторизации: {e}")

	@staticmethod
	def load_auth_cache(user_repo: SQLiteUserRepository, auth_cache_path='.auth'):
		if os.path.exists(auth_cache_path):
			try:
				with open(auth_cache_path, 'r') as f:
					encoded_data = f.read()
				
				if not encoded_data:
					print("Отсутствуют данные авторизации в кэше.")
					return None

				decoded_data = base64.b64decode(encoded_data).decode('utf-8')
				login, password = decoded_data.split(':', 1)  # Разделяем на login и password

				if user_repo.verify_user(login, password):
					user_data = user_repo.get_user(login)
					print(*user_data)
					return User(*user_data, user_repo = user_repo)
				else:
					print("Пользователь из кэша не найден в репозитории.")
			except json.JSONDecodeError:
				print("Некорректный формат JSON в кэше авторизации.")
			except (base64.binascii.Error, ValueError) as e:
				print(f"Ошибка декодирования данных авторизации: {e}")
			except OSError as e:
				print(f"Ошибка при работе с файлом кэша: {e}")
		else:
			print("Кэш авторизации не существует.")
		return None

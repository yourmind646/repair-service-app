# QT
from PyQt5.QtWidgets import (
	QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
	QLabel, QPushButton, QListWidget, QMessageBox, QListWidgetItem
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize

# Models
from models.user import User
from models.repair_service import SQLiteServiceRepository, ServiceFactory
from models.booking import Booking

# Utils
from utils.path_tools import resource_path
from utils.icon_paths import *

# Another
import os


class RepairServiceApp(QMainWindow):
	def __init__(self, service_repo: SQLiteServiceRepository, user: User):
		super().__init__()
		self.service_repo = service_repo
		self.user = user
		self.selected_service = None
		self.configure_window()
		self.init_ui()
		self.populate_services()
		self.apply_styles()

	def configure_window(self):
		screen = self.screen().availableGeometry()  # Получаем доступное разрешение экрана
		screen_width = screen.width()
		screen_height = screen.height()

		# Пропорциональный расчет размеров окна
		window_width = int(screen_width * 0.3125)  # 600 / 1920
		window_height = int(screen_height * 0.3704)  # 400 / 1080

		# Применяем настройки
		self.setWindowTitle("RepairService - Main")
		self.setWindowIcon(QIcon(REPAIR_SHOP_ICO))
		self.setFixedSize(QSize(window_width, window_height))

	def init_ui(self):
		# Создаем центральный виджет и устанавливаем его в качестве центрального
		central_widget = QWidget()
		self.setCentralWidget(central_widget)

		# Создаем основной вертикальный layout
		main_layout = QVBoxLayout()

		# Верхняя горизонтальная компоновка для пользователя и VIP статуса
		header_layout = QHBoxLayout()

		# ---- Информация о пользователе ----
		user_info_layout = QHBoxLayout()

		# Иконка пользователя
		user_icon_label = QLabel()
		user_pixmap = QPixmap(USER_ICO)
		if user_pixmap.isNull():
			print("Не удалось загрузить иконку пользователя. Проверьте путь к файлу.")
		else:
			# Масштабируем иконку до 32x32
			user_pixmap = user_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
			user_icon_label.setPixmap(user_pixmap)
		
		user_icon_label.setFixedSize(32, 32)  # Устанавливаем размер 32x32 пикселя
		user_icon_label.setScaledContents(True)  # Масштабирование содержимого по размеру QLabel

		# Текст приветствия
		self.label_welcome = QLabel(f"{self.user.login}")
		self.label_welcome.setFont(QFont('Ubuntu', 14, QFont.Bold))

		# Добавляем иконку и текст в user_info_layout
		user_info_layout.addWidget(user_icon_label)
		user_info_layout.addSpacing(5)  # Отступ между иконкой и текстом
		user_info_layout.addWidget(self.label_welcome)

		# ---- Информация о VIP статусе ----
		vip_info_layout = QHBoxLayout()

		# Иконка VIP уровня
		self.vip_icon_label = QLabel()
		self.vip_icon_label.setToolTip(f"Скидка составляет: {self.user.get_membership_discount() * 100}%")
		vip_icon_path = self.get_vip_icon_path(self.user.membership_level)
		vip_pixmap = QPixmap(vip_icon_path) if vip_icon_path else QPixmap()
		if vip_pixmap.isNull():
			print("Не удалось загрузить иконку VIP уровня. Проверьте путь к файлу.")
			self.vip_icon_label.setText("Нет VIP")
			self.vip_icon_label.setFont(QFont('Ubuntu', 10, QFont.Bold))
		else:
			# Масштабируем иконку до 32x32
			vip_pixmap = vip_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
			self.vip_icon_label.setPixmap(vip_pixmap)
		
		self.vip_icon_label.setFixedSize(32, 32)  # Устанавливаем размер 32x32 пикселя
		self.vip_icon_label.setScaledContents(True)  # Масштабирование содержимого по размеру QLabel

		# Текст VIP статуса
		self.vip_label = QLabel(f"VIP: {self.user.membership_level}")
		self.vip_label.setFont(QFont('Ubuntu', 12, QFont.Bold))
		self.vip_label.setToolTip(f"Скидка составляет: {self.user.get_membership_discount() * 100}%")

		# Добавляем иконку и текст в vip_info_layout
		vip_info_layout.addWidget(self.vip_icon_label)
		vip_info_layout.addSpacing(5)  # Отступ между иконкой и текстом
		vip_info_layout.addWidget(self.vip_label)

		# Добавляем user_info_layout и vip_info_layout в header_layout с промежуточным расширением
		header_layout.addLayout(user_info_layout)
		header_layout.addStretch()  # Заполняет промежуток между пользователем и VIP статусом

		header_layout.addLayout(vip_info_layout)

		# Добавляем header_layout в основной layout
		main_layout.addLayout(header_layout)

		# Список услуг
		self.list_services = QListWidget()
		main_layout.addWidget(self.list_services)

		# Layout для кнопок действий
		action_buttons_layout = QHBoxLayout()

		# Создание кнопки "Оформить заказ" с иконкой
		self.button_process_order = QPushButton("Оформить заказ")
		self.button_process_order.setIcon(QIcon(MONEY_ICO))
		self.button_process_order.setIconSize(QSize(24, 24))  # Устанавливаем размер иконки (по желанию)
		self.button_process_order.setToolTip("Оформите выбранную услугу")
		self.button_process_order.clicked.connect(self.process_order)

		# Создание кнопки "Выйти" с иконкой
		self.button_logout = QPushButton("Выйти")
		self.button_logout.setIcon(QIcon(EXIT_ICO))
		self.button_logout.setIconSize(QSize(24, 24))
		self.button_logout.setToolTip("Выйти из аккаунта")
		self.button_logout.clicked.connect(self.logout)

		# Добавляем кнопки в action_buttons_layout
		action_buttons_layout.addWidget(self.button_process_order)
		action_buttons_layout.addStretch()  # Заполнение пространства между кнопками
		action_buttons_layout.addWidget(self.button_logout)

		# Добавляем action_buttons_layout в основной layout
		main_layout.addLayout(action_buttons_layout)

		# Устанавливаем основной layout для центрального виджета
		central_widget.setLayout(main_layout)

	def get_vip_icon_path(self, vip_level):
		"""Возвращает путь к иконке VIP уровня"""
		vip_icons = {
			"bronze": BRONZE_ICO,
			"silver": SILVER_ICO,
			"gold": GOLD_ICO,
			"platinum": PLATINUM_ICO
		}
		return vip_icons.get(vip_level.lower())

	def apply_styles(self):
		styles_path = resource_path("resources/styles/dark_theme.css")
		with open(styles_path, "r", encoding = "utf-8") as style_fp:
			self.setStyleSheet(style_fp.read())

	def populate_services(self):
		services = self.service_repo.get_services()
		self.list_services.clear()  # Очистка списка перед добавлением новых элементов
		for service in services:
			item = QListWidgetItem(service.get_description())
			item.setData(Qt.UserRole, service.uid)  # Сохраняем ID услуги
			self.list_services.addItem(item)

	def process_order(self):
		current_item = self.list_services.currentItem()
		
		if current_item is None:
			QMessageBox.warning(self, "Ошибка", "Сначала выберите услугу!")
			return
		
		# Предполагается, что данные услуги хранятся в тексте элемента
		selected_service_uid = current_item.data(Qt.UserRole)
		selected_service_data = self.service_repo.get_service(selected_service_uid)
		selected_service = ServiceFactory.create_service(*selected_service_data)

		booking = Booking(self.user, selected_service)
		cost = booking.process_booking()
		self.user.add_spent(cost)

		# update
		vip_icon_path = self.get_vip_icon_path(self.user.membership_level)
		vip_pixmap = QPixmap(vip_icon_path) if vip_icon_path else QPixmap()
		vip_pixmap = vip_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.vip_icon_label.setPixmap(vip_pixmap)
		self.vip_icon_label.setToolTip(f"Скидка составляет: {self.user.get_membership_discount() * 100}%")

		# Текст VIP статуса
		self.vip_label.setText(f"VIP: {self.user.membership_level}")
		self.vip_label.setToolTip(f"Скидка составляет: {self.user.get_membership_discount() * 100}%")

		QMessageBox.information(self, "Заказ оформлен", f"Стоимость: ${cost}")

	def logout(self):
		"""Обработка выхода пользователя"""
		reply = QMessageBox.question(
			self,
			'Выйти',
			'Вы действительно хотите выйти?',
			QMessageBox.Yes | QMessageBox.No,
			QMessageBox.No
		)
		if reply == QMessageBox.Yes:
			os.remove(".auth")
			self.close()
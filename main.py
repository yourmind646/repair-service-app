# QT
from PyQt5.QtWidgets import QApplication, QDialog

# Windows
from app import *

# Models
from models import *

# Utils
from utils import *

# Another
import sys


def main():
	app = QApplication(sys.argv)
	service_repo = SQLiteServiceRepository("services.db")
	user_repo = SQLiteUserRepository("users.db")

	# Проверка авторизационного кеша
	user = AuthDialog.load_auth_cache(user_repo)

	# Проверяем, есть ли услуги в базе данных, и добавляем их, если база пустая
	if not service_repo.get_services():
		services_to_add = [
			PlumbingService(description="Замена крана", cost=50.0),
			ElectricalService(description="Ремонт электропроводки", cost=80.0),
			PlumbingService(description="Устранение утечек", cost=60.0),
			ElectricalService(description="Установка розеток", cost=70.0),
			PlumbingService(description="Чистка труб", cost=55.0),
			ElectricalService(description="Обслуживание электрощитов", cost=90.0),
			PlumbingService(description="Монтаж водопровода", cost=65.0),
			ElectricalService(description="Установка светильников", cost=75.0),
			PlumbingService(description="Ремонт сифонов", cost=45.0),
			ElectricalService(description="Диагностика электрооборудования", cost=85.0)
		]

		for service in services_to_add:
			service_repo.add_service(service)

	if user:
		# Если пользователь уже авторизован, открыть главное окно
		main_window = RepairServiceApp(service_repo, user)
		main_window.show()
	else:
		# Иначе показать диалог авторизации/регистрации
		auth_dialog = AuthDialog(user_repo)
		if auth_dialog.exec_() == QDialog.Accepted and auth_dialog.user:
			main_window = RepairServiceApp(service_repo, auth_dialog.user)
			main_window.show()
		else:
			# Если авторизация не прошла, завершить приложение
			sys.exit()

	sys.exit(app.exec_())


if __name__ == "__main__":
	main()

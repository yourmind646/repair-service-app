import os, sys, unittest, uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models import *


class TestRepairServices(unittest.TestCase):

	def test_plumbing_service(self):
		service = PlumbingService()
		self.assertIsInstance(service, PlumbingService)
		self.assertTrue(service.get_uid())
		self.assertEqual(service.get_description(), "Сантехнические работы")
		self.assertEqual(service.get_cost(), 50.0)

	def test_electrical_service(self):
		service = ElectricalService()
		self.assertIsInstance(service, ElectricalService)
		self.assertTrue(service.get_uid())
		self.assertEqual(service.get_description(), "Электромонтажные работы: ремонт проводки и электрощитков.")
		self.assertEqual(service.get_cost(), 80.0)

	def test_service_factory_plumbing(self):
		uid = str(uuid.uuid4())
		service = ServiceFactory.create_service(uid=uid, service_type="PlumbingService")
		self.assertIsInstance(service, PlumbingService)
		self.assertEqual(service.get_uid(), uid)
		self.assertEqual(service.get_description(), "Сантехнические работы")
		self.assertEqual(service.get_cost(), 50.0)

	def test_service_factory_electrical(self):
		uid = str(uuid.uuid4())
		service = ServiceFactory.create_service(uid=uid, service_type="ElectricalService")
		self.assertIsInstance(service, ElectricalService)
		self.assertEqual(service.get_uid(), uid)
		self.assertEqual(service.get_description(), "Электромонтажные работы: ремонт проводки и электрощитков.")
		self.assertEqual(service.get_cost(), 80.0)

	def test_sqlite_service_repository(self):
		# Создаем тестовую базу данных в памяти
		db_name = ":memory:"
		repo = SQLiteServiceRepository(db_name)

		# Создаем сервисы
		plumbing_service = PlumbingService()
		electrical_service = ElectricalService()

		# Добавляем сервисы в репозиторий
		repo.add_service(plumbing_service)
		repo.add_service(electrical_service)

		# Получаем все сервисы из репозитория
		services = repo.get_services()
		self.assertEqual(len(services), 2)

		service_uids = [service.get_uid() for service in services]
		self.assertIn(plumbing_service.get_uid(), service_uids)
		self.assertIn(electrical_service.get_uid(), service_uids)

		# Проверяем получение конкретного сервиса по UID
		retrieved_service = repo.get_service(plumbing_service.get_uid())
		self.assertIsNotNone(retrieved_service)
		retrieved_service = ServiceFactory.create_service(*retrieved_service)
		self.assertEqual(retrieved_service.get_uid(), plumbing_service.get_uid())
		self.assertEqual(retrieved_service.get_description(), plumbing_service.get_description())
		self.assertEqual(retrieved_service.get_cost(), plumbing_service.get_cost())

		# Проверяем, что запрос несуществующего сервиса возвращает None
		non_existent_service = repo.get_service("non-existent-uid")
		self.assertIsNone(non_existent_service)


if __name__ == '__main__':
	unittest.main()

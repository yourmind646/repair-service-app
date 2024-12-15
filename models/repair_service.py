# DB
import sqlite3

# Another
from abc import ABC, abstractmethod
import uuid


class RepairService(ABC):
	def __init__(self, uid: str = None, description: str = "", cost: float = 0.0):
		self.uid = uid or str(uuid.uuid4())
		self.description = description
		self.cost = cost

	@abstractmethod
	def get_uid(self) -> str:
		pass

	@abstractmethod
	def get_description(self) -> str:
		pass

	@abstractmethod
	def get_cost(self) -> float:
		pass
	

class PlumbingService(RepairService):
	def __init__(self, uid: str = None, description: str = "Сантехнические работы", cost: float = 50.0):
		super().__init__(uid, description, cost)

	def get_uid(self) -> str:
		return self.uid

	def get_description(self) -> str:
		return self.description

	def get_cost(self) -> float:
		return self.cost


class ElectricalService(RepairService):
	def __init__(self, uid: str = None, description: str = "Электромонтажные работы: ремонт проводки и электрощитков.", cost: float = 80.0):
		super().__init__(uid, description, cost)

	def get_uid(self) -> str:
		return self.uid

	def get_description(self) -> str:
		return self.description

	def get_cost(self) -> float:
		return self.cost
	
class ServiceFactory:
	@staticmethod
	def create_service(uid: str, service_type: str, description: str = "", cost: float = 0.0) -> RepairService:
		service_type = service_type.replace('Service', '').lower()
		if service_type.lower() == "plumbing":
			return PlumbingService(uid=uid, description=description or "Сантехнические работы", cost = cost or 50.0)
		elif service_type.lower() == "electrical":
			return ElectricalService(uid=uid, description=description or "Электромонтажные работы: ремонт проводки и электрощитков.", cost = cost or 80.0)
		else:
			raise ValueError(f"Unknown service type: {service_type}")
		
class ServiceRepository(ABC):
	@abstractmethod
	def add_service(self, service: RepairService):
		pass

	@abstractmethod
	def get_services(self) -> list:
		pass


class SQLiteServiceRepository(ServiceRepository):
	def __init__(self, db_name: str):
		self.connection = sqlite3.connect(db_name)
		self.create_table()

	def create_table(self):
		with self.connection:
			self.connection.execute('''
				CREATE TABLE IF NOT EXISTS services (
					id TEXT PRIMARY KEY,
					type TEXT NOT NULL,
					description TEXT NOT NULL,
					cost REAL NOT NULL
				)
			''')
			self.connection.commit()

	def add_service(self, service: RepairService):
		with self.connection:
			self.connection.execute('''
				INSERT INTO services (id, type, description, cost) 
				VALUES (?, ?, ?, ?)
			''', (service.get_uid(), service.__class__.__name__, service.get_description(), service.get_cost()))
			self.connection.commit()

	def get_services(self) -> list:
		cursor = self.connection.cursor()
		cursor.execute('SELECT id, type, description, cost FROM services')
		rows = cursor.fetchall()
		services = []
		for uid, service_type, description, cost in rows:
			service = ServiceFactory.create_service(
				service_type=service_type.replace('Service', '').lower(),
				uid=uid,
				description=description,
				cost=cost
			)
			services.append(service)
		return services
	
	def get_service(self, uid: str) -> list:
		cursor = self.connection.cursor()
		cursor.execute('SELECT * FROM services WHERE id = ?', (uid,))
		row = cursor.fetchone()
		return row

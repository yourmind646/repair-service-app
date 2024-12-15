# DB
import sqlite3

# Another
from abc import ABC, abstractmethod
import bcrypt


class UserRepository(ABC):

	@abstractmethod
	def create_table(self) -> None:
		...

	@abstractmethod
	def is_login_exists(self, login: str) -> bool:
		...

	@abstractmethod
	def add_user(self, login: str, password: str) -> bool:
		...

	@abstractmethod
	def get_user_password_hash(self, login: str) -> bool:
		...

	@abstractmethod
	def verify_user(self, password: str) -> bool:
		...


# Репозиторий пользователей для хранения и проверки пользователей
class SQLiteUserRepository(UserRepository):
	def __init__(self, db_name):
		self.connection = sqlite3.connect(db_name)
		self.create_table()
	
	def create_table(self) -> None:
		with self.connection:
			self.connection.execute('''
				CREATE TABLE IF NOT EXISTS users (
					login TEXT NOT NULL PRIMARY KEY,
					password_hash TEXT NOT NULL,
					total_spent REAL NOT NULL,
					membership_level TEXT NOT NULL
				)
			''')
			self.connection.commit()

	def is_login_exists(self, login: str) -> bool:
		with self.connection:
			cursor = self.connection.execute(
				"SELECT 1 FROM users WHERE login = ? LIMIT 1", (login,)
			)
			return cursor.fetchone() is not None

	def add_user(self, login: str, password: str) -> bool:
		if self.is_login_exists(login):
			return False
		
		with self.connection:
			self.connection.execute('''
				INSERT INTO users (login, password_hash, total_spent, membership_level) 
				VALUES (?, ?, ?, ?)
			''', (login, self.hash_password(password), 0.0, "Bronze"))
			self.connection.commit()
		return True

	def get_user(self, login: str) -> list:
		cursor = self.connection.cursor()
		cursor.execute('SELECT * FROM users WHERE login = ?', (login,))
		row = cursor.fetchall()

		if row:
			return row[0]
		return None

	def get_user_password_hash(self, login: str) -> str:
		cursor = self.connection.cursor()
		cursor.execute('SELECT password_hash FROM users WHERE login = ?', (login,))
		row = cursor.fetchone()

		if row:
			return row[0]
		return None
	  
	def get_user_membership_level(self, login: str) -> str:
		cursor = self.connection.cursor()
		cursor.execute('SELECT membership_level FROM users WHERE login = ?', (login,))
		row = cursor.fetchone()

		if row:
			return row[0]
		return None

	def verify_user(self, login: str, password: str) -> bool:
		if not self.is_login_exists(login):
			return False

		stored_hash = self.get_user_password_hash(login)
		if stored_hash is None:
			return False

		return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

	@staticmethod
	def hash_password(password: str) -> bytes:
		# Генерируем соль и хешируем пароль
		salt = bcrypt.gensalt()
		return bcrypt.hashpw(password.encode('utf-8'), salt)
	
	def update_spending(self, login: str, amount: float) -> bool:
		"""
		Инкрементирует поле total_spent на заданную сумму и обновляет уровень членства, если необходимо.

		:param login: Логин пользователя.
		:param amount: Сумма для добавления к total_spent.
		:return: True, если обновление прошло успешно, False в противном случае.
		"""
		if not self.is_login_exists(login):
			return False

		try:
			with self.connection:
				# Получаем текущую сумму
				cursor = self.connection.execute(
					"SELECT total_spent FROM users WHERE login = ?", (login,)
				)
				row = cursor.fetchone()
				if row is None:
					return False
				current_total = row[0]

				# Инкрементируем сумму
				new_total = current_total + amount

				# Определяем новый уровень членства
				new_level = User.determine_membership_level(new_total)

				# Обновляем базу данных
				self.connection.execute('''
					UPDATE users 
					SET total_spent = ?, membership_level = ?
					WHERE login = ?
				''', (new_total, new_level, login))
				self.connection.commit()
			return True
		except sqlite3.Error as e:
			print(f"Ошибка при обновлении расходов пользователя: {e}")
			return False


# Класс пользователя
class User():
	def __init__(
		self,
		login: str,
		password_hash: str,
		total_spent: float,
		membership_level: str,
		user_repo: SQLiteUserRepository
	):
		self.login = login
		self.password_hash = password_hash
		self.membership_level = membership_level
		self.total_spent = total_spent
		self.user_repo = user_repo
	
	def get_membership_discount(self):
		if self.membership_level == "Platinum":
			return 0.15
		elif self.membership_level == "Gold":
			return 0.1
		elif self.membership_level == "Silver":
			return 0.05
		else:
			return 0.0
		
	def add_spent(self, sum: float) -> None:
		self.total_spent += sum
		self.user_repo.update_spending(self.login, sum)
		self.membership_level = self.determine_membership_level(self.total_spent)

	@staticmethod
	def determine_membership_level(total_spent: float) -> str:
		"""
		Определяет уровень членства на основе общей суммы расходов.

		:param total_spent: Общая сумма расходов пользователя.
		:return: Строка с уровнем членства.
		"""
		if total_spent >= 1000:
			return "Platinum"
		elif total_spent >= 500:
			return "Gold"
		elif total_spent >= 200:
			return "Silver"
		else:
			return "Bronze"

import os, sys, bcrypt, unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.user import SQLiteUserRepository 


class TestSQLiteUserRepository(unittest.TestCase):
	DB_FILE = ":memory:"

	def setUp(self):
		"""Настраиваем тестовую среду перед каждым тестом."""
		self.repo = SQLiteUserRepository(self.DB_FILE)

	def tearDown(self):
		"""Очищаем тестовую базу данных после каждого теста."""
		self.repo.connection.close()  # Закрытие соединения
		if os.path.exists(self.DB_FILE):
			os.remove(self.DB_FILE)

	def test_create_table(self):
		"""Проверяем создание таблицы."""
		with self.repo.connection:
			tables = self.repo.connection.execute(
				"SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
			).fetchone()
		self.assertIsNotNone(tables, "Таблица users не создана.")

	def test_add_user_success(self):
		"""Проверяем успешное добавление нового пользователя."""
		result = self.repo.add_user("test_user", "secure_password")
		self.assertTrue(result, "Пользователь должен быть добавлен успешно.")
		self.assertTrue(self.repo.is_login_exists("test_user"), "Логин должен существовать.")

	def test_add_user_duplicate(self):
		"""Проверяем, что добавление пользователя с существующим логином не выполняется."""
		self.repo.add_user("test_user", "secure_password")
		result = self.repo.add_user("test_user", "another_password")
		self.assertFalse(result, "Повторное добавление пользователя должно быть запрещено.")

	def test_get_user_password_hash(self):
		"""Проверяем получение хэша пароля пользователя."""
		self.repo.add_user("test_user", "secure_password")
		password_hash = self.repo.get_user_password_hash("test_user")
		self.assertIsNotNone(password_hash, "Хэш пароля должен быть получен.")
		self.assertTrue(
			bcrypt.checkpw("secure_password".encode("utf-8"), password_hash),
			"Хэш пароля должен совпадать с исходным паролем.",
		)

	def test_verify_user_valid(self):
		"""Проверяем верификацию пользователя с правильным паролем."""
		self.repo.add_user("test_user", "secure_password")
		is_verified = self.repo.verify_user("test_user", "secure_password")
		self.assertTrue(is_verified, "Пользователь с правильным паролем должен быть верифицирован.")

	def test_verify_user_invalid(self):
		"""Проверяем, что верификация не проходит с неправильным паролем."""
		self.repo.add_user("test_user", "secure_password")
		is_verified = self.repo.verify_user("test_user", "wrong_password")
		self.assertFalse(is_verified, "Пользователь с неправильным паролем не должен быть верифицирован.")

	def test_update_spending_successful(self):
		"""Проверяем, что обновление суммы total_spent работает корректно."""
		self.repo.add_user("test_user", "secure_password")
		self.repo.update_spending("test_user", 150.0)
		user = self.repo.get_user("test_user")
		self.assertEqual(user[2], 150.0, "Сумма total_spent должна обновиться до 150.0.")

	def test_update_spending_invalid_user(self):
		"""Проверяем, что невозможно обновить сумму для несуществующего пользователя."""
		result = self.repo.update_spending("non_existent_user", 100.0)
		self.assertFalse(result, "Обновление для несуществующего пользователя должно возвращать False.")

	def test_membership_upgrade(self):
		"""Проверяем корректное обновление уровня членства при увеличении total_spent."""
		self.repo.add_user("test_user", "secure_password")
		self.repo.update_spending("test_user", 500.0)
		membership_level = self.repo.get_user_membership_level("test_user")
		self.assertEqual(membership_level, "Gold", "Уровень членства должен обновиться до 'Gold'.")
	
	def test_is_login_exists(self):
		"""Проверяем существование логина в базе данных."""
		self.repo.add_user("test_user", "secure_password")
		self.assertTrue(self.repo.is_login_exists("test_user"))
		self.assertFalse(self.repo.is_login_exists("non_existent_user"))


if __name__ == "__main__":
	unittest.main()

import os, sys


def resource_path(relative_path):
	"""Получает абсолютный путь к ресурсу, работает как в режиме разработки, так и при упаковке PyInstaller."""
	try:
		# PyInstaller создает временную папку с атрибутом _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)

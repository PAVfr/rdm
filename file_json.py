
import os
import json


class EasyFileJson:
	def __init__(self, path="EasyFileJson.json"):
		"""
		:param path: str | list
		:type path: str or list
		"""
		self.path = path
		self.encoding = "utf-8"
		self.__data: dict = {}

	def data(self):
		return self.__data

	def load(self):
		"""Conversion d'un fichier JSON en dictionnaire Python. """
		with open(self.path, mode="r", encoding=self.encoding) as file:
			self.__data = json.loads(file.read())
		return self

	def loads(self, s: str):
		"""Conversion d'une chaîne JSON (str) en un dictionnaire Python. """
		self.__data = json.loads(s)
		return self

	def save(self, sort_keys=False, indent=4, ensure_ascii=None):
		"""
		Écrase le dictionnaire Python dans le fichier JSON.
		Créé les dossiers récursifs s'ils n'existent pas.

		:type sort_keys: bool
		:type indent: int
		:type ensure_ascii: bool
		"""
		with open(self.path, mode="w", encoding=self.encoding) as file:
			json.dump(self.__data, file, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii)

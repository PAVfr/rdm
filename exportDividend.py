
import requests
from bs4 import BeautifulSoup
import pandas

from file_json import EasyFileJson


s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0"


class ExportDividend:
	def __init__(self):
		self.fileEnterprise = EasyFileJson("bdd_entreprise.json").load()
		self.fileDividend = EasyFileJson("bdd_dividend.json")
		try:
			self.fileDividend.load()
		except FileNotFoundError:
			pass

	def updateNewAllEnterprise(self):
		for ticker in self.fileEnterprise.data().keys():
			self.updateNewOneEnterprise(ticker=ticker)

	def updateNewOneEnterprise(self, ticker: str):
		# Récupère les données du site
		data: dict = self.fileEnterprise.data().get(ticker)
		URL = f"""https://rendementbourse.com{data.get("HREF_RENDEMENTBOURSE")}/dividendes"""
		resp = s.get(URL).text.encode("utf-8")
		soup = BeautifulSoup(resp, features="html.parser")
		table = soup.find("table", attrs={"id": "allDivs"})
		lines = []
		try:
			for line in [[v.text.strip().replace("\xa0€", "") for v in line.find_all("td")] for line in table.find("tbody").find_all("tr")]:
				lines.append({
					"TICKER": ticker,
					"YEAR": line[0],
					"DATE": line[1],
					"AMOUNT": line[2],
					"TYPE": line[3] if line[3] != "" else None
					})
			# Inverse le sens du tableau du plus ancien vers le plus récent
			lines.reverse()
		except AttributeError:
			pass

		if self.fileDividend.data().get(ticker) is None or not lines:
			# Si le TICKER n'existe pas ajoute la liste
			self.fileDividend.data()[ticker] = lines
		else:
			ticker_datas: list = self.fileDividend.data().get(ticker)
			for line in lines:
				# Vérifie que la date n'existe pas (pour pouvoir modifier la bdd manuellement
				if line.get("DATE") not in [date.get("DATE") for date in ticker_datas]:
					ticker_datas.append(line)
		# Sauvegarde le fichier
		self.fileDividend.save(sort_keys=True)

	def exportCSV(self, path="export_dividend.csv"):
		data = self.fileDividend.data()
		values = []
		for value in data.values():
			for line in value:
				values.append(line)

		dataframe1 = pandas.DataFrame(values, columns=values[0].keys())
		dataframe1.to_csv(path, index=None)


if __name__ == '__main__':
	exp = ExportDividend()
	# exp.updateNewAllEnterprise()
	exp.exportCSV()


import re
import time
import requests
from bs4 import BeautifulSoup
import pandas

from file_json import EasyFileJson

FILE_ADD_HREF = open("_ADD_HREF.txt", mode="r").read()
FILE_IGNORE_CODE = open("_IGNORE_CODE.txt", mode="r").read()

s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0"


class BousoBankSite:
	@staticmethod
	def searchHREF(ISIN: str, place="Euronext Paris"):
		resp = s.get(url=f"https://www.boursorama.com/recherche/ajax?query={ISIN}&searchId=")
		soup = BeautifulSoup(resp.text, features="html.parser")

		for result in soup.find_all("a"):
			p = result.find("p")
			if p is None:
				continue
			elif place == str(p.text).strip():
				return result.get("href")


class RendementBourseSite:
	def __init__(self):
		self.fileJson = EasyFileJson("bdd_entreprise.json")
		self.fileJson.load()

	def values(self) -> list[dict]:
		return self.fileJson.data().values()

	def updateAllEnterprise(self):
		# Check la liste à partir du site
		self.updateByTableSite()
		# Réccupère les données de chaque page
		hrefs = [d.get("HREF_RENDEMENTBOURSE") for d in self.values()]
		_ = [hrefs.append(h) for h in FILE_ADD_HREF.splitlines() if h not in hrefs]
		for v in hrefs:
			print(v)
			self.updateOneEnterprise(url=f"https://rendementbourse.com{v}")
			time.sleep(0.1)
		# Affiche les ISIN manquant
		self.getAllNoneISIN()

	def updateOneEnterprise(self, url: str):
		resp = self.getDataSite(url=url)
		ticker = resp.get("TICKER")
		# Vérifie que le ticker existe, sinon commence avec le dict par défaut
		if self.fileJson.data().get(ticker) is None:
			self.fileJson.data()[ticker] = self.getDefaultDict()
		else:
			for k, v in self.getDefaultDict().items():
				if k not in list(self.fileJson.data()[ticker].keys()):
					self.fileJson.data()[ticker][k] = v
		# Remplace les anciennes données par les nouvelles
		for k, v in resp.items():
			self.fileJson.data()[ticker][k] = v
		# Vérifie le HREF de boursorama
		ISIN = self.fileJson.data()[ticker].get("ISIN")
		if self.fileJson.data()[ticker].get("HREF_BOURSORAMA") is None and ISIN:
			self.fileJson.data()[ticker]["HREF_BOURSORAMA"] = BousoBankSite.searchHREF(ISIN)
		# Sauvegarde le fichier
		self.fileJson.save(sort_keys=True)

	@classmethod
	def getDataSite(cls, url: str) -> dict:
		data = {}
		resp = s.get(url).text.encode("utf-8")
		soup = BeautifulSoup(resp, features="html.parser")

		# TICKER / NAME / ISIN / PEA-PME / PEA
		table_main = soup.select_one("#app > main > div.mb-4.py-3 > div > div.col-lg-7.col-xl-5 > div:nth-child(1) > div.d-table")
		txts = [v.text.strip() for v in table_main.find_all("span")]
		for txt in txts:
			if re.match(r"\w+(\.[A-Z]+).+", txt):
				data["TICKER"] = txt.split("–")[0].strip().split(".")[0]
				data["DESIGNATION"] = txt.split("–")[-1].strip()
			elif txt.startswith("ISIN:"):
				data["ISIN"] = txt.split()[-1]
			elif txt == "Éligible PEA-PME":
				data["PEA-PME"] = True
			elif txt == "Éligible PEA":
				data["PEA"] = True
		# SOCIETE
		data["NAME"] = soup.select_one(
			"#quoteHeader > div > div.d-sm-flex.align-items-center > div > div:nth-child(2) > h1").text.strip().splitlines()[-1].strip()
		# SECTEUR
		data["SECTEUR"] = txts[-1]
		# href
		data["HREF_RENDEMENTBOURSE"] = "/" + url.rsplit("/", maxsplit=1)[-1]
		return data

	def getAllNoneISIN(self, show=True):
		"""Retourne la liste des Ticker qui n'ont pas de n° ISIN"""

		r = [k for k, v in self.fileJson.data().items() if v.get("ISIN") is None]
		if show:
			print("""
				------------------------------------------------------
				TOUS LES ISINS MANQUANT"
				------------------------------------------------------
				""")
			_ = [print(v) for v in r]
		return r

	@staticmethod
	def getDefaultDict():
		return {
			"ISIN": None,
			"DESIGNATION": None,
			"DIVIDENDE": None,
			"HREF_BOURSORAMA": None,
			"HREF_RENDEMENTBOURSE": None,
			"NAME": None,
			"PEA": None,
			"PEA-PME": None,
			"SECTEUR": None,
			"TICKER": None
			}

	def updateByTableSite(self) -> dict:
		"""
		Met à jour à partir du tableau recherche du site
		https://rendementbourse.com/screener
		"""
		a = 0
		c = 50
		ignored = 0
		while (a + ignored) < c:
			URL = f"https://rendementbourse.com/screener-data?columns[0][data]=0&columns[0][name]=&columns[0][searchable]=true&columns[0][orderable]=true&columns[0][search][value]=&columns[0][search][regex]=false&columns[1][data]=1&columns[1][name]=&columns[1][searchable]=true&columns[1][orderable]=true&columns[1][search][value]=&columns[1][search][regex]=false&columns[2][data]=2&columns[2][name]=&columns[2][searchable]=true&columns[2][orderable]=true&columns[2][search][value]=&columns[2][search][regex]=false&columns[3][data]=3&columns[3][name]=&columns[3][searchable]=true&columns[3][orderable]=true&columns[3][search][value]=&columns[3][search][regex]=false&columns[4][data]=4&columns[4][name]=&columns[4][searchable]=true&columns[4][orderable]=true&columns[4][search][value]=&columns[4][search][regex]=false&columns[5][data]=5&columns[5][name]=&columns[5][searchable]=true&columns[5][orderable]=false&columns[5][search][value]=&columns[5][search][regex]=false&columns[6][data]=6&columns[6][name]=&columns[6][searchable]=true&columns[6][orderable]=true&columns[6][search][value]=&columns[6][search][regex]=false&columns[7][data]=7&columns[7][name]=&columns[7][searchable]=true&columns[7][orderable]=true&columns[7][search][value]=&columns[7][search][regex]=false&columns[8][data]=8&columns[8][name]=&columns[8][searchable]=true&columns[8][orderable]=true&columns[8][search][value]=&columns[8][search][regex]=false&columns[9][data]=9&columns[9][name]=&columns[9][searchable]=true&columns[9][orderable]=false&columns[9][search][value]=&columns[9][search][regex]=false&order[0][column]=1&order[0][dir]=asc&start={a}&length=100&search[value]=&search[regex]=false&filters[quoteTypes][]=EQUITY&filters[markets][]=4&filters[hasPea][]=1&filters[trailingAnnualDividendYield][]=0.005&filters[trailingAnnualDividendYield][]=0.1"
			rjson: dict = s.get(URL).json()
			c = rjson.get("recordsTotal")
			for line in rjson.get('data'):
				_ticker = BeautifulSoup(line[0], features="html.parser").text.split(".")[0]

				# ignore_code_mnémonique
				if _ticker in [v.strip() for v in FILE_IGNORE_CODE.splitlines()]:
					ignored += 1
					continue

				if self.fileJson.data().get(_ticker) is None:
					self.fileJson.data()[_ticker] = self.getDefaultDict()

				self.fileJson.data()[_ticker]["TICKER"] = _ticker
				self.fileJson.data()[_ticker]["NAME"] = BeautifulSoup(line[1], features="html.parser").find("a").text
				self.fileJson.data()[_ticker]["HREF_RENDEMENTBOURSE"] = BeautifulSoup(line[1], features="html.parser").find("a").get("href")
				self.fileJson.data()[_ticker]["SECTEUR"] = BeautifulSoup(line[1], features="html.parser").find("small").text
				self.fileJson.data()[_ticker]["DIVIDENDE"] = True

			a += len(rjson.get('data'))
		self.fileJson.save(sort_keys=True)

	def addEnterpriseCMD(self):
		while True:
			resp = input("Quel est l'adresse du site à ajouter ?\tY pour fermer\n")
			if resp.lower() == "y":
				break
			self.updateOneEnterprise(url=resp.strip())

	def exportTXT(self, path="export_enterprise.txt"):
		# Ajoute les en-tête
		lines = [";".join(list(list(self.values())[0].keys()))]
		# Convertie les lignes en texte
		for data in self.values():
			lines.append(";".join([str(v) for v in data.values()]))
		# Sauvegarde le fichier TXT
		with open(path, mode="w", encoding="utf-8") as file:
			file.write("\n".join(lines))

	def exportCSV(self, path="export_enterprise.csv"):
		data = {a: [] for a in [line for line in self.values()][0].keys()}
		values: list[dict] = [n for n in [d for d in self.values()]]
		for line in values:
			for k in data.keys():
				v = line.get(k) if line.get(k) is not None else ""
				data[k].append(v)

		dataframe1 = pandas.DataFrame(data)
		dataframe1.to_csv(path, index=None)


if __name__ == '__main__':
	rdm = RendementBourseSite()
	rdm.updateAllEnterprise()
	rdm.exportCSV()

	# bourso = BousoBankSite.searchHREF("FR0010340141")
	# print(bourso)


from exportEnterprise import RendementBourseSite
from exportDividend import ExportDividend


if __name__ == '__main__':
	# rdm = RendementBourseSite()
	# rdm.updateOneEnterprise("https://rendementbourse.com/aldbt-dbt")
	# rdm.updateAllEnterprise()
	# rdm.exportCSV()

	exp = ExportDividend()
	exp.updateNewAllEnterprise()
	exp.exportCSV()

import sqlite3
import TWStock.core.FinMarShare as FinMarShare
from TWStock.core.Timeseries import Timeseries
from TWStock.core.TWSException import *

ins_cmd = 'INSERT OR IGNORE INTO ' + FinMarShare.table_name + '(' + ','.join(FinMarShare.ins_cols)+ ') VALUES (:' + ',:'.join(FinMarShare.ins_cols) + ')'
sel_cmd = 'SELECT ' + ','.join(FinMarShare.sel_cols) + ' FROM ' + FinMarShare.table_name + ' WHERE no = ? ORDER BY date ASC'
create_cmd = 'CREATE TABLE IF NOT EXISTS ' + FinMarShare.table_name \
	+ ' (' + (','.join(FinMarShare.create_cols)) \
	+ ', UNIQUE(' + (','.join(FinMarShare.uniq)) + ') )'

class FinMarDownloader:

	def __init__(self, db_fname):
		self.db_fname = db_fname
		self.dbh = None

	def __enter__(self):
		self.dbh = self.connectDB()
		return self

	def __exit__(self, extype, exvalue, extrace):
		self.dbh.close()	

	def connectDB(self):
		c = sqlite3.connect(self.db_fname)
		c.execute(create_cmd)
		c.commit()
		return c

	def writeDB(self, data):
		print("寫入%d筆資料" % (len(data),))
		for row in data:
			self.dbh.execute(ins_cmd, row)
			self.dbh.commit()

	def download(self, **kwargs):
		"""
		This method must be implemented to download data from various sites.

		# RETURN
		A list of stock data must be returned.

		"""
		raise NotImplementedError


class FinMarReader:
	
	def __init__(self, db_fname):
		self.db_fname = db_fname
		self.dbh = None

	def __enter__(self):
		self.connectDB()
		return self

	def __exit__(self, extype, exvalue, extrace):
		self.disconnectDB()	

	def connectDB(self):
		self.dbh = sqlite3.connect(self.db_fname)

	def disconnectDB(self):
		self.dbh.close()

	def readByNo(self, no):
		result = {}

		tmp = list(zip(* self.dbh.execute(sel_cmd, (no, )).fetchall()))
		if len(tmp) != 0:
			result = Timeseries(tmp.pop(0)) # 'date' column
			for i, key in enumerate(FinMarShare.sel_cols[1:]):
				result.add(key, tmp[i])
			return result

		else:
			raise NoDataException("No data is available")

	def getListOfNo(self):
		return list(zip(*self.dbh.execute('SELECT no FROM ' + FinMarShare.table_name + ' GROUP BY no ORDER BY no ASC').fetchall()))[0]


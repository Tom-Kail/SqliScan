# coding=utf-8
import request
import result
import Levenshtein
import copy
import re
from color_printer import colors
         
#SQLIPayload = "d';z\"0`\\"                       
SQLIPayload = "d'z\"0"                       
DB2 = 'IBM DB2 database'
MSSQL = 'Microsoft SQL database'
ORACLE = 'Oracle database'
SYBASE = 'Sybase database'
POSTGRE = 'PostgreSQL database'
MYSQL = 'MySQL database'
JAVA = 'Java connector'
ACCESS = 'Microsoft Access database'
INFORMIX = 'Informix database'
INTERBASE = 'Interbase database'
DMLDATABASE = 'DML Language database'
UNKNOWN = 'Unknown database'
SQLErrors = (
	# ASP / MSSQL
	(r'System\.Data\.OleDb\.OleDbException', MSSQL),
	(r'\[SQL Server\]', MSSQL),
	(r'\[Microsoft\]\[ODBC SQL Server Driver\]', MSSQL),
	(r'\[SQLServer JDBC Driver\]', MSSQL),
	(r'\[SqlException', MSSQL),
	(r'System.Data.SqlClient.SqlException', MSSQL),
	(r'Unclosed quotation mark after the character string', MSSQL),
	(r"'80040e14'", MSSQL),
	(r'mssql_query\(\)', MSSQL),
	(r'odbc_exec\(\)', MSSQL),
	(r'Microsoft OLE DB Provider for ODBC Drivers', MSSQL),
	(r'Microsoft OLE DB Provider for SQL Server', MSSQL),
	(r'Incorrect syntax near', MSSQL),
	(r'Sintaxis incorrecta cerca de', MSSQL),
	(r'Syntax error in string in query expression', MSSQL),
	(r'ADODB\.Field \(0x800A0BCD\)<br>', MSSQL),
	(r"Procedure '[^']+' requires parameter '[^']+'", MSSQL),
	(r"ADODB\.Recordset'", MSSQL),
	(r"Unclosed quotation mark before the character string", MSSQL),
	(r"'80040e07'", MSSQL),
	(r'Microsoft SQL Native Client error', MSSQL),
	# DB2
	(r'SQLCODE', DB2),
	(r'DB2 SQL error:', DB2),
	(r'SQLSTATE', DB2),
	(r'\[CLI Driver\]', DB2),
	(r'\[DB2/6000\]', DB2),
	# Sybase
	(r"Sybase message:", SYBASE),
	(r"Sybase Driver", SYBASE),
	(r"\[SYBASE\]", SYBASE),
	# Access
	(r'Syntax error in query expression', ACCESS),
	(r'Data type mismatch in criteria expression.', ACCESS),

	(r'Microsoft JET Database Engine', ACCESS),
	(r'\[Microsoft\]\[ODBC Microsoft Access Driver\]', ACCESS),
	# ORACLE
	(r'(PLS|ORA)-[0-9][0-9][0-9][0-9]', ORACLE),
	# POSTGRE
	(r'PostgreSQL query failed:', POSTGRE),
	(r'supplied argument is not a valid PostgreSQL result', POSTGRE),
	(r'pg_query\(\) \[:', POSTGRE),
	(r'pg_exec\(\) \[:', POSTGRE),
	# MYSQL
	(r'supplied argument is not a valid MySQL', MYSQL),
	(r'Column count doesn\'t match value count at row', MYSQL),
	(r'mysql_fetch_array\(\)', MYSQL),
	(r'mysql_', MYSQL),
	(r'on MySQL result index', MYSQL),
	(r'You have an error in your SQL syntax;', MYSQL),
	(r'You have an error in your SQL syntax near', MYSQL),
	(r'MySQL server version for the right syntax to use', MYSQL),
	(r'\[MySQL\]\[ODBC', MYSQL),
	(r"Column count doesn't match", MYSQL),
	(r"the used select statements have different number of columns",
		MYSQL),
	(r"Table '[^']+' doesn't exist", MYSQL),
	(r"DBD::mysql::st execute failed", MYSQL),
	(r"DBD::mysql::db do failed:", MYSQL),
	# Informix
	(r'com\.informix\.jdbc', INFORMIX),
	(r'Dynamic Page Generation Error:', INFORMIX),
	(r'An illegal character has been found in the statement',
		INFORMIX),
	(r'\[Informix\]', INFORMIX),
	(r'<b>Warning</b>:  ibase_', INTERBASE),
	(r'Dynamic SQL Error', INTERBASE),
	# DML
	(r'\[DM_QUERY_E_SYNTAX\]', DMLDATABASE),
	(r'has occurred in the vicinity of:', DMLDATABASE),
	(r'A Parser Error \(syntax error\)', DMLDATABASE),
	# Java
	(r'java\.sql\.SQLException', JAVA),
	(r'Unexpected end of command in statement', JAVA),
	# Coldfusion
	(r'\[Macromedia\]\[SQLServer JDBC Driver\]', MSSQL),
	# Generic errors..
	(r'SELECT .*? FROM .*?', UNKNOWN),
	(r'UPDATE .*? SET .*?', UNKNOWN),
	(r'INSERT INTO .*?', UNKNOWN),
	(r'Unknown column', UNKNOWN),
	(r'where clause', UNKNOWN),
	(r'SqlServer', UNKNOWN)
)

#main class in this .py file 
class Sqli(object):
	def __init__(self,req):
		self._req = copy.deepcopy(req)

	def match_sql_error(self,response):
		'''
		if find sql error return database type  else return ""
		'''
		dataBaseType = ""
		find_error = False
		for index in xrange(len(SQLErrors)):
			pattern = r".*?%s.*?"%(SQLErrors[index][0])
			rePattern = re.compile(pattern,re.S)
			match = rePattern.match(response)
			if match:
				dataBaseType = SQLErrors[index][1]
				break
		
		return dataBaseType;
			
	#begin sql injection vlun checking 
	def sqliCheck(self):
		payloadQueryList = request.get_payload_query_list(self._req._query,SQLIPayload)
		for i in payloadQueryList:
			req = copy.deepcopy(self._req)
			rsp = request.sendPayload(req,i)
			if rsp  == None:
				return None
			db = self.match_sql_error(rsp.text)
			if db != "":			
				colors.yellow( "**************************")
				colors.yellow( "*  Find sqli vlun")
				colors.yellow( "*  Url:"+req._url)
				colors.yellow(  "*  Payload:"+ SQLIPayload)
				colors.yellow(  "*  Database: "+db)
				colors.yellow(  "**************************")
				
				return result.Result([req],[rsp],[SQLIPayload],vulnName='sqli',advice='use orm',db=db)			
		return None
	
def start(req):
	si = Sqli(req)
	return si.sqliCheck()
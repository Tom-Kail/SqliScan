# coding=utf-8
import request
import result
                           
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
SQL_ERRORS = (
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
class CSqli(object):
	'''
	match database errors in http response contents
	'''
	
	def __init__(self,url,method = "post",cookies = "", eq_limit = 0.90):
		
		if url =="":
			raise Exception("url mustn't be empty!\n")
		nPos = url.find("?");
		if nPos == -1 or nPos == len(url)-1:
			raise Exception("Can't find sqli in such format of url!\n")
			
		self._url = url
		self._cookies = cookies
		self._eq_limit = eq_limit
		
		if method.lower() == "post" or method.lower() == "get":
			self._method = method.lower()
		else:
			raise Exception("Method not supported!\n")

	def match_sql_error(self,response):
		'''
		if find sql error return database type  else return ""
		'''
		dataBaseType = ""
		find_error = False
		for index in xrange(len(SQL_ERRORS)):
			pattern = r".*?%s.*?"%(SQL_ERRORS[index][0])
			rePattern = re.compile(pattern,re.S)
			match = rePattern.match(response)
			if match:
				dataBaseType = SQL_ERRORS[index][1]
				break
		
		return dataBaseType;
			
	#begin sql injection vlun checking 
	def start_sqli(self):
		'''
		#login dvwa
		url='http://192.168.1.10/dvwa/login.php'
		post =  "username=admin&password=admin&Login=Login"
		so.post_http(url,post,SPTobj)
		print "################################################\npost response\n",SPTobj.contents.pResponse
		self._cookies = SPTobj.contents.pGetCookie
		SPTobj.contents.pSetCookie = self._cookies
		'''
		#begin test sqli
		andPos = self._url.find("&")
		quePos = self._url.find("?")
		equPos = self._url.find("=")
		tmpUrl = ""
		db = ""
		if andPos == -1:
			tmpUrl = self._url[0:equPos+1] + "d'z\"0"
		else:
			tmpUrl = self._url[0:equPos+1] + "d'z\"0" + self._url[andPos:]
		
		if self._method.lower() == "post":
			urlHead = tmpUrl[0:quePos]
			urlPara = tmpUrl[quePos+1:]
			so.post_http(urlHead,urlPara,SPTobj)
		elif self._method.lower() == "get":
			so.get_http(tmpUrl,SPTobj)
		print "###########################",SPTobj.contents.pResponse
		db = self.match_sql_error(SPTobj.contents.pResponse)
		if db != "":
			so.insert_highRisk("localhost", "root", "123456", "webscan", iUrlId ,iScanId,iHostId,20, self._url)
			print "****************************************************"
			print "*  Find sqli vlun"
			print "*  Database: ",db
			print "****************************************************"
			return True
			
		return False
	
def main(env):
	optionString = env.option()
	global iScanId
	global iUrlId
	global iHostId
	
	optionName = "url"
	url = BkGlobal.get_option(optionName,optionString)
	optionName ="method"
	method = BkGlobal.get_option(optionName,optionString)
	optionName ="scanId"
	iScanId = BkGlobal.get_option(optionName,optionString)
	optionName ="hostId"
	iHostId = BkGlobal.get_option(optionName,optionString)
	optionName = "urlId"
	urlId = BkGlobal.get_option(optionName,optionString)
	iUrlId = BkGlobal.atoi(urlId)
	optionName = "cookie"
	cookie = BkGlobal.get_option(optionName,optionString)
	SPTobj.contents.pSetCookie = cookie
	
	IFvuln = 0
	# -2 means run error  -1 means visit error 	 0 means vuln is not exist   1 means vuln is exist     
	si = CSqli(url,method)
	IFvuln = si.start_sqli()
	if IFvuln:
		return 1
	return 0
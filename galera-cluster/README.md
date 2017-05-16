# On Zabbix Server
* apt-get install unixodbc
* download mysql-connector

/etc/odbcinst.ini
```
[MySQL]
Description = ODBC for MySQL
Driver = /usr/local/lib/odbc/libmyodbc5a.so
Setup = /usr/local/lib/odbc/libodbcmyS.so
FileUsage = 1
```

/etc/odbc.ini
```
[hostname]
Description	= MySQL connection to  database
Driver		= MySQL
Database	= mysql
Server		= x.x.x.x
User		= db_user
Password	= db_password
Port		= 3306
Socket		= /var/run/mysqld/mysqld.sock
```

Do not forget to create db_user :)

Import template, and link the host to the template.

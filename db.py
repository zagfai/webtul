#!/usr/bin/python
# -*- coding: utf-8 -*-
""" DB module
"""
__author__ = 'Zagfai'
__created__ = '2013-10-21'


class MySQL:
    """Use obj = MySQL(...) to create an MySQL object.
    You could connect server by hand, but i suggest that you don't do that.
    Use obj.execute(sql, param=()) to execute sqls, it will connect itself.
    Be careful that autocommit set as False by default.
    obj.execute() return two values, an int(may be None) and a tuple.
    the tuple contains dicts, and when the int is None, execute error.
    This class was written with Mysql5.5, MySQLdb1.2.3.
    """
    def __init__(self, host, port, user, passwd,
                 db, charset="utf8", autocommit=False,
                 cursorclass='dict'):
        import MySQLdb
        import MySQLdb.cursors

        self.db_module = MySQLdb
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.dbname = db
        self.charset = charset
        self.autocommit = autocommit
        if cursorclass == 'tuple':
            self.cursorclass = MySQLdb.cursors.Cursor
        elif cursorclass == 'dict':
            self.cursorclass = MySQLdb.cursors.DictCursor
        else:
            self.cursorclass = cursorclass

    def connect(self):
        """obj.connect() => True or raise Error from MySQLdb.
        You aren't suggested to use this function by your hand,
        because this func may cause Exception.
        """
        self.conn = self.db_module.connect(
                host=self.host, port=int(self.port), user=self.user,
                passwd=self.passwd, db=self.dbname, charset=self.charset,
                cursorclass=self.cursorclass)
        self.conn.autocommit(self.autocommit)
        return True

    def commit(self):
        try:
            self.conn.ping()
        except (self.db_module.OperationalError,
                self.db_module.InterfaceError), e:
            return None, e

        try:
            self.conn.commit()
            return True, ""
        except Exception, e:
            self.conn.rollback()
            return None, e

    def close(self):
        """Also I don't recommand that you use this function to close
        the connection, because it raises an error while you haven't
        use the db object to execute one sql.
        """
        return self.conn.close()

    def _execute(self, sql, param=()):
        def do_exec(sql, param):
            cursor = self.conn.cursor()
            ret = cursor.execute(sql, param)
            res = cursor.fetchall()
            cursor.close()
            return ret, res
        # start execute
        try:
            ret, res = do_exec(sql, param)
        except (AttributeError, self.db_module.OperationalError):
            self.connect()
            ret, res = do_exec(sql, param)
        return ret, res

    def execute(self, sql, param=()):
        try:
            return self._execute(sql, param)
        except Exception, e:
            return None, e


def test_mysql():
    db = MySQL('localhost',3306, '','', 'test', autocommit=True)
    print db.execute("DROP TABLE IF EXISTS `t_test`;")
    print db.execute("""
            CREATE TABLE `t_test` (
              `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
              `str` varchar(255) NOT NULL,
              `numb` int(11) DEFAULT NULL,
              `time_stamp` date NOT NULL,
              PRIMARY KEY (`id`),
              UNIQUE KEY `IDX_ID` (`id`),
              UNIQUE KEY `IDX_STR` (`str`) USING BTREE
            ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
    """)

    print db.execute("INSERT INTO t_test (str, numb, time_stamp) "
                     "VALUES ('123', 456, '2013-10-10')")
    print db.execute("SELECT * FROM t_test")

    # protect from sql injection with data as paramters
    print db.execute("INSERT INTO t_test (str, numb, time_stamp) "
                     "VALUES (%s, %s, %s)", ('123', 456, '2013-01-01'))
    print db.execute("SELECT * FROM t_test")

    print db.execute("INSERT INTO t_test (str, numb, time_stamp) "
                     "VALUES (%s, %s, %s)", ('321', 456, '2013-01-01'))
    print db.execute("SELECT * FROM t_test")

    # error data format
    print db.execute("INSERT INTO t_test (str, numb, time_stamp) "
                     "VALUES (%s, %s, %s)", ('456', 456, '2013'))
    print db.execute("SELECT * FROM t_test")
    print db.execute("DELETE FROM t_test where time_stamp='0000-00-00'")

    print db.execute("UPDATE t_test SET str=%s WHERE id > %s", ("512", 1))

    ret, res = db.execute("SELECT * FROM t_test WHERE id > %s", 1)
    print ret
    row = res[0]
    print row.get('str'), row.get('time_stamp'), row.get('no_col')

    print db.execute("DROP TABLE `t_test`;")


if __name__ == '__main__':
    test_mysql()
    raw_input()

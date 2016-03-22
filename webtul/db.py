#!/usr/bin/python
# -*- coding: utf-8 -*-
""" DB module of webtul.
Now it contains only an MySQL class which is wrapped.
"""
__author__ = 'Zagfai'
__license__ = 'MIT@2014-01'

from time import sleep
from Queue import Queue, Empty

__all__ = ['MySQL', 'MySQLPool']

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
                 cursorclass='dict', dbmodule='', logger = None):
        if dbmodule == 'pymysql':
            import pymysql as dbm
            import pymysql.cursors as curs
        else:
            import MySQLdb as dbm
            import MySQLdb.cursors as curs
        self.log = logger

        self.db_module = dbm
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.dbname = db
        self.charset = charset
        self.autocommit = autocommit
        if cursorclass == 'tuple':
            self.cursorclass = curs.Cursor
        elif cursorclass == 'dict':
            self.cursorclass = curs.DictCursor
        else:
            self.cursorclass = cursorclass
        self.log and self.log.debug('MySQL inited.')

    def execute(self, sql, param=(), times=1):
        """This function is the most use one, with the paramter times
        it will try x times to execute the sql, default is 1.
        """
        self.log and self.log.debug('%s %s' % ('SQL:', sql))
        if param is not ():
            self.log and self.log.debug('%s %s' % ('PARAMs:', param))
        for i in xrange(times):
            try:
                ret, res = self._execute(sql, param)
                return ret, res
            except Exception, e:
                self.log and self.log.warn("The %s time execute, fail" % i)
                self.log and self.log.warn(e)
            if i: sleep(i**1.5)
        self.log and self.log.error(e)
        return None, e

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

    def close(self):
        """Also I don't recommand that you use this function to close
        the connection, because it raises an error while you haven't
        use the db object to execute one sql.
        """
        return self.conn.close()

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

    def _execute(self, sql, param=()):
        def do_exec(sql, param):
            if not isinstance(param, list) and not isinstance(param, tuple):
                param = (param,)
            cursor = self.conn.cursor()
            if param is not ():
                ret = cursor.execute(sql, param)
            else:
                ret = cursor.execute(sql)
            res = cursor.fetchall()
            cursor.close()
            return ret, res
        # start execute
        try:
            ret, res = do_exec(sql, param)
        except (AttributeError, self.db_module.OperationalError):
            self.connect()
            ret, res = do_exec(sql, param)
        # make sure Atct not to be set inside procedure
        self.conn.autocommit(self.autocommit)
        return ret, res

class MySQLPool():
    """Pool for db connections, for the ugly multprsig."""
    def __init__(self, *argl, **argd):
        if argd.get('size'):
            size = argd.get('size')
            del argd['size']
        else:
            size = 2

        self.q = Queue()
        for i in xrange(size):
            self.q.put(MySQL(*argl, **argd))

    def execute(self, sql, param=(), times=1, timeout=None):
        try:
            db = self.q.get(timeout is None, timeout)
        except Empty:
            return None, "Pool has no a free connection now."
        ret, res = db.execute(sql, param, times)
        self.q.put(db)
        return ret, res


def test_mysql():
    dbs = [
        MySQL('localhost',3306, '','', 'test', autocommit=True),
        MySQLPool('localhost',3306, '','', 'test', autocommit=True)
    ]
    for db in dbs:
        print db.execute("DROP TABLE IF EXISTS `t_test`")
        print db.execute("""
                CREATE TABLE `t_test` (
                  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
                  `str` varchar(255) NOT NULL,
                  `numb` int(11) DEFAULT NULL,
                  `time_stamp` date NOT NULL,
                  PRIMARY KEY (`id`),
                  UNIQUE KEY `IDX_ID` (`id`),
                  UNIQUE KEY `IDX_STR` (`str`) USING BTREE
                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8
        """)

        print db.execute("INSERT INTO t_test (str, numb, time_stamp) "
                         "VALUES ('123', 456, '2013-10-10')")
        print db.execute("SELECT * FROM t_test")

        # protect from sql injection with data as paramters
        print db.execute("INSERT INTO t_test (str, numb, time_stamp) "
                         "VALUES (%s, %s, %s)", ('123', 456, '2013-01-01'), 3)
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
        print '---------------------'


if __name__ == '__main__':
    test_mysql()


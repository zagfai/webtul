#!/usr/bin/python
# -*- coding: utf-8 -*-
""" DAL
"""
__author__ = 'Zagfai'
__date__ = '2018-06'

import asyncio
import logging
import aiomysql


class DAL(object):
    """Data Access Layer Template"""
    def __init__(self, db, transaction):
        super(DAL, self).__init__()
        self.autocommit = db
        self.transaction = transaction

        logging.info("DAL Initial.")

    async def init_aiomysql(host, user, password, db, maxsize=5, autocommit=True,
                            cursorclass=aiomysql.DictCursor, charset='utf8mb4'):
        return await aiomysql.create_pool(
            host=host,
            user=user,
            password=password,
            db=db,
            maxsize=maxsize,
            autocommit=autocommit,
            cursorclass=cursorclass,
            charset=charset)

    async def _execute(self, cur, sql, param=()):
        if not isinstance(param, list) and not isinstance(param, tuple):
            param = (param,)
        ret = await cur.execute(sql, param)
        res = await cur.fetchall()
        return ret, res

    async def execute(self, sql, param=(), times=1):
        ee = None
        for i in range(times):
            async with self.autocommit.acquire() as conn:
                async with conn.cursor() as cur:
                    try:
                        ret, res = await self._execute(cur, sql, param)
                        return ret, res
                    except aiomysql.OperationalError:
                        await conn.ping()
                        ret, res = await self._execute(cur, sql, param)
                        return ret, res
                    except Exception as e:
                        await conn.ping()
                        ee = str(e)
                        logging.error("DB Unknown Error: %s" % str(e))
                    if i:
                        await asyncio.sleep(i**1.5)
        else:
            return None, ee

    async def update(self, tbl, where, sets):
        if not sets or not isinstance(sets, dict):
            return False

        param_name = sets.keys()
        param = [sets[i] for i in param_name]
        param.append(where)
        sql = 'UPDATE %s SET %s, times=times+1 WHERE x=%%s'
        sql_fmt = ['`'+pname+'`=%s' for pname in param_name]
        sql = sql % (tbl, ','.join(sql_fmt))
        # logging.info(sql)
        ret, res = await self.execute(sql, param)
        if ret is None:
            logging.error(str(res))
            return None

        return ret == 1

    # TODO injection here
    async def select(self, tbl, queries=None):
        sql = "SELECT * FROM %s" % (tbl,)
        if queries:
            sql += " " + queries

        ret, res = await self.execute(sql)
        if ret is None:
            logging.error(str(res))
            return None
        return res

    async def insert(self, tbl, row, replace=False):
        replace_op = "REPLACE INTO"
        insert_op = "INSERT INTO"
        op = insert_op if not replace else replace_op

        row_name = row.keys()
        row_val = [row[i] for i in row_name]
        sql_fmt = ['`'+pname+'`=%s' for pname in row_name]

        sql = '%s %s SET %s'
        sql = sql % (op, tbl, ','.join(sql_fmt))
        logging.debug(sql)
        ret, res = await self.execute(sql, row_val)
        logging.debug(str(ret))
        logging.debug(str(res))
        if ret is None:
            logging.error(str(res))
            return None
        return ret > 0

    async def replace(self, tbl, row):
        return await self.insert(tbl, row, replace=True)

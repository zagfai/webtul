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

    async def select(self):
        # TODO
        pass

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

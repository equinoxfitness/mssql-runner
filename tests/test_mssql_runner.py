import os
import unittest
from unittest.mock import MagicMock
from mssql_runner import UNIT_TEST_KEY
from mssql_runner.module import MSSQLRunner


class TestMSSQLRunner(unittest.TestCase):
    def setUp(self):
        os.environ[UNIT_TEST_KEY] = 'True'
        self.testCls = MSSQLRunner(
            db_name='', host='', user='', password='', port='', batchy_server='', batchy_port=''
        )

    def test_run_script(self):
        self.testCls.ms = MagicMock()
        self.testCls.run_script(script='',
                                params=None,
                                sql_command='select * from test_db')

    def test_run_script_with_params(self):
        self.testCls.ms = MagicMock()
        self.testCls.run_script(script='',
                                params='title-test',
                                sql_command='''
                                    select * from test_db
                                    where title=$[?title]
                                ''')

    def test_run_script_with_params_multiple(self):
        self.testCls.ms = MagicMock()
        self.testCls.run_script(script='',
                                params='title-test,firstname-john,lastname-doe',
                                sql_command='''
                                    select * from test_db
                                    where title=$[?title]
                                    and firstname=$[?firstname]
                                    and lastname=$[?lastname]
                                ''')

    def test_run_script_from_date(self):
        self.testCls.ms = MagicMock()
        self.testCls.run_script(script='',
                                params=None,
                                from_date='2020-03-10T0:00:00.00',
                                sql_command='''
                                    select * from test_db
                                    where from_date=$[?from_date]
                                ''')

    def test_run_script_others(self):
        self.testCls.ms = MagicMock()
        self.testCls.run_script(script='',
                                params=None,
                                from_date='2020-03-10T0:00:00.00',
                                to_date='2020-03-12',
                                batch_id='1',
                                sql_command='''
                                    select * from test_db
                                    where from_date=$[?from_date]
                                ''')

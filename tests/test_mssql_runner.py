import os
import unittest
from unittest.mock import MagicMock
from mssql_runner import UNIT_TEST_KEY
from mssql_runner.module import MSSQLRunner


class TestAthenaInteraction(unittest.TestCase):
    def setUp(self):
        os.environ[UNIT_TEST_KEY] = "True"
        self.testCls = MSSQLRunner(
            db_name='', host='', user='', password='', port=''
        )

    def test_run_script(self):
        self.testCls.ms = MagicMock()
        self.testCls.run_script(script='', params=None, sql_command='select * from test_db')
        self.assertTrue(True)  # Assert that this line is reached without error

    def test_run_script_with_params(self):
        self.testCls.ms = MagicMock()
        self.testCls.run_script(script='', params='title-test', sql_command='select * from test_db where title=$[?title]')
        self.assertTrue(True)  # Assert that this line is reached without error

    def test_run_script_with_params_multiple(self):
        self.testCls.ms = MagicMock()
        self.testCls.run_script(script='', params='title-test,firstname-john,lastname-doe',
                                sql_command='select * from test_db where title=$[?title] and firstname=$[?firstname] and lastname=$[?lastname]')
        self.assertTrue(True)  # Assert that this line is reached without error

    def test_run_script_from_date(self):
        self.testCls.ms = MagicMock()
        self.testCls.run_script(script='', params=None, from_date='2020-03-10T0:00:00.00',
                                sql_command='select * from test_db where from_date=$[?from_date]')
        self.assertTrue(True)  # Assert that this line is reached without error

    def test_run_script_from_date(self):
        self.testCls.ms = MagicMock()
        self.testCls.run_script(script='', params=None, from_date='2020-03-10T0:00:00.00', to_date='2020-03-12', batch_id='1',
                                sql_command='select * from test_db where from_date=$[?from_date]')
        self.assertTrue(True)  # Assert that this line is reached without error

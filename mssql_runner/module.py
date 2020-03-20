#!/usr/bin/env python

import sys
import os
import argparse
from datacoco_core.logger import Logger
from datacoco_batch import Batch
from datacoco_db.mssql_tools import MSSQLInteraction
from datetime import datetime
from mssql_runner import DEFAULT_FROM_DATE

from mssql_runner import UNIT_TEST_KEY
from mssql_runner.config_wrapper import ConfigWrapper


class MSSQLRunner:
    """
    generic class for execution of a parameterized script
    in postgres or redshift
    """

    def __init__(self, db_name, host, user, password, port, batchy_server, batchy_port):
        self.ms = None

        self.is_test = os.environ.get(UNIT_TEST_KEY, False)

        self.batchy_server = batchy_server
        self.batchy_port = batchy_port

        if not self.is_test:
            self.ms = MSSQLInteraction(
                dbname=db_name,
                host=host,
                user=user,
                password=password,
                port=port,
            )
            self.ms.conn()

    @staticmethod
    def expand_params(sql, params):
        """
        substitutes params in sql stagement
        :param sql:
        :param params:
        :return: sql, expanded with params
        """
        for p in params.keys():
            var = "$[?" + p + "]"
            val = str(params[p])
            if p == "from_date" and val != "1776-07-04":
                try:
                    val = datetime.strptime(val, "%Y-%m-%dT%H:%M:%S.%f")
                    val = val.strftime("%Y-%m-%d %H:%M:%S")
                    print("removed microsecond from wf from_date")
                except Exception as e:
                    print(e)
                    pass
            sql = sql.replace(var, val)
        return sql

    def run_script(
        self,
        script,
        from_date=None,
        to_date=None,
        batch_id=None,
        params=None,
        batchy_job=None,
        sql_command=None,
    ):
        """
        method for expanding and running sql statements
        :param script:
        :param from_date:
        :param to_date:
        :param batch_id:
        :param params:
        :return:
        """

        paramset = {}

        # set up logger
        if script is not None:
            script_path, script_filename = os.path.split(script)
            logger = Logger(logname=script_filename)
        else:
            logger = Logger(logname="direct_sql")
            sys.excepthook = logger.handle_exception

        # first we retrive params  we will load these into dict first,
        # any additional params specified will override
        if batchy_job:
            wf = batchy_job.split(".")[0]
            try:
                job = (
                    batchy_job.split(".")[1]
                    if len(batchy_job.split(".")[1]) > 0
                    else "global"
                )
            except Exception as e:
                logger.l(e)
                job = "global"
            batchy_params = Batch(
                wf,
                server=self.batchy_server,
                port=self.batchy_port,
            ).get_status()
            paramset.update(batchy_params[job])

        # next we apply custom params and special metadata fields,
        # again this will overrite batchy params if specified
        # convert string params to dict
        try:
            params = dict(
                (k.strip(), v.strip())
                for k, v in (item.split("-") for item in params.split(","))
            )
        except Exception as e:
            logger.l(f"issue parsing params: {e}")

        if isinstance(params, dict):
            paramset.update(params)

        if from_date:
            paramset["from_date"] = from_date
        if to_date:
            paramset["to_date"] = to_date
        if batch_id:
            paramset["batch_id"] = batch_id

        # now defaults for special metadata fields
        if paramset.get("from_date") is None:
            paramset["from_date"] = DEFAULT_FROM_DATE
        if paramset.get("to_date") is None:
            paramset["to_date"] = "9999-12-31"
        if paramset.get("batch_id") is None:
            paramset["batch_id"] = "-1"
        # we'll keep batch_no for backwards compatibility
        paramset["batch_no"] = paramset["batch_id"]

        # check if it's direct SQL or SQL file
        if not self.is_test and script is not None:
            try:
                raw_sql = open(script).read()
            except Exception as e:
                e = f"File not found, please check file path."
                logger.l(e)
                raise RuntimeError(e)
        else:
            raw_sql = sql_command
        sql = self.expand_params(raw_sql, paramset)
        sql_message = (
            "\n\n--sql script start:\n" + sql + "\n--sql script end\n\n"
        )
        logger.l(sql_message)

        self.ms.batch_open()

        logger.l("starting script")
        try:
            self.ms.exec_sql(sql)
            self.ms.batch_commit()
            logger.l("batch commit")
        except Exception as e:
            logger.l("execution failed with error: " + str(e))
            raise RuntimeError(e)
            # os._exit(1)  # this truncates logout in rundeck


def main(args):

    # argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--script", help="""enter a path to your script """, default=None
    )
    # rundeck doesn't like -p '{"param1":"val1", "param2":"val2"}',
    # changed params to string
    parser.add_argument(
        "-p",
        "--parameters",  # type=json.loads, default='{"none":"none"}',
        default="none-none",
        help="""additional params to be substituted in script,
        example: -p param1-val1, param2-val2 """,
    )
    parser.add_argument(
        "-d",
        "--database",
        help="""db alias from etl.cfg, default is life """,
        default="life",
    )

    parser.add_argument(
        "-f", "--from_date", help="""from_date""", default=None
    )
    parser.add_argument("-t", "--to_date", help="""to_date""", default=None)
    parser.add_argument(
        "-b", "--batch_id", help="""enter batch id """, default=None
    )
    parser.add_argument(
        "-wf",
        "--batchy_job",
        help="""fully qualified batchy job name of the format wf.job""",
        default=None,
    )
    parser.add_argument(
        "-c",
        "--sql_command",
        help="""actual sql command to be executed""",
        default=None,
    )

    parser = ConfigWrapper.extend_parser(parser)

    args = parser.parse_args(args)

    (db_name, host, user, password, port, batchy_server, batchy_port) = ConfigWrapper.process_config(args)

    MSSQLRunner(
        db_name=db_name,
        host=host,
        user=user,
        password=password,
        port=port,
        batchy_server=batchy_server,
        batchy_port=batchy_port
    ).run_script(
        args.script,
        args.from_date,
        args.to_date,
        args.batch_id,
        args.parameters,
        args.batchy_job,
        args.sql_command,
    )


if __name__ == "__main__":
    main(sys.argv[1:])

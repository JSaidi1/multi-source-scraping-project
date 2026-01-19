import inspect
import os
import sys
from pathlib import Path

import psycopg2
from config.settings import app_cfg, data_base_cfg
from psycopg2 import OperationalError
from utils.utils_logs import log_message


class PsqlDBStorage:
    def __init__(self):
        # === Get log cfg.
        self.debug_mode = app_cfg.debug_mode
        self.console_log = app_cfg.console_log
        self.file_log = app_cfg.file_log
        # === Init DB
        self.dsn = data_base_cfg.dsn
        self.conn = self._get_connection()
        self._init_quotes_db()


    def _get_connection(self):
        try:
            return psycopg2.connect(self.dsn)
        except OperationalError as e:
            log_message("error", f"database connection error: {e}", self.file_log, self.console_log, self.debug_mode)
        except psycopg2.Error as e:
            log_message("error", f"sql psycopg2 execution error: {e}", self.file_log, self.console_log, self.debug_mode)
        except Exception as e:
            log_message("error", f"unknown error: {e}", self.file_log, self.console_log, self.debug_mode)

    def _init_quotes_db(self):
        """Create PostgresSQL database schema for quotes if not exists"""
        sql_file = "create_etl_quotes_db_schema_if_not_exists.sql"
        try:
            sql_file_path =  str(Path(__file__).resolve().parent / "sql" / sql_file)
            ## Check if SQL file exists:
            if not os.path.exists(sql_file_path):
                raise FileNotFoundError(f"sql file not found: '{sql_file_path}'")

            self.conn.autocommit = True  # Automatically commit commands

            with self.conn.cursor() as cur, open(sql_file_path, 'r') as f:
                sql_script = f.read()
                cur.execute(sql_script)
            log_message("info", "init quotes db successfully", self.file_log, self.console_log, self.debug_mode)
        except OperationalError as e:
            log_message("error", f"database connection error: {e}", self.file_log, self.console_log, self.debug_mode)
        except psycopg2.Error as e:
            log_message("error", f"sql psycopg2 execution error: {e}", self.file_log, self.console_log, self.debug_mode)
        except Exception as e:
            log_message("error", f"unknown error: {e}", self.file_log, self.console_log, self.debug_mode)

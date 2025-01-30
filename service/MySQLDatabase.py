import pymysql
from sshtunnel import SSHTunnelForwarder
import paramiko
import os
from typing import Dict, Any
import time
import logging
import socket

from service.config_adapter import ConfigAdapter

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class DBConnectionManager(metaclass=SingletonMeta):
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._config_adapter = ConfigAdapter()

        self.SSH_HOST = self._config_adapter.get_config('SSH_HOST')
        self.SSH_PORT = int(self._config_adapter.get_config('SSH_PORT'))
        self.SSH_USERNAME = self._config_adapter.get_config('SSH_USERNAME')
        self.SSH_KEY_PATHS = self._config_adapter.get_config('SSH_KEY_PATHS').split(',')

        self.MYSQL_HOST = self._config_adapter.get_config('MYSQL_HOST')
        self.MYSQL_PORT = int(self._config_adapter.get_config('MYSQL_PORT'))
        self.MYSQL_USER = self._config_adapter.get_config('MYSQL_USER')
        self.MYSQL_PASSWORD = self._config_adapter.get_config('MYSQL_PASSWORD')

        self._initialize_connection()

    def _initialize_connection(self):
        self.tunnel = None
        self.connection = None
        for key_path in self.SSH_KEY_PATHS:
            if not os.path.isfile(key_path):
                self.logger.warning(f"Key file not found: {key_path}")
                continue

            try:
                self.tunnel = SSHTunnelForwarder(
                    (self.SSH_HOST, self.SSH_PORT),
                    ssh_username=self.SSH_USERNAME,
                    ssh_pkey=key_path,
                    remote_bind_address=(self.MYSQL_HOST, self.MYSQL_PORT),
                    logger=self.logger
                )
                self.tunnel.start()
                self.logger.info(f"SSH tunnel established using key: {key_path}")
                break
            except paramiko.PasswordRequiredException:
                self.logger.error(f"Password required for key: {key_path}. Skipping this key.")
            except Exception as e:
                self.logger.error(f"Attempt with key {key_path} failed: {e}")

        if not self.tunnel:
            self.logger.error("All SSH authentication attempts failed.")
            raise Exception("SSH authentication failed")

        self.connection = pymysql.connect(
            host='127.0.0.1',
            port=self.tunnel.local_bind_port,
            user=self.MYSQL_USER,
            password=self.MYSQL_PASSWORD,
            cursorclass=pymysql.cursors.DictCursor 
        )
        self.logger.info("MySQL database connection established.")

    def get_connection(self) -> pymysql.connections.Connection:
        return self.connection

    def close(self):
        if self.connection:
            self.connection.close()
            self.logger.info("MySQL database connection closed.")
        if self.tunnel:
            self.tunnel.stop()
            self.logger.info("SSH tunnel closed.")

class ExecuteQuery:
    def __init__(self, db_connection: pymysql.connections.Connection, logger: logging.Logger):
        self.connection = db_connection
        self.logger = logger

    def execute(self, query: str) -> Dict[str, Any]:
        try:
            start_time = time.time()
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                row_count = len(rows)
            end_time = time.time()
            execution_time = end_time - start_time

            return {
                "columns": columns,
                "rows": rows,
                "execution_time": round(execution_time, 4),
                "row_count": row_count
            }
        except pymysql.MySQLError as e:
            return {"error": str(e)}

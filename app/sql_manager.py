import mysql.connector
from mysql.connector.errors import InterfaceError, PoolError

class SqlManager:
    __connection_pool = None
    __config = None

    @classmethod
    def set_config(cls, config):
        cls.__config = config

    @classmethod
    def get_conn(cls):
        try:
            if cls.__connection_pool is None:
                cls.__connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name="mypool",
                    pool_size=10,  # Max connections
                    pool_reset_session=True,
                    **cls.__config
                )
            return cls.__connection_pool.get_connection()
        except InterfaceError :
            print('Could not create the connection pool.')
            raise
        except PoolError:
            print('Could not get a connection from the pool.')
            raise

    @staticmethod
    def execute_query(query, values=None, *, commit=False, fetch=False, dictionary=False):
        try:
            conn = SqlManager.get_conn()
            cursor = conn.cursor(dictionary=dictionary) if dictionary else conn.cursor()
            cursor.execute(query, values)
            if commit:
                conn.commit()
                result = cursor.lastrowid
            if fetch:
                result = cursor.fetchall()
            return result
        except Exception as error:
            print('SqlManager.execute_query() exception : %s %s %s' % (type(error), type(error).__name__, error))
            raise
        finally:
            cursor.close()
            conn.close()

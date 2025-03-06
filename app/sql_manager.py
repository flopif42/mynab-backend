import mysql.connector
from mysql.connector.errors import InterfaceError, PoolError

class SqlManager:
    __connection_pool = None
    __config = None

    @staticmethod
    def set_config(config):
        SqlManager.__config = config

    @staticmethod
    def get_conn():
        try:
            if SqlManager.__connection_pool is None:
                SqlManager.__connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name="mypool",
                    pool_size=0,  # Max connections
                    pool_reset_session=True,
                    **SqlManager.__config
                )
            return SqlManager.__connection_pool.get_connection()
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
            # Choose the appropriate cursor based on the 'dictionary' flag.
            cursor = conn.cursor(dictionary=dictionary) if dictionary else conn.cursor()
            cursor.execute(query, values)
        
            if commit:
                conn.commit()
                result = cursor.lastrowid
            if fetch:
                result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        except Exception as error:
            print('SqlManager.execute_query() exception : %s %s %s' % (type(error), type(error).__name__, error))
            raise

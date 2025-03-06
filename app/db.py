import mysql.connector

class DbPool:
    _pool_instance = None
    _config = None

    def __init__(self):
        if not DbPool._pool_instance:
            raise RuntimeError("Use DbPool.get_instance() instead of instantiating directly.")

    @staticmethod
    def get_instance():
        if DbPool._pool_instance is None:
            try:
                # Create the connection pool once at startup
                DbPool._pool_instance = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name="mypool",
                    pool_size=10,  # Max connections
                    pool_reset_session=True,
                    **DbPool._config
                )
            except Exception as error:
                print('db.get_instance() exception : %s %s' % (type(error).__name__, error))
                raise
        return DbPool._pool_instance

    @staticmethod
    def get_connection():
        try:
            return DbPool.get_instance().get_connection()
        except Exception as error:
            print('db.get_connection() exception : %s %s' % (type(error).__name__, error))
            raise

def execute_query(query, values=None, *, commit=False, fetch=False, dictionary=False):
    try:
        conn = DbPool.get_connection()
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
        print('db.execute_query() exception : %s %s' % (type(error).__name__, error))
        raise

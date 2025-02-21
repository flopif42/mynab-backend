import mysql.connector
import app.db as db
    
def get_profile(id_user, unused):
    try:
        query = "select FIRST_NAME, LAST_NAME, EMAIL_ADDRESS from USER where ID_USER = (%s)"
        result = db.execute_query(query, (str(id_user),), fetch=True)
        return result
    except Exception as err:
        print(f"Could not retrieve user profile : {err}")
        raise

# This function returns the ID_USER if the authentication was successful, otherwise None
def login(request_params):
    try:
        query = "select ID_USER from USER where EMAIL_ADDRESS = (%s) and PASSPHRASE_MD5 = (%s)"
        result = db.execute_query(query, (request_params['email_address'], request_params['passphrase_md5']), fetch=True)
        id_user = result[0][0] if len(result) else None
        return id_user
    except Exception as err:
        print(f"Exception in login() : {err}")
        raise

def signup(request_params):
    try:
        query = "insert into USER (FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PASSPHRASE_MD5) values (%s, %s, %s, %s)"
        values = (
            request_params['first_name'],
            request_params['last_name'],
            request_params['email_address'],
            request_params['passphrase_md5']
        )
        result = db.execute_query(query, values, commit=True)
        print(result)
    except mysql.connector.IntegrityError:
        print(f"Could not create user : email address already used")
        return 403
    except Exception as error:
        print(f"Exception in signup() : {error}")
        return 400
        


def signup_old(formData):
    query = "insert into USER (FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PASSPHRASE_MD5) values (%s, %s, %s, %s)"
    values = (formData['first_name'], formData['last_name'], formData['email_address'], formData['passphrase_md5'])
    try:
        conn = DbPool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return ""
    except Exception as error:
        print('Exception : %s %s' % (type(error).__name__, error))
        return None



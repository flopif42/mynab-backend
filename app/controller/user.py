import app.db as db
    
def get_profile(id_user, unused):
    try:
        query = "select FIRST_NAME, LAST_NAME, EMAIL_ADDRESS from USER where ID_USER = (%s)"
        result = db.excute_query(query, (str(id_user),), fetch=True)
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


def get_profile_old(id_user):
    query_profile = "select FIRST_NAME, LAST_NAME, EMAIL_ADDRESS from USER where ID_USER = %s"
    try:
        conn = DbPool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query_profile, (str(id_user),))
        response = cursor.fetchall()
        cursor.close()
        conn.close()
        return response
    except Exception as error:
        print('Exception : %s %s' % (type(error).__name__, error))
        raise
    return None

def signup(formData):
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



import app.db as db
    
def get_profile(id_user):
    try:
        query = "select FIRST_NAME, LAST_NAME, EMAIL_ADDRESS from USER where ID_USER = (%s)"
        result = db.excute_query(query, (str(id_user),), fetch=True)
        return result
    except Exception as err:
        print(f"Could not retrieve user profile : {err}")
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

# This function checks for the combination of email address and MD5 passphrase sent in parameters.
#  Parameters  : email address (string)
#                MD5 passphrase (string)
#  Return type : int or NoneType
#  Returns     : ID_USER (int) if the authentication was successful or 'None' otherwise
def authenticate(cred):
    query_auth = "select ID_USER from USER where EMAIL_ADDRESS = %s and PASSPHRASE_MD5 = %s"
    try:
        conn = DbPool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query_auth, (cred['email_address'], cred['passphrase_md5']))
        resultset = cursor.fetchall()

        # exactly one row returned, auth successful
        if cursor.rowcount == 1:
            id_user = resultset[0][0]
            response = id_user
        else:
            response = None
        cursor.close()
        conn.close()
    except Exception as error:
        print('Exception : %s %s' % (type(error).__name__, error))
        raise
    return response

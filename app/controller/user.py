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
        id_user = db.execute_query(query, values, commit=True)

        db.execute_query("insert into PARENT_CATEGORY (ID_PARENT_CATEGORY, ID_USER, PARENT_CATEGORY_NAME) values (0, (%s), 'Income')", (id_user,), commit=True)
        db.execute_query("insert into CATEGORY (ID_CATEGORY, ID_USER, ID_PARENT_CATEGORY, CATEGORY_NAME) values (0, (%s), 0, 'Available this month')", (id_user,), commit=True)
        db.execute_query("insert into CATEGORY (ID_CATEGORY, ID_USER, ID_PARENT_CATEGORY, CATEGORY_NAME) values (1, (%s), 0, 'Available next month')", (id_user,), commit=True)

    except mysql.connector.IntegrityError:
        print(f"Could not create user : email address already used")
        return 403
    except Exception as error:
        print(f"Exception in signup() : {error}")
        return 400
        
# This function checks the database to see if an email address is available to use to sign up
# return values: 1 The email address is available
#                0 The email address is already used
#               -1 There was an error in the query
def is_available(request_params):
    try:
        query = "select 1 from USER where EMAIL_ADDRESS = (%s)"
        result = db.execute_query(query, (request_params['email_address'],), fetch=True)
        if len(result) == 1:
            return 0
        else:
            return 1
    except Exception as error:
        print(f"Exception in is_available() : {error}")
        return -1

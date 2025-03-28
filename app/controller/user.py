import mysql.connector
from app.sql_manager import SqlManager
from pydantic import BaseModel, EmailStr
    
class UserSignUpParams(BaseModel):
    first_name: str
    last_name: str
    email_address: EmailStr
    password_md5: str

def get_profile(id_user, unused):
    try:
        query = "select FIRST_NAME, LAST_NAME, EMAIL_ADDRESS from USER where ID_USER = (%s)"
        result = SqlManager.execute_query(query, (id_user,), fetch=True)
        return result
    except Exception as err:
        print(f"Could not retrieve user profile : {err}")
        raise

# This function returns the ID_USER if the authentication was successful, otherwise None
def login(request_params):
    try:
        query = "select ID_USER from USER where EMAIL_ADDRESS = (%s) and PASSPHRASE_MD5 = (%s)"
        result = SqlManager.execute_query(query, (request_params['email_address'], request_params['passphrase_md5']), fetch=True)
        id_user = result[0][0] if len(result) else None
        return id_user
    except Exception as err:
        print(f"Exception in login() : {err}")
        raise

# This function checks the validity of sign up parameters and if all is ok, creates the user in the database.
# Return values:
#   0 : parameters are valid and the user has been created
#   1 : the user could not be created because the submitted email address is already used
#   2 : the user could not be created because some of the parameters are invalid
#
def signup(request_params):
    try:
        user = UserInput(request_params)
        print("All good:", user.dict())
    except Exception as e:
        print("Validation failed:", e)

    try:
        query = "insert into USER (FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PASSPHRASE_MD5) values (%s, %s, %s, %s)"
        values = (
            request_params['first_name'],
            request_params['last_name'],
            request_params['email_address'],
            request_params['passphrase_md5']
        )
        id_user = SqlManager.execute_query(query, values, commit=True)

        # ID_CATEGORY 0 is a technical value for Income.
        SqlManager.execute_query("insert into PARENT_CATEGORY (ID_PARENT_CATEGORY, ID_USER, PARENT_CATEGORY_NAME) values (0, (%s), '(system)')", (id_user,), commit=True)
        SqlManager.execute_query("insert into CATEGORY (ID_CATEGORY, ID_USER, ID_PARENT_CATEGORY, CATEGORY_NAME) values (0, (%s), 0, 'Income')", (id_user,), commit=True)
        return 0
    except mysql.connector.IntegrityError:
        print(f"Could not create user : email address already used")
        return 1
    except Exception as error:
        print(f"Exception in signup() exception : {type(error)} - {type(error).__name__} - {error}")
        raise error
        
# This function checks the database to see if an email address is available to use to sign up
# return values: 1 The email address is available
#                0 The email address is already used
#               -1 There was an error in the query
def is_available(email_address):
    try:
        query = "select 1 from USER where EMAIL_ADDRESS = (%s)"
        result = SqlManager.execute_query(query, (email_address,), fetch=True)
        if len(result) == 0:
            return True
        elif len(result) == 1:
            return False
        else:
            raise
    except Exception as error:
        print(f"Exception in is_available() exception : {type(error)} - {type(error).__name__} - {error}")
        raise error

import re
import mysql.connector
from app.sql_manager import SqlManager
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
    
# This class is used to validate data
class UserSignUpParams(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_address: EmailStr
    passphrase_md5: str

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, value):
        if value in (None, ''):
            return None
        if not value.isalpha():
            raise ValueError('Name must contain only alphabetic characters')
        if len(value) > 50:
            raise ValueError('Name must be 50 characters or fewer')
        return value

    @field_validator('passphrase_md5')
    @classmethod
    def validate_md5(cls, value):
        if not re.fullmatch(r'^[a-fA-F0-9]{32}$', value):
            raise ValueError('Password must be a valid MD5 hash')
        return value

def get_profile(id_user, unused):
    try:
        query = "select FIRST_NAME as first_name, LAST_NAME as last_name, EMAIL_ADDRESS as email_address from USER where ID_USER = (%s)"
        result = SqlManager.execute_query(query, (id_user,), fetch=True, dictionary=True)
        return result[0]
    except Exception as err:
        print(f"Could not retrieve user profile : {err}")
        raise

def login(request_params):
    try:
        query = "select ID_USER from USER where EMAIL_ADDRESS = (%s) and PASSPHRASE_MD5 = (%s)"
        result = SqlManager.execute_query(query, (request_params['email_address'], request_params['passphrase_md5']), fetch=True)
        id_user = result[0][0] if len(result) else None
        return id_user
    except Exception as error:
        print(f"Exception in login() : {type(error)} - {type(error).__name__} - {error}")
        raise error

def signup(request_params):
    """
    This function checks the validity of sign up parameters and if all is ok, creates the user in the database.
    
    Exceptions:
        ValueError : if some of the parameters are invalid
        IntegrityError : the submitted email address is already used
    """
    try:
        user_params = UserSignUpParams(**request_params)
        query = "insert into USER (FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PASSPHRASE_MD5) values (%s, %s, %s, %s)"
        values = (
            user_params.first_name,
            user_params.last_name,
            user_params.email_address,
            user_params.passphrase_md5
        )
        id_user = SqlManager.execute_query(query, values, commit=True)
        SqlManager.execute_query("insert into PARENT_CATEGORY (ID_PARENT_CATEGORY, ID_USER, PARENT_CATEGORY_NAME) values (0, (%s), '(system)')", (id_user,), commit=True)
        SqlManager.execute_query("insert into CATEGORY (ID_CATEGORY, ID_USER, ID_PARENT_CATEGORY, CATEGORY_NAME) values (0, (%s), 0, 'Income')", (id_user,), commit=True)
    except ValueError as e:
        print("Validation failed:", e)
        raise e
    except mysql.connector.IntegrityError:
        raise RuntimeError("Could not create user : email address already used")
    except Exception as error:
        print(f"Exception in signup() : {type(error)} - {type(error).__name__} - {error}")
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
        print(f"Exception in is_available() : {type(error)} - {type(error).__name__} - {error}")
        raise error

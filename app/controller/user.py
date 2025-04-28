import re
from typing import Optional
import mysql.connector
from app.sql_manager import SqlManager as db
from app.jwt_manager import JwtManager
from pydantic import BaseModel, EmailStr, field_validator
from app.utils import validate_not_empty
from app.exceptions import InvalidParametersError, UserMailAdressUnavailableError, UserInvalidCredentialsError
    
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

def is_email_available(id_user_unused, request):
    """
    This function checks the database to see if the specified email address is available to use to sign up.
    
    Return values:
        True : The email address is available
        False : The email address is not available
    """
    email_address = validate_not_empty(request, 'email_address')
    query = "select 1 from USER where EMAIL_ADDRESS = (%s)"
    result = db.execute_query(query, (email_address,), fetch=True)
    return { 'available' : not len(result) }

def signup(id_user_unused, request):
    """
    This function checks the validity of sign up parameters and if all is ok, creates the user in the database.
    
    Exceptions:
        ValueError : if some of the parameters are invalid
        IntegrityError : the submitted email address is already used
    """
    try:
        user_params = UserSignUpParams(**request.json)
        query = "insert into USER (FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PASSPHRASE_MD5) values (%s, %s, %s, %s)"
        values = (
            user_params.first_name,
            user_params.last_name,
            user_params.email_address,
            user_params.passphrase_md5
        )
        id_user = db.execute_query(query, values, commit=True)
        db.execute_query("insert into PARENT_CATEGORY (ID_PARENT_CATEGORY, ID_USER, PARENT_CATEGORY_NAME) values (0, (%s), '(system)')", (id_user,), commit=True)
        db.execute_query("insert into CATEGORY (ID_CATEGORY, ID_USER, ID_PARENT_CATEGORY, CATEGORY_NAME) values (0, (%s), 0, 'Income')", (id_user,), commit=True)
        db.execute_query("insert into USER_PREFERENCES (ID_USER) values (%s)", (id_user,), commit=True)
    except ValueError:
        raise InvalidParametersError
    except mysql.connector.IntegrityError:
        raise UserMailAdressUnavailableError

def login(id_user_unused, request):
    email_address = validate_not_empty(request, 'email_address')
    passphrase_md5 = validate_not_empty(request, 'passphrase_md5')
    query = "select ID_USER from USER where EMAIL_ADDRESS = (%s) and PASSPHRASE_MD5 = (%s)"
    result = db.execute_query(query, (email_address, passphrase_md5), fetch=True)
    id_user = result[0][0] if len(result) else None
    if id_user is None:
        raise UserInvalidCredentialsError
    return JwtManager.generate_access_token(id_user) # HTTP response with status code 200 and cookie set (no body)

def get_profile(id_user, request_unused):
    query = '''
            select
                FIRST_NAME as first_name,
                LAST_NAME as last_name,
                EMAIL_ADDRESS as email_address,
                UI_COLLAPSE_SECTION_CASH as ui_collapse_cash,
                UI_COLLAPSE_SECTION_TRACKING as ui_collapse_tracking,
                UI_COLLAPSE_SECTION_CLOSED as ui_collapse_closed
            from USER u inner join USER_PREFERENCES p
              on p.ID_USER = u.ID_USER
            where u.ID_USER = (%s)
            '''
    result = db.execute_query(query, (id_user,), fetch=True, dictionary=True)
    ret = result[0]
    ret['ui_collapse_cash'] = bool(ret['ui_collapse_cash'])
    ret['ui_collapse_tracking'] = bool(ret['ui_collapse_tracking'])
    ret['ui_collapse_closed'] = bool(ret['ui_collapse_closed'])
    return ret

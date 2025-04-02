import jwt
from jwt.exceptions import DecodeError
import json
import time
from flask import make_response, request

class JwtManager:
    __config = None

    @classmethod
    def set_config(cls, config):
        cls.__config = config

    # returns an HttpResponse with a cookie set for the requested token
    @classmethod
    def generate_access_token(cls, id_user):
        token_exp_time = int(time.time()) + cls.__config['AccessToken']['LifespanSeconds']
        payload = {
            'algorithm': cls.__config['Algorithm'],
            'expirationTime': token_exp_time,
            'idUser': id_user
        }
        try:
            private_key_fd = open(cls.__config['PrivateKeyFile'])
            token = jwt.encode(payload, private_key_fd.read(), algorithm=cls.__config['Algorithm']).decode(cls.__config['Encoding'])
            response = make_response()
            response.set_cookie(cls.__config['AccessToken']['CookieName'], value=token, **cls.__config['CookieSettings'])
            return response
        except Exception as err:
            print(f"Could not generate Access Token token. Exception : {err}")

    @classmethod
    def get_payload(cls, request):
        try:
            token = request.cookies.get(cls.__config['AccessToken']['CookieName'])
            encoded_bytes = token.encode(encoding=cls.__config['Encoding'])
            public_key_fd = open(cls.__config['PublicKeyFile'])
            payload = jwt.decode(encoded_bytes, public_key_fd.read(), algorithms=[cls.__config['Algorithm']])
            return payload
        except AttributeError:
            print(f"Error : Access Token cookie not found.")
        except DecodeError:
            print(f"Error : Could not decode payload from Access Token.")
        except Exception as err:
            print(f"Could not retrieve payload from Access Token. Exception : {err}")

    @classmethod
    def check_token_valid(cls, request):
        try:
            payload = cls.get_payload(request)
            token_exp_time = payload['expirationTime']
            current_time = int(time.time())
            formatted_exp_time = time.strftime('%d/%m/%Y %H:%M:%S', time.localime(token_exp_time))
            formatted_cur_time = time.strftime('%d/%m/%Y %H:%M:%S', time.localime(current_time))
            print(f"Access Token expiration time : {formatted_exp_time}, current time : {formatted_cur_time}")
            if token_exp_time >= current_time:
                return True
            return False
        except Exception as err:
            print(f"Exception in check_token_valid() : {type(error).__name__} - {error}")
            return False
    
    @classmethod
    def get_id_user_from_token(cls, request):
        return cls.get_payload(request)['idUser']

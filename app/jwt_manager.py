import jwt
from jwt.exceptions import DecodeError
import json
import time
from flask import make_response, request

class JwtManager:
    __config = None

    @staticmethod
    def set_config(config):
        JwtManager.__config = config

    # returns an HttpResponse with a cookie set for the requested token
    @staticmethod
    def generate_access_token(id_user: int):
        token_exp_time = int(time.time()) + JwtManager.__config['AccessToken']['LifespanSeconds']
        payload = {
            'algorithm': JwtManager.__config['Algorithm'],
            'expirationTime': token_exp_time,
            'idUser': id_user
        }
        try:
            private_key_fd = open(JwtManager.__config['PrivateKeyFile'])
            token = jwt.encode(payload, private_key_fd.read(), algorithm=JwtManager.__config['Algorithm']).decode(JwtManager.__config['Encoding'])
            response = make_response()
            response.set_cookie(JwtManager.__config['AccessToken']['CookieName'], value=token, **JwtManager.__config['CookieSettings'])
            formatted_exp_time = time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(token_exp_time))
            return response
        except Exception as err:
            print(f"Could not generate Access Token token. Exception : {err}")

    @staticmethod
    def get_payload(request):
        try:
            token = request.cookies.get(JwtManager.__config['AccessToken']['CookieName'])
            encoded_bytes = token.encode(encoding=JwtManager.__config['Encoding'])
            public_key_fd = open(JwtManager.__config['PublicKeyFile'])
            payload = jwt.decode(encoded_bytes, public_key_fd.read(), algorithms=[JwtManager.__config['Algorithm']])
            return payload
        except AttributeError:
            print(f"Error : Access Token cookie not found.")
        except DecodeError:
            print(f"Error : Could not decode payload from Access Token.")
        except Exception as err:
            print(f"Could not retrieve payload from Access Token. Exception : {err}")

    @staticmethod
    def check_token_valid(request):
        try:
            payload = JwtManager.get_payload(request)
            token_exp_time = payload['expirationTime']
            current_time = int(time.time())
            formatted_exp_time = time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(token_exp_time))
            formatted_cur_time = time.strftime('%d/%m/%Y %H:%M:%S', time.gmtime(current_time))
            print(f"Access Token expiration time : {formatted_exp_time}, current time : {formatted_cur_time}")
            if token_exp_time >= current_time:
                return True
            return False
        except Exception as err:
            return False
    
    @staticmethod
    def get_id_user_from_token(request):
        return JwtManager.get_payload(request)['idUser']

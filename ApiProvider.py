import configparser
from gmusicapi import Mobileclient


class ApiProvider:
    __api = None

    @staticmethod
    def get_api():
        if ApiProvider.__api is None:
            config = configparser.ConfigParser()
            config.read('settings.ini')
            email = config['LOGIN']['email']
            password = config['LOGIN']['password']
            android_id = config['LOGIN']['android_id']
            ApiProvider.__api = Mobileclient()
            logged_in = ApiProvider.__api.login(email, password, android_id)
        return ApiProvider.__api
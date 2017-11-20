import configparser
from gmusicapi import Mobileclient

from controller.DataLoader import load_song_data
from controller.RecommendationTool import create_recommended_playlist

from db.Connection import Connection


config = configparser.ConfigParser()
config.read('settings.ini')
email = config['LOGIN']['email']
password = config['LOGIN']['password']
android_id = config['LOGIN']['android_id']
api = Mobileclient()
logged_in = api.login(email, password, android_id)
load_song_data(api)
create_recommended_playlist(api)
Connection.instance().close()

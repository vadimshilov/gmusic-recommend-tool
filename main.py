from ApiProvider import ApiProvider
from controller.DataLoader import load_song_data
from controller.RecommendationTool import create_recommended_playlist


from db.Connection import Connection


api = ApiProvider.get_api()
load_song_data(api)
create_recommended_playlist(api)
# create_artist_playlist(api, 3372, True)
Connection.instance().close()

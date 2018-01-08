from datetime import date

from db.Artist import Artist
from db.Song import Song
from db.repository import ArtistRepository
from db.repository import SongRepository


def load_song_data(api):
    songs = api.get_promoted_songs()
    artists = set()
    liked_songs = set()
    for song in songs:
        artists.add(song['artistId'][0])
        liked_songs.add(song['nid'])
    loaded_artists = set()
    artist_blacklist = ArtistRepository.get_artist_blacklist()
    artist_data = {x.google_id: x for x in ArtistRepository.find_all()}
    for id in artists:
        _load_artist(api, 'A' + id, loaded_artists, True, artist_blacklist, artists, artist_data)

    artist_map = ArtistRepository.get_google_id_id_map()
    for song in songs:
        if 'A' + song['artistId'][0] in artist_map:
            artist_id = artist_map['A' + song['artistId'][0]]
            _init_tracks([song], Artist(artist_id, '', '', None), False)


def _load_artist(api, id, loaded_artists, load_related, artist_blacklist, promoted_artists, artist_data):
    if not id.startswith('A'):
        id = 'A' + id
    if id in loaded_artists or id in artist_blacklist:
        return
    loaded_artists.add(id)
    print("Retrieving artist with ID = " + id)
    iterations = 10
    artist = None
    while artist is None and iterations > 0:
        try:
            artist = api.get_artist_info(id, max_top_tracks=10000, max_rel_artist=20)
        except:
            iterations -= 1
    if artist is None:
        return
    print("Artist " + artist['name'] + " retrieved")
    if 'topTracks' not in artist:
        return
    print("Track count " + str(len(artist['topTracks'])))
    db_artist = _create_db_artist(artist)
    if db_artist.google_id in artist_data:
        db_artist.load_albums_date = artist_data[db_artist.google_id].load_albums_date
    ArtistRepository.save_one(db_artist)
    tracks = artist['topTracks']
    db_tracks = set(_init_tracks(tracks, db_artist, True))
    if _should_load_albums(db_tracks) and 'albums' in artist:
        load_albums = True
        today = date.today().toordinal()
        if db_artist.load_albums_date is not None:
            if today - db_artist.load_albums_date < 7:
                load_albums = False
        if load_albums:
            for album in artist['albums']:
                album_info = api.get_album_info(album['albumId'])
                if 'tracks' not in album_info:
                    continue
                album_tracks = set(_init_tracks(album_info['tracks'], db_artist, False))
                db_tracks.union(album_tracks)
            db_artist.load_albums_date = today
            ArtistRepository.save_one(db_artist)
    SongRepository.save_many(db_tracks)
    if (load_related or _should_load_related_artists(db_tracks) or id in promoted_artists) \
            and 'related_artists' in artist:
        ArtistRepository.save_related_artist(id, artist['related_artists'])
        for related_artist in artist['related_artists']:
            _load_artist(api, related_artist['artistId'], loaded_artists, False, artist_blacklist, promoted_artists,
                         artist_data)


def _should_load_albums(tracks):
    if len(tracks) == 0:
        return False
    known_track_count = 0
    for track in tracks:
        if track.playcount >= 10 or track.playcount == 5:
            known_track_count += 1

    return known_track_count * 2 >= len(tracks)


def _should_load_related_artists(tracks):
    total_playcount = 0
    for track in tracks:
        if track.playcount != 0:
            total_playcount += track.playcount
    print("Total play count: " + str(total_playcount))
    return total_playcount > 50  # MAGIC


def _init_tracks(tracks, artist, init_ord):
    db_tracks = []
    i = 0
    for track in tracks:
        google_id = track['storeId']
        name = track['title']
        rate = 0
        if 'rating' in track:
            rate = track['rating']
        playcount = 0
        if 'playCount' in track:
            playcount = track['playCount']
        album_id = None
        album_google_id = track['albumId']
        ord = i if init_ord else 2000000000
        db_tracks.append(Song(None, google_id, name, album_id, rate, playcount, album_google_id, artist.id, ord))
        i += 1
    SongRepository.save_many(db_tracks)
    return db_tracks


def _create_db_artist(artist):
    google_id = artist['artistId']
    name = artist['name']
    return Artist(None, google_id, name, None)

import random
import math

from operator import itemgetter
from datetime import date, timedelta
from db.repository import ArtistRepository
from db.repository import SongRepository


def create_recommended_playlist(api):
    songs = SongRepository.find_all()
    song_map = {}
    for song in songs:
        artist_id = song.artist_id
        if artist_id not in song_map:
            song_map[artist_id] = []
        song_map[artist_id].append(song)
    artist_score = {}
    related_score = {}
    history_playcount = _get_playcount_history()
    google_id_id_map = ArtistRepository.get_google_id_id_map()
    blacklist = {google_id_id_map[id] for id in ArtistRepository.get_artist_blacklist() if id in google_id_id_map}
    for artist_id, songs in song_map.items():
        if artist_id in blacklist:
            continue
        artist_score[artist_id] = max(_calc_own_score(songs, history_playcount), 0)
        related_score[artist_id] = 0
        songs = [x for x in songs if x.rate != 1]
        song_map[artist_id] = songs
    related_artists = ArtistRepository.get_related_artists()
    for artist_id, links in related_artists.items():
        if artist_id not in google_id_id_map:
            continue
        id1 = google_id_id_map[artist_id]
        if id1 not in artist_score:
            continue
        i = 0
        for link in links:
            if link not in google_id_id_map:
                continue
            id2 = google_id_id_map[link]
            if id2 not in related_score:
                continue
            if i * 3 < len(links):
                koef = 0.75
            elif i * 3 < len(links):
                koef = 1.25
            else:
                koef = 2.25
            related_score[id2] += artist_score[id1] / koef / len(links) / 1.5
            i += 1
    for artist_id, score in related_score.items():
        artist_score[artist_id] += score
    total_score = 0
    min_score = min([v for (k, v) in artist_score.items() if v >= 0])
    for artist_id, score in artist_score.items():
        if score <= 0:
            artist_score[artist_id] = min_score
        total_score += artist_score[artist_id]
    choosen_songs = set()
    playlist = []
    random.seed()
    _print_artist_score(artist_score)
    while len(choosen_songs) < 1000:
        p = random.random() * total_score
        choosen_artist = ''
        for artist_id, score in artist_score.items():
            choosen_artist = artist_id
            p -= score
            if p <= 0:
                break
        artist_songs = song_map[choosen_artist]
        ind = _choose_song(artist_songs)
        if ind is None:
            continue
        song_id = artist_songs[ind].google_id
        artist_songs.pop(ind)
        if song_id not in choosen_songs:
            choosen_songs.add(song_id)
    playlist_id = api.create_playlist(date.today().isoformat())
    choosen_song_list = list(choosen_songs)
    random.shuffle(choosen_song_list)
    api.add_songs_to_playlist(playlist_id, choosen_song_list[0:300])


def create_artist_playlist(api, artist_id, include_related_artists):
    all_songs = SongRepository.find_all()
    artist = ArtistRepository.find_one(artist_id)
    if include_related_artists:
        google_id_id_map = ArtistRepository.get_google_id_id_map()
        related_artists =\
            [google_id_id_map[google_id] for google_id in ArtistRepository.get_related_artists()[artist.google_id]]
        songs = [song for song in all_songs if song.artist_id in related_artists or song.artist_id == artist_id]
    else:
        songs = [song for song in all_songs if song.artist_id == artist_id]
    song_ids = [song.google_id for song in songs]
    random.shuffle(song_ids)
    playlist_id = api.create_playlist(artist.name + " " + date.today().isoformat())
    api.add_songs_to_playlist(playlist_id, song_ids[0:300])


def _get_playcount_history(periods=4):
        result = []
        to_date = date.today()
        diff = timedelta(28)
        for week in range(periods):
            from_date = to_date - diff
            result.append(SongRepository.find_playcount_history(from_date, to_date))
            to_date = from_date
        return result


def _print_artist_score(artist_score):
    score = [[key, value] for (key, value) in artist_score.items()]
    score = sorted(score, key=itemgetter(1))
    for x in score:
        print(str(x[1]) + " " + str(x[0]))


def _choose_song(songs):
    if len(songs) == 0:
        return None
    song_map = {songs[i].id: i for i in range(len(songs))}
    known = [song.id for song in songs if song.playcount >= 12 or song.rate == 5]
    unknown = [song.id for song in songs if song.playcount < 12 and song.rate != 5]
    if random.random() < 0.6 and len(unknown) != 0 or len(known) == 0:
        score = [2**(len(unknown) - i) for i in range(len(unknown))]
        song_list = unknown
    else:
        score = [1] * len(known)
        song_list = known
    total_score = sum(score)
    if total_score == 0:
        return None
    p = random.randint(1, total_score)
    for i in range(len(song_list)):
        p -= score[i]
        if p <= 0:
            return song_map[song_list[i]]
    return len(songs) - 1


def _calc_own_score(songs, playcount_history):
    result = 0
    playcount = 0
    history_playcount = 0
    for song in songs:
        if song.playcount is not None and song.rate != 1:
            playcount += song.playcount
        if song.rate == 5:
            result += 5
        if song.rate == 1:
            result -= 5
        i = 1
        for history_map in playcount_history:
            if song.id in history_map:
                history_playcount += history_map[song.id] / i
            i += 1
    return result + math.sqrt(playcount / 4) + history_playcount
from datetime import date

from db.Connection import Connection
from db.Song import Song


def get_cursor():
    return Connection.instance().get_cursor()


def _save_one(song, cursor, db_song):
    if db_song is None:
        cursor.execute("INSERT INTO song (google_id, name, album_id, rate, playcount, album_google_id, artist_id, ord) "
                       "VALUES(:google_id, :name, :album_id, :rate, :playcount, :album_google_id, :artist_id, :ord)",
                       {"google_id": song.google_id, "name": song.name, "album_id": song.album_id,
                        "rate": song.rate, "playcount": song.playcount, "album_google_id": song.album_google_id,
                        "artist_id": song.artist_id, "ord": song.ord})
        song.id = cursor.lastrowid
        if song.playcount != 0:
            cursor.execute("INSERT INTO history(song_id, event_date, playcount_delta) "
                           "VALUES(:song_id, :event_date, :playcount_delta)",
                           {"song_id": song.id, "event_date": date.today().toordinal(),
                            "playcount_delta": song.playcount})
    else:
        cursor.execute("UPDATE song SET google_id = :google_id, name = :name, album_id = :album_id, rate = :rate, "
                       "playcount = :playcount, ord = :ord, artist_id = :artist_id WHERE id = :id",
                       {"id": db_song.id, "google_id": song.google_id, "name": song.name, "album_id": song.album_id,
                        "rate": song.rate, "playcount": song.playcount, "ord": song.ord, "artist_id": song.artist_id})
        playcount_delta = song.playcount - db_song.playcount
        if playcount_delta > 0:
            cursor.execute("SELECT playcount_delta FROM history WHERE song_id = :song_id AND event_date = :event_date",
                           {"song_id": song.id, "event_date": date.today().toordinal()})
            db_data = cursor.fetchone()
            if db_data is not None:
                playcount_delta += db_data[0]
            cursor.execute("REPLACE INTO history(song_id, event_date, playcount_delta) "
                           "VALUES(:song_id, :event_date, :playcount_delta)",
                           {"song_id": db_song.id, "event_date": date.today().toordinal(),
                            "playcount_delta": playcount_delta})


def save_many(song_list):
    songs_google_id_map = {song.google_id: song for song in song_list}
    db_song_map = {db_song.google_id: db_song for db_song in find_all_by_google_id_list(songs_google_id_map.keys())}
    try:
        cursor = get_cursor()
        cursor.execute("begin")
        for song in song_list:
            if song.google_id in db_song_map:
                _save_one(song, cursor, db_song_map[song.google_id])
            else:
                _save_one(song, cursor, None)
        cursor.execute("end")
    except Exception as e:
        cursor.execute("rollback")
        raise e


def find_all_by_google_id_list(google_id_list):
    cursor = get_cursor()
    result = []
    google_id_list = [x for x in google_id_list]
    while len(google_id_list) > 0:
        current_list = google_id_list[:100]
        sql = 'SELECT id, google_id, name, album_id, rate, playcount, album_google_id, artist_id, ord' \
              ' FROM song WHERE google_id IN ({seq})'.format(
                seq=','.join(['?'] * len(current_list)))
        cursor.execute(sql, [x for x in current_list])
        for record in cursor:
            result.append(Song(record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7],
                               record[8]))
        google_id_list = google_id_list[100:]
    return result


def find_all():
    sql = 'SELECT id, google_id, name, album_id, rate, playcount, album_google_id, artist_id, ord FROM song ' \
          'ORDER BY ord - playcount'
    cursor = get_cursor()
    cursor.execute(sql)
    result = []
    for record in cursor:
        result.append(Song(record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7],
                           record[8]))
    return result


def find_playcount_history(from_date, to_date):
    cursor = get_cursor()
    cursor.execute('SELECT song_id, sum(playcount_delta) FROM history GROUP BY song_id '
                   'HAVING event_date <= :to_date and event_date > :from_date',
                   {"from_date": from_date.toordinal(), "to_date": to_date.toordinal()})
    return {result[0]: result[1] for result in cursor}

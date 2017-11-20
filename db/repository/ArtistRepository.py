from db.Artist import Artist
from db.Connection import Connection


def get_cursor():
    return Connection.instance().get_cursor()


def save_one(artist):
    try:
        cursor = get_cursor()
        cursor.execute("begin")
        artist_id = artist.id
        if artist_id is None:
            db_artist = find_one_by_google_id(artist.google_id)
            if not db_artist is None:
                artist_id = db_artist.id
        _save_one(artist, cursor, artist_id)
        cursor.execute("end")
    except Exception as e:
        cursor.execute("rollback")
        raise e


def _save_one(artist, cursor, artist_id):
    if artist_id is None:
        cursor.execute("INSERT INTO artist(google_id, name, load_albums_date) "
                       "VALUES(:google_id, :name, :load_albums_date)",
                       {"google_id": artist.google_id, "name": artist.name, "load_albums_date": artist.load_albums_date}
                       )
        artist.id = cursor.lastrowid
    else:
        cursor.execute("UPDATE artist SET google_id = :google_id, name = :name, load_albums_date = :load_albums_date"
                       " WHERE id = :id",
                       {"id": artist_id, "google_id": artist.google_id, "name": artist.name, "load_albums_date":
                           artist.load_albums_date})
        artist.id = artist_id


def save_many(artist_list):
    artists_without_id = {}
    for artist in artist_list:
        if artist.id is None:
            artists_without_id[artist.google_id] = artist
    for db_artist in find_all_by_google_id_list(artists_without_id.keys()):
        artists_without_id[db_artist.google_id].id = db_artist.id

    try:
        cursor = get_cursor()
        cursor.execute("begin")
        for artist in artist_list:
            _save_one(artist, cursor, artist.id)
        cursor.execute("end")
    except Exception as e:
        cursor.execute("rollback")
        raise e


def findOne(id):
    cursor = get_cursor()
    cursor.execute('SELECT id, google_id, name, load_albums_date FROM artist WHERE id = :id', {':id', id})
    result = cursor.fetchOne()
    if result is None:
        return None
    return Artist(result[0], result[1], result[2], result[3])


def find_one_by_google_id(google_id):
    cursor = get_cursor()
    cursor.execute('SELECT id, google_id, name, load_albums_date FROM artist WHERE google_id = :google_id', {'google_id': google_id})
    result = cursor.fetchone()
    if result is None:
        return None
    return Artist(result[0], result[1], result[2], result[3])


def find_all_by_google_id_list(google_id_list):
    cursor = get_cursor()
    sql = 'SELECT id, google_id, name, load_albums_date FROM artist WHERE google_id IN ({seq})'.format(
        seq = ','.join(['?']*len(google_id_list)))
    cursor.execute(sql, [x for x in google_id_list])
    reuslt = []
    for record in cursor:
        reuslt.append(Artist(record[0], record[1], record[2], record[3]))

    return reuslt


def get_artist_blacklist():
    cursor = get_cursor()
    sql = 'SELECT google_id FROM artist_blacklist'
    cursor.execute(sql)
    return [x[0] for x in cursor]


def save_related_artist(artist, related_artists):
    cursor = get_cursor()
    cursor.execute('begin')
    ord = 0
    for related_artist in related_artists:
        cursor.execute('SELECT count(*) FROM related_artists WHERE '
                       '(google_id1 = :google_id1 AND google_id2 = :google_id2) ',
                       {'google_id1': artist, 'google_id2': related_artist['artistId']})
        if cursor.fetchone()[0] > 0:
            sql = 'UPDATE related_artists SET ord = :ord WHERE ' \
                  'google_id1 = :google_id1 AND google_id2 = :google_id2'
        else:
            sql = 'INSERT INTO related_artists(google_id1, google_id2, ord) VALUES(:google_id1, :google_id2, :ord)'
        cursor.execute(sql, {'google_id1': artist, 'google_id2': related_artist['artistId'], 'ord': ord})
        ord += 1
    cursor.execute('end')


def get_related_artists():
    cursor = get_cursor()
    result = {}
    cursor.execute('SELECT google_id1, google_id2 FROM related_artists order by ord')
    for record in cursor:
        google_id1 = record[0]
        google_id2 = record[1]
        if google_id1 not in result:
            result[google_id1] = set()
        result[google_id1].add(google_id2)
    return result


def get_google_id_id_map():
    cursor = get_cursor()
    cursor.execute('SELECT id, google_id FROM artist')
    result = {}
    for record in cursor:
        result[record[1]] = record[0]
    return result


def find_all():
    cursor = get_cursor()
    sql = 'SELECT id, google_id, name, load_albums_date FROM artist'
    cursor.execute(sql)
    return [Artist(x[0], x[1], x[2], x[3]) for x in cursor]



from db.Album import Album
from db.Connection import Connection


def getCursor():
    return Connection.instance().get_cursor()


def _save_one(album, cursor, album_id):
    if album_id is None:
        cursor.execute("INSERT INTO album (google_id, name, artist_id) VALUES(:google_id, :name, :artist_id)",
                       {"google_id": album.google_id, "name": album.name, "artist_id": album.artist_id})
        album.id = cursor.lastrowid
    else:
        cursor.execute("UPDATE album SET google_id = :google_id, name = :name, artist_id = :artist_id WHERE id = :id",
                       {"id": album_id, "google_id": album.google_id, "name": album.name,
                        "artist_id": album.artist_id})


def save_many(album_list):
    albums_without_id = {}
    for album in album_list:
        if album.id is None:
            albums_without_id[album.google_id] = album
    for db_album in findAllByGoogleIdList(albums_without_id.keys()):
        albums_without_id[db_album.google_id].id = db_album.id

    try:
        cursor = getCursor()
        cursor.execute("begin")
        for album in album_list:
            _save_one(album, cursor, album.id)
        cursor.execute("end")
    except:
        cursor.execute("rollback")


def findOneByGoogleId(google_id):
    cursor = getCursor()
    cursor.execute('SELECT id, google_id, name, artist_id FROM album WHERE google_id = :google_id',
                   {'google_id', google_id})
    result = cursor.fetchOne()
    if result is None:
        return None
    return Album(result[0], result[1], result[2], result[3])


def findAllByGoogleIdList(google_id_list):
    cursor = getCursor()
    sql = 'SELECT id, google_id, name, artist_id FROM album WHERE google_id IN ({seq})'.format(
        seq=','.join(['?'] * len(google_id_list)))
    cursor.execute(sql, [x for x in google_id_list])
    reuslt = []
    for record in cursor:
        reuslt.append(Album(record[0], record[1], record[2], record[3]))

    return reuslt

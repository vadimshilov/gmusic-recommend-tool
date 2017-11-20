def update_database_if_necessary(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name",
                   {'table_name': 'db_version'})
    if cursor.fetchone() is None:
        create_init_database(cursor)


def create_init_database(cursor):
    cursor.execute("begin")

    cursor.execute("""
    CREATE TABLE artist
    (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      google_id        VARCHAR,
      name             VARCHAR,
      load_albums_date BIGINT
    );
        """)

    cursor.execute("""
create table album
(
id INTEGER primary key autoincrement,
google_id VARCHAR,
name VARCHAR,
artist_id INTEGER references artist (id) on update cascade on delete cascade
);
    """)

    cursor.execute("""
CREATE TABLE artist_blacklist
(
  google_id VARCHAR
);
    """)

    cursor.execute("""
CREATE TABLE db_version
(
  version INTEGER
);
    """)

    cursor.execute("INSERT INTO db_version(version) VALUES(1)")

    cursor.execute("""
CREATE TABLE history
(
  song_id         INT
    REFERENCES song (id)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
  event_date      INTEGER,
  playcount_delta INTEGER
);
    """)

    cursor.execute("CREATE UNIQUE INDEX history_idx ON history (song_id, event_date);")

    cursor.execute("""
CREATE TABLE related_artists
(
  google_id1 VARCHAR,
  google_id2 VARCHAR,
  ord        INT
);
    """)

    cursor.execute("""
CREATE TABLE song
(
  id              INTEGER
    PRIMARY KEY
  AUTOINCREMENT,
  name            VARCHAR,
  album_id        INTEGER
    REFERENCES album (id)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
  rate            SMALLINT,
  google_id       VARCHAR,
  playcount       INT,
  album_google_id VARCHAR,
  artist_id       INTEGER
    REFERENCES artist (id)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
  ord             INT
);
    """)

    cursor.execute("COMMIT")
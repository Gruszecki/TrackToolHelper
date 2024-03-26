import os

import sqlite3

default_db_path = os.path.join(os.environ['APPDATA'], 'djsoft.net', 'tracks.db')
DB_PATH = default_db_path if os.path.exists(default_db_path) else ''


def _get_track_id(cursor, artist, title):
    cursor.execute(f'SELECT track_id FROM taginfo WHERE artist IS "{artist}" AND title IS "{title}";')
    table = cursor.fetchone()

    return table[0] if table else -1


def _has_intro_outro(cursor, song_id) -> bool:
    cursor.execute(f'SELECT intro FROM tracks2 WHERE track_id IS {song_id};')
    intro = cursor.fetchone()

    cursor.execute(f'SELECT outro FROM tracks2 WHERE track_id IS {song_id};')
    outro = cursor.fetchone()

    return True if intro or outro else False


def _add_record(cursor, song_id, intro, outro):
    cursor.execute(f'UPDATE tracks2 SET '
                   f'intro = "{intro}", '
                   f'outro = "{outro}", '
                   f'valid = 1 '
                   f'WHERE track_id = "{song_id}"')


def is_in_db(band_name: str, song_title: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    song_id = _get_track_id(cursor, band_name, song_title)
    has_intro_outro = _has_intro_outro(cursor, song_id)

    conn.close()

    return has_intro_outro


def add_songs_info(overwrite, vocal_time_database):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for audio in vocal_time_database:
        song_id = _get_track_id(cursor, audio['band'], audio['title'])

        if song_id != -1:
            if not overwrite and _has_intro_outro(cursor, song_id):
                continue

            print(f'Adding to db: {audio['band']} - {audio['title']}')
            _add_record(cursor, song_id, audio['start'], audio['end'])

    conn.commit()
    conn.close()

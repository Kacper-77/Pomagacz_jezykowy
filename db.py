import sqlite3


# Funkcje do zarządzania bazą danych
def create_connection():
    conn = sqlite3.connect("translations.db")
    return conn


def create_tables():
    conn = create_connection()
    with conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, original_text TEXT, translated_text TEXT, src_lang TEXT, dest_lang TEXT)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS vocabulary (id INTEGER PRIMARY KEY, word TEXT, translation TEXT, lang TEXT)"
        )


def insert_translation(original_text, translated_text, src_lang, dest_lang):
    conn = create_connection()
    with conn:
        conn.execute(
            "INSERT INTO history (original_text, translated_text, src_lang, dest_lang) VALUES (?, ?, ?, ?)",
            (original_text, translated_text, src_lang, dest_lang)
        )


def insert_vocabulary(word, translation, lang):
    conn = create_connection()
    with conn:
        conn.execute(
            "INSERT INTO vocabulary (word, translation, lang) VALUES (?, ?, ?)",
            (word, translation, lang)
        )


def get_translation_history():
    conn = create_connection()
    with conn:
        history = conn.execute("SELECT id, original_text, translated_text, src_lang, dest_lang FROM history").fetchall()
    return history


def get_vocabulary():
    conn = create_connection()
    with conn:
        vocabulary = conn.execute("SELECT id, word, translation, lang FROM vocabulary").fetchall()
    return vocabulary


def delete_translation(translation_id):
    conn = create_connection()
    with conn:
        conn.execute("DELETE FROM history WHERE id = ?", (translation_id,))


def delete_vocabulary(vocabulary_id):
    conn = create_connection()
    with conn:
        conn.execute("DELETE FROM vocabulary WHERE id = ?", (vocabulary_id,))
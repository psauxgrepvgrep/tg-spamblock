import sqlite3

def init():
# Подключение к базе данных (если файла нет, он создастся автоматически)
    conn = sqlite3.connect('keywords.db')
    cursor = conn.cursor()

    # Создание таблицы keywords, если её ещё нет
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT UNIQUE NOT NULL,
        frequency INTEGER DEFAULT 1
    )
    ''')

    # Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()


def increment_keyword_frequency(keyword: str):
    conn = sqlite3.connect('keywords.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE keywords SET frequency = frequency + 1 WHERE keyword = ?', (keyword,))
    conn.commit()
    conn.close()


def is_keyword_in_db(keyword: str) -> bool:
    conn = sqlite3.connect('keywords.db')
    cursor = conn.cursor()
    cursor.execute('SELECT keyword FROM keywords WHERE keyword = ?', (keyword,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def add_keyword_to_db(keyword: str):
    conn = sqlite3.connect('keywords.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO keywords (keyword) VALUES (?)', (keyword,))
        conn.commit()
        print(f"Ключевое слово '{keyword}' успешно добавлено.")
    except sqlite3.IntegrityError:
        print(f"Ключевое слово '{keyword}' уже существует в базе данных.")
    finally:
        conn.close()


def get_all_keywords() -> list:
    conn = sqlite3.connect('keywords.db')
    cursor = conn.cursor()
    cursor.execute('SELECT keyword FROM keywords')
    keywords = [row[0] for row in cursor.fetchall()]
    conn.close()
    return keywords

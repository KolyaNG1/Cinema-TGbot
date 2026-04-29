# database.py
import sqlite3
import json
from typing import Optional, Dict, List

from config import DATABASE_PATH


class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            films TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        conn.close()

    def get_user(self, user_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            films = json.loads(user[4]) if user[4] else []
            return {
                'user_id': user[0],
                'username': user[1],
                'first_name': user[2],
                'last_name': user[3],
                'films': films,
                'created_at': user[5],
                'last_active': user[6]
            }
        return None

    def save_user(self, user_data: Dict) -> None:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        user_exists = self.get_user(user_data['user_id'])

        if user_exists:
            cursor.execute('''
            UPDATE users 
            SET last_active = CURRENT_TIMESTAMP 
            WHERE user_id = ?
            ''', (user_data['user_id'],))
        else:
            cursor.execute('''
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
            ''', (user_data['user_id'], user_data['username'],
                  user_data['first_name'], user_data['last_name']))

        conn.commit()
        conn.close()

    def update_user_numbers(self, user_id: int, numbers: List[float]) -> None:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        numbers_json = json.dumps(numbers)
        cursor.execute('''
        UPDATE users 
        SET films = ?, last_active = CURRENT_TIMESTAMP
        WHERE user_id = ?
        ''', (numbers_json, user_id))

        conn.commit()
        conn.close()

    def get_stats(self) -> Dict:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM users WHERE films != "[]"')
        active_users = cursor.fetchone()[0]

        conn.close()

        return {
            'total_users': total_users,
            'active_users': active_users
        }

db = Database(DATABASE_PATH)

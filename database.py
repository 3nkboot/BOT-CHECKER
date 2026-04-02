# database.py
import sqlite3
import json
from datetime import datetime
from config import DB_FILE

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        # جدول المستخدمين
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                name TEXT,
                subscription_end INTEGER DEFAULT 0,
                points REAL DEFAULT 0,
                total_checks INTEGER DEFAULT 0,
                live_found INTEGER DEFAULT 0,
                joined_date INTEGER
            )
        ''')
        
        # جدول الملفات المؤقتة
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS temp_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                file_name TEXT,
                file_path TEXT,
                cards_count INTEGER,
                live_count INTEGER,
                declined_count INTEGER,
                unknown_count INTEGER,
                uploaded_date INTEGER,
                results TEXT
            )
        ''')
        
        # جدول البطاقات الحية (للتخزين المؤقت)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS live_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                card_number TEXT,
                month TEXT,
                year TEXT,
                cvv TEXT,
                bank TEXT,
                card_type TEXT,
                country TEXT,
                full_details TEXT,
                found_date INTEGER
            )
        ''')
        
        # جدول البروكسيات
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS proxies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proxy TEXT UNIQUE,
                is_alive INTEGER DEFAULT 1,
                response_time REAL,
                last_checked INTEGER,
                success_count INTEGER DEFAULT 0,
                fail_count INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
    
    # دوال المستخدمين
    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()
    
    def add_user(self, user_id, username, name):
        self.cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, name, joined_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, name, int(datetime.now().timestamp())))
        self.conn.commit()
    
    def update_points(self, user_id, points):
        self.cursor.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points, user_id))
        self.conn.commit()
    
    def set_subscription(self, user_id, days):
        end_time = int(datetime.now().timestamp()) + (days * 86400)
        self.cursor.execute("UPDATE users SET subscription_end = ? WHERE user_id = ?", (end_time, user_id))
        self.conn.commit()
    
    def check_subscription(self, user_id):
        self.cursor.execute("SELECT subscription_end FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        if result and result[0] > int(datetime.now().timestamp()):
            return True
        return False
    
    # دوال الملفات المؤقتة
    def save_file_record(self, user_id, file_name, file_path, cards_count, results):
        self.cursor.execute('''
            INSERT INTO temp_files (user_id, file_name, file_path, cards_count, uploaded_date, results)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, file_name, file_path, cards_count, int(datetime.now().timestamp()), json.dumps(results)))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_file_results(self, file_id, live_count, declined_count, unknown_count):
        self.cursor.execute('''
            UPDATE temp_files 
            SET live_count = ?, declined_count = ?, unknown_count = ?
            WHERE id = ?
        ''', (live_count, declined_count, unknown_count, file_id))
        self.conn.commit()
    
    def get_user_files(self, user_id, limit=10):
        self.cursor.execute('''
            SELECT * FROM temp_files 
            WHERE user_id = ? 
            ORDER BY uploaded_date DESC 
            LIMIT ?
        ''', (user_id, limit))
        return self.cursor.fetchall()
    
    # دوال البطاقات الحية
    def save_live_card(self, user_id, card_data, full_details):
        self.cursor.execute('''
            INSERT INTO live_cards (user_id, card_number, month, year, cvv, bank, card_type, country, full_details, found_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            card_data.get("number", ""),
            card_data.get("month", ""),
            card_data.get("year", ""),
            card_data.get("cvv", ""),
            card_data.get("bank", ""),
            card_data.get("type", ""),
            card_data.get("country", ""),
            json.dumps(full_details),
            int(datetime.now().timestamp())
        ))
        self.conn.commit()
        
        # تحديث إحصائيات المستخدم
        self.cursor.execute("UPDATE users SET live_found = live_found + 1, total_checks = total_checks + 1 WHERE user_id = ?", (user_id,))
        self.conn.commit()
    
    def get_user_live_cards(self, user_id, limit=50):
        self.cursor.execute('''
            SELECT * FROM live_cards 
            WHERE user_id = ? 
            ORDER BY found_date DESC 
            LIMIT ?
        ''', (user_id, limit))
        return self.cursor.fetchall()
    
    # دوال البروكسيات
    def save_proxy(self, proxy, is_alive, response_time):
        self.cursor.execute('''
            INSERT OR REPLACE INTO proxies (proxy, is_alive, response_time, last_checked)
            VALUES (?, ?, ?, ?)
        ''', (proxy, 1 if is_alive else 0, response_time, int(datetime.now().timestamp())))
        self.conn.commit()
    
    def get_alive_proxies(self, limit=20):
        self.cursor.execute('''
            SELECT proxy FROM proxies 
            WHERE is_alive = 1 
            ORDER BY response_time ASC 
            LIMIT ?
        ''', (limit,))
        return [row[0] for row in self.cursor.fetchall()]
    
    def close(self):
        self.conn.close()

# إنشاء نسخة واحدة
db = Database()

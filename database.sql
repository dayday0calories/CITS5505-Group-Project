CREATE TABLE login_history (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    login_time TEXT DEFAULT CURRENT_TIMESTAMP,
    logout_time TEXT
);
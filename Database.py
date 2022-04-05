import sqlite3
conn=sqlite3.connect("project.db")
cur=conn.cursor()


Q1="""CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    username TEXT NOT NULL UNIQUE,
    password TEXT,
    score INTEGER DEFAULT 0,
    date_created
)"""
cur.execute(Q1) 

Q2=""" CREATE TABLE cards (
    card_id INTEGER PRIMARY KEY AUTOINCREMENT,
    deckname TEXT NOT NULL,
    created_on DATETIME,
    front TEXT,
    back TEXT,
    last_rev DATETIME,
    username TEXT,
    FOREIGN KEY (username) REFERENCES users(username) 
)"""
cur.execute(Q2)

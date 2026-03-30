import sqlite3

try:
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    # Create userinfo table
    cursor.execute('''
     CREATE TABLE IF NOT EXISTS userinfo (
         userId INTEGER PRIMARY KEY AUTOINCREMENT,
         username TEXT NOT NULL UNIQUE,
         password TEXT NOT NULL
     )
     ''')
    
    #Create userstats table
    cursor.execute('''
     CREATE TABLE IF NOT EXISTS userstats (
         userId INTEGER NOT NULL,
         gamesPlayed INTEGER DEFAULT 0,
         gamesWon INTEGER DEFAULT 0,
         gamesLoss INTEGER DEFAULT 0,
         WinRatio DECIMAL(5, 2) GENERATED ALWAYS AS (CASE WHEN gamesPlayed = 0 THEN 0 ELSE CAST(gamesWon AS FLOAT) / gamesPlayed END) STORED,
         rank INTEGER DEFAULT 0,
         FOREIGN KEY (userId) REFERENCES userinfo(userId)
     )
     ''')
    
     # Create gamesaves table
    cursor.execute('''
     CREATE TABLE IF NOT EXISTS gamesaves (
         saveId INTEGER PRIMARY KEY AUTOINCREMENT,
         userId INTEGER NOT NULL,
         gameResult TEXT NOT NULL,
         gameDuration INTEGER NOT NULL,
         movesCount INTEGER NOT NULL,
         FOREIGN KEY (userId) REFERENCES userinfo(userId)
     )
     ''')

   
    # Commit the changes
    conn.commit()
    print("Tables created successfully.")
    
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
    
finally:
    # Close the connection
    if conn:
        conn.close()





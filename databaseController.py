from datetime import datetime
import sqlite3 as sqlite
from datetime import datetime

def booksFromList(books):
    output = {}
    for i in range(len(books)):
        output[books[i][1]] = {"id": books[i][0], "author": books[i][2], "rating": books[i][3], "release": books[i][4], "image": books[i][5], "page": books[i][6], "status": getStatus(books[i][0])}

    return output

def libraryBooksFromList(books):
    output = {}
    for book in books:
        print(book[7])
        print(book[7].split("|||"))
        output[book[1]] = {"id": book[0], "author": book[2], "rating": book[3], "pages": book[4], "release": book[5], "image": book[6], "tags": book[7].split("|||") if book[7] else book[7], "location": book[8], "description": book[9], "quotes": book[10].split("|||") if book[10] else book[10], "size": book[11], "date": book[12], "status": getStatus(book[0])}

    return output

def createDatabase():
    connection = sqlite.connect("data.db")
    connection.execute("CREATE TABLE IF NOT EXISTS popularEbooks(id integer PRIMARY KEY, name TEXT NOT NULL, author TEXT NOT NULL, rating TEXT NOT NULL, release TEXT NOT NULL, image TEXT NOT NULL, page TEXT NOT NULL, date TIMESTAMP)")
    connection.execute("CREATE TABLE IF NOT EXISTS library(id integer PRIMARY KEY, name TEXT NOT NULL, author TEXT NOT NULL, rating TEXT NOT NULL, pages TEXT NOT NULL, release TEXT NOT NULL, image TEXT NOT NULL, tags TEXT NOT NULL, location TEXT NOT NULL, description TEXT NOT NULL, quotes TEXT NOT NULL, size TEXT NOT NULL, date TIMESTAMP)")
    connection.execute("CREATE TABLE IF NOT EXISTS wanted(id integer PRIMARY KEY, name TEXT NOT NULL, author TEXT NOT NULL, rating TEXT NOT NULL, release TEXT NOT NULL, image TEXT NOT NULL, page TEXT NOT NULL)")
    connection.execute("CREATE TABLE IF NOT EXISTS statusTable(id integer PRIMARY KEY, status TEXT NOT NULL)")
    connection.commit()
    connection.close()


def getPopularEbooks():
    connection = sqlite.connect("data.db")
    connection.execute("DELETE FROM popularEbooks WHERE date <= date('now', '-1 day')")
    connection.commit()
    results = connection.execute("SELECT * FROM popularEbooks").fetchall()
    connection.close()

    if len(results) == 0:
        return False
    
    else:
        return booksFromList(results)

def getWantedEbooks():
    connection = sqlite.connect("data.db")
    results = connection.execute("SELECT * FROM wanted").fetchall()
    return booksFromList(results)

def getLibraryBooks():
    connection = sqlite.connect("data.db")
    results = connection.execute("SELECT * FROM library").fetchall()
    return libraryBooksFromList(results)

def getLatestLibraryBooks():
    connection = sqlite.connect("data.db")
    results = connection.execute("SELECT * FROM library WHERE date >= date('now', '-3 days') ").fetchall()
    return libraryBooksFromList(results)

def getBookFromLibrary(book_id):
    connection = sqlite.connect("data.db")
    book = connection.execute("SELECT * FROM library WHERE id = ?", (book_id, )).fetchone()
    return {"id": book[0], "title": book[1], "author": book[2], "rating": book[3], "pages": book[4], "release": book[5], "image": book[6], "tags": book[7].split("|||") if book[7] else book[7], "location": book[8], "description": book[9], "quotes": book[10].split("|||") if book[10] else book[10], "size": book[11], "date": book[12], "status": getStatus(book[0])}



def insertIntoPopularEbooks(books:list):
    connection = sqlite.connect("data.db")
    for book in books:
        connection.execute("INSERT INTO popularEbooks VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (book['id'], book['title'], book['author'], book['rating'], book['release'], book['image'], datetime.now(), book['page']))
    connection.commit()
    connection.close()

def insertIntoWanted(book):
    connection = sqlite.connect("data.db")
    connection.execute("INSERT INTO wanted VALUES(?, ?, ?, ?, ?, ?, ?)", (book['id'], book['title'], book['author'], book['rating'], book['release'], book['image'], book['page']))
    connection.commit()
    connection.close()

#id integer , name , author , rating, pages , release , image, tags, location , description L, quotes, TIME
def insertIntoLibrary(book):
    connection = sqlite.connect("data.db")
    connection.execute("INSERT INTO library VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (book["id"], book["title"], book["author"], book["rating"], book["pages"], book["release"], book["image"], "|||".join(book["tags"]), book["location"], book["description"], "|||".join(book["quotes"]), book["size"], datetime.now()))
    connection.commit()
    connection.close()


def removeFromWanted(book_id):
    connection = sqlite.connect("data.db")
    connection.execute(f"DELETE FROM wanted WHERE id = {book_id}")
    connection.commit()
    connection.close()



def checkIfInLibrary(book_id):
    connection = sqlite.connect("data.db")
    result = connection.execute(f"SELECT * FROM library WHERE id = {book_id}").fetchall()
    return True if len(result) > 0 else False

def checkIfInWanted(book_id):
    connection = sqlite.connect("data.db")
    result = connection.execute(f"SELECT * FROM wanted WHERE id = {book_id}").fetchall()
    connection.close()
    return True if len(result) > 0 else False



def getBookInfoFromWanted(book_id):
    connection = sqlite.connect("data.db")
    book_raw = connection.execute(f"SELECT * FROM wanted WHERE id = {book_id}").fetchall()[0]
    return {"id": book_raw[0], "title": book_raw[1], "authors": book_raw[2], "rating": book_raw[3], "release": book_raw[5], "image": book_raw[6], "page": book_raw[7]}



def getStatus(book_id):
    connection = sqlite.connect("data.db")
    try:
        status = connection.execute(f"SELECT status FROM statusTable WHERE id = {book_id}").fetchone()[0]

    except:
        status = ""

    return status


def updateStatus(book_id, status):
    connection = sqlite.connect("data.db")
    
    if getStatus(book_id):
        connection.execute("UPDATE statusTable SET status = ? WHERE id = ?", (status, book_id))
        connection.commit()
    else:
        connection.execute("INSERT INTO statusTable VALUES(?, ?)", (book_id, status))
        connection.commit()
    connection.close()
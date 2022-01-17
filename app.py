import flask
import databaseController
import goodReadsScraper
import libgenDownloader
import threading

app = flask.Flask(__name__, static_folder = './build', static_url_path = '/')

@app.route("/", methods = ["GET"])
def index():
    return app.send_static_file("index.html")


@app.route("/getPopular", methods = ["GET"])
def getPopular():
    #books = databaseController.getPopularEbooks()
    books = False

    if books == False or books == []:
        books = goodReadsScraper.getPopularWeekEbooks()
        #databaseController.insertIntoPopularEbooks(books)

    return goodReadsScraper.booksToDict(books)

@app.route("/getWanted", methods = ["GET"])
def getWanted():
    return databaseController.getWantedEbooks()

@app.route("/getLibraryLatest", methods = ["GET"])
def getLibraryLatest():
    books = databaseController.getLatestLibraryBooks()
    if books:
        return books
    
    else:
        return flask.Response({"success": True}, status=204)

@app.route("/getLibrary", methods = ["GET"])
def getLibrary():
    books = databaseController.getLibraryBooks()
    if books:
        return books
    
    else:
        return flask.Response({"success": True}, status=204)

@app.route("/search", methods = ["POST"])
def search():
    print(flask.request.json["query"])
    return goodReadsScraper.searchBooks(flask.request.json["query"])

@app.route("/book/<int:book_id>", methods = ["GET", "POST"])
def getBook(book_id):
    if flask.request.method == "GET":
        return app.send_static_file('index.html')

    else:
        if databaseController.checkIfInLibrary(book_id):
            return databaseController.getBookFromLibrary(book_id)

        else:
            return goodReadsScraper.getBookInfo(book_id)

@app.route("/request", methods = ["POST"])
def request():
    book = goodReadsScraper.getBookInfo(flask.request.json['book_id'])
    databaseController.insertIntoWanted(book)
    try:
        link = libgenDownloader.getBookDownloadLink(book)
        databaseController.updateStatus(book["id"], "Downloading")
        threading.Thread(target=libgenDownloader.downloadBookFromLink, args=(link, book)).start()
    except:
        databaseController.updateStatus(book["id"], "Missing")
    
    return {"success": True}

@app.route("/getBookStatus", methods = ["POST"])
def getBookStatus():
    return {"book_status": databaseController.getStatus(flask.request.json["book_id"])}

databaseController.createDatabase()

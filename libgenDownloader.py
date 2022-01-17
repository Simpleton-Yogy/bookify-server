import requests
import bs4
import databaseController
import re
import os

def getBookDownloadLink(book):
    book_name = book["title"].lstrip()
    try:
        soup_results = bs4.BeautifulSoup(requests.get(f"https://libgen.is/search.php?req={book_name} - {book['author']}").text, features="html.parser")
        soup_download = bs4.BeautifulSoup(requests.get(f"{soup_results.find('a', {'title': 'this mirror'})['href']}").text, features="html.parser")
        return soup_download.find(lambda tag:tag.name=="a" and "Cloudflare" in tag.text)['href']
    except:
        soup_results = bs4.BeautifulSoup(requests.get(f"https://libgen.is/fiction/?q={book_name} - {book['author']}").text, features="html.parser")
        soup_download = bs4.BeautifulSoup(requests.get(f"{soup_results.find('a', {'title': 'Libgen.rs'})['href']}").text, features="html.parser")
        return soup_download.find(lambda tag:tag.name=="a" and "Cloudflare" in tag.text)['href']

def downloadBookFromLink(link, book):
    book_author = re.sub(r"([^\w])", "", book["author"])

    if not os.path.isdir(f"./{book_author}"):
        os.makedirs(f"./{book_author}")
    
    file_raw = requests.get(link)
    location = f"./{book_author}/{book['id']}{link[link.find('.', len(link) - 5):]}"

    with open(location, "wb") as file:
        file.write(file_raw.content)
        file.close()

    book["location"] = f"./{book_author}/{book['id']}"
    book["size"] = os.path.getsize(location)
    databaseController.updateStatus(book['id'], "Available")
    databaseController.removeFromWanted(book['id'])
    databaseController.insertIntoLibrary(book)

    

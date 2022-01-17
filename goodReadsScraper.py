import requests
import re
import bs4
import databaseController

# TODO: rewrite to bs4
def getPopularWeekEbooks():
    contents = requests.get("https://www.goodreads.com/shelf/show/most-read-this-week").text
    regexID = re.compile(r"/book/show/(\d*)-")
    regexTitle = re.compile(r"<a class=\"bookTitle\" href=\"/book/show/.*>(.*)</a>", re.MULTILINE)
    regexPage = re.compile(r"<a title=.*href=\"(.*)\">", re.MULTILINE)
    regexRating = re.compile(r"avg rating (.*) —", flags=re.MULTILINE)
    regexRelease = re.compile(r"published (.*).*?", flags=re.MULTILINE)
    regexImage = re.compile(r"<img alt=\".*\" src=\"(.*)\" /></a>", flags=re.MULTILINE)
    regexAuthors = re.compile(r"<a class=\"authorName\" itemprop=\"url\".*?<span itemprop=\"name\">(.*?)</span></a>")
    titlesRaw = regexTitle.findall(contents)
    pages = regexPage.findall(contents)
    ratings = regexRating.findall(contents)
    releases = regexRelease.findall(contents)
    images = regexImage.findall(contents)
    authors = regexAuthors.findall(contents)
    books = []
    book = {}

    print(f"{len(titlesRaw)} | {len(pages)} | {len(ratings)} | {len(releases)} | {len(images)} | {len(authors)}")

    for i in range(len(titlesRaw)):
        image = re.sub(r"(._S.\d\d_)", "", images[i])
        status = databaseController.getStatus(regexID.findall(pages[i].replace(".", "-"))[0])

        if "(" in titlesRaw[i]:
            book = {'id': regexID.findall(pages[i].replace(".", "-"))[0], 'title': re.sub(r"[(].*[)]", "", titlesRaw[i]), 'page': f"https://www.goodreads.com{pages[i]}", 'rating': ratings[i], 'release': re.sub(r"[\n\t\s]*", "", releases[i]), 'image': image, 'author': authors[i], 'status': status}

        else:
            book = {'id': regexID.findall(pages[i].replace(".", "-"))[0], 'title': titlesRaw[i], 'page': f"https://www.goodreads.com{pages[i]}", 'rating': ratings[i], 'release': re.sub(r"[\n\t\s]*", "", releases[i]), 'image': image, 'author': authors[i], 'status': status}

        books.append(book)

    return books

def booksToDict(books:list):
    output = {}
    
    for book in books:
        output[book['title']] = {'author': book['author'], 'release': book['release'], 'rating': book['rating'], 'page': book['page'], 'image': book['image'], 'id': book['id'], 'status': book['status']}


    return output

def searchBooks(query):
    soup = bs4.BeautifulSoup(requests.get(f"https://www.goodreads.com/search?q={query}").text, features="html.parser")

    bookTable = soup.findAll('table', {'class': 'tableList'})[0]
    regexRelease = re.compile(r"—.*?published.*(\d\d\d\d).*—", flags=re.DOTALL)
    books = {}

    for book in bookTable.findAll('tr', {'itemtype': 'http://schema.org/Book'}):
        books[book.find('span', {'itemprop': 'name', 'role': 'heading'}).text] = {
            'author': ", ".join([author.text for author in book.findAll('a', {'class': 'authorName'})]),
            'rating': re.sub(r" avg rating — .*", "", book.find('span', {'class': 'minirating'}).text),
            'release': regexRelease.findall(book.find('span', {'class': 'greyText smallText uitext'}).text)[0] if len(regexRelease.findall(book.find('span', {'class': 'greyText smallText uitext'}).text)) > 0 else "Undefined",
            'image': re.sub(r"(._S.\d\d_)", "", book.find('img', {'class': 'bookCover'})['src']),
            'id': re.findall(r"/book/show/(\d*)", book.find('a', {'class': 'bookTitle'})['href'])[0],
            'status': databaseController.getStatus(re.findall(r"/book/show/(\d*)", book.find('a', {'class': 'bookTitle'})['href'])[0])
        }

    return books

# TODO: rewrite to bs4
def getBookInfo(book_id):
    print("GETTING BOOK INFO")
    contents = requests.get(f"https://www.goodreads.com/book/show/{book_id}").text
    #contents = request.urlopen(f"https://www.goodreads.com/book/show/{book_id}").read()
    print("GOT GOODREADS PAGE")
    regexTitle = re.compile(r"<h1 id=\"bookTitle\" class=\"gr-h1 gr-h1--serif\" itemprop=\"name\">.(.*)</h1>.<h2 id=\"bookSeries\">", flags=re.MULTILINE | re.DOTALL)
    regexAuthors = re.compile(r"<a class=\"authorName\" itemprop=\"url\" href=\".*\"><span itemprop=\"name\">(.*)</span></a>")
    regexPages = re.compile(r"<span itemprop=\"numberOfPages\">(.*) pages</span></div>")
    regexRelease = re.compile(r"Published.*(\d\d\d\d).*by")
    regexRating = re.compile(r"<span itemprop=\"ratingValue\">.*(\d[.]\d\d).</span>.<span class=\"greyText\">", flags=re.MULTILINE | re.DOTALL)
    regexDescription = re.compile(r"<span id=\"freeText\d*\" style=\"display:none\">(.*)</span>")
    regexImage = re.compile(r"<img id=\"coverImage\" alt=\".*?\" src=\"(.*)\" /></a>")
    regexTags = re.compile(r"<a class=\"actionLinkLite bookPageGenreLink\" href=\"/genres/.*\">(.*)</a>")   
    regexQuotes = re.compile(r"<span class=\"readable\">&ldquo;(.*)&rdquo;</span>")
    print("COMPILED REGEXES")

    print(book_id)

    pages = regexPages.findall(contents)
    print(list(set(regexTags.findall(contents)))[0:4] if len(list(set(regexTags.findall(contents)))) > 4 else list(set(regexTags.findall(contents))))

    return {"title": regexTitle.findall(contents)[0], 
            "author": ", ".join(regexAuthors.findall(contents)),
            "pages": 0 if pages == [] else pages[0],
            "release": regexRelease.findall(contents)[1] if len(regexRelease.findall(contents)) > 0 else "",
            "rating": regexRating.findall(contents)[0],
            "description": re.sub(r"(<.*?>)", "", regexDescription.findall(contents)[0]),
            "image": regexImage.findall(contents)[0],
            "tags": list(set(regexTags.findall(contents)))[0:4] if len(list(set(regexTags.findall(contents)))) > 4 else list(set(regexTags.findall(contents))),
            "quotes": regexQuotes.findall(contents),
            "id": book_id,
            "page": f"https://www.goodreads.com/book/show/{book_id}",
            "status": databaseController.getStatus(book_id)
             }
import threading
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

class URLHandler(threading.Thread):

    def __init__(self, url, urlqueue, emailqueue):
        threading.Thread.__init__(self)
        self.url = url
        self.urlqueue = urlqueue
        self.emailqueue = emailqueue

    def isEmail(self, link):
        pl = urllib.parse.urlparse(link)
        return pl.scheme == 'mailto'

    def run(self):
        print("Handling URL {} ...".format(self.url))
        with urllib.request.urlopen(self.url) as response:
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            for link in soup.find_all('a'):
                href = link.get('href')
                if self.isEmail(href):
                    print("email found ==  {}".format(href))
                #print(href)

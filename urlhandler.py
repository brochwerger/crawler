import threading
import urllib.request
import urllib.parse
import queue
from bs4 import BeautifulSoup

class URLHandler(threading.Thread):

    def __init__(self, urlqueue, emailqueue, maxdepth=-1):
        threading.Thread.__init__(self)
        self.urlqueue = urlqueue
        self.emailqueue = emailqueue
        self.maxdepth = maxdepth
        self.processed_urls = {}

    # def isEmail(self, link):
    #     pl = urllib.parse.urlparse(link)
    #     return pl.scheme == 'mailto'

    def run(self):

        depth = -1
        while not self.urlqueue.empty() and (depth < self.maxdepth if self.maxdepth > 0 else True):

            url, depth = self.urlqueue.get()

            if not url in self.processed_urls.keys():

                self.processed_urls[url] = True

                print("Processing {} at depth {}".format(url, depth))

                with urllib.request.urlopen(url) as response:
                    html = response.read()
                    soup = BeautifulSoup(html, 'html.parser')
                    for link in soup.find_all('a'):
                        href = link.get('href')
                        parsedurl = urllib.parse.urlparse(href)
                        if parsedurl.scheme == "mailto":
                            print("email found ==  {}".format(href))
                        else:
                            if parsedurl.scheme == "":
                                href = url + href
                            self.urlqueue.put([href, depth+1])

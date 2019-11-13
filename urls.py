import urllib
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

class AbstractUrl(ABC):

    def __init__(self, url, queue=None):
        self.url = url
        self.queue = queue
        super().__init__()

    @abstractmethod
    def process(self, depth):
        pass

    @abstractmethod
    def up2date(self):
        pass

    def enqueue(self, x):
        if self.queue:
            self.queue.put(x)

class EmailUrl(AbstractUrl):

    def _init__(self, url, queue=None):
        super()

    processed = {}

    def process(self, depth):
        print("Email:{}".format(self.url))
        self.enqueue(self.url)

        EmailUrl.processed[self.url] = self.url

    def up2date(self):
        return self.url in EmailUrl.processed.keys()

class WebPageUrl(AbstractUrl):

    processed = {}

    # def _init__(self, url, queue):
    #     GenericUrl(url, queue)

    def process(self, depth):
        print("Web Page: {}".format(self.url))
        try:
            with urllib.request.urlopen(self.url) as response:
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
                for link in soup.find_all('a'):
                    href = link.get('href')
                    self.enqueue([self.url, href, depth+1])

        except:
            print("ERROR processing: {}".format(self.url))

        WebPageUrl.processed[self.url] = self.url

    def up2date(self):
        return self.url in WebPageUrl.processed.keys()





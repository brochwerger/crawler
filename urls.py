import logging
import threading
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
import time

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

    processed = {}

    def process(self, depth):
        logging.debug("Email found : {}".format(self.url))
        self.enqueue(self.url)

        EmailUrl.processed[self.url] = self.url

    def up2date(self):
        return self.url in EmailUrl.processed.keys()

class WebPageUrl(AbstractUrl):

    processed = {}

    def __init__(self, url, queue=None):
        AbstractUrl.__init__(self, url, queue)
        # self.cleaner = self.Cleaner()
        # self.cleaner.start()

    # class Cleaner(threading.Thread):
    #
    #     def __init__(self):
    #         threading.Thread.__init__(self)
    #         self.keepongoing = True
    #
    #     def run(self):
    #         while (self.keepongoing):
    #             logging.debug("KV size currently is {}".format(len(WebPageUrl.processed)))
    #             time.sleep(10)

    def process(self, depth):
        logging.debug("Processing web page: {}".format(self.url))
        try:
            with urllib.request.urlopen(self.url) as response:
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
                for link in soup.find_all('a'):
                    href = link.get('href')
                    self.enqueue([self.url, href, depth+1])

        except urllib.error.URLError:
            logging.error("Unable to fetch [{}]".format(self.url))

        except:
            logging.error("Unable to parse [{}]".format(self.url))

        WebPageUrl.processed[self.url] = self.url

    def up2date(self):
        return self.url in WebPageUrl.processed.keys()

import logging
import urllib.request
import urllib.error
import redis

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

class AbstractUrl(ABC):

    kvs = None

    def __init__(self, url, queue=None, redissrv=None, aging=-1):
        super().__init__()
        self.url = url
        self.queue = queue
        self.redis_server = redissrv
        self.aging_in_minutes = aging

        if AbstractUrl.kvs == None:
            if self.redis_server:
                AbstractUrl.kvs = redis.Redis(host=self.redis_server, port=6379, db=0)
                AbstractUrl.kvs.flushdb()
            else:
                AbstractUrl.kvs = {}

    def is_up2date(self):
        if type(AbstractUrl.kvs) is redis.Redis:
            v = self.kvs.get(self.url)
            return  v != None
        else:
            return self.url in self.kvs.keys()

    def enqueue(self, x):
        if self.queue:
            self.queue.put(x)

    def save(self, timeout=None):
        if type(AbstractUrl.kvs) is redis.Redis:
            AbstractUrl.kvs.set(self.url, self.url, ex=(timeout*60) if timeout else None) # NOTE: EX in seconds, timeout in minutes
        else:
            AbstractUrl.kvs[self.url] = self.url

    @abstractmethod
    def process(self, depth):
        pass

class EmailUrl(AbstractUrl):

    def process(self, depth):
        logging.debug("Email found : {}".format(self.url))
        self.enqueue(self.url)
        self.save()

class WebPageUrl(AbstractUrl):

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

        self.save(timeout=self.aging_in_minutes)

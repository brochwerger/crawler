import logging
import urllib.request
import urllib.error
import hashlib

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

from keyvaluestore import RedisKVS, BasicKVS

class AbstractUrl(ABC):

    kvs = None

    def __init__(self, url, queue=None, redissrv=None):
        super().__init__()
        self.url = url
        self.queue = queue
        self.redis_server = redissrv

        if AbstractUrl.kvs == None:
            AbstractUrl.kvs = RedisKVS(redissrv) if self.redis_server else BasicKVS()

    def is_up2date(self):
        return AbstractUrl.kvs.get(self.url) != None

    def enqueue(self, x):
        if self.queue:
            self.queue.put(x)

    @abstractmethod
    def process(self, depth):
        pass

class EmailUrl(AbstractUrl):

    def save(self):
        AbstractUrl.kvs.put(self.url, self.url)

    def process(self, depth):
        logging.debug("Email found : {}".format(self.url))
        self.enqueue(self.url)
        self.save()

class WebPageUrl(AbstractUrl):

    def __init__(self, url, queue=None, redissrv=None, aging=None):
        super().__init__(url, queue, redissrv)
        #self.md5 = hashlib.sha256()
        self.md5 = hashlib.blake2b()
        self.aging=aging

    # def is_up2date(self):
    #     return False

    def save(self):
        AbstractUrl.kvs.put(self.url, self.md5.digest(), aging=self.aging)

    def process(self, depth):

        logging.debug("Processing web page: {}".format(self.url))
        try:

            with urllib.request.urlopen(self.url) as response:
                html = response.read()
                self.md5.update(html)
                # digest = self.md5.digest()
                # if digest != AbstractUrl.kvs.get(self.url):
                try:
                    soup = BeautifulSoup(html, 'html.parser')
                    for link in soup.find_all('a'):
                        href = link.get('href')
                        self.enqueue([self.url, href, depth+1])
                except:
                    logging.error("Unable to parse [{}]".format(self.url))

                # else:
                #     logging.debug("Unchanged web page [{}] - aborting".format(self.url))

        except urllib.error.URLError:
            logging.error("Unable to fetch [{}]".format(self.url))

        self.save()
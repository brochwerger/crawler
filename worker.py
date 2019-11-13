import threading
import urllib

from urls import EmailUrl, WebPageUrl

class Worker(threading.Thread):

    def __init__(self, urlqueue, emailqueue, maxdepth=-1):
        threading.Thread.__init__(self)
        self.urlqueue = urlqueue
        self.emailqueue = emailqueue
        self.maxdepth = maxdepth

    def categorize(self, prevUrl, url):

        parsedUrl = urllib.parse.urlparse(url)
        if parsedUrl.scheme == "mailto":
            return EmailUrl(url, self.emailqueue)
        elif parsedUrl.scheme in ["http", "https"]:
            return WebPageUrl(url, self.urlqueue)
        elif prevUrl and parsedUrl.scheme == '' and parsedUrl.path != '':
            parsedPrevUrl = urllib.parse.urlparse(prevUrl)
            url = '{}://{}{}'.format(parsedPrevUrl.scheme, parsedPrevUrl.netloc, parsedUrl.path)
            return WebPageUrl(url, self.urlqueue)
        else:
            if prevUrl:
                parsedPrevUrl = urllib.parse.urlparse(prevUrl)
            print(parsedPrevUrl)
            print(parsedUrl)
            return None

    def run(self):

        depth = -1
        while not self.urlqueue.empty() and (depth < self.maxdepth if self.maxdepth > 0 else True):

            purl, url, depth = self.urlqueue.get()

            curl = self.categorize(purl, url)

            if curl and not curl.up2date():
                curl.process(depth)

import threading
import urllib.request
import urllib.parse
import logging
import os.path

from urls import EmailUrl, WebPageUrl, AbstractUrl


# IGNORE_EXTENSIONS = ['.jpg', '.png', '.mp4']

class Worker(threading.Thread):

    def __init__(self, id, urlqueue, emailqueue, maxdepth=-1, max_depth_reached=None, redis=None, aging=-1):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.id = id
        self.name = 'W#{:05d}'.format(self.id)
        self.urlqueue = urlqueue
        self.emailqueue = emailqueue
        self.maxdepth = maxdepth
        self.max_depth_reached = max_depth_reached
        self.redis = redis
        self.aging = aging

    def classify(self, prevUrl: str, url: str) -> AbstractUrl:

        parsedUrl = urllib.parse.urlparse(url)

        # Is URL an email ?
        if parsedUrl.scheme == "mailto":
            return EmailUrl(url, self.emailqueue)

        # Save time by not fetching files with the extension in the IGNORE_EXTENSIONS list
        # try :
        #     path = parsedUrl.path.decode()
        #     if path != '':
        #         x = os.path.basename(path).split('.')
        #         if len(x) == 2 and x[1] in IGNORE_EXTENSIONS:
        #             logging.debug("Skipping [{}]".format(url))
        #             return None
        # except:
        #     logging.debug("Something is broken with parsed data: {}".format(parsedUrl))

        # Is URL scheme https or http - probably it is a properly build URL
        if parsedUrl.scheme in ["http", "https"]:
            return WebPageUrl(url, self.urlqueue, self.redis, self.aging)

        # If scheme is empty, it may be a link to a page local to previous resource, hence we try to build a full URL
        # combinaning data from previous (if available) URL and current URL
        elif prevUrl and parsedUrl.scheme == '' and parsedUrl.path != '':
            parsedPrevUrl = urllib.parse.urlparse(prevUrl)
            # url = '{}://{}{}'.format(parsedPrevUrl.scheme, parsedPrevUrl.netloc, parsedUrl.path)
            if parsedUrl.path[0] == '/':
                url = '{}://{}{}'.format(parsedPrevUrl.scheme, parsedPrevUrl.netloc, parsedUrl.path)
            else:
                url = '{}://{}/{}'.format(parsedPrevUrl.scheme, parsedPrevUrl.netloc, parsedUrl.path)
            return WebPageUrl(url, self.urlqueue, self.redis, self.aging)

        # If none of the above, then print out both previous and current parsed URLs to help improve the code
        else:
            logging.debug("Unable to categorize:")
            if prevUrl:
                parsedPrevUrl = urllib.parse.urlparse(prevUrl)
                logging.debug(parsedPrevUrl)
            logging.debug(parsedUrl)
            return None

    def run(self):

        depth = -1
        # while not self.urlqueue.empty() and (depth < self.maxdepth if self.maxdepth > 0 else True):
        while depth < self.maxdepth if self.maxdepth > 0 else True:

            prevurl, url, depth = self.urlqueue.get()

            logging.debug('{} working on [{}]'.format(self.name, url))

            caturl = self.classify(prevurl, url)

            if caturl and not caturl.is_up2date():
                caturl.process(depth)

        logging.debug("{} finished ...".format(self.name))

        if self.max_depth_reached:
            self.max_depth_reached.set()


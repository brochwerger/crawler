import argparse
import queue

from urlhandler import URLHandler

usage = "USAGE: Required parameter: -f <filename> OR -u <URL>"

def crawler(args):

    urlqueue = queue.Queue()
    emailqueue = queue.Queue()

    if args.url:
        urlqueue.put([args.url, 1])

    if args.filename:
        with open(args.filename) as file:
            for url in file:
                urlqueue.put([url, 1])

    u = URLHandler(urlqueue, emailqueue, args.maxdepth if args.maxdepth else -1)
    u.start()

    u.join()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--nthreads", type=int, default=10)
    parser.add_argument("--maxdepth", type=int)
    parser.add_argument("-f", "--filename") #, required=True)
    parser.add_argument("-u", "--url") #, required=True)
    args = parser.parse_args()
    if args.filename == None and args.url == None:
        print(usage)
        exit()

    crawler(args)
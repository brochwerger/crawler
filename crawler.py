#!/usr/bin/python3

import argparse
import logging
import queue
from threading import Event

from queues import RabbitMQueue
from worker import Worker
from writer import Writer

usage_hint1 = "USAGE HINT: Required parameter: -f <filename> OR -u <URL>"
usage_hint2 = "USAGE HINT: Incompatible flags, use EITHER --verbose OR --quiet"

def crawler(args):

    mlogger = logging.getLogger('crawler')
    # Create the queues
    if args.rabbitmq:
        urlqueue = RabbitMQueue(server=args.rabbitmq, queue='urls')
        emailqueue = RabbitMQueue(server=args.rabbitmq, queue='emails')
        # urlqueue = RabbitMQueue(server='localhost', queue='urls')
        # emailqueue = RabbitMQueue(server='localhost', queue='emails')
    else:
        urlqueue = queue.Queue()
        emailqueue = queue.Queue()

    if args.url:
        urlqueue.put([None, args.url, 1])

    if args.input:
        with open(args.input) as file:
            for url in file:
                urlqueue.put([None, url, 1])

    max_depth_reached = Event() if args.maxdepth else None

    # Start the worker threads
    workers = []
    for w in range(args.nthreads):
        worker = Worker(w, urlqueue, emailqueue, args.maxdepth if args.maxdepth else -1, max_depth_reached, args.redis, args.aging)
        worker.start()
        workers.append(worker)

    # Start the writer thread
    writer = Writer(args.output, emailqueue)
    writer.start()

    if max_depth_reached:
        max_depth_reached.wait()
        mlogger.debug("One of the workers reached maximum depth -- clean up and exit !!!")
    else:
        # Wait for all worker threads to finish (which may happen if we limit the depth of the search)
        for t in workers:
            t.join()
        mlogger.debug("All workers finished -- clean up and exit !!!")

    # All worker threads have finished --> force the writer thread to finish too
    writer.stop()
    writer.join()



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--nthreads", type=int, default=10)
    parser.add_argument("--maxdepth", type=int)
    parser.add_argument("-i", "--input") #, required=True)
    parser.add_argument("-u", "--url") #, required=True)
    parser.add_argument("-o", "--output", required=True) #default="emails_found.txt")
    parser.add_argument("--verbose", action='store_true')
    parser.add_argument("--quiet", action='store_true')
    parser.add_argument("--logfile")

    parser.add_argument("--redis")
    parser.add_argument("--aging", type=int, default=60*24) # URL aging in MINUTES, default 1 day

    parser.add_argument("--rabbitmq")

    args = parser.parse_args()

    if args.input == None and args.url == None:
        print(usage_hint1)
        exit()

    if args.quiet and args.verbose:
        print(usage_hint2)
        exit()

    logger = logging.getLogger('crawler')
    logger.setLevel(logging.DEBUG if args.verbose else logging.CRITICAL if args.quiet else logging.INFO)
    format = logging.Formatter('%(name)s:%(levelname)s: %(message)s')
    handler = logging.FileHandler(args.logfile) if args.logfile else logging.StreamHandler()
    handler.setFormatter(format)
    logger.addHandler(handler)

    # loglevel = logging.INFO
    # if args.verbose:
    #     loglevel = logging.DEBUG
    # elif args.quiet:
    #     loglevel = logging.CRITICAL
    #
    # if args.logfile:
    #     logging.basicConfig(filename=args.logfile, format="%(levelname)s: %(message)s", level=loglevel)
    # else:
    #     logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    crawler(args)

import argparse
import queue

from urlhandler import URLHandler

def crawler(args):
    print("Hello")
    u = URLHandler(args.filename, None, None)
    u.start()

    u.join()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--nthreads", type=int, default=10)
    parser.add_argument("-f", "--filename", required=True)
    args = parser.parse_args()
    crawler(args)
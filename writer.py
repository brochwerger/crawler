import threading

class Writer(threading.Thread):

    def __init__(self, filename, emailqueue):
        threading.Thread.__init__(self)
        self.filename = filename
        self.emailqueue = emailqueue
        self.keepgoing = True
        self.out = open(self.filename, "a+", buffering=1)

    def stop(self):
        self.keepgoing = False

    def run(self):
        while self.keepgoing:
            msg = self.emailqueue.get()
            self.out.write(msg+'\n')
        self.out.close()
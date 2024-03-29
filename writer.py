import threading

class Writer(threading.Thread):

    def __init__(self, filename, emailqueue):
        threading.Thread.__init__(self)
        self.filename = filename
        self.emailqueue = emailqueue
        self.keepgoing = True
        self.out = open(self.filename, "a+", buffering=1)

    def stop(self):
        self.emailqueue.put("<EXIT>")

    def run(self):
        msg = None
        while True:
            msg = self.emailqueue.get()
            if msg == "<EXIT>":
                break
            self.out.write(msg+'\n')
        self.out.close()
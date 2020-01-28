from threading import Thread

class ContinuousThread(Thread):
    def __init__(self, group=None, target=None, name=None,args=(), kwargs=None, verbose=None,daemon=False):
        super(ContinuousThread,self).__init__(group=group, target=target, name=name,daemon=daemon)
        self.running=True
        self._args=args
        self._kwargs=kwargs

    def run(self):
        if(self._target):
            while(self.running):
                self._target(*self._args)

    def stop(self):
        self.running = False

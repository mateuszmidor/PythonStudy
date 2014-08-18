'''
Created on 18-08-2014

@author: mateusz
'''
from time import sleep
from Queue import Queue

class Task():
    def __init__(self, target):
        self.target = target
        
    def run(self):
        return self.target.send(None)
    
class Sheduler():
    tasks = Queue()

    def sheduleTask(self, task):
        self.tasks.put(task)

    def pickNextTask(self):
        return self.tasks.get()

    def handleNextTask(self):
        try:
            task = self.pickNextTask()
            result = task.run()
            self.sheduleTask(task)
            return result

        except StopIteration:
            return None

    def run(self):
        while True:
            result = self.handleNextTask()
            if (result):
                print "result is: %r" % result

def f1():
    while True:
        print "[tick]"
        sleep(0.5)
        yield

 

def f2():
    f = 1
    for i in xrange(1,10):
        f *= i  
        print "fibb(%d) = %d" % (i, f)
        yield
    yield f
 
if __name__ == '__main__':
    sheduler = Sheduler()
    t1 = Task(f1())
    t2 = Task(f2())
    sheduler.sheduleTask(t1)
    sheduler.sheduleTask(t2)
    sheduler.run() 
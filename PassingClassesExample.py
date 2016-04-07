class OverSeerClass:
    def __init__(self, workerClassInstance,worker2ClassInstance):
        self.worker = workerClassInstance
        self.worker2 = worker2ClassInstance
 
    def CallWorkerClassFunc(self):
        self.worker.DoWork()

    def CallWorker2ClassFunc(self):
        self.worker2.DoWork()
 
 
class WorkerClass:
    def DoWork(self):
        print "Working"
 
class Worker2Class:
    def DoWork(self):
        print "Working2"
 
 
w = WorkerClass()
w2 = Worker2Class()

print w
print w2
 
test = OverSeerClass(w,w2)
test.CallWorkerClassFunc()
test.CallWorker2ClassFunc()
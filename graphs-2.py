#!/usr/bin/python
import Queue
import threading
import time

exitFlag = 0

class myThread (threading.Thread):
   def __init__(self, threadID, q):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.q = q
   def run(self):
      print "Starting %s" % self.threadID
      process_data(self.threadID, self.q)
      print "Exiting %s" % self.threadID

def process_data(threadID, q):
   while not exitFlag:
      queueLock.acquire()
      if not workQueue.empty():
          data = q.get()
          queueLock.release()
          print "%s processing %s" % (threadID, data)
      else:
          queueLock.release()
      time.sleep(1)

nameList = ["One", "Two", "Three", "Four", "Five", "six", "niels", "piet"]
queueLock = threading.Lock()
workQueue = Queue.Queue()
threads = []
threadID = 1

# Create new threads
for tName in range(0,5):
   thread = myThread(threadID, workQueue)
   thread.start()
   threads.append(thread)
   threadID += 1

# Fill the queue
queueLock.acquire()
for word in nameList:
   workQueue.put(word)
queueLock.release()

# Wait for queue to empty
while not workQueue.empty():
   pass

# Notify threads it's time to exit
exitFlag = 1

# Wait for all threads to complete
for t in threads:
   t.join()
print "Exiting Main Thread"

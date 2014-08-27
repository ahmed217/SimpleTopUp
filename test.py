import time
import datetime
import sched

s = sched.scheduler(time.time, time.sleep)

def print_time(): print "From print_time", time.time()

def print_some_times():
     while True: 
	s.enter(2, 10, print_time, ())
     	s.run()


if __name__ == '__main__':
	 print_some_times()

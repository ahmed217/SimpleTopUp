import warid
import grameen
import robi
import banglalink
import multiprocessing
import datafetcher

if __name__== '__main__':

	# define the queues 
	# this queue is for warid, we will add 5 more queues 
	wdQ = multiprocessing.Queue() 
	
	# this queue is for grameen 
	gpQ = multiprocessing.Queue() 
	
	# this queue is for robi 
	rbQ = multiprocessing.Queue() 
	
	# this queue is for banglalink 
	blQ = multiprocessing.Queue() 
	
	df = datafetcher.DataFetcher(wdQ,gpQ,rbQ,blQ)
 	df.deamon = True
	df.start()	


	# initialize the modems
	
	# 5060 is the pin number for the current SIM of warid
	# send the wdQ to this warid modem 
	# !!! be careful with the baudrate, depends on the modems
	
	#wd = warid.Warid('/dev/ttyUSB0',9600,'5060',wdQ) 
	#wd.deamon = True
	#wd.start()

	#gp = grameen.Grameen('/dev/ttyUSB0',115200,'9171',gpQ)
	#gp.deamon = True
	#gp.start()
	
	#rb = robi.Robi('/dev/ttyUSB0',115200,'1144',rbQ)
	#rb.deamon = True
	#rb.start()
	
	bl = banglalink.Banglalink('/dev/ttyUSB0',115200,'9172',blQ)
	bl.deamon = True
	bl.start()
	
	df.join()
	#wd.join()
	gp.join()
	#rb.join()
	bl.join()





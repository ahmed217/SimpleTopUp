import serial
import time
import multiprocessing
import sys
import logging
import smtplib
from email.mime.text import MIMEText

class Modem(multiprocessing.Process):
    def __init__(self,port,speed):
        multiprocessing.Process.__init__(self)
       
	self.port = port
	self.speed = speed
 
	try:
            self.serialport = serial.Serial(port, speed, timeout=1)
        except:
            print "Unexpected error:", sys.exc_info()[0]
	
	logging.basicConfig(level=logging.INFO)
	self.logger = logging.getLogger(__name__)

    def sendEmail(self,modem):
	msg = modem + ' need restart'
	msg['Subject'] = 'Modem '+ modem + ' needs restart '
	msg['From'] = 'info@bduino.com'
	msg['To'] = 'shariful.islam@bduino.com'
	s = smtplib.SMTP('localhost')
	s.sendmail('info@bduino.com','shariful.islam@bduino.com',msg.as_string())
	s.quit()
	 
    def close(self):
        self.serialport.close()

    def reopen(self):
	self.close()
        self.logger.info('Re-opening the modem after closing')
	time.sleep(5)
	try:
            self.serialport = serial.Serial(self.port,self.speed, timeout=1)
        except:
            print "Reopening Unexpected error:", sys.exc_info()[0]

    def modemOk(self,modemname):
	msg = self.command('AT')
	if msg != None:
		msg = ' '.join(msg.split())
	self.logger.info('Modem '+modemname+' responded '+msg )
	if msg.find('OK') >= 0:
		self.logger.info('Modem is responding ok ')
		return True
	else:
		self.logger.info('Modem is NOT responding ok ')
		return False
    
    def command(self,cmd):
        self.serialport.write(bytes(cmd+'\r\n'))
        time.sleep(3)
        out = ''
        while self.serialport.inWaiting() > 0:
            out += self.serialport.read(1).decode('ascii', 'ignore')
        self.logger.info(cmd+' '+out)
	return out

    def waitFor(self,str):
	self.serialport.flushInput()
	trynow = 3
	while trynow > 0:
		out = ''
        	while self.serialport.inWaiting() > 0:
            		out += self.serialport.read(1).decode('ascii', 'ignore')
		if out.find(str) > 0:
			self.logger.info(out)
	    		return out
		else:
			trynow = trynow - 1
		time.sleep(2)
	
			
    def controlZ(self,cmd):
        self.serialport.write(bytes(str(cmd)+'\x1A'))
        time.sleep(3)
    
    def doTransfer(self):
	raise NotImplementedError	

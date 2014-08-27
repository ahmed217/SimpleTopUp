import serial
import time
import sys
import modem
import db

class Robi(modem.Modem):
    def __init__(self, port,speed,pin,taskQ):

        super(Robi, self).__init__(port,speed)
   	self.pin = pin
	self.taskQ = taskQ
	self.command('ATZ')
	self.command('ATZ')
 
    def doTransfer(self,id,to,amount,type,d):

	#self.command('AT+STSF=2,"5fffffff7f",100')
	self.command('AT+CFUN=1')
	self.waitFor('+STIN:')
	self.command('AT+STGI=0')
	#self.command('AT+STGR=0,1,129') # this line is for wavecom modem
	if type == 'prepaid':
		self.command('AT+STGR=0,1,2') # prepaid 
	else:
		self.command('AT+STGR=0,1,3') # postpaid !!! need to confirm 
			
	self.command('AT+STGI=3')
	self.command('AT+STGR=3,1')
	self.controlZ(to)			
	self.command('AT+STGI=3')
	self.command('AT+STGR=3,1')
	self.controlZ(amount)
	self.command('AT+STGI=1')
	self.command('AT+STGR=1')
	self.command('AT+STGI=3')
	self.command('AT+STGR=3,1')
	self.controlZ(self.pin)
	self.command('AT+STGI=9')
				
    def run(self):
	d = db.DB('b4that.com','root','roott987!!','cavoxnetbt')
        while True:
            # look for incoming request
            if not self.taskQ.empty():
                (id,recp,amount,type) = self.taskQ.get()

		recp = recp[1:]

		self.logger.info('Task found id:%s recp:%s amount:%s type:%s' % (id,recp,amount,type))	
		self.doTransfer(id,recp,amount,type,d)	

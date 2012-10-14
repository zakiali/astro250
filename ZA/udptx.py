import socket
import optparse, sys
import struct, time
import threading



FPGA_BRAMS = ['data_bram', 'ddc_bram']
FPGA_WRITES = ['freq', 'trig']

class server:
    def __init__(self, pid=None, fpga_brams = FPGA_BRAMS, port = 8888, host='localhost',
                 nomix = False, mixinfreq = 1, test = False):
        #on board set up

        self.test = test 
        if self.test: 
            self.bram = open('testdata', 'r')
            self.trig = open('trigger', 'w')
            self.nomix = True

        else:
            self.basename = '/proc/%d/hw/ioreg'%pid
            self.nomix = nomix
            if self.nomix:
                self.bram = open('/proc/%d/hw/ioreg/data_bram'%pid)
            else:
                self.bram = open('/proc/%d/hw/ioreg/ddc_bram'%pid)
            
            self.addr = open('/proc/%d/hw/ioreg/ddc_addr'%pid)
            self.freq = open('/proc/%d/hw/ioreg/freq'%pid)
            self.trig = open('/proc/%d/hw/ioreg/trig'%pid)

        self.data = ''
        #network stuff
        self.host = host
        self.port = port
            

    def get_addr(self):
        ''' gets the address of the ddc bram''' 
        self.last_addr = struct.unpack('>I',self.addr.read(4))[0]
        return self.last_addr
        
    def read(self):
        '''read the data and send it.'''
        if self.nomix:  
            while self.connected:
                self.trig.seek(0)
                self.trig.write(struct.pack('>I',1)) 
                self.trig.seek(0)
                self.trig.write(struct.pack('>I',0)) 
                self.trig.seek(0)
                time.sleep(1)
                self.bram.seek(0)
                self.data += (self.bram.read())
                self.send()
                self.data = ''
            exit()
                
        add1 = 0
        time.sleep(.01)
        add2 = self.get_addr()
        while self.connected:
            if add2 < add1:
                #if address 2 is less than address 1 read until the 
                #end of the bram and then seek back to the beginning.
                self.data.join(self.bram.read())
                self.bram.seek(0)
                add1 = 0
            self.data.join(self.bram.read((add2 - add1)*4))
            self.send()
            self.data = []
            add1 = add2 + 1
            add2 = self.get_addr()
            
    def net_start(self):
        '''create a socket and start sending data'''
        print 'Opening Socket for UDP...',
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print 'done.' 
        print 'Connecting to host %s on port %d'%(self.host,self.port)
        self.sock.connect((self.host,self.port))
        self.connected = True

    def _send(self):
        '''sends the big chunk of data in small chunks'''
        LEN = len(self.data)
        sent = 0
        while sent < LEN:   
            s = self.sock.send(self.data[sent:sent+8192])
            print s
            sent = sent + 8192
            if sent == LEN: break
          
    def send(self): 
        'send data to what '
        print 'Sending data: size = %d'%len(self.data)
        self._send()
        print 'Sent'

o = optparse.OptionParser()

o.add_option('-i', '--ip', type='string', dest = 'host', default='localhost',
            help = 'host ip address (i.e. the computer that will be reading the data.')
o.add_option('-p', '--port', type = 'int', default = 12345, dest = 'port',
            help = 'port to connect over.')
o.add_option('-t', '--test', action='store_true', dest='test',
            help = 'enter test mode')
opts, args = o.parse_args(sys.argv[1:])
pid = args[0]

service = server(port=opts.port, host=opts.host, pid=int(pid), nomix=True, test=opts.test)
service.net_start()
service.read()
        
        
        
             


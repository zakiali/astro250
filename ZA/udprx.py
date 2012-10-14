import socket , time
import struct 
import threading
import pylab  as plt
import numpy as n

class udprx:
    def __init__(self,port=8888,host='localhost', maxbuf=8192):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.data = [] 
        self.maxbuff = maxbuf #bytes
        self.host = host
        self.port = port
    def _listen(self): 
        self.sock.bind((self.host,self.port))    
        self.is_connected = False
        print 'Listening for data...'
        while True:
            _data = self.sock.recv(self.maxbuff) 
            self.data.append(list(struct.unpack('>%dh'%(len(_data)/2),_data)))
            self.is_connected = True
        self.is_connected = False
    
    def listen(self):
        print 'Starting Server on port %d'%self.port  
        self._listen_thread = threading.Thread(target=self._listen)
        self._listen_thread.daemon = True
        self._listen_thread.start()
        
    def plot_init(self):
        '''Sets up the plotter'''
        print 'setting up plot thread''' 
        plt.ion()
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.set_xlabel('time steps')
        self.ax1.set_ylabel('volts')
        self.ax1.set_ylim(-16,16)
        self.ax1.set_xlim(0,20)
    def plotter(self):
        self.plot_init()
        c = 0
        while True:
            try:
                ydata = self.data.pop(0)
                xdata = n.arange(len(ydata)) 
                if c == 0:
                    self.hl, = self.ax1.plot(xdata,ydata)
                else:
                    c+=1
                    self.hl.set_xdata(n.array(xdata))
                    self.hl.set_ydata(n.array(ydata))
                plt.draw()
            except IndexError:
                print 'no data received yet'
                time.sleep(1)
                continue
                
         
rx = udprx(port = 12345, host = 'localhost')
rx.listen()
time.sleep(2)
rx.plotter()

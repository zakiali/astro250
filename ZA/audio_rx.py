#! /usr/bin/env python -u
import socket , time
import struct 
import threading
import pylab  as plt
import numpy as n

class udprx:
    def __init__(self,port=8888,host='localhost', maxbuf=8192):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.data =  ''
        self.ants = []
        self.times = []
        self.maxbuff = maxbuf #bytes
        self.host = host
        self.port = port

    def _listen(self): 
        self.sock.bind((self.host,self.port))    
        self.is_connected = False
        print 'Listening for data...'
        while True:
            _data = self.sock.recv(self.maxbuff) 
            self.data = self.data + _data
            self.is_connected = True
        self.is_connected = False
    
    def listen(self):
        print 'Starting Server on port %d'%self.port  
        self._listen_thread = threading.Thread(target=self._listen)
        self._listen_thread.daemon = True
        self._listen_thread.start()
     
    def unpack(self,data):
        '''unpacks the data into payload and header'''
        ant,time = struct.unpack('<II',data[0:8])
        self.ants.append(ant)
        self.times.append(time)
        self.data += data[8:] 
        
    def unpack(self):
        raw_dat = self.data[0:513*8]
        print len(raw_dat)
        head = raw_dat[0:8]
        self.ant, self.time = struct.unpack('II',head)
        print len(raw_dat[8:])
        self.fft_data = n.frombuffer(raw_dat[8:], dtype='complex64')
        self.data=''
    
        
    def plot_init(self):
        '''Sets up the plotter'''
        print 'setting up plot thread''' 
        plt.ion()
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.set_xlabel('time steps')
        self.ax1.set_ylabel('volts')
        self.ax1.set_xlim(0,512)
        self.ax1.set_ylim(-1000,1000)

    def plotter(self):
        self.plot_init()
        c = 0
        while True:
#            time.sleep(.2)
            try:
                plt.cla()
                self.unpack()
                ydata = n.abs(self.fft_data)
                #xdata = n.arange(len(ydata)) 
                xdata = n.arange(512)*44100/1024.
                print self.ant, self.time
                if c == 0:
                    self.hl, = self.ax1.plot(xdata,ydata)
                    self.hl.axes.set_ylim(0,100000)
                else:
                    c+=1
                    self.hl.set_xdata(n.array(xdata))
                    self.hl.set_ydata(n.array(ydata))
                plt.draw()
            except Exception, e:
                print e
                time.sleep(.1)
                continue

        
                
         
rx = udprx(port = 8888, host = 'localhost')
rx.listen()
time.sleep(2)
rx.plotter()

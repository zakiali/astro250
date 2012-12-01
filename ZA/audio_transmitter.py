#! /usr/bin/env python -u
import pyaudio as pa, numpy as n
import pylab as pl
import socket, time, struct

#pl.ion()
#p = pa.PyAudio()
#stream = p.open(format=pa.paInt16,channels=1,rate=44100,input=True,frames_per_buffer=1024)
#NSAMPLES = 1024
#
#
#d = stream.read(NSAMPLES)
#d = n.frombuffer(d, dtype=n.int16)
#lines, = pl.plot(d)
#while True:
#    try:
#        d = stream.read(NSAMPLES)
#    except IOError, e: 
#        print e 
#    d = n.frombuffer(d, dtype=n.int16)
#    lines.set_ydata(d)
#    pl.draw()


NSAMPLES = 1024
class audiowaves(pa.PyAudio):
    def __init__(self, port=8888,host='localhost', antenna=0):
        pa.PyAudio.__init__(self)
        stream = self.open(format=pa.paInt16,channels=1,rate=44100,input=True,frames_per_buffer=1024)
        self.stream = stream
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.sock.connect((self.host, self.port))
        self.connected = True

        self.dt = NSAMPLES/44100.

        self.ant = antenna
        
    def readmic(self):  
        '''Reads data from the audio buffer and fft's it.
           Makes it ready for packetization. '''
        try:
            self.d = n.frombuffer(self.stream.read(NSAMPLES), dtype=n.int16)
        except IOError, e:
            print e
        self.data = n.fft.rfft(self.d)[:512]
        self.data = n.array(self.data, dtype='complex64')
    def _send(self):
        '''send all data for one fft data'''
        tm = n.floor(n.round(time.time()/self.dt))
        st = struct.pack('I',int(tm))
        ant = struct.pack('I',self.ant) 
        s = self.data.tostring()
        ds = ant+st+s

        s = self.sock.sendto(ds,(self.host, self.port))
    
    def send(self):
        print 'Sending data...'
        self._send()
         
    def transmit(self):
        '''Tramsmitter...Brings all the above together.'''
        while self.connected:
            self.readmic()
            self.send()
        
        
        
ad = audiowaves()
ad.transmit()

import numpy as n
import struct
import pylab as p
import optparse, sys


def read_bram(file):    
    op = open(file, 'r')
    dr = op.read()
    Num = len(dr)/4
    dd = struct.unpack('>%di'%Num,dr)
    return dd

def freq_arr(samp_freq,nsamp):
    sdf = (samp_freq/2.)/nsamp
    freqs = n.arange(-(samp_freq/2.),(samp_freq/2.),sdf)
    return freqs
    

o = optparse.OptionParser()
o.add_option('-f', '--sfreq', dest='samp_freq', type='int', default=200,
              help='sampling frequency in MHz. Default is 200MHz.')
opts,args = o.parse_args(sys.argv[1:])

brams=['data/data_bram_200mhz_noise',
       'data/data_bram_10MHz',
       'data/data_bram_100mhz_noise',
       'data/data_bram_110MHz',
       'data/data_bram_90MHz'] 

samp_freq = opts.samp_freq

for i, data_file in enumerate(brams):
    data = read_bram(data_file)
    ft = n.fft.fftshift(n.fft.fft(data))
    p.figure(i)
    freqs = freq_arr(samp_freq, len(data)/2.)
    p.plot(freqs, n.abs(ft))
    p.title(data_file)

p.show()

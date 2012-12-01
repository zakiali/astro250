import aipy as a 
import numpy as n
import pylab as p
import optparse,sys

# Size = 2 times the max size times the resolution

class uvplane():
    def __init__(self, size, res):
        '''
            size = total size of the array. This needs to be greater than 
            res = resolution of each pixel in wavelengths. That is the number of
                  wavelengths contained in each pixel.
        '''
        self.plane = n.zeros((size/res,size/res), dtype=n.complex64) 
        self.samples = n.zeros((size/res,size/res)) 
        self.size = size
        self.res = res

    def input(self, uv, data):
        u = n.round(uv[0] / self.res)
        v = n.round(uv[1] / self.res)
        self.plane[-v,-u] += data 
        self.plane[v,u] += n.conjugate(data)
        self.samples[v,u] += 1 
        self.samples[-v,-u] += 1 

    def get_img(self):
        '''Makes image of the sky (0 in center).'''
        self.sky = n.fft.fftshift(n.fft.fft2(self.plane))
        return self.sky

    def shift_uv(self):
        '''Shifts the uv-plane so that 0 sample is in the center.'''
        self.plane = n.fft.fftshift(self.plane)

    def rephase(self, uv, phscent = [0.,0.]):
        '''Change the phase center of your image.
           pc is the new phase center of your array. It is a unit vector
           that gives the coordinates of your phasecenter.
        '''
        if (uv[0] == 0) and (uv[1] == 0):
            phi = 0
            theta = 0
        else:
            phi = phscent[0]/uvwlen(uv)
            theta = phscent[1]/uvwlen(uv)
        uvw = n.dot(self.rot3d(theta=0., phi=45.,psi=0.,type='deg') , uv)
        
        return uvw

    def rot3d(self,theta=0,psi=0,phi=0, type='rad'):
        ''' A generic 3-d rotation matrix where 
            psi   = rotation around z-axis
            theta = rotation around y-axis
            phi   = rotation around x-axis'''
        if type == 'deg':
            psi   = (n.pi/180)*psi
            phi   = (n.pi/180)*phi
            theta = (n.pi/180)*theta
        
        rot3d = [[n.cos(theta)*n.cos(psi), -n.cos(phi)*n.sin(psi) +
n.sin(phi)*n.sin(theta)*n.cos(psi), n.sin(phi)*n.sin(psi) +
n.cos(phi)*n.sin(theta)*n.cos(psi)], 
                  [n.cos(theta)*n.sin(psi),
n.cos(phi)*n.cos(psi)+n.sin(phi)*n.sin(theta)*n.sin(psi),
-n.sin(phi)*n.cos(psi)+n.cos(phi)*n.sin(theta)*n.sin(psi)],
                 [-n.sin(theta), n.sin(phi)*n.cos(theta),
n.cos(phi)*n.cos(theta)]]
        return rot3d 


        
         


class griduvplane(uvplane):
    def __init__(self, size, res, npix = 4):
        uvplane.__init__(self,size,res) 
        self.npix = npix
        
    def input_grid(self, uv, data, gridfunc):
        u = uv[0]/self.res
        v = uv[1]/self.res
        ru,rv = n.round(u), n.round(v)
        wgt = gridfunc(u,v,ru,rv+1,self.npix)
        self.plane[-rv-1,-ru] = data * wgt
        self.samples[-rv-1,-ru] += wgt
        wgt = gridfunc(u,v,ru+1,rv,self.npix)
        self.plane[-rv,-ru-1] = data * wgt
        self.samples[-rv,-ru-1] += wgt 
        wgt = gridfunc(u,v,ru,rv-1,self.npix)
        self.plane[-rv+1,-ru] = data * wgt
        self.samples[-rv+1,-ru] += wgt      
        wgt = gridfunc(u,v,ru-1,rv,self.npix)
        self.plane[-rv,-ru+1] = data * wgt
        self.samples[-rv,-ru+1] += wgt
        wgt = gridfunc(u,v,ru,rv,self.npix)
        self.plane[-rv,-ru] = data * wgt
        self.samples[-rv,-ru] += wgt
       
      
       
def lingrid(u,v,ui,vi,npix):
    ''' u,v = true uv pixel coordinates.
        ui, vi = what you think the uv pixel should be in
        data = vis data.''' 
    wgt = .5*(2 - (u-ui)/4. - (v-vi)/4.)
    return wgt



def uvwlen(uvw):
    '''Find the length of a baseline, or any n dimensional array.'''
    return  n.sqrt(n.dot(uvw,uvw))

def get_freqs(sdf,sfreq, nchans):
    '''returns a frequency array.'''
    freqs = n.arange(nchans)*sdf + sfreq
    return freqs

def get_maxbl(uv,freqs=None):
    '''
        Returns the maximum baseline length in nanoseconds by default.
        If freqs array is given it returns max baseline length for all
        frequencies (returns in wavelength)
    '''
    maxd = 0
    maxbl = 0
    for (uvw,t,bl), data, flags in uv.all(raw=True):
        dd = uvwlen(uvw)
        if dd > maxd: 
            maxd = dd
            maxbl = bl
    if freqs != None:
        return n.max(n.round((maxd*freqs))) 
    else:
        return maxd
   
#######################################################
o = optparse.OptionParser()
o.add_option('-r','--res', dest='res', type='float',
            help='resolution of grid.')
o.add_option('-s', '--size', dest='size', type='int',
            help='size of image/uvplane. By default it is 2*(max baseline length times 2).') 
opts,args = o.parse_args(sys.argv[1:])

uv = a.miriad.UV('sim.uv')
freqs = get_freqs(uv['sdf'],uv['sfreq'],uv['nchan'])

#Trying to determine the maximum length of a baseline.
if opts.size == None:
    size = 2*get_maxbl(uv, freqs)
    print size
else: 
    size = opts.size
uv.rewind()
res = opts.res

################################################
#gridding by rounding 
plane = uvplane(size,res)

for (uvw,t,bl), data, flags in uv.all(raw=True):
    for ind, fr in enumerate(freqs):
        #print fr, uvw[0]
        ruvw = plane.rephase(uvw, phscent = [0,1])
        plane.input(ruvw[0:2]*fr, data[ind]*n.exp(-2*n.pi*ruvw[2]*fr*1j))
        
#uv.rewind()
################################################
#gridding by a new gridding funct. IN this case it is linear
#gplane = griduvplane(size,res)
#for (uvw,t,bl), data, flags in uv.all(raw=True):
#    for ind, fr in enumerate(freqs):
#        gplane.input_grid(uvw[0:2]*fr, data[ind], lingrid)

    

plane.shift_uv()
p.figure(1)
#p.imshow(n.abs(plane.plane))
#p.figure(2)
image =(plane.get_img())
p.imshow(n.abs(image))

#gplane.shift_uv()
#p.figure(3)
#p.imshow(n.abs(gplane.plane))
#p.figure(4)
#image =(gplane.get_img())
#p.imshow(n.abs(image))

p.show()
        


   


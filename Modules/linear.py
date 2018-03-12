'''
Module to perform linear systems calculations

Uses polynomials form numpy:
http://docs.scipy.org/doc/numpy/reference/routines.polynomials.package.html
http://docs.scipy.org/doc/numpy/reference/routines.polynomials.classes.html

History:
  12/04/2016 : First version
  16/04/2016 : Add of linear frequency response. Some plot corrections.
  19/04/2016 : Add of 3D s-plane graphs
  29/03/2017 : Add of help system
  12/03/2018 : Added Python 2.7 and 3.x compatibility
'''

# Python 2.7 compatibility
from __future__ import print_function
from __future__ import division

'''
@root
This is the main page of the Linear module help
List of topics:

   linblk : Linear block class
     plot : Plot functions
     util : Utility functions  	
	  
You can also input the name of a particular command	
@plot
Plot functions topics:

  Linear frequency:
     showFreqMag
     showFreqComplex

  Log frequency:	 
     showBodeMag
     showBodePhase
     drawBodePlot
     addBodePlot
	 
  Pole/Zero:	 
     addPoleZeroPlot
     drawPoleZeroPlot	 
	 
  showPlot
@util
Utility functions topics:

   frange : Generates log range
      f2w : Hz to rad/s
      w2f : rad/s to Hz
       dB : Linear to dB
  damping : Damping from poles
        q : Q from poles

  poleZeroPolar : Create pole or zero pair
'''

import numpy as np               # Import numpy for numeric calculations
import pylab as pl               # Import pylab
import matplotlib.pyplot as plt
from matplotlib import cm                     # Colormaps
from mpl_toolkits.mplot3d import Axes3D       # For 3D graphs
from numpy.polynomial import polynomial as P  # Polinomial functions

# External files
HELP_FILE = "Linear_Help.dat"

# Exception code
class LinearEx(Exception):
    def __init__(self, msg=""):
        print('** ' + msg) 
        print("\n")    
    def __str__(self):
        return repr(self.code)

#################### HELP CODE ###########################       

'''
Gives help information
Parameters:
   topic : Text to give information about
           Defaults to root
'''
def help(topic="root"):
    while (True):
        print()
        ftopic = "@"+topic
        topic_found = False
        with open(HELP_FILE, 'r') as hfile:
            for line in hfile:
                if line.startswith("#"):
                    continue
                if not topic_found:
                    if line.startswith("@#"):
                        print( "'" + topic + "' topic not found")
                        break
                    elif line.upper().startswith(ftopic.upper()):
                        topic_found = True
                else:
                    if line.startswith("@"):
                        break
                    print(line[0:-1])
        print()
        print("root topic goes to main page")
        print("Just hit return to exit help")
        print()
        topic = raw_input("Help topic : ")
        if topic == "":
            print()
            return		

##################### FREQUENCY HELPER FUNCTIONS #############################

'''
@frange
frange(start,end,ndec,ppd)
Generates a logarithmic range

Required parameters:
  start : start value
    end : end value
   ndec : number of decades
   ppd : points per decade (defaults to 20)

Either end or ndec must be provided   

Returns a vector with the frequencies   
   
Examples      
  >> f = frange(fstart,fend)          # Range with default 20 ppd
  >> f = frange(fstary,fend,ppd=10)   # Range with 10 ppd
  >> f = frange(fstart,ndec=4)        # 4 decades from fstart with default 20 ppd
  >> f = frange(fstrat,ndec=4,ppd=10) # 4 decades with custom ppd
'''
def frange(start,end=0,ndec=0,ppd=20):
    stlog = np.log10(start)
    # We don't provide end 
    if end == 0:
        if ndec == 0:
            raise LinearEx('Need to provide end or decades')  
        return 10**np.arange(stlog,stlog+ndec,1.0/ppd) 
    # We provide end
    endlog = np.log10(end)
    return 10**np.arange(stlog,endlog,1.0/ppd)

'''
@f2w
f2w(f)
Converts frequency from Hz to rad/s
Returns frequency in rad/s   
'''	
def f2w(f):
    return f*2*np.pi

'''
@w2f
w2f(w)
Converts frequency from rad/s to Hz
Returns frequency in Hz  
'''    
def w2f(w):
    return w/(2*np.pi)

################## LINEAR FREQUENCY PLOT HELPER FUNCTIONS ##################

'''
@showFreqMag
showFreqMag(f,mag,title,ylabel)
Linear frequency magnitude plot

Required parameters:
     f : Frequency vector (Hz)
   mag : Magnitude vector 
   
Optional parameters:   
  title : Plot title
 ylabel : Y axis label
 
Returns nothing 
'''    
def showFreqMag(f,mag,title='Magnitude Frequency Plot',ylabel='Magnitude'):
    plt.figure(facecolor="white")   # White border
    pl.grid()
    pl.semilogx(f, mag)
    pl.xlabel('Frequency (Hz)')     # Set X label
    pl.ylabel(ylabel)               # Set Y label
    pl.title(title)                 # Set title
    pl.show()    
    
'''
@showFreqComplex
showFreqComplex(f,vector,title)
Linear frequency magnitude and phase plot

Required parameters:
      f : Frequency vector (Hz)
 vector : Complex vector
 
Optional parameters:
  title : Plot title
  
Returns nothing  
'''	
def showFreqComplex(f,vector,title='Magnitude/Phase Frequency Plot'):
    plt.figure(facecolor="white")   # White border
    
    pl.subplot(2,1,1)
    pl.grid()
    mag = np.absolute(vector)
    pl.semilogx(f, mag)
    pl.xlabel('Frequency (Hz)')     # Set X label
    pl.ylabel('Magnitude')          # Set Y label
    pl.title(title)                 # Set title
    
    pl.subplot(2,1,2)
    pl.grid(True)
    phase = np.angle(vector,deg=True)
    pl.semilogx(f, phase)
    pl.xlabel('Frequency (Hz)')     # Set X label
    pl.ylabel('Phase')              # Set Y label
    
    pl.show()   

   
    
######################## BODE HELPER FUNCTIONS ############################    
 
'''
@dB
dB(gain)
Converts linear gain in dB
Returns value in dB
''' 
def dB(gain):
    return 20*np.log10(gain)

'''
@showBodeMag
Show Bode magnitude plot

Required parameters:
    f : Frequency vector (Hz)
  mag : Magnitude vector (dB)
  
Optional parameter:  
 title : Plot title
 
Returns nothing 
'''	
def showBodeMag(f,mag,title='Magnitude Bode Plot'):
    plt.figure(facecolor="white")   # White border
    pl.grid(True)
    pl.semilogx(f, mag)
    pl.xlabel('Frequency (Hz)')     # Set X label
    pl.ylabel('Magnitude (dB)')     # Set Y label
    pl.title(title)                 # Set title
    pl.show()

'''
@showBodePhase
showBodePhase(f,phase,title)
Show Bode phase plot

Required parameters:
      f : Frequency vector (Hz)
  phase : Phase vector (deg)
  
Optional parameter:  
 title : Plot title
  
Returns nothing 
'''	
def showBodePhase(f,phase,title='Phase Bode Plot'):
    plt.figure(facecolor="white") # White border
    pl.grid(True)
    pl.semilogx(f, phase)
    pl.xlabel('Frequency (Hz)')   # Set X label
    pl.ylabel('Phase (deg)')      # Set Y label
    pl.title(title)               # Set title
    pl.show() 

# Start value of handles    
plot_handles = []

# No current plot
noPlot = True
# Set white background
#plt.figure(facecolor="white") # White border
    
'''
@addBodePlot
addBodePlot(f,mag,phase,title,label)
Adds a new bode plot
Useful to show different Bode curves together

Required parameters:
      f : Frequency vector (Hz)
    mag : Magnitude vector(dB)
  phase : Phase vector (deg)
  
Optional parameters:  
  title : Plot title
  label : Label for the curve

Returns nothing
  
It is recommended to put the title in the last plot of the series
    Example:
    >> addBodePlot(f,mag1,phase1,label='Curve 1') 
    >> addBodePlot(f,mag2,phase2,title='Comparison',label='Curve 2')      
    >> showPlot()
	
See also showPlot	
'''     
def addBodePlot(f,mag,phase,title=None,label=None):
    global plot_handles,noPlot

    if noPlot:
        plt.figure(facecolor="white") # White border
        noPlot = False
    
    pl.subplot(2,1,1)
    pl.grid(True)
    pl.semilogx(f, mag)
    pl.xlabel('Frequency (Hz)')   # Set X label
    pl.ylabel('Magnitude (dB)')     # Set Y label
    if title:
        pl.title(title)             # Set title
    
    pl.subplot(2,1,2)
    pl.grid(True)
    if label:
        hand, = pl.semilogx(f, phase, label=label)
        plot_handles.append(hand)
    else:
        hand, = pl.semilogx(f, phase)
        plot_handles.append(hand)
    pl.xlabel('Frequency (Hz)')   # Set X label
    pl.ylabel('Phase (deg)')      # Set Y label

	
'''
@showPlot
showPlot()
Shows a multigraph plot
Returns nothing
'''	
def showPlot():
    global plot_handles,noPlot
    if plot_handles != []:
        plt.legend(handles=plot_handles)
    pl.show()
    plot_handles = []
    noPlot = True
     
'''
@drawBodePlot
drawBodePlot(f,mag,phase,title)
Draws a bode plot

Required parameters:
      f : Frequency vector (Hz)
    mag : Magnitude vector(dB)
  phase : Phase vector (deg)
  
Optional parameters:  
  title : Plot title (optional)
  
Returns nothing  
'''	 
def drawBodePlot(f,mag,phase,title='Bode Plot'):
    global plot_handles
    addBodePlot(f,mag,phase,title=title)
    plot_handles = []   # Don't show legend
    showPlot()

#################### S PLOT HELPER FUNCTIONS ######################

'''
@addPoleZeroPlot
addPoleZeroPlot(poles,zeros,title,color)
Adds poles to the current plot

Parameters:
  poles : List of poles
  zeros : List of zeros       
  title : Graph title (optional)
  color : Color of symbols (defaults to blue)  

Returns nothing  

See also showPlot
'''
def addPoleZeroPlot(poles=[],zeros=[],title=None,color='blue'):
    global noPlot
    
    if noPlot:
        plt.figure(facecolor="white") # White border
        noPlot = False    
    
    if title:
        pl.title(title)             # Set title
    if len(poles):
        re = np.real(poles)
        im = np.imag(poles)    
        pl.scatter(re,im,marker='x',color=color)       
    if len(zeros):
        re = np.real(zeros)
        im = np.imag(zeros)    
        pl.scatter(re,im,marker='o',color=color)
    pl.grid()
    pl.xlabel('Real axis')           # Set X label
    pl.ylabel('Imaginary axis')      # Set Y label

'''
@drawPoleZeroPlot
drawPoleZeroPlot(poles,zeros,title,color)
Draw a poles-zero plot

Parameters:
  poles : List of poles
  zeros : List of zeros
  title : Graph title (optional)
  color : Color of symbols (optional)
  
Returns nothing  
'''	
def drawPoleZeroPlot(poles=[],zeros=[],title=None,color=None):
    addPoleZeroPlot(poles,zeros,title,color)
    showPlot()

'''
@damping
damping(pole)
Returns the damping associated to a single pole
The results make no sense for real poles
   0 : Undamped (Oscillator)
  <1 : Underdamped (Decaying oscillations)
   1 : Critically damped or Overdamped (No oscillations) 
'''	
def damping(pole):
    return -np.real(pole)/np.absolute(pole)

'''
@q
q(pole)
Returns the Q factor associated to a single pole
The result make no sense for real poles
'''	
def q(pole):
    damp = damping(pole)
    return 1.0/(2.0*damp)

######################### LINBLK CLASS ############################    
        
'''
@linblk
class linblk
Linear block class

A new object can be created with:
  >> l1 = linblk()               # H(s) = 1 
  >> l2 = linblk([1],[1,1/p1])   # H(s) = 1 / ( 1 + s/p1 )
  
Or you can also use linFromPZ or lin1

Additional topics:
   linFromPZ, lin1, operators, methods
@operators
Operators available on the linblk class:

  str : Shows numerator/denominator
    * : Cascade of two systems  
    / : Cascade with second system pole <-> zero
    + : System output addition for same input
    - : Negation operator
    - : System substraction
@methods	
Methods available on the linblk class:
They are seachable as help topics
	
           nf : Negative feedback nf()
           pf : Positive feedback pf
         eval : Evaluation in s plane
        weval : Evaluation at jw
         bode : Pode plot
        freqR : Frequency response 
     showBode : Bode plot
      addBode : Add Bode plot
        poles : List of poles
        zeros : List of zeros
         gain : System gain
    addPZplot : Add PZ plot
   showPZplot : PZ plot
      printPZ : Print PZ list
        clean : PZ cancelation
      pzRange : Range for all PZ
   plotSplane : Linear 3D Magnitude "s" plot
    bode3Dmag : Log 3D Magnitude "s" plot
  bode3Dphase : Log 3D Phase "s" plot
'''		

'''
@nf
L1.nf(L2)
L2 gives negative feedback on L1

Retuns composite system
@pf
L1.nf(L2)
L2 gives positive feedback on L1

Retuns composite system
@eval
L1.eval(x)
Evaluate the system on a point of the s plane
   x : Complex value
Returns a complex value
@weval
L1.weval(w)
Evaluate the system on a point on the imaginary axis
   w : Value on the j axis (Real value)
Returns a complex value  
@bode
L1.bode(f)
Generates the bode plot vector results
   f : Frequency vector
Returns:  
    mag : Magnitude vector (dB)
  phase : Phase vector (deg)
@freqR  
L1.freqR(f):
Generates the frequency response as a vector
  f : Frequency vector
Returns frecuency response (complex)  
@showBode
L1.showBode(f,title):
Shows the bode plot of the system
      f : Frequency vector
  title : Plot title (optional)
Returns nothing   
@addBode
L1.addBode(f,title,label)
Add the bode plot to the current image
      f : Frequency vector
  title : Plot title (optional)
  label : Plot label (optional)
Use showPlot() to see the final image  
Returns noting
@poles     
L1.poles()
Gives the list of poles of the system
@zeros
L1.zeros()
Gives the list of zeros of the system  
@gain
gain()
Gives the gain of the system
We define gain as the quotient of the first coef (in increase order)
of num and den that is not zero
@addPZplot
L1.addPZplot(title,color)
Add the pole-zero plot to the current image
    title : Plot title (optional)
    color : Color used (optional)
Use showPlot() to see the final image
Returns nothing
@showPZplot
L1.showPZplot(title,color): 
Show he pole-zero plot of the system
    title : Plot title (optional)
    color : Color used (optional)
Returns nothing    
@printPZ
L1.printPZ()
Show poles and zeros on screen
Returns nothing
@clean
L1.clean(ratio)
Eliminates poles and zeros that cancel each other
A pole and a zero are considered equal if their distance
is lower than 1/ratio its magnitude
   ratio : Ratio to cancel PZ (default = 1000)
Returns a new object
@pzRange
L1.pzRange()
Returns in a tuple the range in the complex domain 
that includes all the poles and zeros
@plotSplane
L1.plotSplane(zmax)
Plots the magnitude of the evaluation of the
system inside the s plane in dB(magnitude)
    zmax : Maximum in Z axis (dB) (Optional)
Returns nothing    
@bode3Dmag
L1.bode3Dmag(sfmax,zmax)
Plots the magnitude of the evaluation of the
system inside the s plane in dB(magnitude)
The plot uses log10 of frequency in the axes
    fmax : Maximum frequency (optional)
    zmax : Maximum in Z axis (dB) (optional)
Returns nothing
@bode3Dphase
L1.bode3Dphase(fmax)
Plots the phase of the evaluation of the
system inside the s plane in dB(magnitude)
The plot uses log10 of frequency in the axes
    fmax : Maximum frequency
Returns nothing    
'''		
		
class linblk():
    def __init__(self,num=[1.0],den=[1.0]):
        '''A new object can be created with:
        >> l1 = linblk()               # H(s) = 1 block
        >> l2 = linblk([1],[1,1/p1])   # H(s) = 1 / ( 1 + s/p1 )
        ''' 
        self.num = P.Polynomial(num)
        self.den = P.Polynomial(den)
        
    def __str__(self):    
        '''Using print shows the numerator and denominator
        '''
        st = str(self.num.coef) + ' / ' + str(self.den.coef)
        return st
        
    def __mul__(self,other):
        '''Multiplication operator  (*)
        Returns a cascade of two systems
        '''
        obj = linblk()
        obj.num = self.num * other.num
        obj.den = self.den * other.den
        return obj
           
    def __div__(self,other):
        '''Division operator (/)
        Returns a cascade of the first system with
        the second one changing poles to zeros
        '''
        obj = linblk()
        obj.num = self.num * other.den
        obj.den = self.den * other.num
        return obj        
        
    def __add__(self,other):
        '''Addition operator (+)
        Returns a system that whose output is the sum of
        two systems with the same input
        '''    
        obj = linblk()
        obj.num = (self.num * other.den) + (self.den*other.num)
        obj.den = self.den * other.den
        return obj
    
    def __neg__(self):
        '''Negation operator (-)
        Returns a system with sign change
        '''
        obj = linblk()
        obj.num = -self.num
        obj.den = self.den
        return obj
    
    def nf(self,other):
        '''Negative feedback
        Use other system to give negative feedback
        '''
        obj = linblk()
        obj.num = self.num * other.den
        obj.den = (self.den * other.den) + (self.num * other.num)
        return obj
        
    def pf(self,other):
        '''Positive feedback
        Use other system to give positive feedback
        '''    
        obj = linblk()
        obj.num = self.num * other.den
        obj.den = (self.den * other.den) - (self.num * other.num)
        return obj        
        
    def eval(self,x):
        '''Evaluate the system on a point of the s plane
          x : Complex value
        '''
        y = self.num(x)/self.den(x)
        return y
        
    # Evaluation at jw
    def weval(self,w):
        '''Evaluate the system on a point on the imaginary axis
          w : Value on the j axis (Real value)
        '''
        x = w*1j
        y = self.num(x)/self.den(x)
        return y
        
    def bode(self,f):
        '''Generates the bode plot vector results
          f : Frequency vector
        Returns:  
            mag : Magnitude vector (dB)
          phase : Phase vector (deg)
        '''    
        w = f2w(f)
        res = self.weval(w)
        mag = dB(np.absolute(res))
        phase = np.angle(res,deg=True)
        return mag, phase
        
    def freqR(self,f):
        '''Generates the frequency response vector results
          f : Frequency vector
        Returns:  
          res : Freuency response (complex)
        '''    
        w = f2w(f)
        res = self.weval(w)
        return res       

    def showBode(self,f,title='Bode Plot'):
        '''Shows the bode plot of the system
          f : Frequency vector
        '''        
        mag, phase = self.bode(f)
        drawBodePlot(f,mag,phase,title)
        
    def addBode(self,f,title=None,label=None):
        '''Add the bode plot to the current image
          f : Frequency vector
        Use showPlot() to see the final image  
        '''
        mag, phase = self.bode(f)
        if title:
            addBodePlot(f,mag,phase,title,label=label)    
        else:    
            addBodePlot(f,mag,phase,label=label)
            
    def poles(self):
        '''Get the list of poles of the system
        '''
        # Code to eliminate
        # Order in Polynomials is reverse to needed in roots
        #return np.roots(self.den.coef[::-1])
        return self.den.roots()
        
    def zeros(self):
        '''Get the list of zeros of the system
        '''
        # Code to eliminate
        # Order in Polynomials is reverse to needed in roots
        #return np.roots(self.num.coef[::-1])  
        return self.num.roots()

    def gain(self):
        '''Get the gain of the system
        We define gain as the quotient of the first coef (in increase order)
        of num and den that is not zero
        '''
        for c in self.num.coef:
            if c!= 0.0:
                cnum = c
                break
        for c in self.den.coef:
            if c!= 0.0:
                cden = c
                break                
        #print str(self.num.coef)   #Remove this line
        #print str(self.den.coef)   #Remove this line
        # gain = self.num.coef[0] / self.den.coef[0]
        gain = cnum/cden
        return gain        

    def addPZplot(self,title=None,color=None):
        '''Add the pole-zero plot to the current image
        Use showPlot() to see the final image
          title : Plot title (optional)
        '''
        poles = self.poles()
        zeros = self.zeros()
        addPoleZeroPlot(poles,zeros,title,color)
        
    def showPZplot(self,title=None,color=None): 
        '''Add the pole-zero plot to the current image
          title : Plot title (optional)
        '''    
        self.addPZplot(title,color)
        showPlot()
        
    def printPZ(self):
        '''Show poles and zeros on screen
        '''
        poles = self.poles()
        zeros = self.zeros()
        gain = self.gain()
        print('Poles : ' + str(poles))
        print('Zeros : ' + str(zeros))
        print('Gain : '  + str(gain))
        
    def clean(self,ratio=1000.0):
        '''Eliminates poles and zeros that cancel each other
        A pole and a zero are considered equal if their distance
        is lower than 1/ratio its magnitude
           ratio : Ratio to cancel PZ (default = 1000)
        Return a new object   
        '''
        gain = self.gain()
        poles = self.poles()
        zeros = self.zeros()
        
        # Return if there are no poles or zeros
        if len(poles)==0: return
        if len(zeros)==0: return
        
        outPoles=[]          # Empty pole list
        for pole in poles:
            outZeros=[]      # Empty zero list
            found = False
            for zero in zeros:
                if not found:
                    distance = np.absolute(pole-zero)
                    threshold = ( np.absolute(pole) + np.absolute(zero) ) / (2.0*ratio)
                    if distance > threshold:
                        outZeros.append(zero)
                    else:
                        found = True
                else:
                    outZeros.append(zero)
            if not found:
                outPoles.append(pole)
            zeros = outZeros
        poles = outPoles
        
        s = linblk()
        s.den=P.Polynomial(P.polyfromroots(poles))
        s.num=P.Polynomial(P.polyfromroots(zeros))
        
        # Add gain    
        # curr = s.num.coef[0]/s.den.coef[0]
        curr = s.gain()
        s.num = s.num * gain / curr
        
        return s
             
    def pzRange(self):
        '''Returns the range in the complex domain that includes
        all the poles and zeros
        '''
        list = np.append(self.poles(),self.zeros())
        ReMin = np.amin(np.real(list))
        ReMax = np.amax(np.real(list))
        ImMin = np.amin(np.imag(list))
        ImMax = np.amax(np.imag(list))
        return ReMin + ImMin*1j , ReMax + ImMax*1j
        
    def plotSplane(self,zmax=100.0):
        '''Plots the magnitude of the evaluation of the
        system inside the s plane in dB(magnitude)
           zmax : Maximum in Z axis (dB)
        '''
        min,max = self.pzRange()
        fig = plt.figure(facecolor="white")    # White border
        ax = fig.gca(projection='3d')
        X = np.linspace(1.5*np.real(min),0.0,100)
        Y = np.linspace(1.5*np.imag(min),1.5*np.imag(max),100)
        X, Y = np.meshgrid(X, Y)
        Z = np.clip(dB(np.absolute(self.eval(X + 1j*Y))),0.0,zmax)
        surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm, 
                       linewidth=0, antialiased=False)
 
        ax.contour(X, Y, Z)
        ax.set_xlabel('Real')
        ax.set_ylabel('Imaginary')
        ax.set_zlabel('dB')

        plt.show()
        
    def bode3Dmag(self,fmax=None,zmax=100.0):
        '''Plots the magnitude of the evaluation of the
        system inside the s plane in dB(magnitude)
        The plot uses log10 of frequency in the axes
           fmax : Maximum frequency
           zmax : Maximum in Z axis (dB)
        '''
        if fmax is None:
            min,max = self.pzRange()
            fmax = np.max([np.absolute(np.real(min))
                       ,np.absolute(np.real(max))
                       ,np.absolute(np.imag(min))
                       ,np.absolute(np.real(max))])
                       
        max = np.log10(2.0*fmax)
        fig = plt.figure(facecolor="white")    # White border
        ax = fig.gca(projection='3d')
        X = np.linspace(-max,0.0,100)
        Y = np.linspace(-max,max,100)
        X, Y = np.meshgrid(X, Y)
        Z = np.clip(dB(np.absolute(self.eval(np.sign(X)*10.0**np.absolute(X) 
                  + 1j*np.sign(Y)*10.0**np.absolute(Y)))),0.0,zmax)
        surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm, 
                       linewidth=0, antialiased=False)
 
        ax.contour(X, Y, Z)
        ax.set_xlabel('Real (decade)')
        ax.set_ylabel('Imaginary (decade)')
        ax.set_zlabel('dB')

        plt.show()     

    def bode3Dphase(self,fmax=None):
        '''Plots the phase of the evaluation of the
        system inside the s plane in dB(magnitude)
        The plot uses log10 of frequency in the axes
           fmax : Maximum frequency
           zmax : Maximum in Z axis (dB)
        '''
        if fmax is None:
            min,max = self.pzRange()
            fmax = np.max([np.absolute(np.real(min))
                       ,np.absolute(np.real(max))
                       ,np.absolute(np.imag(min))
                       ,np.absolute(np.real(max))])
                       
        max = np.log10(2.0*fmax)
        fig = plt.figure(facecolor="white")    # White border
        ax = fig.gca(projection='3d')
        X = np.linspace(-max,0.0,100)
        Y = np.linspace(-max,max,100)
        X, Y = np.meshgrid(X, Y)
        Z = np.clip(np.angle(self.eval(np.sign(X)*10.0**np.absolute(X) 
                  + 1j*np.sign(Y)*10.0**np.absolute(Y)))*180.0/np.pi,-180.0,180.0)
        surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm, 
                       linewidth=0, antialiased=False)
 
        ax.contour(X, Y, Z)
        ax.set_xlabel('Real (decade)')
        ax.set_ylabel('Imaginary (decade)')
        ax.set_zlabel('Phase')

        plt.show()         
        
################# HELPER SYSTEM FUNCTIONS ########################

'''
@linFromPZ
linFromPZ(poles,zeros,gain,ingain)
Creates a system from the list of poles and zeros

Parameters:
  poles : List of poles
  zeros : List of zeros 

Gain can be defined as:
   gain : Gain defined as the quotient of first num/den coef.
  igain : Gain defined at infinite freq. in high pass 

Returns a linblk object 
'''        
def linFromPZ(poles=[],zeros=[],gain=1.0,ingain=None):
    # Create new block
    s = linblk()
    '''
    # Removed this code as polyfromroots is easier
    
    # Add poles
    for pole in poles:
        if pole == 0.0:
            poly = P.Polynomial([0,1])
        else:
            poly = P.Polynomial([1,-1/pole])
        s.den = s.den * poly
    # Add zeros    
    for zero in zeros:
        if zero == 0.0:
            poly = P.Polynomial([0,1])
        else:
            poly = P.Polynomial([1,-1/zero])
        s.num = s.num * poly
    ''' 
    #if len(poles):
    s.den=P.Polynomial(P.polyfromroots(poles))
    #if len(zeros):
    s.num=P.Polynomial(P.polyfromroots(zeros))
    print(s.den,s.num)
    # Add gain  
    '''    
    curr = s.num.coef[0]/s.den.coef[0]
    if curr == 0:
        # There is a 0 zero
        s.num = s.num *gain*s.den.coef[0]
    else:
        # There is no 0 zero
        s.num = s.num * gain / curr
    '''
    if ingain == None:
        curr = s.gain()
        s.num = s.num * gain / curr
    else:
        curr = s.num.coef[-1] * s.den.coef[-1]
        s.num = s.num * gain /curr
    return s   

'''
@poleZeroPolar
poleZeroPolar(mag,angle)
Generates a list of two poles or zeros from
their magnitude and angle on the s plane

Required parameters:
    mag : magnitude
  angle : angle of one pole or zero (0 to 90)
  
Returns a list of two poles or zeros
'''	
def poleZeroPolar(mag,angle):
    radians = angle * np.pi / 180.0
    p1 = -mag*np.cos(radians) + 1j*mag*np.sin(radians)
    p2 = -mag*np.cos(radians) - 1j*mag*np.sin(radians)
    return [p1,p2]
    
    
            
####################### PREDEFINED SYSTEMS ###################

'''
@lin1
lin1
Identity system H(s)=1
'''

# Linear indentiy system H(s) = 1
lin1 = linblk()


 
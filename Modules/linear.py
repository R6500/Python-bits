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
               Improvement of plotting on Colaboratory
               Added version string
               Help comments are now Python help compatible
  15/03/2018 : Add of substraction overload operator             
               Add autorange for the frequencies of bode
  16/03/2018 : Corrections on plotSplane               
               Added tResponse member function
'''

# Python 2.7 compatibility
from __future__ import print_function
from __future__ import division

try:
   input = raw_input
except NameError:
   pass

version = '16/3/2018-D'   
   
"""
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
"""

import numpy as np               # Import numpy for numeric calculations
import pylab as pl               # Import pylab
import matplotlib.pyplot as plt
from matplotlib import cm                     # Colormaps
from mpl_toolkits.mplot3d import Axes3D       # For 3D graphs
from numpy.polynomial import polynomial as P  # Polinomial functions

import calc

# External files
HELP_FILE = "Linear_Help.dat"

# Define normal mode outside colaboratory
colaboratory = False

# Exception code
class LinearEx(Exception):
    def __init__(self, msg=""):
        print('** ' + msg) 
        print("\n")    
    def __str__(self):
        return repr(self.code)

#################### HELP CODE ###########################       


def help(topic="root"):
    """
    Gives help information
    Parameters:
        topic : Text to give information about
                Defaults to root
    Exits with a meesage if the help file is not found           
    """    
    while (True):
        print()
        ftopic = "@"+topic
        topic_found = False
        try:
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
        except:
            print('Help file ',HELP_FILE,' is not available')
            return
        print()
        print("root topic goes to main page")
        print("Just hit return to exit help")
        print()
        topic = input("Help topic : ")
        if topic == "":
            print()
            return		

##################### FREQUENCY HELPER FUNCTIONS #############################


def frange(start,end=0,ndec=0,ppd=20):
    """
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
    """
    stlog = np.log10(start)
    # We don't provide end 
    if end == 0:
        if ndec == 0:
            raise LinearEx('Need to provide end or decades')  
        return 10**np.arange(stlog,stlog+ndec,1.0/ppd) 
    # We provide end
    endlog = np.log10(end)
    return 10**np.arange(stlog,endlog,1.0/ppd)

def f2w(f):
    """
    @f2w
    f2w(f)
    Converts frequency from Hz to rad/s
    Returns frequency in rad/s   
    """
    return f*2*np.pi


def w2f(w):
    """"
    @w2f
    w2f(w)
    Converts frequency from rad/s to Hz
    Returns frequency in Hz  
    """   
    return w/(2*np.pi)

# COLABORATORY FLAG FOR PLOTTING #####################################################

def setColaboratory(flag=True):
    """
    @setColaboratory
    setColaboratory(flag=True)
    Indicates that we are in Colaboartory
    Don't return anything
    """  
    global colaboratory
    colaboratory = flag    
    
# Internal plot functions ############################################################

def _plotStart():
    """"
    _plotStart
    (Internal use function)
    Starts a new plot
    Returns:
      fig : Figure object 
    """
    if colaboratory:
        fig=plt.figure()
        return fig
    # Outside colaboratory
    fig=plt.figure(facecolor="white")   # White border
    return fig     

def _subplotStart(fig,n,title="",xt="",yt="",grid=True):
    """
    _subplotStart
    (Internal use function)
    Starts a new subplot
    Paramenters:
      fig   : Figure to add the subplot
      title : Title of the subplot (deafults to none)
      xt    : x label of the subplot (defaults to none)
      yt    : y label of the subplot (defaults to none)
      grid  : Determines if there is grid (defaults to True)
    Returns:
      ax  : Axes object  
    """    
    # If we are inside colaboratory
    if colaboratory:
        ax = fig.add_subplot(n)
        ax.set_facecolor("white")
        ax.set_title(title)
        ax.set_xlabel(xt)
        ax.set_ylabel(yt) 
        if (grid):
            plt.grid(True,color="lightgrey",linestyle='--')
        return ax
    # Outside colaboratory
    ax = fig.add_subplot(n)
    ax.set_title(title)
    ax.set_xlabel(xt)
    ax.set_ylabel(yt)
    if grid:
        pl.grid()
    return ax    
    
def _subplotEnd(ax,labels=[],location='best'):
    """
    _subplotEnd
    (Internal use function)
    Ends a subplot
    Parameters:
        ax       : Subplot axes
        labels   : List of label names (Default to no labels)
        location : Location for labels (Default to 'best')
    Returns nothing    
    """
    if colaboratory:
        if not labels == []:
            pl.legend(loc=location)
        xmin, xmax = plt.xlim()
        ymin, ymax = plt.ylim()
        ax.axvline(x=xmin,linewidth=2, color='black')
        ax.axvline(x=xmax,linewidth=2, color='black')
        ax.axhline(y=ymin,linewidth=2, color='black')
        ax.axhline(y=ymax,linewidth=2, color='black')    
    # Outside colaboratory
    if not labels == []:
        pl.legend(loc=location) 

def _plotEnd():
    """
    _plotEnd
    Ends a previously started plot
    Takes no parameters
    Returns nothing  
    """
    if colaboratory:
        plt.show()   
        return        
    # Outside colaboratory
    pl.show() 
    pl.close() 
    
################## LINEAR FREQUENCY PLOT HELPER FUNCTIONS ##################
  
def showFreqMag(f,mag,title='Magnitude Frequency Plot',ylabel='Magnitude'):
    """
    @showFreqMag
    showFreqMag(f,mag,title,ylabel)
    Linear frequency magnitude plot
    
    Required parameters:
        f : Frequency vector (Hz)
      mag : Magnitude vector (in linear units)
   
    Optional parameters:   
      title : Plot title
     ylabel : Y axis label
 
    Returns nothing 
    """  
    fig=_plotStart()
    ax  = _subplotStart(fig,111,title,'Frequency (Hz)',ylabel)
    pl.semilogx(f, mag)
    _subplotEnd(ax)
    _plotEnd()
    
def showFreqComplex(f,vector,title='Magnitude/Phase Frequency Plot'):
    """
    @showFreqComplex
    showFreqComplex(f,vector,title)
    Linear frequency magnitude and phase plot

    Required parameters:
           f : Frequency vector (Hz)
      vector : Complex vector
 
    Optional parameters:
       title : Plot title
  
    Returns nothing  
    """
    fig=_plotStart()
    ax  = _subplotStart(fig,211,title,'','Magnitude')
    mag = np.absolute(vector)
    pl.semilogx(f, mag)
    _subplotEnd(ax)
    
    ax  = _subplotStart(fig,212,'','Frequency (Hz)','Phase')
    phase = np.angle(vector,deg=True)
    pl.semilogx(f, phase)
    _subplotEnd(ax)
    _plotEnd()    

   
    
######################## BODE HELPER FUNCTIONS ############################    
 

def dB(gain):
    """
    @dB
    dB(gain)
    Converts linear gain in dB
    Returns value in dB
    """
    return 20*np.log10(gain)

def showBodeMag(f,mag,title='Magnitude Bode Plot'):
    """
    @showBodeMag
    Show Bode magnitude plot

    Required parameters:
          f : Frequency vector (Hz)
        mag : Magnitude vector (dB)
  
    Optional parameter:  
      title : Plot title
 
    Returns nothing 
    """	
    fig=_plotStart()
    ax=_subplotStart(fig,111,title,'Frequency (Hz)','Magnitude (dB)')
    pl.semilogx(f, mag)
    _subplotEnd(ax)
    _plotEnd()

def showBodePhase(f,phase,title='Phase Bode Plot'):
    """
    @showBodePhase
    showBodePhase(f,phase,title)
    Show Bode phase plot

    Required parameters:
          f : Frequency vector (Hz)
      phase : Phase vector (deg)
  
    Optional parameter:  
      title : Plot title
  
    Returns nothing 
    """	
    fig=_plotStart()
    ax=_subplotStart(fig,111,title,'Frequency (Hz)','Phase (deg)')
    pl.semilogx(f, phase)
    _subplotEnd(ax)
    _plotEnd() 

# Information about bodes
bodeLabels = []
bodeFrequencies = []
bodeMagnitudes = []
bodePhases = []
     
def addBodePlot(f,mag,phase,label=''):
    """
    @addBodePlot
    addBodePlot(f,mag,phase,label)
    Adds a new bode plot
    Useful to show different Bode curves together

    Required parameters:
          f : Frequency vector (Hz)
        mag : Magnitude vector(dB)
      phase : Phase vector (deg)
  
    Optional parameters:  
      label : Label for the curve (Defaults to no label)

    Returns nothing
  
    See also showBodePlot	
    """    
    global bodeFrequencies,bodeMagnitudes,bodePhases,bodeLabels
    bodeFrequencies.append(f)
    bodeMagnitudes.append(mag)
    bodePhases.append(phase)
    bodeLabels.append(label)

	
def showBodePlot(title='Bode Plot',location='best'):  
    """"
    @showPlot
    showPlot()
    Shows a multigraph plot
    Optional parameters:
          title : Title for the plot
       location : Location for the labels (Defaults to 'best')
    Returns nothing
    """	
    global bodeFrequencies,bodeMagnitudes,bodePhases,bodeLabels
    fig=_plotStart()
    ax  = _subplotStart(fig,211,title,'','Magnitude (dB)')
    for element in zip(bodeFrequencies,bodeMagnitudes,bodeLabels):
        if len(bodeFrequencies) == 1:
            pl.semilogx(element[0],element[1],label='Nada')
        else:
            pl.semilogx(element[0],element[1],label=element[2])
    # Legend only in phase plot        
    #if len(bodeFrequencies) > 1:
    #    pl.legend(loc=location)        
    _subplotEnd(ax)
    ax  = _subplotStart(fig,212,'','Frequency (Hz)','Phase (deg)')
    for element in zip(bodeFrequencies,bodePhases,bodeLabels):
        if len(bodeFrequencies) == 1:
            pl.semilogx(element[0],element[1],label='Nada')
        else:
            pl.semilogx(element[0],element[1],label=element[2])        
    if len(bodeFrequencies) > 1:
        pl.legend(loc=location)         
    _subplotEnd(ax)
    _plotEnd() 
    # Reset bode plots
    bodeFrequencies = []
    bodeLabels = []
    bodeMagnitudes = []
    bodePhases = []
     
def drawBodePlot(f,mag,phase,title='Bode Plot'):
    """
    @drawBodePlot
    drawBodePlot(f,mag,phase,title)
    Draws a bode plot

    Required parameters:
          f : Frequency vector (Hz)
        mag : Magnitude vector(dB)
      phase : Phase vector (deg)
  
    Optional parameters:  
      title : Plot title
  
    Returns nothing  
    """ 
    addBodePlot(f,mag,phase)
    showBodePlot(title)

#################### S PLOT HELPER FUNCTIONS ######################

# Global variables
pzPlotPoles  = []
pzPlotZeros  = []
pzPlotLabels = []
pzPlotColors = []

def addPoleZeroPlot(poles=[],zeros=[],label=None,color='blue'):
    """
    @addPoleZeroPlot
    addPoleZeroPlot(poles,zeros,title,color)
    Adds poles to the current plot

    Parameters:
       poles : List of poles
       zeros : List of zeros       
       label : Label (optional)
       color : Color of symbols (defaults to 'blue')  

    Returns nothing  

    See also showPoleZeroPlot
    """
    global pzPlotPoles,pzPlotZeros,pzPlotLabels,pzPlotColors
    pzPlotPoles.append(poles)
    pzPlotZeros.append(zeros)
    pzPlotLabels.append(label)
    pzPlotColors.append(color)
    
def showPoleZeroPlot(title='Pole(x) / Zero(o)  plot',location='best'):   
    """
    @showPoleZeroPlot
    showPoleZeroPlot(title,location)
    Draws a pole-zero plot after calls to addPoleZeroPlot
    Optional parameters:
       title    : Title for the plot
       location : Location for the legend
    """
    global pzPlotPoles,pzPlotZeros,pzPlotLabels,pzPlotColors
    labelBox = False
    fig=_plotStart()
    ax=_subplotStart(fig,111,title,'Real axis','Imaginary axis')
       
    for poles,zeros,label,color in zip(pzPlotPoles
                       ,pzPlotZeros,pzPlotLabels,pzPlotColors):
        showLabel = (label != None)
        if len(poles):
            re = np.real(poles)
            im = np.imag(poles)    
            if showLabel: 
                pl.scatter(re,im,marker='x',label=label,color=color) 
                labelBox=True
                showLabel = False
            else:
                pl.scatter(re,im,marker='x',color=color)
        if len(zeros):
            re = np.real(zeros)
            im = np.imag(zeros)
            if showLabel: 
                pl.scatter(re,im,marker='x',label=label,color=color) 
                labelBox=True
            else:
                pl.scatter(re,im,marker='o',color=color) 

    # Zero lines        
    ax.axvline(x=0,linewidth=1, color='black', linestyle='--')
    ax.axhline(y=0,linewidth=1, color='black', linestyle='--')
            
    if labelBox == True:
        pl.legend(loc=location)     
      
    _subplotEnd(ax)
    _plotEnd()  
    # Reset lists
    pzPlotPoles  = []
    pzPlotZeros  = []
    pzPlotLabels = []
    pzPlotColors = []    

def drawPoleZeroPlot(poles=[],zeros=[]
                     ,title='Pole(x) & Zero(o)  plot'
                     ,color='blue'):
    """
    @drawPoleZeroPlot
    drawPoleZeroPlot(poles,zeros,title,color)
    Draw a poles-zero plot

    Parameters:
       poles : List of poles
       zeros : List of zeros
       title : Graph title (optional)
       color : Color of symbols (optional)
  
    Returns nothing  
    """	                     
    addPoleZeroPlot(poles,zeros,color=color)
    showPoleZeroPlot()

def damping(pole):
    """
    @damping
    damping(pole)
    Returns the damping associated to a single pole
    The results make no sense for real poles
        0 : Undamped (Oscillator)
       <1 : Underdamped (Decaying oscillations)
        1 : Critically damped or Overdamped (No oscillations) 
    """	
    return -np.real(pole)/np.absolute(pole)

def q(pole):
    """
    @q
    q(pole)
    Returns the Q factor associated to a single pole
    The result make no sense for real poles
    """
    damp = damping(pole)
    return 1.0/(2.0*damp)

######################### LINBLK CLASS ############################    
        
"""
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
"""	
		
class linblk():
    def __init__(self,num=[1.0],den=[1.0]):
        """
        linblk Class constructor
        A new object can be created with:
        >> l1 = linblk()               # H(s) = 1 block
        >> l2 = linblk([1],[1,1/p1])   # H(s) = 1 / ( 1 + s/p1 )
        """ 
        self.num = P.Polynomial(num)
        self.den = P.Polynomial(den)
        
    def __str__(self):    
        """
        Converts a linblk object to string
        Shows the numerator and denominator
        """
        st = str(self.num.coef) + ' / ' + str(self.den.coef)
        return st
        
    def __mul__(self,other):
        """
        Multiplication operator  (*)
        Returns a cascade of two systems
        """
        obj = linblk()
        obj.num = self.num * other.num
        obj.den = self.den * other.den
        return obj
           
    def __div__(self,other):
        """
        Division operator (//)
        Returns a cascade of the first system with
        the second one changing poles to zeros
        """
        obj = linblk()
        obj.num = self.num * other.den
        obj.den = self.den * other.num
        return obj  

    def __truediv__(self,other):
        """
        True Division operator (/)
        Returns a cascade of the first system with
        the second one changing poles to zeros
        """
        obj = linblk()
        obj.num = self.num * other.den
        obj.den = self.den * other.num
        return obj          
        
    def __add__(self,other):
        """
        Addition operator (+)
        Returns a system that whose output is the sum of
        two systems with the same input
        """    
        obj = linblk()
        obj.num = (self.num * other.den) + (self.den*other.num)
        obj.den = self.den * other.den
        return obj
        
    def __sub__(self,other):
        """
        Substraction operator (+)
        Returns a system that whose output is the substraction of
        two systems with the same input
        """    
        obj = linblk()
        obj.num = (self.num * other.den) - (self.den*other.num)
        obj.den = self.den * other.den
        return obj        
    
    def __neg__(self):
        """
        Negation operator (-)
        Returns a system with sign change
        """
        obj = linblk()
        obj.num = -self.num
        obj.den = self.den
        return obj
    
    def nf(self,other):
        """
        Negative feedback
        Use other system to give negative feedback
        """
        obj = linblk()
        obj.num = self.num * other.den
        obj.den = (self.den * other.den) + (self.num * other.num)
        return obj
        
    def pf(self,other):
        """
        Positive feedback
        Use other system to give positive feedback
        """    
        obj = linblk()
        obj.num = self.num * other.den
        obj.den = (self.den * other.den) - (self.num * other.num)
        return obj        
        
    def eval(self,x):
        """
        Evaluate the system on a point of the s plane
          x : Complex value
        """
        y = self.num(x)/self.den(x)
        return y
        
    # Evaluation at jw
    def weval(self,w):
        """
        Evaluate the system on a point on the imaginary axis
          w : Value on the j axis (Real value)
        """
        x = w*1j
        y = self.num(x)/self.den(x)
        return y
        
    def bode(self,f):
        """
        Generates the bode plot vector results
          f : Frequency vector
        Returns:  
            mag : Magnitude vector (dB)
          phase : Phase vector (deg)
        """    
        w = f2w(f)
        res = self.weval(w)
        mag = dB(np.absolute(res))
        phase = np.angle(res,deg=True)
        return mag, phase
        
    def freqR(self,f):
        """
        Generates the frequency response vector results
          f : Frequency vector
        Returns:  
          res : Freuency response (complex)
        """    
        w = f2w(f)
        res = self.weval(w)
        return res       

    def autoRange(self):
        """
        Creates a frequency vector that includes all poles and zeros
        Returns the frequency vector
        """
        min,max = self.wRange()
        min = (min/10)/(2*np.pi)
        max = (max*10)/(2*np.pi)    
        fv = frange(min,max)
        return fv    
        
    def showBode(self,f=None,title='Bode Plot'):
        """
        Shows the bode plot of the system
          f : Frequency vector
        """        
        if f is None: f=self.autoRange()
        mag, phase = self.bode(f)
        drawBodePlot(f,mag,phase,title)
        
    def addBode(self,f=None,label=None):
        """
        Add the bode plot to the current image
          f : Frequency vector
        Use showBodePlot() to see the final image  
        """
        if f is None: f=self.autoRange() 
        mag, phase = self.bode(f)
        addBodePlot(f,mag,phase,label=label)    
            
    def poles(self):
        """
        Get the list of poles of the system
        """
        return self.den.roots()
        
    def zeros(self):
        """
        Get the list of zeros of the system
        """
        return self.num.roots()

    def gain(self):
        """
        Get the gain of the system
        We define gain as the quotient of the first coef (in increase order)
        of num and den that is not zero
        """
        for c in self.num.coef:
            if c!= 0.0:
                cnum = c
                break
        for c in self.den.coef:
            if c!= 0.0:
                cden = c
                break                
        gain = cnum/cden
        return gain        
        
    def addPZplot(self,label=None,color='blue'):
        """
        Add the pole-zero plot to the current image
        Use showPoleZeroPlot() to see the final image
          label : Label for the set (optional)
          color : Color for the set (Defaults to 'blue')
        """
        poles = self.poles()
        zeros = self.zeros()
        addPoleZeroPlot(poles,zeros,label=label,color=color)
        
    def showPZplot(self,title='',color='blue'): 
        """
        Add the pole-zero plot to the current image
          title : Plot title (optional)
          color : Simbol colors (Defaults to 'blue')
        """    
        self.addPZplot(color=color)
        showPoleZeroPlot(title)
        
    def printPZ(self):
        """
        Show poles and zeros on screen
        """
        poles = self.poles()
        zeros = self.zeros()
        gain = self.gain()
        print('Poles : ' + str(poles))
        print('Zeros : ' + str(zeros))
        print('Gain : '  + str(gain))
        
    def clean(self,ratio=1000.0):
        """
        Eliminates poles and zeros that cancel each other
        A pole and a zero are considered equal if their distance
        is lower than 1/ratio its magnitude
           ratio : Ratio to cancel PZ (default = 1000)
        Return a new object   
        """
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
        """
        Returns the range in the complex domain that includes
        all the poles and zeros
        """
        li = np.array(list(self.poles()[:]) + list(self.zeros()[:]))
        ReMin = np.amin(np.real(li))
        ReMax = np.amax(np.real(li))
        ImMin = np.amin(np.imag(li))
        ImMax = np.amax(np.imag(li))
        return ReMin + ImMin*1j , ReMax + ImMax*1j
        
    def wRange(self):      
        """
        Returns the angula frequency range that includes all poles and zeros
        that are not zero
        """        
        li = np.array(list(self.poles()[:]) + list(self.zeros()[:]))
        if len(li) == 0: return None
        li = np.abs(li)
        li = [x for x in li if x!=0.0]
        return min(li),max(li)
                
    def plotSplane(self,zmax=100.0):
        """
        Plots the magnitude of the evaluation of the
        system inside the s plane in dB(magnitude)
        Optional parameter:
        zmax : Maximum in Z axis (dB) (Defaults to 100 dB)
        """
        min,max = self.pzRange()
        fig = _plotStart()
        ax = fig.gca(projection='3d')
        
        X = np.linspace(2.0*np.real(min),0.0,100)
        Y = np.linspace(2.0*np.imag(min),2.0*np.imag(max),100)
        X, Y = np.meshgrid(X, Y)
        Z = np.clip(dB(np.absolute(self.eval(X + 1j*Y))),0.0,zmax)
        surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm, 
                       linewidth=0, antialiased=False)
 
        if colaboratory:# For colaboratory
            ax.set_facecolor("white") 
        ax.xaxis.pane.set_edgecolor('black')
        ax.yaxis.pane.set_edgecolor('black')
        ax.zaxis.pane.set_edgecolor('black')
        ax.xaxis.pane.fill = True
        ax.yaxis.pane.fill = True
        ax.zaxis.pane.fill = True
    
        # Set pane colors
        ax.xaxis.set_pane_color((0.8, 0.9, 0.9, 1.0))
        ax.yaxis.set_pane_color((0.9, 0.8, 0.9, 1.0))
        ax.zaxis.set_pane_color((0.9, 0.9, 0.8, 1.0))
       
        # Improve ticks and axes legend
        [t.set_va('center') for t in ax.get_yticklabels()]
        [t.set_ha('left') for t in ax.get_yticklabels()]
        [t.set_va('center') for t in ax.get_xticklabels()]
        [t.set_ha('right') for t in ax.get_xticklabels()]
        [t.set_va('center') for t in ax.get_zticklabels()]
        [t.set_ha('left') for t in ax.get_zticklabels()]
    
        ax.contour(X, Y, Z)
          
        ax.view_init(30, 30)
   
        ax.set_xlabel('Real')
        ax.set_ylabel('Imaginary')
        ax.set_zlabel('dB')
    
        _subplotEnd(ax)
        _plotEnd()
        
    def tResponse(self,vt,ts=None,fs=None):
        if fs == None:
            if ts == None:
                raise LinearEx('ts or fs must be provided')
            else:
                fs = 1/ts
                
        # Convert to frequency domain        
        data = np.fft.fft(vt)
        
        # Create frequency vector
        ldata = int(len(data)/2)
        wv = np.pi*fs*np.array(list(range(0,ldata)) + [x - ldata for x in range(0,ldata)])/ldata
        
        # Calculate response  
        resp = self.weval(wv)
        
        data = data * resp
        # Return to time domain
        result = np.real(np.fft.ifft(data))
        return result        
        
'''  
The bode3Dmag and bode3Dphase are currently deprecated as they are useful
  
    def bode3Dmag(self,fmax=None,zmax=100.0):
        """
        Plots the magnitude of the evaluation of the
        system inside the s plane in dB(magnitude)
        The plot uses log10 of frequency in the axes
           fmax : Maximum frequency
           zmax : Maximum in Z axis (dB)
        """
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
        ax.view_init(30, 30)

        plt.show()     

    def bode3Dphase(self,fmax=None):
        """
        Plots the phase of the evaluation of the
        system inside the s plane in dB(magnitude)
        The plot uses log10 of frequency in the axes
           fmax : Maximum frequency
           zmax : Maximum in Z axis (dB)
        """
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
        ax.view_init(30, 30)
        
        plt.show()         
'''        
        
################# HELPER SYSTEM FUNCTIONS ########################

def linFromPZ(poles=[],zeros=[],gain=1.0,wgain=0,ingain=None):
    """
    @linFromPZ
    linFromPZ(poles,zeros,gain,ingain)
    Creates a system from the list of poles and zeros

    Parameters:
      poles : List of poles
      zeros : List of zeros 

    Gain can be defined as:
      gain : Gain defined as the quotient of first num/den coef.
     wgain : Frequency where gain is defined 
     igain : Gain defined at infinite freq. in high pass 

    Returns a linblk object 
    """        
    # Create new block
    s = linblk()
    s.den=P.Polynomial(P.polyfromroots(poles))
    s.num=P.Polynomial(P.polyfromroots(zeros))
    # Add gain  
    if ingain == None:
        #curr = s.gain()
        curr=np.abs(s.eval(1j*wgain))
        s.num = s.num * gain / curr
    else:
        curr = s.num.coef[-1] / s.den.coef[-1]
        s.num = s.num * gain /curr
    return s   

def poleZeroPolar(mag,angle):
    """
    @poleZeroPolar
    poleZeroPolar(mag,angle)
    Generates a list of two poles or zeros from
    their magnitude and angle on the s plane

    Required parameters:
       mag : magnitude
     angle : angle of one pole or zero (0 to 90)
  
    Returns a list of two poles or zeros
    """	
    radians = angle * np.pi / 180.0
    p1 = -mag*np.cos(radians) + 1j*mag*np.sin(radians)
    p2 = -mag*np.cos(radians) - 1j*mag*np.sin(radians)
    return [p1,p2]
    
    
            
####################### PREDEFINED SYSTEMS ###################

"""
@lin1
lin1
Identity system H(s)=1
"""

# Linear indentiy system H(s) = 1
lin1 = linblk()


 
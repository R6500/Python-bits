'''
Basic Calc module
Includes funtions related to 
   Show parameters
   Draw curves
   Some electrical calculations

History:
   6/10/2017 : First version
   3/03/2018 : Added compatibility with Python 3
   5/03/2018 : Added "grid" parameter to plot functions
   9/03/2018 : Added plotHist
  13/03/2018 : Added version string 
  14/03/2018 : Added f2s and decimal formatting in printVar and printR
'''

# Python 2.7 compatibility
from __future__ import print_function
from __future__ import division

import numpy as np               # Import numpy for numeric calculations
import pylab as pl               # Import pylab
import matplotlib.pyplot as plt

version = '13/3/2018'

#########################################################################################
# PRINTING CODE                                                                         #
#########################################################################################

def f2s(v):
    """
    f2s (float2string)
    Takes one float value and converts it to string
    If greater or equal than 1000, uses two decimal places
    If greater than one, uses three decimal places
    if less than one, uses three significant decimal places
    """
    a = abs(v)
    if a <1:
        ndec = 3-np.log10(a)
        return ('{0:.%df}' % ndec).format(v)
    if a < 1000:
        return "{0:.3f}".format(v)
    # Default option  
    return "{0:.2f}".format(v)

def printVar(name,value,unit=""):
    """
    Print a variable name, value and units
    """
    print(name + " = " + f2s(value) + " " + unit)
    

def printR(name,value):
    """
    Print a resistor value
    -1.0 means infinite
    """
    if value == -1.0:
        print(name + " = Open")
    else:        
        print(name + " = " + f2s(value) + " Ohm")
           
def printTitle(title):
    """
    Print a title with blank lines after and before
    """ 
    print()
    print(title)
    print()

#########################################################################################
# DRAWING CODE                                                                          #
#########################################################################################

'''
Plot two magnitudes using log if needed
Used by the plot11, plot1n and plotnn commands
'''
def plotXY(x,y,label="",logx=False,logy=False):
    if not logx and not logy:
        pl.plot(x,y,label=label)
        return
    if logx and not logy:
        pl.semilogx(x,y,label=label)
        return
    if logy and not logx:
        pl.semilogy(x,y,label=label)
        return
    if logx and logy:
        pl.loglog(x,y,label=label)
        return
        
'''
@plot11@
plot11(x,y,title,xt,yt,logx,logy,grid)
Plot one input against one output
If x is an empty list [], a sequence number
will be used for the x axis

Required parameters:
  x : Horizontal vector
  y : Vertical vector
  
Optional parameters:
  title : Plot title (Defaults to none)
     xt : Label for x axis (Defaults to none)
     yt : Label for y axis (Defaults to none)
   logx : Use logarithmic x axis (Defaults to False)
   logy : Use logarithmic x axis (Defaults to False)
   grid : Draw a grid (Defaults to true)

Returns nothing
'''
def plot11(x,y,title="",xt="",yt="",logx=False,logy=False,grid=True):
     
    # Generate sequence if x is not provided
    if x == []:
        x = np.arange(0,len(y))
       
    plt.figure(facecolor="white")   # White border
    plotXY(x,y,logx=logx,logy=logy)
    pl.xlabel(xt)
    pl.ylabel(yt)
    pl.title(title)
    if grid:
        pl.grid()
    pl.show()
    pl.close()
    
'''
@plot1n@
plot1n(x,ylist,title,xt,yt,labels,location,logx,logy,grid)
Plot one input against several outputs
If x is an empty list [], a sequence number
will be used for the x axis

Required parameters:
      x : Horizontal vector
  ylist : List of vertical vectors
  
Optional parameters:
    title : Plot title (Defaults to none)
       xt : Label for x axis (Defaults to none)
       yt : Label for y axis (Defaults to none)
   labels : List of legend labels (Defaults to none)
 location : Location for legend (Defaults to 'best')
     logx : Use logarithmic x axis (Defaults to False)
     logy : Use logarithmic x axis (Defaults to False)
     grid : Draw a grid (Defaults to true)

Returns nothing
'''
def plot1n(x,ylist,title="",xt="",yt="",labels=[],location='best',logx=False,logy=False,grid=True):

    # Generate sequence is x is not provided
    if x == []:
        x = np.arange(0,len(ylist[0]))        
        
    plt.figure(facecolor="white")   # White border
    if labels == []:
        for y in ylist:
            plotXY(x,y,logx=logx,logy=logy)
            #pl.plot(x,y)
    else:
        for y,lbl in zip(ylist,labels):
            plotXY(x,y,label=lbl,logx=logx,logy=logy)
            #pl.plot(x,y,label=lbl)
    pl.xlabel(xt)
    pl.ylabel(yt)
    pl.title(title)
    if grid:
        pl.grid()
    if not labels == []:
        pl.legend(loc=location)
    pl.show() 
    pl.close()    
  
'''
@plotnn@
plotnn(xlist,ylist,title,xt,yt,labels,location,logx,logy,grid)
Plot several curves with different inputs and outputs

Required parameters:
  xlist : List of horizontal vector
  ylist : List of vertical vectors
  
Optional parameters:
    title : Plot title (Defaults to none)
       xt : Label for x axis (Defaults to none)
       yt : Label for y axis (Defaults to none)
   labels : List of legend labels (Defaults to none)
 location : Location for legend (Defaults to 'best')
     logx : Use logarithmic x axis (Defaults to False)
     logy : Use logarithmic x axis (Defaults to False)
     grid : Draw a grid (Defaults to true)

Returns nothing
'''
def plotnn(xlist,ylist,title="",xt="",yt="",labels=[],location='best',logx=False,logy=False,grid=False):

    plt.figure(facecolor="white")   # White border
    if labels == []:
        for x,y in zip(xlist,ylist):
            plotXY(x,y,logx=logx,logy=logy)
    else:
        for x,y,lbl in zip(xlist,ylist,labels):
            plotXY(x,y,label=lbl,logx=logx,logy=logy)
    pl.xlabel(xt)
    pl.ylabel(yt)
    pl.title(title)
    pl.grid()
    if not labels == []:
        pl.legend(loc=location)
    pl.show()  
    pl.close()  
  
'''
@plotHist@
plotHist(v,bins=10,title="",xt="",yt="",grid)
Plot an histagram from provided data

Required parameters:
  v : Data vector
  
Optional parameters:
     bins : Number of bins for the histogram (Defaults to 10)
    title : Plot title (Defaults to none)
       xt : Label for x axis (Defaults to none)
       yt : Label for y axis (Defaults to none)
     grid : Use grid (Default to True)     
     
Returns nothing   
'''    
def plotHist(v,bins=10,title="",xt="",yt="",grid=True):
      
    plt.figure(facecolor="white")   # White border
    
    plt.hist(v,bins)
    
    pl.xlabel(xt)
    pl.ylabel(yt)
    pl.title(title)
    if grid:
        pl.grid()
    pl.show()
    pl.close()
   
  
#########################################################################################
# DIFFERENTIAL EQUATIONS CODE                                                           #
#########################################################################################      
    
'''
Calculates the Euler solution of a dynamical system
System is defined as:
 dx/dt = f(x,t)
Parameters:
   x : State variable or vector 
   t : Current time
   f : function f(x,t)
   h : time step interval
Returns:
   xNew : New value of x at time t+h
'''
def euler(x, t, f, h):
    xNew = x + h * f(x,t)
    return xNew
    
'''
Calculates the 4th order Runge-Kutta approximation for a dynamical system
System is defined as:
 dx/dt = f(x,t)
Parameters:
   x : State variable or vector 
   t : Current time
   f : function f(x,t)
   h : time step interval
Returns:
   xNew : New value of x at time t+h
'''    
def rk4(x, t, f, h): 
    k1 = h * f(x,t)
    k2 = h * f(x + k1/2.0 , t + h/2.0)
    k3 = h * f(x + k2/2.0 , t + h/2.0)
    k4 = h * f(x + k3     , t + h)
    xNew = x + ( k1/6 + k2/3 + k3/3 + k4/6 )
    return xNew
    
#########################################################################################
# GEOMETRIC CODE                                                                        #
#########################################################################################     

'''
Normalize a line that passes thorugh two points
 Generates line as y = Ax + B
Parameters:
  x1 : First point x
  y1 : First point y
  x2 : Second point x
  y2 : Second point y
Return:
  A : Slope
  B : Zero cross  
'''
def normalizeLine(x1,y1,x2,y2):
    a = (y2*1.0 - y1*1.0)/(x2*1.0 - x1*1.0)
    b = (y1*1.0 - a*x1)
    return a,b
    
#########################################################################################
# DC ELECTRONICS CODE                                                                   #
#########################################################################################   

'''
Obtain Vth and Rth from a circuit
(Va)---<Ra>---(Out)----<Rb>---(Vb)
Returns a vector with:
  Vth, Rth
'''
def divider2thevenin(va,vb,ra,rb):
    raa=ra*1.0
    rbb=rb*1.0
    vth=va+(vb-va)*raa/(raa+rbb)
    rth=raa*rbb/(raa+rbb)
    return vth,rth

'''
Obtain a divider from the thevenin equivalent
(Va)---<Ra>---(Out)----<Rb>---(Vb)
Returns a vector with:
  Ra,Rb
A -1.0 value means infinite resistance  
'''    
def thevenin2divider(va,vb,vth,rth):
    vaa=va*1.0
    vbb=vb*1.0
    vthh=vth*1.0
    rthh=rth*1.0
    
    if vaa-vthh == 0.0:
        rb = -1.0
    else:    
        rb=(rthh*vthh-vbb*rthh+(vaa-vthh)*rthh)/(vaa-vthh) 
    
    if vthh-vbb == 0.0:
        ra = -1.0
    else:    
        ra=rb*(vaa-vthh)/(vthh-vbb)
        
    return ra,rb
    
'''
Non inverting amplifier ----------------------------------------------------
Obtain the values of the function:
   Vo = A*Vi + B 
From the components:
   Vr : Reference voltage
   Rs : Series resistances with Vr
   Rf : Feedback resistance
Returns:
    A : Proportional constant
    B : Zero cross constant
'''    
def niAmplifier(vr,rs,rf):
    vrr=vr*1.0
    rss=rs*1.0
    rff=rf*1.0
    A=1+rff/rss
    B=-vr*rff/rss
    return A,B
    
'''
Obtain the components from the function
Parameters:
  A  : Proportional constant
  B  : Zero cross constant
  Rs : Series resistance 
Returns: 
  Rf : Feedback resistance
  vr : Reference voltage 
'''   
def niAmplifierR(a,b,rs):
    aa=a*1.0
    bb=b*1.0
    rss=rs*1.0
    rf=rss*(aa-1)
    vr=-bb*rss/rf
    return rf,vr
    

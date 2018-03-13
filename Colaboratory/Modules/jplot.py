'''
jplot
Basic plot module for Colaboratory (Jupyter)
Compatible with Python 2.7 and 3.x
Includes funtions related for drawing curves
 
History:
  11/03/2018 : First version
  13/03/2018 : Add version string
'''

from __future__ import print_function

import numpy as np               # Import numpy for numeric calculations
import pylab as pl               # Import pylab
import matplotlib.pyplot as plt

# Version string
version = '13/3/2018'

#########################################################################################
# DRAWING CODE                                                                          #
#########################################################################################

# Internal functions ####################################################################

'''
_plotStart
Starts a new plot
Paramenters:
  title : Title of the plot (defaults to none)
  xt    : x label of the plot (defaults to none)
  yt    : y label of the plot (defaults to none)
  grid  : Determines if there is grid (defaults to True)
Returns:
  fig : Figure object
  ax  : Axes object  
'''
def _plotStart(title="",xt="",yt="",grid=True):
    fig=plt.figure()
    ax = fig.add_subplot(111)
    ax.set_facecolor("white")
    ax.set_title(title)
    ax.set_xlabel(xt)
    ax.set_ylabel(yt)
    if (grid):
        plt.grid(True,color="lightgrey",linestyle='--')
    return fig,ax

'''
_plotEnd
Ends a previously started plot
Paramenters:
  fig      : Figure object obtained from plotStart
  ax       : Axes obtained from plotStart
  labels   : List of labels for the curves (defaults to none)
  location : Location for labels (defaults to 'best')
Returns nothing  
'''    
def _plotEnd(fig,ax,labels=[],location='best'):
    if not labels == []:
        pl.legend(loc=location)
    xmin, xmax = plt.xlim()
    ymin, ymax = plt.ylim()
    ax.axvline(x=xmin,linewidth=2, color='black')
    ax.axvline(x=xmax,linewidth=2, color='black')
    ax.axhline(y=ymin,linewidth=2, color='black')
    ax.axhline(y=ymax,linewidth=2, color='black')
    plt.show()

'''
_plotXY
Plot two magnitudes using log if needed
Used by the plot11, plot1n and plotnn commands
'''
def _plotXY(x,y,label="",logx=False,logy=False):
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
     
# Public functions ######################################################################
     
'''
@plot11@
plot11(x,y,title,xt,yt,logx,logy)
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
   grid : Use grid (Default to True)

Returns nothing     
'''
def plot11(x,y,title="",xt="",yt="",logx=False,logy=False,grid=True):

    # Generate sequence if x is not provided
    if x == []:
        x = np.arange(0,len(y))
       
    fig,ax = _plotStart(title,xt,yt,grid)

    _plotXY(x,y,logx=logx,logy=logy)
    
    _plotEnd(fig,ax)
    
'''
@plot1n@
plot1n(x,ylist,title,xt,yt,labels,location,logx,logy)
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
     grid : Use grid (Default to True)     

Returns nothing    
'''
def plot1n(x,ylist,title="",xt="",yt="",labels=[],location='best',logx=False,logy=False,grid=True):

    # Generate sequence is x is not provided
    if x == []:
        x = np.arange(0,len(ylist[0]))        
        
    fig,ax=_plotStart(title,xt,yt,grid)
    
    if labels == []:
        for y in ylist:
            _plotXY(x,y,logx=logx,logy=logy)
    else:
        for y,lbl in zip(ylist,labels):
            _plotXY(x,y,label=lbl,logx=logx,logy=logy)

    _plotEnd(fig,ax,labels,location)   
  
'''
@plotnn@
plotnn(xlist,ylist,title,xt,yt,labels,location,logx,logy)
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
     grid : Use grid (Default to True)     

Returns nothing    
'''
def plotnn(xlist,ylist,title="",xt="",yt="",labels=[],location='best',logx=False,logy=False,grid=True):

    fig,ax=_plotStart(title,xt,yt,grid)
    
    if labels == []:
        for x,y in zip(xlist,ylist):
            _plotXY(x,y,logx=logx,logy=logy)
    else:
        for x,y,lbl in zip(xlist,ylist,labels):
            _plotXY(x,y,label=lbl,logx=logx,logy=logy)
            
    _plotEnd(fig,ax,labels,location)  
    
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

    fig,ax = _plotStart(title,xt,yt,grid)

    plt.hist(v,bins)
    
    _plotEnd(fig,ax)    
    

    

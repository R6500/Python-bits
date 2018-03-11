'''
mmVars.py
Module to work with variables defined by maximum, minimum and typical values

ToDo:
  [ ] Add sqrt function

History:
   9/03/2018 : First version
  10/03/2018 : Improvement of doMontecarlo
               sq() now is not member but external function
               Added exp() log() ipow(b,e) sin() cos()
'''
# Python 2.7 compatibility
from __future__ import print_function
from __future__ import division

import random
import numpy as np
import functools

# Exception code
class mmEx(Exception):
    # Exception Methods ----------------------------------
    def __init__(self, msg=""):
        self.msg = msg
        print("\n** MM Exception")
        print('** ' + msg)
        print("\n")    
        
    def __str__(self):
        return repr(self.code)

'''
mmVar Class definition
 
Constuctors
   mmVar(a,b)        Variable bound between a and b
   mmVar(a,b,c)      Variable bound between a and b with c typical value
   mmVar(a,tol=vTol) Variable bound between a*(1-tol) and b*(1+tol)
   mmVar(a)          Constan variable with value a
Additional parameters:
   ns                 Treats distribution as normal with ns sigmas in max,min
  

Normal mode: Max and Min values are propagated
              A variable can only be used one time if unique is set
Constant mode: Only val property is propagated
               val is set in special methods
                  .typical() sets val = typ
'''
 
class mmVar:
    # CONSTRUCTOR ###################################
    
    def __init__(self,a,b=None,typ=None,tol=None,ns=0):
        # State memeber data
        self.val=None       # Current value of variable
        self.unique=False   # Unique variable can only be used once
        self.used=False     # Variable already used if unique
        self.ns=ns          # Number of sigmas if normal
        # max, min, typ member data
        if b==None:
            # No b value is given
            if tol==None:
                # No tolerance is given
                self.max=a
                self.min=a
                self.typ=a
                return
            else:
                # Tolerance is given
                self.typ=a
                a1 = a*(1.0+tol)
                a2 = a*(1.0-tol) 
                self.max=max(a1,a2)
                self.min=min(a1,a2)
        else:     
            # b value is given
            if tol != None:
                raise mmEx("Ilegal use of tol argument")
           
            self.max=max(a,b)
            self.min=min(a,b)
            # Check is typical is between min and max
            if typ == None:
                if ns != 0:
                    # In normal distribution
                    typ = (self.max+self.min)/2
            else: 
                if typ < self.min or typ > self.max:
                    raise mmEx("Typical value out of bounds")    
            self.typ=typ         

    # INTERNAL METHODS ###################################
    
    def _n_mode(self):
        # Internal use
        # Indicates if we are operating in normal mode
        # and checks the double usage
        if self.val==None:
            # Normal mode
            if self.used:
                raise mmEx('Variable used two times')
            else:
                if self.unique:
                    self.used = True
                return True
        else:
            # Constant value mode
            return False
          
    def _get_values(self):
        # Internal use
        # Get current values
        if self._n_mode():
            return self.max,self.min,self.typ
        else:
            return self.val,self.val,self.val
          
    def __str__(self):
        # String that represents the value (max:typ:min)
        if self.val != None:
            return str(self.val)
        if self.max == self.min:
            return str(self.max)
        else:  
            return '('+str(self.max)+':'+str(self.typ)+':'+str(self.min)+')'
        
    # ARITHMETIC OPERATORS #################################     
        
    def __add__(self,other):
        # Adds two values (other can be mmVar or number) '+'
        
        # Get self values
        ma1,mi1,ty1 = self._get_values()
        
        # Get other values
        if isinstance(other,mmVar):
            ma2,mi2,ty2=other._get_values()
        else:
            ma2=other
            mi2=other
            ty2=other
            
        # Calculate limits    
        ma1=ma1+ma2
        mi1=mi1+mi2            
            
        # Check if limits are equal
        if ma1 == mi1:
            return ty1            
            
        # Check typical for none    
        if ty1 == None or ty2 == None:
            ty1 = None
        else:
            ty1 = ty1 + ty2    
            
        # Return new variable
        mm = mmVar(ma1,mi1,ty1)
        return mm
          
    def __radd__(self,other):
        # Implements other+self when other is not mmVar '+'
        
        # Get self values
        ma1,mi1,ty1 = self._get_values()
        
        # Calculate limits
        ma2=other+ma1
        mi2=other+mi1
        
        # Check if limits are equal    
        if ma2 == mi2:
            return ma1
        
        # Check self typical for none
        if self.typ == None:
            ty2 = None
        else:
            ty2 = other+self.typ
        
        # Return new variable
        mm = mmVar(ma2,mi2,ty2)
        return mm          
          
    def __neg__(self):
        # Changes sign
        ma1,mi1,ty1 = self._get_values()
        
        # New limits
        ma1 = -ma1
        mi1 = -mi1
        
        # Check if limits are equal
        if ma1 == mi1:
            return ma1

        # Check typical value  
        if ty1 != None:
            ty1 = -ty1
        
        # Return new variable
        mm = mmVar(ma1,mi1,ty1)
        return mm 
                  
    def __sub__(self,other):
        # Substracts two values (other can be mmVar or number) '-'
        
        # Get self values
        ma1,mi1,ty1 = self._get_values()
        
        # Get other instance values
        if isinstance(other,mmVar):
            ma2,mi2,ty2=other._get_values()
        else:
            ma2=other
            mi2=other
            ty2=other
            
        # New limits   
        ma1=ma1-mi2
        mi1=mi1-ma2
        
        # Check if limits are equal
        if ma1 == mi1:
            return ma1
        
        # Check typical for none    
        if ty1 == None or ty2 == None:
            ty1 = None
        else:
            ty1 = ty1 - ty2    
        
        # Return new variable
        mm = mmVar(ma1,mi1,ty1)
        return mm          
          
    def __rsub__(self,other):
        # Implements other-self when other is not mmVar '-'
        
        # Get self values
        ma1,mi1,ty1 = self._get_values()
        
        # Calculate limits
        ma2=other-mi1
        mi2=other-ma1
        
        # Check if limits are equal
        if ma2 == mi2:
            return ma2
          
        # Check self typical forn none
        if self.typ == None:
            ty2 = None
        else:
            ty2 = other-self.typ
            
        # Return new variable
        mm = mmVar(ma2,mi2,ty2)
        return mm
        
    def __mul__(self,other):
        # Multiplies two values (other can be mmVar or number) '*'
        
        # Get self values
        ma1,mi1,ty1 = self._get_values()
        
        # Get other valus
        if isinstance(other,mmVar):
            ma2,mi2,ty2=other._get_values()
        else:
            ma2=other
            mi2=other
            ty2=other
            
        # Calculate limits    
        v=ma1*ma2  
        ma3=v
        mi3=v
        
        v=ma1*mi2
        ma3=max(ma3,v)
        mi3=min(mi3,v)
        
        v=mi1*ma2
        ma3=max(ma3,v)
        mi3=min(mi3,v)
        
        v=mi1*mi2
        ma3=max(ma3,v)
        mi3=min(mi3,v) 
        
        # Check if limits are equal
        if ma3 == mi3:
            return ma3
          
        # Check typical for none
        if ty1 == None or ty2 == None:
            ty3 = None
        else:
            ty3 = ty1 * ty2
        
        # Return new variable
        mm = mmVar(ma3,mi3,ty3)
        return mm  
      
    def __rmul__(self,other):
        # Implements other*self when other is not mmVar '*'
        
        # Get self values
        ma1,mi1,ty1 = self._get_values()
        
        # Calculate limits    
        v=other*ma1  
        ma3=v
        mi3=v
        
        v=other*mi1
        ma3=max(ma3,v)
        mi3=min(mi3,v)
        
        # Check if limits are equal    
        if ma3 == mi3:
            return ma3
        
        # Check self typical for none
        if self.typ == None:
            ty3 = None
        else:
            ty3 = other*self.typ
        
        # Return new variable
        mm = mmVar(ma3,mi3,ty3)
        return mm
      
    def __truediv__(self,other):
        # Divides two values (other can be mmVar or number) '/'
        
        # Get self values
        ma1,mi1,ty1 = self._get_values()
        
        # Get other values
        if isinstance(other,mmVar):
            ma2,mi2,ty2=other._get_values()
        else:
            ma2=other
            mi2=other
            ty2=other
            
        # Check for zero division
        if ma2>0 and mi2<0:
            raise mmEx('Quotient range includes zero')
            
        # Calculate limits
        v=ma1/ma2  
        ma3=v
        mi3=v
        
        v=ma1/mi2
        ma3=max(ma3,v)
        mi3=min(mi3,v)
        
        v=mi1/ma2
        ma3=max(ma3,v)
        mi3=min(mi3,v)
        
        v=mi1/mi2
        ma3=max(ma3,v)
        mi3=min(mi3,v)  
        
        # Check if limits are equal    
        if ma3 == mi3:
            return ma3
        
        # Check typical for none
        if ty1 == None or ty2 == None:
            ty3 = None
        else:
            ty3 = ty1 / ty2
        
        # Return new variable
        mm = mmVar(ma3,mi3,ty3)
        return mm                
        
    def __rtruediv__(self,other):
        # Implements other/self when other is not mmVar '/'
        
        # Check for zero division
        if self.max>0 and self.min<0:
            raise mmEx('Quotient range includes zero')
        
        # Get self values
        ma1,mi1,ty1 = self._get_values()
        
        # Calculate limits    
        v=other/ma1  
        ma3=v
        mi3=v
        
        v=other/mi1
        ma3=max(ma3,v)
        mi3=min(mi3,v)
        
        # Check if limits are equal    
        if ma3 == mi3:
            return ma3
        
        # Check self typical for none
        if self.typ == None:
            ty3 = None
        else:
            ty3 = other/self.typ
        
        # Return new variable
        mm = mmVar(ma3,mi3,ty3)
        return mm
        
    # RELATIONAL OPERATORS #################################  
    
    def __eq__(self,other):
        # Check for equity '=='
        # ToDo : Consider if other is not mmVar
        
        # Get self values
        ma1,mi1,ty1 = self._get_values()
        
        # Get other values
        ma2,mi2,ty2 = other._get_values()
        
        # Check for equity
        if ma1 == ma2 and mi1 == mi2 and ty1 == ty2:
            return True
        else:
            return False
        
    # ACCES TO CONTENTS ####################################  
      
    def maximum(self):
        # Return the maximum
        return self.max
      
    def minimum(self):
        # Return the minimum
        return self.min
      
    def typical(self):
        # Return the typical value
        return self.typ
         
    # FROZEN VALUE ##########################################    
        
    def setTypical(self):
        # Set value to typical one 
        # Object won't be aleatory anymore
        if self.typ == None:
            raise mmEx('Undefined typical value')
        self.val=self.typ
        return self.val
            
    def montecarlo(self):
        # Set value unifor random between bounds
        range = self.max - self.min
        midpoint = (self.max+self.min)/2
        if self.ns == 0:
            #Uniform distribution 
            self.val = self.min + range*np.random.rand()
        else:
            #Normal distribution
            sigma = range/(2*self.ns)            
            self.val = np.random.normal(midpoint,sigma)
        return self.val
      
    # VARIABLE VALUE ########################################  
      
    def individual(self):
        # Sets object to be aleatory
        # and makes each variable individual so an exception
        # will be raised if used two times
        self.val=None
        self.used=False
        self.unique=True
          
    def generic(self):
        # Sets object to be aleatory
        # and makes each variable generic so no exception
        # will be raised if used two times      
        self.val=None
        self.used=False
        self.unique=False

# Helper functions  

def get_values(x):
    # Return maximum, minimum and typical if x is mmVAr
    # If not, return tuple (x,x,x)
    if isinstance(x,mmVar):
        # Get self values
        ma,mi,ty = x._get_values()
    else:
        ma = x
        mi = x
        ty = x    
    return ma,mi,ty        
      
        
# Mathematical functions

def sq(x):
    # Get x values
    ma1,mi1,ty1 = get_values(x)
        
    # Check if max = min
    if ma1 == mi1:
        return ma1*ma1
          
    # Check for zero in range
    if mi1 < 0 < ma1:
        mi2 = 0
        ma2 = max(ma1*ma1,mi1*mi1)
    else:
        mi2 = min(ma1*ma1,mi1*mi1)
        ma2 = max(ma1*ma1,mi1*mi1)
            
    # Check self typical for none
    if ty1 == None:
        ty2 = None
    else:
        ty2 = ty1*ty1
           
    # Return new variable
    mm = mmVar(ma2,mi2,ty2)
    return mm
      
def sqrt(x):
    # Get x values
    ma1,mi1,ty1 = get_values(x)
        
    # Check sign
    if mi1 < 0:
        raise mmEx('Function sqrt() can only operate with always positive numbers')    
        
    # Check if max = min
    if ma1 == mi1:
        return np.sqrt(ma1)
      
    # Calculate limits 
    ma3 = np.sqrt(ma1)
    mi3 = np.sqrt(mi1)
            
    # Check self typical for none
    if ty1 == None:
        ty3 = None
    else:
        ty3 = np.sqrt(ty1)
           
    # Return new variable
    mm = mmVar(ma3,mi3,ty3)
    return mm            
      
def exp(x):
    # Get x values
    ma1,mi1,ty1 = get_values(x)
        
    # Check if max = min
    if ma1 == mi1:
        return np.exp(ma1)
      
    # Calculate limits 
    ma3 = np.exp(ma1)
    mi3 = np.exp(mi1)
            
    # Check self typical for none
    if ty1 == None:
        ty3 = None
    else:
        ty3 = np.exp(ty1)
           
    # Return new variable
    mm = mmVar(ma3,mi3,ty3)
    return mm       
        
def log(x):
    # Get x values
    ma1,mi1,ty1 = get_values(x)
        
    # Check sign
    if mi1 <= 0:
        raise mmEx('Function sqrt() can only operate with always positive numbers')          
        
    # Check if max = min
    if ma1 == mi1:
        return np.log(ma1)
      
    # Calculate limits 
    ma3 = np.log(ma1)
    mi3 = np.log(mi1)
            
    # Check self typical for none
    if ty1 == None:
        ty3 = None
    else:
        ty3 = np.log(ty1)
           
    # Return new variable
    mm = mmVar(ma3,mi3,ty3)
    return mm          
        
def ipow(base,exp):
    '''
    Obtains base^exp
    Restrictions:
       exp must be integer positive
    ''' 
    # Check for zero
    if exp == 0:
        return 1
        
    # Check exp type
    if type(exp) != int:
        raise mmEx('Exponent should be integer')

    # Check exp sign
    if exp < 0:
        raise mmEx('Exponent should be positive or zero')     
        
    # Get base values
    ma1,mi1,ty1 = get_values(base)
        
    # Check if max = min
    if ma1 == mi1:
        return np.power(ma1,exp)
    
    # Basic solution
    val1 = np.power(ma1,exp)
    val2 = np.power(mi1,exp)
    mi3 = min(val1,val2)
    ma3 = max(val1,val2)
    
    # Special case for zero in range and even exponent
    if (exp//2 == exp/2) and (mi1 < 0 < ma1):
        mi3 = 0
    
    # Check self typical for none
    if ty1 == None:
        ty3 = None
    else:
        ty3 = np.power(ty1,exp)
           
    # Return new variable
    mm = mmVar(ma3,mi3,ty3)
    return mm        
        
def sin(x):
    # Get x values
    ma1,mi1,ty1 = get_values(x)
        
    # Check if max = min
    if ma1 == mi1:
        return np.sin(ma1)
          
    # Default monotonous solution      
    val1 = np.sin(ma1)
    val2 = np.sin(mi1)
    mi3 = min(val1,val2)
    ma3 = max(val1,val2)
    
    # Check for maximum in range
    n1 = np.ceil((mi1-np.pi/2)/(2*np.pi))
    n2 = np.floor((ma1-np.pi/2)/(2*np.pi)) 
    if n1 <= n2:
        ma3 = 1.0 # There is maximum
        
    # Check for minimum in range
    n1 = np.ceil((mi1-3*np.pi/2)/(2*np.pi))
    n2 = np.floor((ma1-3*np.pi/2)/(2*np.pi)) 
    if n1 <= n2:
        mi3 = -1.0 # There is minimum        
            
    # Check self typical for none
    if ty1 == None:
        ty3 = None
    else:
        ty3 = np.sin(ty1)
           
    # Return new variable
    mm = mmVar(ma3,mi3,ty3)
    return mm    

def cos(x):
    # Get x values
    ma1,mi1,ty1 = get_values(x)
        
    # Check if max = min
    if ma1 == mi1:
        return np.cos(ma1)
          
    # Default monotonous solution      
    val1 = np.cos(ma1)
    val2 = np.cos(mi1)
    mi3 = min(val1,val2)
    ma3 = max(val1,val2)
    
    # Check for maximum in range
    n1 = np.ceil(mi1/(2*np.pi))
    n2 = np.floor(ma1/(2*np.pi)) 
    if n1 <= n2:
        ma3 = 1.0 # There is maximum
        
    # Check for minimum in range
    n1 = np.ceil((mi1-np.pi)/(2*np.pi))
    n2 = np.floor((ma1-np.pi)/(2*np.pi)) 
    if n1 <= n2:
        mi3 = -1.0 # There is minimum  
            
    # Check self typical for none
    if ty1 == None:
        ty3 = None
    else:
        ty3 = np.cos(ty1)
           
    # Return new variable
    mm = mmVar(ma3,mi3,ty3)
    return mm        
        
# Functions to get a value instance from the mmVAr objects ########
        
def setTypical(*args):
    '''Sets all variable arguments as typical values
      Argumnents : numbers or mmVar objects
      Returns a tuple with the values
    '''  
    ret=[]
    for element in args:
        if isinstance(element,mmVar): 
           ret.append(element.setTypical())
        else:    
           ret.append(element)
    return tuple(ret)        
           
def montecarlo(*args):
    '''Sets all variable arguments as a montecarlo instances
      Argumnents : numbers or mmVar objects
      Returns a tuple with the values
    '''
    ret=[]
    for element in args:
        if isinstance(element,mmVar): 
           ret.append(element.montecarlo())
        else:    
           ret.append(element)
    return tuple(ret)          
  
# Functions to set mmVAr objects as variable in their range ############
  
def individual(*args):
    '''Sets all variable arguments as unique
      Arguments : list of mmVar objects
    '''
    for element in args:
        element.individual()  
  
def generic(*args):
    '''Sets all variable arguments as not unique
      Arguments : list of mmVar objects
    '''  
    for element in args:
        element.generic() 
        
# Functions to tests several cases

'''
def doMontecarlo(n,func,*vars):
    Performs several montecarlo executions
    Arguments:
      n     : Number of montecarlo runs
      func  : Function to evaluate with *vars arguments
      *vars : List of nnVars contained in the function
    Returns a list with all evaluations  
    
    ret = [] # Return list
    for i in range(n):              # For all montecarlo cases
        mVars = montecarlo(*vars)   # Calculate vars for this case
        value = func(*mVars)        # Obtain function value
        ret.append(value)           # Add result to return vector
    return ret                      # Return vector
'''    
  
# Montecarlo compare helper function  
def _monteCompare(a,b):
    return a[0]-b[0]
  
def doMontecarlo(n,func,*vars):
    '''Performs several montecarlo executions
    Arguments:
      n       : Number of montecarlo runs
      func    : Function to evaluate with *vars arguments
      *vars   : List of nnVars contained in the function
    Returns:
      vRes    : A sorted list of func values on each run
      vData   : A sorted list of elements. Each one is a list with:
                    Value of the function
                    Tuple of coordinates of the function
    '''
    vRet  = []                        # Return list
    vData = []                        # Data list
    for i in range(n):                # For all montecarlo cases
        mVars = montecarlo(*vars)  # Calculate vars for this case
        value = func(*mVars)          # Obtain function value
        vRet.append(value)            # Add resut to vRet
        subList = [value,mVars]    
        vData.append(subList)         # Add data to vData
       
    # Sort lists
    vRet.sort() 
    vData.sort(key=functools.cmp_to_key(_monteCompare));            
    return vRet,vData
       
def cumulative(v):
    '''
    Generates a cumulative function from a sorted vector of values
    Arguments:
      v : Input vector
    Returns:
      y : Cumulative values 
    '''
    y = []
    count = 0
    for value in v:
        count = count+1
        y.append(count)
    y = np.array(y)/count
    return y
     
def prob(v,a,b):
    '''
    Calculates the probability to have a value between min and max
    Paramenters:
      v : Sorted vector
      a : Limit 1
      b : Limit 2
    Returns the probability  
    '''   
    mi = min(a,b)
    ma = max(a,b)    
    total = 0
    count = 0    
    for element in v:
        total = total + 1
        if mi <= element <= ma:
            count = count + 1
    return count/total   
    
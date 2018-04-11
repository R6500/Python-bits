'''
units.py

Module to work with S.I. units

History:
   3/04/2018 : First version
   4/04/2018 : Addition of non S.I. units and Physics constants
   5/04/2018 : Modifications to work with numpy arrays
               Connection with sympy
   6/04/2018 : Connection with calc
   9/04/2018 : Units as text in make* functions
  10/04/2018 : Corrections in unitless and Hz 
  11/04/2018 : Addition of setSciForPrint
'''

# Python 2.7 compatibility
from __future__ import print_function
from __future__ import division

version = '11/04/2018'

# Basic imports
import numpy as np
import inspect

# Try to load sympy
try:		
    import sympy
except:
    sympy_imported = False
else:
    sympy_imported = True

# Try to load calc    
try:
    import calc
except:
    calc_imported = False
else:
    calc_imported = True    
    
# Try to load mmVars    
try:
    import mmVars as mm
except:
    mmVars_imported = False
else:
    mmVars_imported = True      

# Exception code ######################################################

class unitsEx(Exception):
    def __init__(self, msg=""):
        self.msg = msg
        print("\n** Units Exception")
        print('** ' + msg)
        print("\n")    

      
# Globals ############################################################      
      
# Number of base units  
nbase   = 7   

# Vector with no units
v_none  = np.array([0,0,0,0,0,0,0])

# Base unit names
v_names = ['m','kg','s','A','K','mol','cd']

# Indicate if we use sci for __str__
sci4str = False

# Number presentation code ###########################################

# This is the same code included in calc.py 

def f2s(v,nd=None):
    """
    f2s (float2string)
    Takes one float value and converts it to string
    If greater or equal than 1000, uses two decimal places
    If greater than one, uses three decimal places
    if less than one, uses three significant decimal places
    The optional parameter can fix the number of significant digits
    """
    # Base number of decimals
    a = abs(v)
    if nd == None:
        ndec = 3
        if (a>=1000): ndec = 2
        if (a<1): 
            if a!=0: ndec = int(np.floor(3-np.log10(a)))
    else:
        ndec = nd
        if (a<1):
            if a!=0: ndec = int(np.floor(nd-np.log10(a)))

    # Check for significance
    v2 = np.floor(v*10**ndec)/(10**ndec)
    for i in range(0,ndec):
        if np.floor(v2) == v2:
            ndec = i+1
            break
        v2 = v2*10.0    
    
    # Return string
    return ('{0:.%df}' % ndec).format(v)
   
def f2sci(v,unit='',nd=3,prefix=True,sep=''):
    """
    Takes one float and converts it to scientific notation
    Required parameters
       v : Number to convert
    Optional parameters
        unit : Unit to show
          nd : Number of decimal places (Default to 3) 
      prefix : Use standard prefixes for powers of 10 up to +/-18
         sep : Separator between prefix and unit (Defaults to none)
    """
    potH=['k','M','G','T','P','E']
    potL=['m','u','n','p','f','a']
    a = abs(v)
    ndec = int(np.floor(np.log10(a)))
    pot = int(np.floor(ndec/3))
    exp = 3*pot
    base = v/(10.0**exp)
    s = f2s(base,nd)
    if pot==0: 
        return s + ' ' + unit
      
    if (prefix):
        if 1 <= pot <=6:
            s = s + ' ' + potH[pot-1] + sep + unit
            return s
        if 1 <= -pot <=6:
            s = s + ' '+ potL[-pot-1] + sep + unit
            return s
    
    s = s + 'E' + ('{:+d}').format(exp) + ' ' + unit
    return s        
    
def _unitName(unit):
    """
    Special internal function for printVar
    """ 
    if isinstance(unit,uVar): 
        return unit.name 
    return unit 

def _usePrefix(unit,prefix):
    """
    Special internal function for printVar
    """
    if isinstance(unit,uVar): 
        if unit.complex:
            return False
        else:
            return prefix
    return prefix   

def _printUnit(unit):
    """
    Special internal function for printVar
    """ 
    if unit == '': 
        print()
        return
    print(' '+_unitName(unit))     
             
def printVar(name,value=None,unit='',sci=True,prefix=True,sep='',level=0):
    """
    Print a variable name, value and units
    Required parameters:
        name : Name of the variable
    Optional parameters:
       value : value of to show (Defaults to be obtained from globals)
        unit : units to use (Defaults to self ones)
         sci : use sci numeric format (Defaults to True)
      prefix : use powers of 10 prefixes (Defaults to True)
         sep : separator between prefix and units (Defaults to none)
    Internal use parameters:
       level : stack level of caller to inspect globals
    """
    # Try to evaluate variable if not given
    if value is None:
        value = _getVar(name,level=level+1)
    
    # Code if value is not an uVar object
    if not isinstance(value,uVar):
        # Special case for numpy arrays
        if isinstance(value,np.ndarray):
            print(name + ' = ' + str(value),end='')
            _printUnit(unit)
        if sci:
            prefix = _usePrefix(unit,prefix)
            print(name + " = " + f2sci(value,_unitName(unit),prefix=prefix,sep=sep))
        else:
            print(name + " = " + f2s(value) + " " + _unitName(unit))
        return

    # Code if value is a uVar object
    if unit != "" and not isinstance(unit,uVar):
        raise unitsEx('If value is an uVar object, unit shall be of the same kind')    
    if unit != "":
        value=value.convert(unit)
        
    if isinstance(value.value,np.ndarray):
        print(name + " = " + str(value)) 
        return
            
    if sci:
        print(name + " = " + value.sci(prefix=prefix,sep=sep))
    else:
        print(name + " = " + str(value))    

def printUnit(name,unit='',sci=True,prefix=True,sep=''):  
    """
    Special call to printVar without value
    """   
    printVar(name,value=None,unit=unit,sci=sci,prefix=prefix,sep=sep,level=1)    
    
def setSciForPrint(flag=True):
    global sci4str
    sci4str = flag

    
# uVar class #########################################################

class uVar:
  
    # Constructor -----------------------------------------------------
    
    def __init__(self,name,vector,value=1.0,scale=1.0):
        """
        uVar constructor
        uVar(name,vector,value=1.0)
        Creates a new uVar object
        Parameters:
          name   : Name of the units
          vector : Vector of base units exponents
          value  : Numeric value (defaults to 1.0)
          scale  : Scaling factor from S.I. units
        Returns a new uVar object
        """
        if len(vector)!=7:
            raise unitsEx('Constructor vector size must be seven')    
        self.vector = np.array(vector)  # Base unit powers
        self.value  = value             # Numerical value
        self.name   = name              # Name of the units
        self.complex = False            # No single name for units
        self.scale = scale              # Scaling factor for this unit
        
    # Copy object

    def copy(self):
        """
        Returns a copy of the current object
        """ 
        res = uVar(self.name,self.vector,self.value,self.scale)
        res.complex = self.complex  
        return res        
        
    # Get internal elements ----------------------------------------------------- 
        
    def get_value(self):
        """
        Returns the numeric value of the object
        """
        return self.value
      
    def get_vector(self):
        """
        Return the vector of base units exponents
        """
        return self.vector
      
    def get_name(self):
        """
        Return the name of the object units
        """
        return self.name  
    
    # Set internal elements -----------------------------------------------------
    
    def set_name(self,name,complex=False):
        """
        Set the name of the object units
        If complex is false (default) power of 10 prefixed could be used
        """
        self.name=name
        self.complex = complex
        
    def set_value(self,value):
        """
        Returns the numeric value of the object
        """
        self.value = value
        
    # Especial constructors  ----------------------------------------------------

    def operateValue(self,func):   
        """
        Execute a function on the value of the uVar object
        Returns a new object
        """
        new = self.copy()
        new.value = func(new.value)
        return new
        
    def newValue(self,value):
        """
        Sets a new value
        Returns a new object        
        """
        new = self.copy()
        new.value = value
        return new
        
    def newUnit(self):
        """
        Return the units of a uVar object as a new object
        """
        new = self.copy()
        new.value = 1
        return new
      
    # Private methods -----------------------------------------------------------
      
    def _construct_name_old(self): 
        """
        Private function
        Return a new complex name from the base units exponents
        Old version to be eliminated
        """
        first = True
        name = ''
        for i in range(0,nbase):
            if self.vector[i] != 0:
                if not first:
                    name = name + '*'
                first = False    
                name = name + v_names[i]
                if self.vector[i] != 1:
                    name = name + '^' + str(self.vector[i])
        return name  

    def _reconstruct(self,defaults=True):
        """
        Private function
        Reconstruct the own name from base units
        If defaults is True, will use defaults if available
        """
        # Remove the scaling
        self.value = self.value * self.scale
        self.scale = 1.0
        
        # Check if it targets a default unit
        if defaults:
            tup = tuple(self.vector)
            if tup in register:
                unit = register[tup]
                self.value = self.value/unit.scale
                self.name = unit.name
                self.complex = unit.complex
                return
        
        # Not complex by default
        self.complex = False
        
        # It is not a default unit
        name =''
        num = False
        den = False
        # Check if there is numerator and denominator
        for i in range(0,nbase):
            if self.vector[i]>0: num = True
            if self.vector[i]<0: den = True  
        # If there is no numerator            
        if not num:
            # No numerator and no denominator 
            if not den:
                self.name = ''
                self.complex = True # don't use prefixes
                return
            # No numerator but there is denominator                
            name += '1'
            self.complex = True    
        else:
            # There is numerator
            first = True
            nSubs = 0
            for i in range(0,nbase):
                exponent = self.vector[i] 
                if exponent == int(exponent): exponent = int(exponent)                
                if exponent>0:
                    if exponent > 1: self.complex = True
                    nSubs += 1
                    if not first:
                        name = name + '*'
                    first = False
                    name = name + v_names[i]
                    if self.vector[i] != 1:
                        name = name + '^' + str(exponent)
            if nSubs > 1: self.complex = True           
        if not den:
            self.name = name
            return
        name += '/' 
        self.complex = True        
        first = True
        for i in range(0,nbase): 
            exponent = self.vector[i]   
            if exponent == int(exponent): exponent = int(exponent)            
            if exponent<0:
                if not first:
                    name = name + '*'
                first = False
                name = name + v_names[i]
                if self.vector[i] != -1:
                    name = name + '^' + str(-exponent)  
        self.name = name            
        return                        
      
    # Generate unit from uVar ---------------------------------------------------

    def makeUnit(self,name,sci=False,reg=False):
        """
        Convert the self object in a new unit
        Parameters:
           name : Name of the unit
           sci  : Use sci prefixes on unit
           reg  : Register as default
        Returns itself
        """
        self.scale = self.scale*self.value
        self.value = 1.0
        self.name = name
        self.complex = not sci
        if reg:
            regUnit(self)
        return self
      
    # Unit conversion -----------------------------------------------------------

    def convert(self,other):
        """
        Convert to another compatible unit
        """ 
        if not self.check(other):
            raise unitsEx('Cannot convert to incompatible unit')
        name   = other.name
        value  = self.value*self.scale/other.scale 
        vector = self.vector
        scale = other.scale
        res = uVar(name,vector,value,scale)
        if other.complex: res.complex = True
        return res
           
    def convert2base(self):
        """
        Convert to base units of the S.I.
        """
        res = self.copy()
        res._reconstruct(False)
        return res
           
    # Logic checks -------------------------------------------------------------- 
      
    def is_none(self):
        """
        Returns True if object has no units
        """
        # Returns true if it has no units
        if np.array_equal(self.vector,v_none):
            return True
        else:
            return False
          
    def check(self,other):
        """
        Returns True if object has compatible units with other
        It can be used in assert
        assert object.check(unit)
        """
        if np.array_equal(self.vector,other.vector):
            return True
        return False             
        
    def same_units(self,other):
        """
        Returns True if object has same units as other
        """
        if not np.array_equal(self.vector,other.vector):
            return False
        if self.scale != other.scale:
            return False
        return True                 
                
    # Aritmetic operations -----------------------------------------------------       
        
    def __add__(self,other):
        """
        Overload of operator +
        new = self + other
        Raises exception is units are not the same
        Returns a new uVar object
        """
        # If other is uVar instance
        if isinstance(other,uVar):
            if not self.check(other):
                raise unitsEx('Incompatible units') 
            if self.same_units(other):
                value = self.value+other.value
                res = uVar(self.name,self.vector,value,self.scale)
                return res
            else:
                value = self.value*self.scale + other.value*other.scale
                res = uVar('?',self.vector,value)
                res._reconstruct()
                return res                

        # If other is not uVar instance        
        if not self.is_none():
            raise unitsEx('Cannot add dimensionless value')
        value = self.value*self.scale + other    
        return uVar('',self.vector,value)
          
    def __radd__(self,other):
        """
        Overload of operator + used in reverse
        new = other + self
        Returns a new uVar object
        """
        return self.__add__(other)
      
    def __neg__(self):
        """
        Overload of sign change -
        new = -self
        Returns a new uVar object
        """
        return uVar(self.name,self.vector,-self.value,self.scale)
        
    def __sub__(self,other):
        """
        Overload of substraction -
        new = self - other
        Returns a new uVar object
        """
        return self.__add__(-other)
      
    def __rsub__(self,other):
        """
        Overload of substraction - used in reverse
        new = other - self
        Returns a new uVar object
        """
        aux = -self
        return aux.__add__(other)
      
    def __mul__(self,other):
        """
        Overload of multiplication *
        new = self * other
        Returns a new uVar object
        """
        # If other is uVar instance
        if isinstance(other,uVar):
            value = self.value*other.value
            vector = self.vector+other.vector
            if self.is_none():
                name = other.name
                scale = other.scale
                res = uVar(name,vector,value,scale)
                res.complex = other.complex
                return res
            if other.is_none():
                name = self.name
                scale = self.scale
                res = uVar(name,vector,value,scale)
                res.complex = self.complex
                return res
             
            value = value*self.scale*other.scale
            res = uVar('?',vector,value)
            res._reconstruct()
            return res            
                
        # If other is noy uVar instance
        value  = self.value*other
        vector = self.vector
        name   = self.name
        scale  = self.scale
        res = uVar(name,vector,value,scale)
        res.complex = self.complex
        return res
            
    def __rmul__(self,other):
        """
        Overload of multiplication * used in reverse
        new = other * self
        Returns a new uVar object
        """
        return self.__mul__(other) 
      
    def __truediv__(self,other):
        """
        Overload of division /
        new = self/other
        Returns a new uVar object
        """
        # If other is uVar instance
        if isinstance(other,uVar):
            vector = self.vector-other.vector
            if self.is_none():
                value = self.value*self.scale/(other.value*other.scale)
                res = uVar('?',vector,value)
                res._reconstruct()
                return res
            if other.is_none():
                value = self.value/other.value
                name = self.name
                scale = self.scale
                res = uVar(name,vector,value,scale)
                res.complex = self.complex
                return res
             
            value = self.value*self.scale/(other.value*other.scale)
            res = uVar('?',vector,value)
            res._reconstruct()
            return res            
                
        # If other is not uVar instance
        value  = self.value/other
        vector = self.vector
        name   = self.name
        scale  = self.scale
        res = uVar(name,vector,value,scale)
        res.complex = self.complex
        return res
      
    def __rtruediv__(self,other):
        """
        Overload of division / used in reverse
        new = other/self
        Returns a new uVar object
        """
        value  = other/(self.value*self.scale)
        vector = -self.vector
        res = uVar('?',vector,value)
        res._reconstruct()
        return res   
      
    def __abs__(self):
        """
        Overload of absolute value
        new = abs(self)
        Returns a new uVar object
        """
        name = self.name
        vector = self.vector
        value = abs(self.value)
        scale = self.scale
        res = uVar(name,vector,value,scale)
        res.complex = self.complex
        return res
      
    def __pow__(self,other):
        """
        Overload of power **
        new = self ** other
        Returns a new uVar object
        """
        if isinstance(other,uVar):
            if other.is_none():
                other = other.value
            else:
                raise unitsEx('Exponents must be dimensionless')
        value = (self.value*self.scale)**other     
        vector = self.vector*other
        res = uVar('?',vector,value)
        res._reconstruct()
        return res
      
    def __rpow__(self,other):
        """
        Overload of power ** used in reverse
        new = other ** self
        Returns a new uVar object
        """
        if not self.is_none():
            raise unitsEx('Exponents must be dimensionless')    
        value = other**(self.value*self.scale)
        vector = self.vector
        name = ''
        return uVar(name,vector,value)
      
    # Printing and representation ----------------------------------------------------- 
      
    def __str__(self):
        """
        Basic conversion to string
        Just gives the value followed by the units name
        """
        # Special case for numpy arrays
        if isinstance(self.value,np.ndarray):
            return str(self.value)+' '+self.name
        # Special case for mmVar objects
        if mmVars_imported:
            if isinstance(self.value,mm.mmVar):
                return str(self.value)+' '+self.name
        # Check sci4str flag
        if sci4str:        
            return self.sci()   
        # Default case    
        return f2s(self.value)+' '+self.name      
      
    def strUnit(self,unit):
        """
        Gives result in give units
        Raises exception if units don't match
        """
        if not self.check(unit):
            message = 'Units are not compatible'
            raise unitsEx(message)
        value = self.value*self.scale/unit.scale
        # Special case for numpy arrays
        if isinstance(value,np.ndarray):
            return str(value)+' '+unit.name
        # Default case    
        return f2s(value)+' '+unit.name  
      
    def sci(self,unit=None,prefix=True,sep=''):
        """
        Gives result in sci notation
        Optional parameters:
           unit   : Units to use (Default own units)
           prefix : Use power of 10 prefixes (Default to True)
           sep    : Separator between prefix and unit (Defaults to none)
        Power of 10 prefixes won't be used in composed units    
        """
        if unit is None:
            if self.complex:
                prefix = False   
            return f2sci(self.value,self.name,prefix=prefix,sep=sep)
        if not self.check(unit):
            message = 'Units are not compatible'
            raise unitsEx(message)    
        new = self.convert(unit)    
        if new.complex:
            prefix = False
        return f2sci(new.value,new.name,prefix=prefix,sep=sep) 

    def print(self,name,unit="",sci=True,prefix=True,sep=''):
        """
        Prints the unit as in the same way as the printVar function
        """
        printVar(name,self,unit,sci,prefix,sep)
   
  
# Unary non dimensionless functions ########################################

def sqrt(var):
    """
    Returns the square root of a variable
    Modifies the units as needed
    """
    if not isinstance(var,uVar):
        return function(var)
    value = np.sqrt(var.value*var.scale)
    vector = var.vector/2
    res = uVar('?',vector,value)
    res._reconstruct()
    return res 
  
# Special constructors #####################################################

def _evalPrefix(cad):
    """
    Internal function
    """
    pot={'k':1e3,'M':1e6,'G':1e9,'T':1e12,'P':1e15,'E':1e18
        ,'m':1e-3,'u':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18}
    if cad in pot:
        return pot[cad]
    return None    

def _evalUnit(name,level=1):
    """
    Internal function
    """   
    # Try to evaluate as unit variable
    try:
        var = _getVar('u_'+name,level+1)
    except:
        return None
    if not isinstance(var,uVar):
        raise unitsEx('unit name does not eval to uVar object')
    return var    
    
def _getUnit(unit,level=1):
    """
    Internal function used by makeVar and makeArray
    Parameters:
      unit  : Unit as uVar or string
      level : Stack level for eval
    """
    # Check if unit is a  uVar object
    if isinstance(unit,uVar):
        return unit
    # Check if unit is a string    
    if type(unit) != str:
        raise unitsEx('unit shall be uVar object or string')
        
    # Check '_' at position 1
    if len(unit)>1 and unit[1] == '_':
        power = _evalPrefix(unit[0])
        if power is None:
            raise unitsEx('invalid prefix')
        var = _evalUnit(unit[2:])
        if var is None:
            raise unitsEx('unit does not evaluate to any variable')
        return var*power
    
    # Try to evaluate all the name
    var = _evalUnit(unit,level=level+1)
    if not var is None:
        return var
        
    if len(unit)<2:
        raise unitsEx('cannot evaluate unit string')
        
    # Try to evaluate prefix if anything fails
    power = _evalPrefix(unit[0]) 
    if power is None:
        raise unitsEx('cannot evaluate unit string')
    var = _evalUnit(unit[1:])
    if var is None:
        raise unitsEx('cannot evaluate unit string')
    return var*power    

def makeVar(value,unit):
    """
    Creates a uVar object with indicated value
    Parameters:
       value : value to set
       unit : unit uVar object or string
    returns a new uVar object   
    """    
    unit = _getUnit(unit)
    return unit*value

def makeArray(list,unit):
    """
    Creates a uVar object with numpy array as value
    Parameters:
       list : list, iterable or numpy array
       unit : unit uVar object
    returns a new uVar object   
    """    
    unit = _getUnit(unit)
    return unit*np.array(list)
  
# Unary dimensionless functions ############################################

def unary(var,function):
    """
    Operates a variable on a function
    Parameters:
      var      : Variable to operate
      function : Unary function to execute on the variable
    Returns a new uVar object if var is an uVar object
    Raises exception if var has units
    """
    if not isinstance(var,uVar):
        return function(var)
    else:
        if not var.is_none():
            raise unitsEx('Only unitless variables are allowed')
        value = function(var.value)
        name  = ''
        vector = var.vector
        return uVar(name,vector,value)
      
def sin(var):
    """
    Sine function
    Only works on unitless uVar objects
    """
    return unary(var,np.sin)
  
def cos(var):
    """
    Cosine function
    Only works on unitless uVar objects
    """
    return unary(var,np.cos)
  
def exp(var):
    """
    Exponential function
    Only works on unitless uVar objects
    """
    return unary(var,np.exp)
  
def log(var):
    """
    Natural logarithm function
    Only works on unitless uVar objects
    """
    return unary(var,np.log)
  
def log10(var):
    """
    Base 10 logarithm function
    Only works on unitless uVar objects
    """
    return unary(var,np.log10)    
  
# Other non member functions ######################################

def sci(var,unit=None,prefix=True):
    """
    Same function as sci member but also works on non nVar objects
    Parameters:
       var    : Variable
       unit   : Units of variable (Defaults to no units)
       prefix : Use of power of ten prefix (Defaults to True)
    Returns a string   
    """
    if not isinstance(var,uVar):
        if unit is None:
            return f2sci(var,'',prefix=prefix)
        value = var*unit  
        return value.sci(prefix=prefix)
    return var.sci(unit,prefix)   
    
# SymPy evaluation ################################################

if sympy_imported: # Only if correct import of sympy
    def sympy2var(expr):
        """
        Converts a sympy expression to uVar objects using the registered variables
        """
        # Get caller globals and locals
        caller_globals = dict(inspect.getmembers(inspect.stack()[1][0]))["f_globals"]
        caller_locals = dict(inspect.getmembers(inspect.stack()[1][0]))["f_locals"]
        # Get symbols on the expression
        stuple = tuple(expr.free_symbols)
        # Convert to function
        func = sympy.lambdify(stuple,expr)
        # Create list of parameters
        list = []
        for symbol in stuple:
            name=symbol.name
            object = eval(name,caller_globals,caller_locals)
            list.append(object)
        # Evaluate function    
        res = func(*tuple(list))   
        return res
            
# Units register ##################################################

# Start with empty register
register = {}

def regUnit(unit):
    """
    Register one unit as default one
    """ 
    global register
    tup = tuple(unit.vector)
    register[tup]=unit    

# calc module access ##############################################

def _getVar(name,level=1):
    """
    Get a variable from its name
    Level indicates stack level of the caller
    Level 1 is appropiate if this function is called from a function
    that is called from the target context
    """
    # Get caller globals and locals
    caller_globals = dict(inspect.getmembers(inspect.stack()[level+1][0]))["f_globals"]
    caller_locals = dict(inspect.getmembers(inspect.stack()[level+1][0]))["f_locals"]
    # Print for debugging stack level (comment for normal use)
    #print('__name__=',eval('__name__',caller_globals,caller_locals))
    # Get variable
    var = eval(name,caller_globals,caller_locals)
    # Return variable
    return var
       
# Those functions will be created only if the calc module is imported    
   
if calc_imported: # Only if correct import of calc
    def plot11(x,y,title='',xt='',yt='',logx=False,logy=False,grid=True,latex=False):
        # Get objects for the axis
        xv = _getVar(x)
        yv = _getVar(y)
        # Create axes labels if needed
        if xt == '':
            if latex:
                xt = '$' + x + '\quad (' + xv.name + ')$'
            else:
                xt = x + ' (' + xv.name + ')'
        else:
            xt = xt.replace('<unit>',xv.name)
        if yt == '':
            if latex:
                yt = '$' + y + '\quad (' + yv.name + ')$'
            else:
                yt = y + ' (' + yv.name + ')'    
        else:
            yt = yt.replace('<unit>',yv.name)
        calc.plot11(xv.value,yv.value,title=title,xt=xt,yt=yt,logx=logx,logy=logy,grid=grid)   

def _getValues(list):
    '''
    Internal function for the plot1n and plotnn functions
    '''
    values = [list[0].value]
    if len(list) > 1:
            for i in range(1,len(list)):
                # Check if units are compatible
                if not list[0].check(list[i]):
                    raise unitsEx('All elements in one axis should feature compatible units')
                # Convert compatible units if needed    
                if list[i].name != list[0].name:
                    list[i] = list[i].convert(list[0])
                # Add value to list
                values.append(list[i].value)
    return values            
    
        
if calc_imported: # Only if correct import of calc
    def plot1n(x,ylist,title="",xt="",yt="",labels=[],location='best'
               ,logx=False,logy=False,grid=True,latex=False):
        # Get objects for the axis
        xv = _getVar(x)
        ylistv = [_getVar(element,level=2) for element in ylist]
        # Get values of the y list
        yvalues = _getValues(ylistv)
        # Create axes labels if needed
        if xt == '':
            if latex:
                xt = '$' + x + '\quad (' + xv.name + ')$'
            else:
                xt = x + ' (' + xv.name + ')'
        else:
            xt = xt.replace('<unit>',xv.name)
        if yt == '':
            if latex:
                yt = '$(' + ylistv[0].name + ')$'
            else:
                yt = '(' + ylistv[0].name + ')'
        else:
            yt = yt.replace('<unit>',ylistv[0].name)
        # Create curve labels if needed
        if labels == []:
            labels = ylist
        # Execute the plot command           
        calc.plot1n(xv.value,yvalues,title=title,xt=xt,yt=yt,labels=labels,location=location
               ,logx=logx,logy=logy,grid=grid)       

if calc_imported: # Only if correct import of calc
    def plotnn(xlist,ylist,title="",xt="",yt="",labels=[],location='best'
              ,logx=False,logy=False,grid=True,latex=False):
        # Get objects for the axes (level 3 because of list generator)
        xlistv = [_getVar(element,level=2) for element in xlist]
        ylistv = [_getVar(element,level=2) for element in ylist]
        # Get values of the axes lists
        xvalues = _getValues(xlistv)
        yvalues = _getValues(ylistv)
        # Create axes labels if needed
        if xt == '':
            if latex:
                xt = '$' + xlist[0] + '\quad (' + xlistv[0].name + ')$'
            else:
                xt = xlist[0] + ' (' + xlistv[0].name + ')'
        else:
            xt = xt.replace('<unit>',xlistv[0].name)
        if yt == '':
            if latex:
                yt = '$(' + ylistv[0].name + ')$'
            else:
                yt = '(' + ylistv[0].name + ')'
        else:
            yt = yt.replace('<unit>',ylistv[0].name)
        # Create curve labels if needed
        if labels == []:
            labels = ylist
        # Execute the plot command
        calc.plotnn(xvalues,yvalues,title=title,xt=xt,yt=yt,labels=labels,location=location
                    ,logx=logx,logy=logy,grid=grid)        
        
if calc_imported: # Only if correct import of calc
    def plotHist(v,bins=10,title="",xt="",yt="",grid=True,latex=False):  
        # Get vector
        vv = _getVar(v)
        # Create axes labels if needed
        if xt == '':
            if latex:
                xt = '$' + v + '\quad (' + vv.name + ')$'
            else:
                xt = v + ' (' + vv.name + ')'
        else:
            xt = xt.replace('<unit>',vv.name)
        if yt == '':
            if latex:
                yt = '$Frequency$'
            else:
                yt = 'Frequency'  
        # Execute the plot command                
        calc.plotHist(vv.value,bins=bins,title=title,xt=xt,yt=yt,grid=grid)
   
# Base units ######################################################

u_none = uVar('',[0,0,0,0,0,0,0])    # No units
u_none.complex = True                # Don't use prefixes on this unit
u_m    = uVar('m',[1,0,0,0,0,0,0])   # meter
u_kg   = uVar('kg',[0,1,0,0,0,0,0])  # kilogram
u_s    = uVar('s',[0,0,1,0,0,0,0])   # second
u_A    = uVar('A',[0,0,0,1,0,0,0])   # ampere
u_K    = uVar('K',[0,0,0,0,1,0,0])   # kelvin
u_mol  = uVar('mol',[0,0,0,0,0,1,0]) # mole
u_cd   = uVar('cd',[0,0,0,0,0,0,1])  # Candela

# Derived units ###################################################

u_rad  = (u_none*1.0).makeUnit('rad',True) # radian

u_sr   = (u_none*1.0).makeUnit('sr',True) # steradian

u_Hz   = (1.0/u_s).makeUnit('Hz',True) # hertz

u_N    = (u_m*u_kg/u_s/u_s).makeUnit('N',True,True) # newton (Default for Force)

u_Pa   = (u_N/u_m/u_m).makeUnit('Pa',True,True) # pascal (Default for Pressure)

u_J    = (u_N*u_m).makeUnit('J',True,True)  # joule (Default for Energy)

u_W    = (u_J/u_s).makeUnit('W',True,True) # watt (Default for Power)

u_C    = (u_s*u_A).makeUnit('C',True,True) # coulomb (Default for Charge)

u_V    = (u_W/u_A).makeUnit('V',True,True) # volt (Default for Voltage)

u_F    = (u_C/u_V).makeUnit('F',True,True) # farad (Default for Capacitance)

u_ohm  = (u_V/u_A).makeUnit('ohm',True,True) # ohm (Default for Resistance)

u_S    = (u_A/u_V).makeUnit('S',True,True) # siemens (Default for Conductance)

u_Wb   = (u_V*u_s).makeUnit('Wb',True,True) # weber (Default for Magnetic flux)

u_T    = (u_Wb/u_m/u_m).makeUnit('T',True,True) # tesla (Default for Magnetic flux density)

u_H    = (u_Wb/u_A).makeUnit('H',True,True) # henry (Default for Inductance)

u_dC   = (u_K*1.0).makeUnit('dC',True) # celsius

u_lm   = (u_cd*1.0).makeUnit('lm',True) # lumen

u_lx   = (u_lm/u_m/u_m).makeUnit('lx',True,True) # lux 

# Non SI units with sci prefixes ################################################

u_g = (u_kg/1000).makeUnit('g',True) # gram

u_eV = (1.6e-19*u_J).makeUnit('eV',True) # eV

# Non SI units with no sci prefixes #############################################

u_in = (25.4e-3*u_m).makeUnit('in') # inch

u_ft = (12*u_in).makeUnit('ft') # foot

y_yd = (3*u_ft).makeUnit('yd') # yard

u_mil = (u_in/1000).makeUnit('mil') # mil

u_cm = (u_m/100).makeUnit('cm') # cm

u_Ang = (1e-10*u_m).makeUnit('Ang') # Angstrom

u_deg = (np.pi*u_rad/180).makeUnit('deg') # degree

u_min = (u_s*60).makeUnit('min') # minute

u_h = (u_min*60).makeUnit('h') # hour

u_day = (u_h*24).makeUnit('day') # days

u_percent = (u_none*0.01).makeUnit('%') # percent

u_ppm = (u_none*1e-6).makeUnit('ppm') # parts per million

# Special units ###############################################################

'''
Special units cover special cases but are not always coherent with
other defined units
Use them with care or don't use them at all
'''

u_rad_s = (u_Hz/2/np.pi).makeUnit('rad/s') # rad/s

# Phisics constants ###########################################################

# Electron charge
c_q = 1.6e-19 * u_C 

# Vacuum permitivity
c_e0 = 8.85e-14 * u_F/u_cm

# Free space permeability
c_u0 = 4 * np.pi * u_H/u_m

# Boltzman constant
c_k = 8.62e-5 * u_eV/u_K

# Plank constant
c_h = 6.63e-34 * u_J * u_s

# Electron mass (steady)
c_m0 = 9.11e-31 * u_kg

# Gravity constant
c_G = 6.674e-11 * u_N*u_m**2/u_kg**2

# Gravital acceleration
c_g = 9.80665 * u_m/u_s**2

# Speed of light
c_c = 299792458 * u_m/u_s

# Avogadro constant
c_Na = 6.022140857e23 / u_mol



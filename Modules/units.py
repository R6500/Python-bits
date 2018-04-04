'''
units.py

Module to work with S.I. units

History:
   3/04/2018 : First version
   4/04/2018 : Addition of non S.I. units and Physics constants
'''

# Python 2.7 compatibility
from __future__ import print_function
from __future__ import division

# Basic imports
import numpy as np

version = '4/04/2018-B'

# Exception code ######################################################

class unitsEx(Exception):
    def __init__(self, msg=""):
        self.msg = msg
        print("\n** Units Exception")
        print('** ' + msg)
        print("\n")    
        
    def __str__(self):
        return repr(self.code)
      
# Globals ############################################################      
      
# Number of base units  
nbase   = 7   

# Vector with no units
v_none  = np.array([0,0,0,0,0,0,0])

# Base unit names
v_names = ['m','kg','s','A','K','mol','cd']

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
        if (a<1): ndec = int(np.floor(3-np.log10(a)))
    else:
        ndec = nd
        if (a<1): ndec = int(np.floor(nd-np.log10(a)))

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
    
def printVar(name,value,unit="",sci=True,prefix=True,sep=''):
    """
    Print a variable name, value and units
    """
    # Code if value is not an uVar object
    if not isinstance(value,uVar):
        if sci:
            print(name + " = " + f2sci(value,unit,prefix=prefix,sep=sep))
        else:
            print(name + " = " + f2s(value) + " " + unit)
        return

    # Code if value is a uVar object
    if unit != "" and not isinstance(unit,uVar):
        raise unitsEx('If value is an uVar object, unit shall be of the same kind')    
    if unit != "":
        value=value.convert(unit)
            
    if sci:
        print(name + " = " + value.sci(prefix=prefix,sep=sep))
    else:
        print(name + " = " + str(value))    

# uVar class #########################################################

class uVar:
  
    # Constructor -----------------------------------------------------
    
    def __init__(self,name,vector,value=1.0):
        """
        uVar constructor
        uVar(name,vector,value=1.0)
        Creates a new uVar object
        Parameters:
          name   : Name of the units
          vector : Vector of base units exponents
          value  : Numeric value (defaults to 1.0)
        Returns a new uVar object
        """
        if len(vector)!=7:
            raise unitsEx('Constructor vector size must be seven')    
        self.vector = np.array(vector)  # Base unit powers
        self.value  = value             # Numerical value
        self.name   = name              # Name of the units
        self.complex = False            # No single name for units
        
    # Get internal elements ----------------------------------------------------- 
        
    def value(self):
        """
        Returns the numeric value of the object
        """
        return self.value
      
    def vector(self):
        """
        Return the vector of base units exponents
        """
        return self.vector
      
    def name(self):
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
      
    # Private methods -----------------------------------------------------------
      
    def _construct_name(self): 
        """
        Private function
        Return a new complex name from the base units exponents
        """
        first = True
        name = ''
        for i in range(0,7):
            if self.vector[i] != 0:
                if not first:
                    name = name + '*'
                first = False    
                name = name + v_names[i]
                if self.vector[i] != 1:
                    name = name + '^' + str(self.vector[i])
        return name     
      
    # Unit conversion -----------------------------------------------------------

    def convert(self,other):
        """
        Convert to another compatible unit
        """ 
        if not self.same_units(other):
            raise unitsEx('Cannot convert to incompatible unit')
        name   = other.name
        value  = self.value/other.value 
        vector = self.vector
        return uVar(name,vector,value)
    
        if not self.same_units(unit):
            message = 'Units is not ' + unit.name
            raise unitsEx(message)    
            
        value = self.value/unit.value  
        if unit.complex:
            prefix = False
        return f2sci(value,unit.name,prefix=prefix,sep=sep)   
      
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
          
    def same_units(self,other):
        """
        Returns True if object has same units as other one
        """
        # Returns true if both have the same units
        if np.array_equal(self.vector,other.vector):
            return True
        else:  
            return False
                
    # Aritmetic operations -----------------------------------------------------       
        
    def __add__(self,other):
        """
        Overload of operator +
        new = self + other
        Raises exception is units are not the same
        Returns a new uVar object
        """
        if isinstance(other,uVar):
            if not self.same_units(other):
                raise unitsEx('Inconsistent units')   
            value = self.value+other.value    
            if self.name == other.name:
                name = self.name
                res = uVar(name,self.vector,value)
            else:
                name = self._construct_name()
                res = uVar(name,self.vector,value)
                res.complex = True
            return res
        else:
            if not self.is_none():
                raise unitsEx('Cannot add dimensionless value')
            value = self.value + other    
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
        return uVar(self.name,self.vector,-self.value)
        
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
        if isinstance(other,uVar):
            value = self.value*other.value
            vector = self.vector+other.vector
            if self.is_none():
                name = other.name
            elif other.is_none():
                name = self.name
            else:    
                name = '?'  
        else:
            value  = self.value*other
            vector = self.vector
            name   = self.name
        res = uVar(name,vector,value)
        if res.name == '?':
            res.name = res._construct_name()
            res.complex = True
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
        if isinstance(other,uVar):
            value = self.value/other.value
            vector = self.vector-other.vector
            if self.is_none():
                name = other.name
            elif other.is_none():
                name = self.name
            else:    
                name = '?'  
        else:
            value  = self.value/other
            vector = self.vector
            name   = self.name
        res = uVar(name,vector,value)
        if res.name == '?':
            res.name = res._construct_name()
            res.complex = True
        return res 
      
    def __rtruediv__(self,other):
        """
        Overload of division / used in reverse
        new = other/self
        Returns a new uVar object
        """
        if isinstance(other,uVar):
            return other.__truediv__(self)
        else:
            value  = other/self.value
            vector = -self.vector
            name   = '?'
        res = uVar(name,vector,value)
        if res.name == '?':
            res.name = res._construct_name()
            res.complex = True
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
        return uVar(name,vector,value)
      
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
        name = '?'        
        value = self.value**other     
        vector = self.vector*other
        res = uVar(name,vector,value)
        res.name = res._construct_name()
        res.complex = True
        return res
      
    def __rpow__(self,other):
        """
        Overload of power ** used in reverse
        new = other ** self
        Returns a new uVar object
        """
        if not self.is_none():
            raise unitsEx('Exponents must be dimensionless')
        value = other**self.value
        vector = self.vector
        name = ''
        return uVar(name,vector,value)
      
    # Printing and representation ----------------------------------------------------- 
      
    def __str__(self):
        """
        Basic conversion to string
        Just gives the value followed by the units name
        """
        return f2s(self.value)+' '+self.name      
      
    def strUnit(self,unit):
        """
        Gives result in give units
        Raises exception if units don't match
        """
        if not self.same_units(unit):
            message = 'Units is not ' + unit.name
            raise unitsEx(message)
        value = self.value/unit.value
        return str(value)+' '+unit.name  
      
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
        if not self.same_units(unit):
            message = 'Units is not ' + unit.name
            raise unitsEx(message)    
        value = self.value/unit.value  
        if unit.complex:
            prefix = False
        return f2sci(value,unit.name,prefix=prefix,sep=sep)    
   
  
# Unary non dimensionless functions ########################################

def sqrt(var):
    """
    Returns the square root of a variable
    Modifies the units as needed
    """
    if not isinstance(var,uVar):
        return function(var)
    value = np.sqrt(var.value)
    name = '?'
    vector = var.vector/2
    res = uVar(name,vector,value)
    res.name = res._construct_name()
    res.complex = True
    return res 
  
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
  
# Base units ######################################################

u_none = uVar('',[0,0,0,0,0,0,0])    # No units
u_m    = uVar('m',[1,0,0,0,0,0,0])   # meter
u_kg   = uVar('kg',[0,1,0,0,0,0,0])  # kilogram
u_s    = uVar('s',[0,0,1,0,0,0,0])   # second
u_A    = uVar('A',[0,0,0,1,0,0,0])   # ampere
u_K    = uVar('K',[0,0,0,0,1,0,0])   # kelvin
u_mol  = uVar('mol',[0,0,0,0,0,1,0]) # mole
u_cd   = uVar('cd',[0,0,0,0,0,0,1])  # Candela

# Derived units ###################################################

u_rad  = u_none*1.0     # radian
u_rad.set_name('rad')

u_sr   = u_none*1.0     # steradian
u_sr.set_name('sr')

u_Hz   = 1.0/u_s        # hertz
u_Hz.set_name('Hz')

u_N    = u_m*u_kg/u_s/u_s # newton
u_N.set_name('N')

u_Pa   = u_N/u_m/u_m    # pascal
u_Pa.set_name('Pa')

u_J    = u_N*u_m        # joule
u_J.set_name('J')

u_W    = u_J/u_s        # watt
u_W.set_name('W')

u_C    = u_s*u_A        # coulomb
u_C.set_name('C')

u_V    = u_W/u_A        # volt
u_V.set_name('V')

u_F    = u_C/u_V        # farad
u_F.set_name('F')

u_ohm  = u_V/u_A        # ohm
u_ohm.set_name('ohm')

u_S    = u_A/u_V        # siemens
u_S.set_name('S')

u_Wb   = u_V*u_s        # weber
u_Wb.set_name('Wb')

u_T    = u_Wb/u_m/u_m   # tesla
u_T.set_name('T')

u_H    = u_Wb/u_A       # henry
u_H.set_name('H')

u_dC   = u_K*1.0        # celsius
u_dC.set_name('?C')

u_lm   = u_cd*1.0       # lumen
u_lm.set_name('lm')

u_lx   = u_lm/u_m/u_m   # lux
u_lx.set_name('lx')

# Non SI units ################################################################

u_in = 25.4e-3*u_m    # Inch
u_in.set_name('in',True)

u_mil = u_in/1000     # mils
u_mil.set_name('mil',True)

u_cm = u_m/100 # cm
u_cm.set_name('cm',True)

u_eV = 1.6e-19 *u_J # eV
u_eV.set_name('eV')

u_Ang = 1e-10 * u_m # Angstrom
u_Ang.set_name('Ang',True)

u_g = u_kg / 1000 # gram
u_g.set_name('g')

# Phisics constants ###########################################################

# Electron charge
c_q = 1.6e-19 * u_C 

# Vacuum permitivity
c_e0 = 8.85e-14 * u_F/u_cm

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



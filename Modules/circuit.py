'''
circuit.py

Module to solve electrical circuits

History:
  25/03/2018 : First version
  26/03/2018 : Adding components now return the associated symbols
               Correct error in VM processing
               Change in some class member names
'''

# Python 2.7 compatibility
from __future__ import print_function
from __future__ import division

# Needed imports
import sympy
import numpy as np

version='26/03/2018-D'

verbose = False

# EXCEPTION CODE ###########################################################################

class circuitEx(Exception):
    def __init__(self, msg=""):
        print('**')
        print('** Circuit exception')
        print('**')
        print('** ' + msg) 
        print('**')
        print("\n")    

# GLOBAL OPERATIONS ########################################################################

# Define the "s" symbol
s = sympy.Symbol('s')

def setVerbose(flag=True):
    """
    Set module to be verbose
    Module starts not being verbose
    Parameter:
       flag : Be verbose? (Defaults to True)
    """
    global verbose
    verbose = flag

class circuit():

    def __init__(self):
        """
        Constructor to start a new circuit from zero
        """
        self.components = []   # List of components in the circuit
        self.subsDic = {}      # Substitution dictionary for values
        self.meas = {}         # Dictionary of measurement objects
        self.sSolution = None  # Analytical solution (key = symbols)
        self.solution = None   # Analytical solution (key = names)
        self.particular = None # Nummeric or "s" solution (key = names)
        self.name = {}         # Name dictionary with symbols for keys
        self.symbol = {}       # Symbol dictionary with name keys
        if verbose:
            print('Starting a new circuit')
   
# ADD COMPONENTS TO THE CIRCUIT #########################################################
   
# Component values are added to the substitution dictionary   
   
    def addR(self,name,node1,node2,value=None):
        """
        Add a resistor to the circuit
        Parameters:
             name : Name of the resistor
            node1 : First node
            node2 : Second node
            value : Value of the resistor (Defaults to None)
        Return the resistor symbol    
        """    
        # Define a symbol for the resistor
        sy = sympy.Symbol(name)
        # Define the dictionary
        dict = {}
        dict['k']  = 'r'
        dict['n']  = name
        dict['n1'] = node1
        dict['n2'] = node2
        dict['v']  = value
        dict['sy'] = sy
        # Add entry to list of components
        self.components.append(dict)
        # Add to name dictionary
        self.symbol[name] = sy
        # Add entry to substitution dictionary
        if value != None:
            self.subsDic[sy] = value
        if verbose:
            if value:
                print('Resistor',name,'added between nodes',node1,'and',node2,'with value',value)
            else:
                print('Resistor',name,'added between nodes',node1,'and',node2) 
        return sy        
                
    def addC(self,name,node1,node2,value=None):
        """
        Add a capacitor to the circuit
        Parameters:
             name : Name of the capacitor
            node1 : First node
            node2 : Second node
            value : Value of the capacitor (Defaults to None)
        Return the capacitor symbol    
        """    
        # Define a symbol for the capacitor
        sy = sympy.Symbol(name)
        # Define the dictionary
        dict = {}
        dict['k']  = 'c'
        dict['n']  = name
        dict['n1'] = node1
        dict['n2'] = node2
        dict['v']  = value
        dict['sy'] = sy
        # Add entry to list of components
        self.components.append(dict)
        # Add to name dictionary
        self.symbol[name] = sy
        # Add entry to substitution dictionary
        if value != None:
            self.subsDic[sy] = value
        if verbose:
            if value:
                print('Capcitor',name,'added between nodes',node1,'and',node2,'with value',value)
            else:
                print('Capacitor',name,'added between nodes',node1,'and',node2)  
        return sy        

    def addL(self,name,node1,node2,value=None):
        """
        Add a inductor to the circuit
        Parameters:
             name : Name of the inductor
            node1 : First node
            node2 : Second node
            value : Value of the inductor (Defaults to None)
        Return the inductor symbol    
        """    
        # Define a symbol for the inductor
        sy = sympy.Symbol(name)
        # Define the dictionary
        dict = {}
        dict['k']  = 'l'
        dict['n']  = name
        dict['n1'] = node1
        dict['n2'] = node2
        dict['v']  = value
        dict['sy'] = sy
        # Add entry to list of components
        self.components.append(dict)
        # Add to name dictionary
        self.symbol[name] = sy
        # Add entry to substitution dictionary
        if value != None:
            self.subsDic[sy] = value
        if verbose:
            if value:
                print('Inductor',name,'added between nodes',node1,'and',node2,'with value',value)
            else:
                print('Inductor',name,'added between nodes',node1,'and',node2)                 
        return sy        
                
    def addV(self,name,node1,node2,value=None): 
        """
        Add an independent voltage supply to the circuit
        Parameters:
             name : Name of the supply
            node1 : First node  (+)
            node2 : Second node (-)
            value : Value of the supply (Defaults to None)
        Return the source symbol and the current symbol    
        """    
        # Define a symbol for the supply
        sy = sympy.Symbol(name)
        # Define the dictionary
        dict = {}
        dict['k']  = 'vs'    
        dict['n']  = name
        dict['n1'] = node1
        dict['n2'] = node2
        dict['v']  = value
        dict['sy'] = sy
        # Create unknow for the current
        isy = sympy.Symbol('i'+name)
        dict['isy'] = isy
        # Add entry to symbol dictionary
        self.name[isy] = 'i'+name
        # Add to name dictionary
        self.symbol[name] = sy
        self.symbol['i'+name] = isy
        # Add entry to list of components
        self.components.append(dict)
        # Add entry to substitution dictionary
        if value != None:
            self.subsDic[sy] = value
        if verbose:
            if value:
                print('Voltage supply',name,'added between nodes',node1,'and',node2,'with value',value)
            else:
                print('Voltage supply',name,'added between nodes',node1,'and',node2)  
        return sy       

    def addI(self,name,node1,node2,value=None): 
        """
        Add an independent current supply to the circuit
        Parameters:
             name : Name of the supply
            node1 : First node  (+)
            node2 : Second node (-)
            value : Value of the supply (Defaults to None)
        Return the source symbol    
        """ 
        # Define a symbol for the supply
        sy = sympy.Symbol(name)
        # Define the dictionary
        dict = {}
        dict['k']  = 'is'    
        dict['n']  = name
        dict['n1'] = node1
        dict['n2'] = node2
        dict['v']  = value
        dict['sy'] = sy
        # Add entry to list of components
        self.components.append(dict)
        # Add to name dictionary
        self.symbol[name] = sy
        # Add entry to substitution dictionary
        if value != None:
            self.subsDic[sy] = value
        if verbose:
            if value:
                print('Current supply',name,'added between nodes',node1,'and',node2,'with value',value)
            else:
                print('Current supply',name,'added between nodes',node1,'and',node2)    
        return sy        
    
    def addVM(self,name,node1,node2): 
        """
        Add an voltage mesurement to the circuit
        Parameters:
             name : Name of the unknown to add
            node1 : First node  (+)
            node2 : Second node (-)
        Return the measurement symbol    
        """    
        # Define a symbol for the unknown
        sy = sympy.Symbol(name)
        # Define the dictionary
        dict = {}
        dict['k']  = 'vm'    
        dict['n']  = name
        dict['n1'] = node1
        dict['n2'] = node2
        dict['sy'] = sy
        # Add entry to symbol dictionary
        self.name[sy] = name
        # Add to name dictionary
        self.symbol[name] = sy
        # Add entry to list of components
        self.components.append(dict)
        # Add entry to measurement elements
        self.meas[name] = dict
        if verbose:
            print('Voltage measurement',name,'added between nodes',node1,'and',node2)
        return sy    
            
    def addIM(self,name,node1,node2): 
        """
        Add an current mesurement to the circuit
        Current goes from (-) to (+)
        The two nodes are at short circuit
        Parameters:
             name : Name of the unknown to add
            node1 : First node  (+)
            node2 : Second node (-)
        Return the measurement symbol    
        """    
        # Define a symbol for the unknown
        sy = sympy.Symbol(name)
        # Define the dictionary
        dict = {}
        dict['k']  = 'im'    
        dict['n']  = name
        dict['n1'] = node1
        dict['n2'] = node2
        dict['sy'] = sy
        # Add entry to symbol dictionary
        self.name[sy] = name
        # Add to name dictionary
        self.symbol[name] = sy
        # Add entry to list of components
        self.components.append(dict)
        # Add entry to measurement elements
        self.meas[name] = dict
        if verbose:
            print('Current measurement',name,'added between nodes',node1,'and',node2)   
        return sy            
    
    def addCVS(self,name,node1,node2,cont,value=None):
        """
        Add an Controlled Voltage Source to the circuit
        Parameters:
             name : Name of the proportionality constant
            node1 : First node  (+)
            node2 : Second node (-)
             cont : Coltroller name
            value : Value of the proportionality constant (Defaults to None)
        Return the CVS symbol and the current on the source    
        """    
        # Check the controller
        try:
            ctr = self.meas[cont]
        except KeyError:
            raise circuitEx('CVS controller must be defined previously')        
        # Define a symbol for the CVS
        sy = sympy.Symbol(name)
        # Define the dictionary
        dict = {}
        dict['k']  = 'cvs'    
        dict['n']  = name
        dict['n1'] = node1
        dict['n2'] = node2
        dict['v']  = value
        dict['sy'] = sy
        dict['ctr'] = ctr
        # Create unknow for the current
        isy = sympy.Symbol('i'+name)
        dict['isy'] = isy
        # Add entry to symbol dictionary
        self.name[isy] = 'i'+name
        # Add to name dictionary
        self.symbol[name] = sy
        self.symbol['i'+name] = isy
        # Add entry to list of components
        self.components.append(dict)
        # Add entry to substitution dictionary
        if value != None:
            self.subsDic[sy] = value
        if verbose:
            if value:
                print('VcVs',name,'added between nodes',node1,'and',node2,'with value',value)
            else:
                print('VcVs',name,'added between nodes',node1,'and',node2)
        return sy      
            
    def addCIS(self,name,node1,node2,cont,value=None): 
        """
        Add an controlled current supply to the circuit
        Parameters:
             name : Name of the supply
            node1 : First node  (+)
            node2 : Second node (-)
             cont : Coltroller name
            value : Value of the supply (Defaults to None)
        Return the CIS symbol    
        """ 
        # Check the controller
        try:
            ctr = self.meas[cont]
        except KeyError:
            raise circuitEx('CIS controller must be defined previously')
        # Define a symbol for the CIS
        sy = sympy.Symbol(name)
        # Define the dictionary
        dict = {}
        dict['k']  = 'cis'    
        dict['n']  = name
        dict['n1'] = node1
        dict['n2'] = node2
        dict['v']  = value
        dict['sy'] = sy
        dict['ctr'] = ctr
        # Add entry to list of components
        self.components.append(dict)
        # Add to name dictionary
        self.symbol[name] = sy
        # Add entry to substitution dictionary
        if value != None:
            self.subsDic[sy] = value
        if verbose:
            if value:
                print('Current supply',name,'added between nodes',node1,'and',node2,'with value',value)
            else:
                print('Current supply',name,'added between nodes',node1,'and',node2)      
        return sy         
            
# INTERNAL FUNCTIONS TO SOLVE THE CIRCUI ###################################################### 

    def _numNodes(self):
        """
        Get the list of nodes
        """
        # Create a set of nodes
        self.nodeList = set([])
        # Check if there are components in circuit    
        if len(self.components)==0:
            raise circuitEx('No components in the circuit')
        # Add all nodes to the set    
        for component in self.components:
            self.nodeList.add(component['n1'])
            self.nodeList.add(component['n2'])
        # Convert set to list    
        self.nodeList = list(self.nodeList)    
        if verbose:
            print('There are',len(self.nodeList),'nodes :')    
            for node in self.nodeList:
                print('    ',node)    

    def _nodeVariables(self):
        """
        Define the node variables in the circuit
        They are associated to all nodes
        They are also added to the unknowns list
        """   
        # Define an empt dictionary with node variables
        self.nodeVars = {}
        # Check for no nodes in the circuit    
        if len(self.nodeList) == 0:
            raise circuitEx('No nodes in the circuit')
        if verbose:
            print('Creating node variables')  
        zeroFound = False        
        for node in self.nodeList:
            if node == 0:
                zeroFound = True
            else:
                name = 'v'+str(node)
                ns = sympy.Symbol(name)
                self.nodeVars[node] = ns
                self.unknowns.add(ns)
                # Add entry to symbol dictionary
                self.name[ns] = name
                # Add to name dictionary
                self.symbol[name] = ns
                if verbose:
                    print('    ',name)    
        if not zeroFound:
            raise circuitEx('No 0 node in circuit')    

    def _addRtoNode(self,res,eq,node):
        """
        Add resistor to node equation if it connect to it
        """ 
        # Nodes in the resistor
        n1 = res['n1']
        n2 = res['n2']
        # Check if resistor is connected to n1
        if n1 == node:
            if n2 == 0:
                eq = eq - self.nodeVars[n1]/res['sy']
            else:
                eq = eq - (self.nodeVars[n1]-self.nodeVars[n2])/res['sy']
        # Check if resistor is connected to n2    
        if n2 == node:
            if n1 == 0:
                eq = eq - self.nodeVars[n2]/res['sy']
            else:
                eq = eq - (self.nodeVars[n2]-self.nodeVars[n1])/res['sy']
        return eq  

    def _addCtoNode(self,cap,eq,node):
        """
        Add capacitor to node equation if it connect to it
        """ 
        # Nodes in the capacitor
        n1 = cap['n1']
        n2 = cap['n2']
        # Check if capacitor is connected to n1
        if n1 == node:
            if n2 == 0:
                eq = eq - cap['sy']*s*self.nodeVars[n1]
            else:
                eq = eq - cap['sy']*s*(self.nodeVars[n1]-self.nodeVars[n2])
        # Check if capacitor is connected to n2    
        if n2 == node:
            if n1 == 0:
                eq = eq - cap['sy']*s*self.nodeVars[n2]
            else:
                eq = eq - cap['sy']*s*(self.nodeVars[n2]-self.nodeVars[n1])
        return eq        

    def _addLtoNode(self,ind,eq,node):
        """
        Add inductir to node equation if it connect to it
        """ 
        # Nodes in the inductor
        n1 = ind['n1']
        n2 = ind['n2']
        # Check if inductor is connected to n1
        if n1 == node:
            if n2 == 0:
                eq = eq - self.nodeVars[n1]/(ind['sy']*s)
            else:
                eq = eq - (self.nodeVars[n1]-self.nodeVars[n2])/(ind['sy']*s)
        # Check if inductor is connected to n2    
        if n2 == node:
            if n1 == 0:
                eq = eq - self.nodeVars[n2]/(ind['sy']*s)
            else:
                eq = eq - (self.nodeVars[n2]-self.nodeVars[n1])/(ind['sy']*s)
        return eq          
        
    def _addVtoNode(self,vs,eq,node):
        """
        Add independent voltage source to node equation if it connect to it
        """ 
        # Nodes in the voltage source
        n1 = vs['n1']
        n2 = vs['n2']
        # Check if voltage source is connected to n1
        if n1 == node:
            eq = eq + vs['isy']
        # Check if resistor is connected to n2    
        if n2 == node:
            eq = eq - vs['isy']
        return eq 

    def _addItoNode(self,isr,eq,node):
        """
        Add independent current source to node equation if it connect to it
        """ 
        # Nodes in the current source
        n1 = isr['n1']
        n2 = isr['n2']
        # Check if voltage source is connected to n1
        if n1 == node:
            eq = eq + isr['sy']
        # Check if resistor is connected to n2    
        if n2 == node:
            eq = eq - isr['sy']
        return eq 

    def _addIMtoNode(self,im,eq,node):
        """
        Add current measurement to node equation if it connect to it
        """ 
        # Nodes in the current source
        n1 = im['n1']
        n2 = im['n2']
        # Check if voltage source is connected to n1
        if n1 == node:
            eq = eq + im['sy']
        # Check if resistor is connected to n2    
        if n2 == node:
            eq = eq - im['sy']
        return eq         
       
    def _addKCLequations(self):
        """
        Add the KCL equations
        """
        if verbose:
            print('Creating KCL equations')
        # One equation for each node that is not 0    
        for node in self.nodeList:
            if node != 0:
                equation = sympy.Rational(0,1) 
                for cm in self.components:
                    if cm['k'] == 'r':
                        equation = self._addRtoNode(cm,equation,node)
                    elif cm['k'] == 'c':
                        equation = self._addCtoNode(cm,equation,node) 
                    elif cm['k'] == 'l':
                        equation = self._addLtoNode(cm,equation,node)                         
                    elif cm['k'] == 'vs' or cm['k'] == 'cvs':
                        equation = self._addVtoNode(cm,equation,node) 
                    elif cm['k'] == 'is' or cm['k'] == 'cis':
                        equation = self._addItoNode(cm,equation,node)
                    elif cm['k'] == 'im':
                        equation = self._addIMtoNode(cm,equation,node)                          
                # Add to the list of equations        
                self.equations.append(equation)                
                if verbose:
                    print('    ',equation)        
        
    def _substEqs(self,oldS,newS):
        """
        Substitute one symbol in all equations
        """
        newList = []
        for eq in self.equations:
            newList.append(eq.subs(oldS,newS))
        self.equations = newList        
    
        
    def _addVequations(self):
        """
        Add equations associated to the voltage sources
        The currents are added to the unknowns
        Unknowns are removed if needed
        """    
        if verbose:
            print('Adding V source equations')
        for cm in self.components:
            if cm['k']=='vs' or cm['k']=='cvs':
                # Add current to unknowns
                self.unknowns.add(cm['isy'])
                n1 = cm['n1']
                n2 = cm['n2']
                if   n1 == 0:
                    self.equations.append(sympy.Eq(cm['sy'],-self.nodeVars[n2]))
                elif n2 == 0:
                    self.equations.append(sympy.Eq(cm['sy'],self.nodeVars[n1]))
                else:
                    self.equations.append(sympy.Eq(cm['sy'],self.nodeVars[n1]-self.nodeVars[n2]))
                """
                if   n1 == 0:
                    self._substEqs(self.nodeVars[n2],cm['sy'])
                    self.unknowns.remove(self.nodeVars[n2])
                    self.nodeVars[n2]=cm['sy']
                elif n2 == 0:    
                    self._substEqs(self.nodeVars[n1],cm['sy'])
                    self.unknowns.remove(self.nodeVars[n1])
                    self.nodeVars[n1]=cm['sy']
                else:
                    self.equations.append(sympy.Eq(cm['sy'],self.nodeVars[n1]-self.nodeVars[n2])) 
                """    
                
    def _processVM(self):
        """
        Process the voltage measurement components
        They are added to the unknowns list
        They can substitute node voltages
        """    
        if verbose:
            print('Adding V measurement equations')
        for cm in self.components:
            if cm['k']=='vm':
                # Add to unknowns
                self.unknowns.add(cm['sy'])
                n1 = cm['n1']
                n2 = cm['n2']
                if   n1 == 0:
                    self._substEqs(self.nodeVars[n2],-cm['sy'])
                    try:
                        self.unknowns.remove(self.nodeVars[n2])
                    except KeyError:
                        # Already removed by voltage source
                        self.equations.append(sympy.Eq(cm['sy'],self.nodeVars[n2]))               
                elif n2 == 0:    
                    self._substEqs(self.nodeVars[n1],cm['sy'])
                    try:
                        self.unknowns.remove(self.nodeVars[n1])
                    except KeyError:
                        # Already removed by voltage source
                        self.equations.append(sympy.Eq(cm['sy'],self.nodeVars[n1]))                
                else:
                    self.equations.append(sympy.Eq(cm['sy'],self.nodeVars[n1]-self.nodeVars[n2]))  

    def _processIM(self):
        """
        Process the current measurement components
        They are added to the unknowns list
        They add new voltage equations
        """    
        if verbose:
            print('Adding I measurement equations')
        for cm in self.components:
            if cm['k']=='im':
                # Add to unknowns
                self.unknowns.add(cm['sy'])
                n1 = cm['n1']
                n2 = cm['n2']
                if n1 == 0:
                    self._substEqs(self.nodeVars[n2],0)
                    self.unknowns.remove(self.nodeVars[n2])
                    self.nodeVars[n2] = 0
                elif n2 == 0:
                    self._substEqs(self.nodeVars[n1],0)
                    self.unknowns.remove(self.nodeVars[n1])
                    self.nodeVars[n1] = 0
                else:
                    self._substEqs(self.nodeVars[n1],self.nodeVars[n2]) 
                    self.unknowns.remove(self.nodeVars[n1])                    
                    self.nodeVars[n1] = self.nodeVars[n2]
                    
                #self.equations.append(sympy.Eq(self.nodeVars[n1],self.nodeVars[n2]))          
           
    def _processCtr(self):
        """
        Process Controlled Voltage and Current Sources
        """    
        if verbose:
            print('Processing controlled elements')
        for cm in self.components:        
            if cm['k'] == 'cvs' or cm['k'] == 'cis':
                self._substEqs(cm['sy'],cm['sy']*cm['ctr']['sy'])     

            
    def _showEquations(self):
        """
        Show all equations
        """
        print('Circuit equations:')
        for eq in self.equations:
            print('    ',eq)    
        
    def _solveEquations(self):
        """
        Solve the circuit equations
        """
        if verbose:
            print('Unknowns:',self.unknowns)
        self.sSolution = sympy.solve(self.equations,list(self.unknowns))
        if verbose:
            print('Circuit solution:')
            print('    ',self.sSolution)
            
    def _nameSolution(self):
        """
        Convert solution to use names as keys
        """        
        self.solution = {}
        for sym in self.sSolution:
            key = self.name[sym]
            self.solution[key] = self.sSolution[sym]
            
    def _substituteSolution(self):
        """
        Substitute values in solution
        """       
        self.particular = {}
        for key in self.solution:
            self.particular[key] = self.solution[key].subs(self.subsDic)  
        if verbose:
            print('Circuit solution with substitutions:')
            print('    ',self.particular)        
     
# SOLVING THE CIRCUIT #############################################################################
     
    def solve(self):
        """
        Solve a circuit
        """
        if verbose:
            print('Solving the circuit')
        # Initialize equation list    
        self.equations  = []
        # Initialize unknowns set
        self.unknowns = set([])
        # Generate a list of nodes in nodeList
        self._numNodes()
        # Create node variables in dict nodeVars
        # Add them to unknowns set
        self._nodeVariables()
        # Add KCLs to equations
        self._addKCLequations()
        # Add Voltage source equations
        # Remove node unknowns for grounded sources
        self._addVequations()
        # Process current measurement elements
        self._processIM()
        # Process voltage measurement elements
        self._processVM()
        # Process controlled voltage sources
        self._processCtr()
        # Show the circuit equations
        if verbose:
            self._showEquations()
        # Solve the circuit equations for the unknowns    
        self._solveEquations()
        # Generate solution with names instead of symbols
        self._nameSolution()
        # Substitute values in the solution
        self._substituteSolution()
        return self.solution
        
    def subs(self):
        """
        Give solution after substituting component values
        """  
        return self.particular       

# HELPER FUNCTIONS #############################################################################

def evalList(expr,var,set):
    """
    Evaluate a sympy expression in a set of values
    """
    return np.array([complex((expr.subs(var,x)).evalf()) for x in set])
    
def evalFreqs(expr,set):    
    """
    Evaluate a sympy expression in a set of frequencies (Hz) for 's' symbols
    """
    return evalList(expr,s,1j*2.0*np.pi*set)
    
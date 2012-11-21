#-------------------------------------------------------------------------------
# Name:         Generator
# Purpose:    This module creates the output for the source code.
#            More important is that any action symbols' methods
#            are defined here.
#
# Author:      Joshua Underwood
#
# Created:    Oct 31, 2012
# Copyright:   (c) Joshua Underwood 2012
# Licence:     GPLv3 or latter
#-------------------------------------------------------------------------------
import SymbolTable

_list = []
_max_temp = []
_max_symbol = 256
_symbol_table =[]


verbose = False

def Display(functionName, inputStr):
    if verbose:
        #output = ""
        print functionName
        """
        if len(inputStr) > 5:
            for S in range(5):
                output += str(inputStr[S][1])
            output += "..."
        else:
            for S in inputStr:
                output += str(S[1])
        print output.rjust(80)
        """

def setVerbose(_bool):
    global verbose
    verbose = _bool

def Start():
    Display("Start", _list)
    global _max_symbol
    _max_symbol = 256
    if not SymbolTable._initilized : SymbolTable.initilize(0, 32)
    SymbolTable.newScope()


def WRITE(strings):
    Display("Write", _list)
    output = ""
    for S in strings:
        output += str(S)
    print output.rjust(80)


def Generate4(S1,S2, S3, S4):
    Display("Generate4", _list)
    WRITE([S1," ",S2,", ",S3,", ",S4])
def Generate3(S1,S2, S3):
    Display("Generate3", _list)
    WRITE([S1," ",S2,", ",S3])
def Generate1(S1):
    Display("Generate1", _list)
    WRITE([S1])


def ExtractRec(Record):
#Record must be tuple (<token>,<name/token>)
#retrieves the memory location for the symbol (variable)
    Display("ExtractRec", _list)
    return SymbolTable.getLocationString(Record)

def ExtractOp(Record):
#Record must be tuple (<token>,<name/token>)
#returns false if the Record is not a recognized operation
    Display("ExtractOp", _list)
    if Record[0] == "MINUSOP":
        return "SUB "
    if Record[0] == "PLUSOP":
        return "ADD "
    else:
        return False


def Extract(Record):
#Record must be tuple (<token>,<name/token>)
#returns semantic content of record
    Display("Extract", _list)
    
    _Op = ExtractOp(Record)
    if _Op: return _Op
    _Rec = ExtractRec(Record)
    if _Rec != None: return _Rec
    #Default return the syntactic input
    return Record[1]

def LookUp(symbol):
#Is symbol in hash table? returns True or False.
    Display("Lookup", _list)
    pointer = SymbolTable.getPointer(symbol)
    if pointer != None:
        return True
    return False

def Enter(symbol):
#add a variable to the hash table and string space
    Display("Enter", _list)
    SymbolTable.enterSymbol(symbol)

def CheckId(symbol):
    Display("CheckId", _list)
    if not LookUp(symbol):
        Enter(symbol)
        Generate3("Declare ", Extract(symbol), "Integer")

def GetTemp():
    Display("GetTemp", _list)
    _max_temp.append("x")
    TempName = []
    TempName.append("ID")
    TempName.append("Temp&" + str(len(_max_temp)))
    CheckId(TempName)
    return TempName[1]

def Copy(_from, _to, S_STACK):
    S_STACK[_to] = S_STACK[_from]

#       Generate code for assignment #Assign
# Store   <source name>   <target name>
def Assign(Target, Source, S_STACK):
    Display("Assign", _list)
    Generate3("Store ", Extract(S_STACK[Source]), Extract(S_STACK[Target]))
#            Generate code for #ReadId
# Read   <var name>   Integer
def ReadId(InVar, S_STACK):
    Display("ReadId", _list)
    Generate3('Read ', Extract(S_STACK[InVar]), 'Integer');

#       Generate code for #WriteExpr
# Write   <expr name>   Integer
def WriteExpr(OutExpr, S_STACK):
    Display("WriteExpr", _list)
    Generate3('Write ', Extract(S_STACK[OutExpr]), 'Integer')

#     Generate code for infix operation #GenInfix
#     Use GetTemp to get the name of a temporary
#     variable to save the result  and setup semantic record
# <op>   <oper1>  <oper2>  <result var >
def GenInfix(E1, Op, E2, _to, S_STACK):
    Display("GenInfix", _list)
    ERec = []
    ERec.append("ID")
    ERec.append(GetTemp())
    Generate4(Extract(S_STACK[Op]), Extract(S_STACK[E1]), Extract(S_STACK[E2]), Extract(ERec))
    S_STACK[_to] = ERec
    return ERec

#       ProcessId: Declare Id, enter it into the semantic table, and
#       build a corresponding semantic record
def ProcessId(E, S_STACK):
    Display("ProcessId", _list)
    CheckId(S_STACK[E])
    #S_STACK[E-1] = S_STACK[E]
    #x = raw_input("Enter to continue")
    return S_STACK[E]


#       ProcessLiteral: Convert literal to a numeric representation
#       and build a semantic record
def ProcessLiteral(E, S_STACK):
    Display("ProcessLiteral", _list)
    #unused because of dynamic type and touple storage from scanner
    #S_STACK[E-1] = S_STACK[E]
    return S_STACK[E]

#   ProcessOp: Produce operator descriptor
def ProcessOp(O, S_STACK):
    Display("ProcessOp", _list)
    # O.Op = CurrentToken
    #unused because of dynamic type and touple storage from scanner
    #S_STACK[O-1] = S_STACK[O]
    return S_STACK[O]

def ClearScope():
# Clears the local variables from SymbolTable upon competion of subprogram
    Display("ClearScope",_list)
    SymbolTable.clearScope()

def Finish():
#   Finish: Generate code to finish program
    Display("Finish", _list)
    Generate1('Halt')

def DOACTION(_action, SYMANTIC_STACK = None, EOP = None):
    #print _action, SYMANTIC_STACK, EOP
    if _action[0] != "#":
        print "!error! /Generator/DOACTION/ input not an action symbol"
        return False
    _action = _action[1:]
    paramaters = []
    try:
        paramStart = _action.index("(")
        paramString = _action[paramStart:]
        _action = _action[:paramStart]
        paramString = paramString[1:-1] #eliminate '(' and ')'
        tempParamaters = paramString.split(",")
        paramaters = []
        for string in tempParamaters:
            paramaters.append(GETPARAMETER(string, SYMANTIC_STACK, EOP))
        #print _action
        #print SYMANTIC_STACK[paramaters]
        try:
            globals()[_action](*paramaters, S_STACK = SYMANTIC_STACK)
        except:
            print "!error! /Generator/DOACTION/ Function", _action,"does not exist, or has error"

    except:
        try:
            globals()[_action]()
        except:
            print "!error! /Generator/DOACTION/ Function", _action,"does not exist, or has error"

def GETPARAMETER(string, SYMANTIC_STACK, EOP):
    try:
        if string == "$$": return EOP.LeftIndex
        elif string == "$1": return EOP.RightIndex + 0
        elif string == "$2": return EOP.RightIndex + 1
        elif string == "$3": return EOP.RightIndex + 2
        elif string == "$4": return EOP.RightIndex + 3
        elif string == "$5": return EOP.RightIndex + 4
        elif string == "$6": return EOP.RightIndex + 5
        elif string == "$7": return EOP.RightIndex + 6
        elif string == "$8": return EOP.RightIndex + 7
        elif string == "$9": return EOP.RightIndex + 8
    except:
        print "!error! /Generator/GETPARAMETER/ index off Symantic Stack"
        return None
    print "!error! /Generator/GETPARAMETER/ invalid string"
    return None



def main():
    setVerbose(True)
    _action = "#GenInfix($$,$1,$2)"
    _action = "#GenInfix($$,$1,$2)"
    _action = "#ProcessId($1)"
    SS = ("(a,a)", "(b,b)", "(c,c)")
    
    
    
    from LLParser import EOP
    eop = EOP(0,1,1,3)
    _action = "#Start"
    DOACTION(_action, SS, eop)
    
    _action = "#ProcessId($1)"
    try:
        DOACTION(_action, SS, eop)
    except:
        print "!error! /Generator/DOACTION/ Function", _action,"does not exist"
    pass

if __name__ == '__main__':
    main()

#-------------------------------------------------------------------------------
# Name:        LLParser
# Purpose:
#
# Author:      Joshua Underwood
#
# Created:     29/08/2012
# Copyright:   (c) Joshua 2012
# Licence:     GPLv3 or latter
#-------------------------------------------------------------------------------
import sys
import scanner2_0
import GrammarAnalizer_0_3
from LL1Table import BUILDTABLE
#from pprint import pprint
from Generator import DOACTION, verbose
import Generator
from SymbolTable import display

VERBOSE = False
DEBUG = False
PARSE_STACK = []
SYMANTIC_STACK = []

class EOP:

    RightIndex = 0
    LeftIndex = 0
    CurrentIndex = 0
    TopIndex = 0

    def __init__(self,  _left_index=None, _right_index = None,
                   _current_index = None, _top_index = None):
        self.RightIndex = _right_index;
        self.LeftIndex = _left_index;
        self.CurrentIndex = _current_index;
        self.TopIndex = _top_index;
        self.type = "EOP"

    def __repr__(self):
        a = "EOP("+str(self.LeftIndex)+", "+str(self.RightIndex)+", "+str(self.CurrentIndex)+", "+str(self.TopIndex)+")"
        return a

def LLDriver(_Grammar, _Table):
    global PARSE_STACK
    global SYMANTIC_STACK
    LeftIndex = 0
    RightIndex = 0
    CurrentIndex = 0
    TopIndex = 1

#   Push(S); -- Push the Start Symbol onto an empty stack
    PARSE_STACK.append(FindSystemGoal(_Grammar))
    SYMANTIC_STACK.append(FindSystemGoal(_Grammar))

    a = scanner2_0.Scanner()

    DISPLAY('Entry into the main loop "while not"',
            a[0] + scanner2_0.InputString[0:-1],
            PARSE_STACK,
            SYMANTIC_STACK,
            EOP(LeftIndex, RightIndex, CurrentIndex, TopIndex))

    while (PARSE_STACK != []):
#   -- let X be the top stack symbol; let a be the current input token
        X = PARSE_STACK[len(PARSE_STACK)-1]
#        print X, a

        if X in _Grammar.nonterminals:
            try: #T(X, a) = X -> Y1Y2. . .Ym, (if table lookup is a production number)
                lookup = _Table[(X,ConvertToSymbol(a[0]))] #hack to try to get tokens to Grammar symbol

                DISPLAY('NonTerminal. Table('+X+", "+(ConvertToSymbol(a[0]))+') = ' + str(lookup),
                        a[0] + scanner2_0.InputString[0:-1],
                        PARSE_STACK,
                        SYMANTIC_STACK,
                        EOP(LeftIndex, RightIndex, CurrentIndex, TopIndex))

            #    -- Expand nonterminal, replace X with Y1Y2. . .Ym on the stack.
            #    -- Begin with Ym, then Ym-1, . . . , and Y1 will be on top of the stack.
                PARSE_STACK.pop()
                PARSE_STACK.append(EOP(LeftIndex, RightIndex, CurrentIndex, TopIndex))
                lookup -= 1 #Lookup table is 0 based not 1 based, so convert
                for i in range(1, (len(_Grammar.productions[lookup].definitionsWithAction) + 1)):
                    Y = _Grammar.productions[lookup].definitionsWithAction[len(_Grammar.productions[lookup].definitionsWithAction) - i]
                    PARSE_STACK.append(Y)
                for i in range(0, len(_Grammar.productions[lookup].definitions)):
                    SYMANTIC_STACK.append(_Grammar.productions[lookup].definitions[i])
                LeftIndex = CurrentIndex
                RightIndex = TopIndex
                CurrentIndex = RightIndex
                TopIndex = TopIndex + len(_Grammar.productions[lookup].definitions)
            except:
            #    -- process syntax error
                print "!error! /LLParset/LLDriver/if/nonterminals/ syntax error."
                if DEBUG: x = raw_input("ERROR!")
            #end if

        elif X == GrammarAnalizer_0_3.LAMBDA:
            DISPLAY("Lambda encountered",
                    a[0] + scanner2_0.InputString[0:-1],
                    PARSE_STACK,
                    SYMANTIC_STACK,
                    EOP(LeftIndex, RightIndex, CurrentIndex, TopIndex))
            PARSE_STACK.pop()        #-- Lambda is not a matchable parse symbol
            SYMANTIC_STACK.pop()

        elif X in _Grammar.terminals or ConvertToToken(X) in _Grammar.terminals: #-- X in terminals
            DISPLAY('Terminal. X = '+X,
                    a[0] + scanner2_0.InputString[0:-1],
                    PARSE_STACK,
                    SYMANTIC_STACK,
                    EOP(LeftIndex, RightIndex, CurrentIndex, TopIndex))
            DISPLAYMATCH(a, scanner2_0.InputString[0:-1],PARSE_STACK)
            if X == a[0] or ConvertToToken(X) == a[0]:
                SYMANTIC_STACK[CurrentIndex] = a    #Place token information from Scanner in SS(CurrentIndex)
                PARSE_STACK.pop()                   #-- Match of X worked
                a = scanner2_0.Scanner()            #-- Get next token
                CurrentIndex += 1
            else:
            #   -- process syntax error
                print "!error! /LLParset/LLDriver/if/terminals/ syntax error."
            #end if;

        elif isinstance(X, EOP):
            DISPLAY('EOP. X = '+str(X),
                    a[0] + scanner2_0.InputString[0:-1],
                    PARSE_STACK,
                    SYMANTIC_STACK,
                    EOP(LeftIndex, RightIndex, CurrentIndex, TopIndex))
            #Restore LeftIndex, RightIndex, CurrentIndex, TopIndex from EOP
            LeftIndex = X.LeftIndex
            RightIndex = X.RightIndex
            CurrentIndex = X.CurrentIndex
            TopIndex = X.TopIndex
            CurrentIndex += 1
            PARSE_STACK.pop()
            SYMANTIC_STACK = SYMANTIC_STACK[:TopIndex]

        else: #X is an action symbol
            DISPLAY("Action. X = " + X,
                    a[0] + scanner2_0.InputString[0:-1],
                    PARSE_STACK,
                    SYMANTIC_STACK,
                    EOP(LeftIndex, RightIndex, CurrentIndex, TopIndex))

            #call symantic function
            DOACTION(PARSE_STACK.pop(), SYMANTIC_STACK, EOP(LeftIndex, RightIndex, CurrentIndex, TopIndex))
            #PARSE_STACK.pop()  #Done in action call


        #end if;
    #end loop;
#end LLDriver;

def FindSystemGoal(_Grammar):
    for i in _Grammar.FollowSet:
        if _Grammar.FollowSet[i] == set([GrammarAnalizer_0_3.LAMBDA]):
            return i
    #reached end of grammar with no start symbol
    print "!error! /LLParset/FindSystemGoal/ No start symbol found in grammar."
    print "!error! /LLParset/FindSystemGoal/ Using first production."
    return _Grammar.productions[0].name

def ConvertToToken(_TerminalSymbol):
    tokens = [
            "BEGIN", "END", "READ", "WRITE", "ID", "INTLITERAL",
            "LPAREN", "RPAREN", "SEMICOLON", "COMMA", "ASSIGNOP",
            "PLUSOP", "MINUSOP", "SCANEOF",
            "EQUALITYOP", "EXPONENTIATIONOP",
            "FUNCTION", "RETURN",
            ]


    symbols = [ "BEGIN", "END", "READ", "WRITE", "ID", "[\d]",
            "(",")",";",",",":=",
            "+","-","$",
            "=", "**",
            "FUNCTION", "RETURN",
            ]
    try:
        index = symbols.index(_TerminalSymbol)
        return tokens[index]
    except:
        return None

def ConvertToSymbol(_TerminalSymbol):
    tokens = [
            "BEGIN", "END", "READ", "WRITE", "ID", "INTLITERAL",
            "LPAREN", "RPAREN", "SEMICOLON", "COMMA", "ASSIGNOP",
            "PLUSOP", "MINUSOP", "SCANEOF",
            "EQUALITYOP", "EXPONENTIATIONOP",
            "FUNCTION", "RETURN",
            ]


    symbols = [ "BEGIN", "END", "READ", "WRITE", "ID", "INTLITERAL",
            "(",")",";",",",":=",
            "+","-","$",
            "=", "**",
            "FUNCTION", "RETURN",
            ]
    index = tokens.index(_TerminalSymbol)
    return symbols[index]

def DISPLAY(_FirstLine, _input, _Parse_Stack, _Symantic_Stack, _EOP):
    if VERBOSE:
        print _FirstLine
        print "Input:"
        print _input
        print "Parse Stack:"
        for i in range(1,len(_Parse_Stack)+1):
            print len(_Parse_Stack)-i,":",_Parse_Stack[len(_Parse_Stack)-i]
        print "Symantic Stack:"
        for i in range(1,len(_Symantic_Stack)+1):
            print len(_Symantic_Stack)-i,":",_Symantic_Stack[len(_Symantic_Stack)-i]
        print "Indices: "
        print _EOP
        for i in range(0,40): print "-",
        print
        print "Symbol Table:"
        display()
        if DEBUG: x = raw_input("Press Enter to continue")

def DISPLAYMATCH(_a, _input,_PARSE_STACK):
    if VERBOSE:
        print "MATCH","||", _a[0], _input,"||",_PARSE_STACK
        for i in range (0,40): print "-",
        print


def ProcessGrammar(filename):
    grammar = GrammarAnalizer_0_3.Grammar()
    grammar.FillProductions(filename)
    GrammarAnalizer_0_3.PredictSetFill(grammar)
    return grammar


def InitilizeScanFile(filename):
#    global scanner2_0.InputString
        try:
            f = open(filename, 'rU') #Open file for reading with Uniform new line
        except:
            print "!error! /InitilizeScanFile/>Invalid filename"
            return

        scanner2_0.InputString = str(f.read())
        f.close()

def GetTable(grammar):
    return BUILDTABLE(grammar)



def main():
    if len(sys.argv) >= 3:
        if "-v" in sys.argv[3:]:
            #global VERBOSE
            Generator.setVerbose(True)
            #VERBOSE = True
        if "-V" in sys.argv[3:]:
            global VERBOSE
            #Generator.setVerbose(True)
            VERBOSE = True
        if "-db" in sys.argv[3:]:
            global DEBUG
            DEBUG = True
        grammar = ProcessGrammar(sys.argv[1])
        table = GetTable(grammar)
        InitilizeScanFile(sys.argv[2])
        LLDriver(grammar, table)

    else:
        print "!help! this program is uses command line input"
        print
        print "!help! try                    /> python LLParser.py <Grammarfilename> <ProgramFilename>"
        print "!help! sometimes windows uses /> LLParser.py <Grammarfilename> <ProgramFilename"

    pass

if __name__ == '__main__':
    main()

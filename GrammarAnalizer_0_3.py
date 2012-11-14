#-------------------------------------------------------------------------------
# Name:        GrammarAnalizer
# Purpose:
#
# Author:      Joshua Underwood
#
# Created:     09/28/2012
# Copyright:   (c) Joshua 2012
# Licence:     GPLv3 or latter
#-------------------------------------------------------------------------------
import sys
from pprint import pprint

LAMBDA = "lambda"

class Terminal:
    def __init__(self):
        self.name = "" #name of Terminal token

class NonTerminal:
    def __init__(self, NonTeminalName):
        self.name = NonTeminalName  #LHS of production
        self.definitions = []       #RHS of production, list of (Non)Terminal tokens
        self.definitionsWithAction = [] #The definitions with the action symbols

    def addDefinition(self, DefinitionString):
        self.definitions.append(DefinitionString)
        self.definitionsWithAction.append(DefinitionString)

    def addActionSymbol(self,DefinitionString):
        self.definitionsWithAction.append(DefinitionString)

class Grammar:
    def __init__(self):
        self.productions = []        #listed productions from grammar
        self.terminals = set()       #set of Terminals from Grammar
        self.nonterminals = set()    #set of nonTerminals from Grammar
        self.FirstSet = dict()       #dictionary of sets of first nonterminals
        self.FollowSet = dict()      #dictionary of sets of following nonterminals
        self.PredictSet = dict()     #predict dictionary of sets of for Grammar
        self.DerivesLambda = dict()  #dictionary of terminals and nonterminals and if they derive lambda
        self.actionsymbols = []      #list of the action symbols to from Grammar

    def FillProductions(self, filename):
        try:
            f = open(filename, 'rU')
            Lines = f.readlines()
            f.close()
        except:
            print "!error! /GrammarAnalizer/>Invalid filename"
            return

        for line in Lines:
            c = 0
            Endc = c
            while c < len(line):
                if line[c] == "<":
                    while line[Endc] !=">" and Endc < len(line):
                        Endc += 1
                    if Endc > len(line):
                        print "!error! /GrammarAnalizer/>reached end of line without closing NonTerminal"
                        print '!error! /GrammarAnalizer/>error in "'+ line[c:] +'"'
                        return
                    self.nonterminals.add(line[c:(Endc+1)])
                    self.productions.append(NonTerminal(line[c:(Endc+1)]))
                    while line[c] == " ":
                        c += 1
                    while line[c:(c+2)] != "->" and(c+2) < len(line):
                        c += 1
                    c += 2
                    break
                c += 1
            while c < len(line) - 1:
                do_while = True
                Endc = c
                if line[c] != " ":
                    while line[Endc] != " " and line[Endc] != ">" and Endc < len(line) -1 and do_while:
                        #print line[c:Endc]
                        Endc += 1
                        if line[Endc] == "<":
                            do_while = False
                    if line[c] == "<":
                        self.nonterminals.add(line[c:(Endc+1)])
                        self.productions[-1].addDefinition(line[c:(Endc+1)])
                    elif line[c] == "#":
                        self.actionsymbols.append(line[c:Endc])
                        self.productions[-1].addActionSymbol(line[c:Endc])
                    else:
                        self.terminals.add(line[c:Endc])
                        self.productions[-1].addDefinition(line[c:Endc])
                    c = Endc
                if not do_while: c -= 1
                c += 1
        if "lambda" in self.terminals: self.terminals.remove("lambda")

    def Display(self):
        print "Non-Terminals:"
        pprint(self.nonterminals)
        print "Terminals:"
        pprint(self.terminals)
        print "Productions:"
        for production in self.productions:
            print production.name, "-> ", ; pprint(production.definitions)
        print "Productions with action symbols:"
        for production in self.productions:
            print production.name, "-> ", ; pprint(production.definitionsWithAction)
        print "LHS: "
        for p in self.productions: pprint(p.name, sys.stdout, 80)
        print
        print "RHS: "
        for sym in self.nonterminals: pprint(sym,sys.stdout, 80)
        for sym in self.terminals: pprint(sym,sys.stdout, 80)
        print

def MarkLambda(_Grammar):
    global LAMBDA
    DerivesLambda = dict()
    Changes = True #Any changes during last iteration?
    RHS_Derives_Lambda = bool() #Does the right-hand side derive lamba?

    for V in _Grammar.nonterminals:
        DerivesLambda[V] = bool(False)  #Initialization
    DerivesLambda[LAMBDA] = True        #LAMBDA derives lambda
    for Terminal in _Grammar.terminals:
        DerivesLambda[Terminal] = False #terminals do not derive lambda

    while Changes:
        Changes = False
        for P in _Grammar.productions:
            RHS_Derives_Lambda = True
            for I in P.definitions:
                RHS_Derives_Lambda = RHS_Derives_Lambda and DerivesLambda[I]
                #for each symbol in the right-hand side of production P
            if RHS_Derives_Lambda and not DerivesLambda[P.name]:
                Changes = True
                DerivesLambda[P.name] =True

    #clean out non-terminals and lambda from dict
    del DerivesLambda[LAMBDA]           #delete LAMBDA
    for Terminal in _Grammar.terminals:
        del DerivesLambda[Terminal]     #delete terminals

    #print "Derives Lambda:",DerivesLambda
    _Grammar.DerivesLambda = DerivesLambda
    return DerivesLambda

def FillFirstSet(_Grammar, DerivesLambda):
    #A: nonterminal; a: terminal;
    global Lambda
    FirstSet = dict()
    #FirstSet[LAMBDA] = set([LAMBDA])
    for A in _Grammar.nonterminals:
        if DerivesLambda[A]:
            FirstSet[A] = set([LAMBDA])
        else:
            FirstSet[A] = set()

    for a in _Grammar.terminals:
        FirstSet[a] = set([a])
        for A in _Grammar.nonterminals:
            #if there exists a production A -> a . . .
            for production in _Grammar.productions:
                if (production.name == A and a == production.definitions[0]):
                        FirstSet[A].add(a)
#    print FirstSet
    Changes = True
    while Changes:
        tempSet = dict(FirstSet)
#        print "TempSet:",tempSet
        for p in _Grammar.productions:
#            print FirstSet, p.name
#            print p.definitions
            FirstSet[p.name] = FirstSet[p.name]|(ComputeFirst(_Grammar, p.definitions, FirstSet))
#        print "FirstSet:",FirstSet
        Changes = (tempSet != FirstSet)
#        print Changes
#        print

        #exit when no changes;
    _Grammar.FirstSet = FirstSet
    return FirstSet

#    function ComputeFirst(x: string_of_symbols) return TermSet is
#For a string x of mixed terminals and nonterminals it returns the set of terminals that
#comprise First(x) assuming that FirstSet for each of the symbols of string x is known.
def ComputeFirst(_Grammar, TermSet, FirstSet):
    global LAMBDA
#    print "/ComputeFirst/", TermSet
    tempSet = set()
    for term in TermSet:
        if term in _Grammar.terminals:
            tempSet = tempSet | FirstSet[term]
            return tempSet
        if term in _Grammar.nonterminals:
            tempSet = tempSet | FirstSet[term]
            if not (LAMBDA in FirstSet[term]):
                return tempSet
    if LAMBDA in TermSet: return set([LAMBDA])
    return tempSet

def FillFollowSet(_Grammar):
    #A, B: nonterminal;
    if _Grammar.FirstSet == None: FillFirstSet(_Grammar,)
    global LAMBDA
    FollowSet = dict()
    for A in _Grammar.nonterminals:
        FollowSet[A] = set()
    Changes = True
    while Changes:
        tempSet = dict(FollowSet)
        #for each production p: A -> xBy
        for production in _Grammar.productions:
            for index,definition in enumerate(production.definitions):
            # occurrence of a nonterminal definition in RHS(p)
                if definition in _Grammar.nonterminals:
                    if (index+1) >= len(production.definitions):
                        y = LAMBDA
                    else:
                        y = production.definitions[index+1]
                    #if FollowSet[definition] == None: FollowSet[definition] = set()
                    FollowSet[definition] |= (ComputeFirst(_Grammar, [y], _Grammar.FirstSet) - set([LAMBDA]))
                    if LAMBDA in ComputeFirst(_Grammar, [y], _Grammar.FirstSet):
                        FollowSet[definition] |= FollowSet[production.name]
        Changes = (tempSet != FollowSet)
#   exit when no changes;

    #FollowSet[START_SYMBOL] = set([LAMBDA])
    for s in FollowSet:
        if FollowSet[s] == set():
            FollowSet[s] = set([LAMBDA])

    _Grammar.FollowSet = FollowSet
    return FollowSet

def PredictSetFill(_Grammar):
    global LAMBDA
    MarkLambda(_Grammar)
    FillFirstSet(_Grammar,_Grammar.DerivesLambda)
    FillFollowSet(_Grammar)
    for nonterm in _Grammar.nonterminals:
        if LAMBDA in _Grammar.FirstSet[nonterm]:
            _Grammar.PredictSet[nonterm] = _Grammar.FirstSet[nonterm] | _Grammar.FollowSet[nonterm]
            _Grammar.PredictSet[nonterm].remove(LAMBDA)
        else:
            _Grammar.PredictSet[nonterm] = _Grammar.FirstSet[nonterm]

def Predict(_Grammar, _Production):
    temp = set()
    temp |= (ComputeFirst(_Grammar,_Production.definitions,_Grammar.FirstSet) - set([LAMBDA]))
    if LAMBDA in ComputeFirst(_Grammar,_Production.definitions,_Grammar.FirstSet):
        temp |= _Grammar.FollowSet[_Production.name]
    return temp

def main():
    a = Grammar()
    if len(sys.argv) == 2:
        a.FillProductions(sys.argv[1])
        print
        a.Display()
        PredictSetFill(a)
        print "Predict Set:"#, a.FirstSet
        for i in a.FirstSet:
            print i, "->",a.FirstSet[i]
        """
        print "Follow Set:"
        for i in a.FollowSet:
            print i, "->",a.FollowSet[i]
        print "Follow Set:", a.FollowSet
        """
        pprint(a.actionsymbols)
#        pprint(a.productions)

    else:
        print "!help! this proram is uses command line input"
        print
        print "!help! try                    /> python GrammarAnalizer.py <filename>"
        print "!help! sometimes windows uses /> GrammarAnalizer.py <filename>"

    pass

if __name__ == '__main__':
    main()

#-------------------------------------------------------------------------------
# Name:        LL1TABLE
# Purpose:
#
# Author:      Joshua Underwood
#
# Created:     10/10/2012
#
# Licence:     GPLv3 or latter
#-------------------------------------------------------------------------------
from GrammarAnalizer_0_3 import *
from pprint import pprint


def BUILDTABLE(_Grammar):
    global LAMBDA
    Table = dict()
    temp = dict()
    for nonterminal in _Grammar.nonterminals:
        for terminal in _Grammar.terminals:
            Table[(nonterminal, terminal)] = None

    for x in range(len(_Grammar.productions)):
        for nonterminal in _Grammar.nonterminals:
            for terminal in _Grammar.terminals:
              if _Grammar.productions[x].name == nonterminal:
                temp = Predict(_Grammar, _Grammar.productions[x])
                if terminal in _Grammar.PredictSet[_Grammar.productions[x].name] and terminal in temp:
                    Table[(_Grammar.productions[x].name,terminal)] = x + 1
                #else:
                #    Table[(_Grammar.productions[x].name,terminal)] = ""
    return Table

def DISPLAYTABLE(_Table, _Grammar):
    display_table = [];
    row = [""]
    for terminal in _Grammar.terminals:
        row.append(terminal)
    #print 
    display_table.append(row)

    for nonterminal in _Grammar.nonterminals:
        row = [nonterminal]
        for terminal in _Grammar.terminals:
            row.append(_Table[(nonterminal,terminal)])
        #print row
        display_table.append(row)

    pprint(display_table, sys.stdout,1,120)
    return True

def main():
    a = Grammar()
    if len(sys.argv) == 2:
        a.FillProductions(sys.argv[1])
        print
        a.Display()
        PredictSetFill(a)
        """
        print "First Set:"#, a.FirstSet
        for i in a.FirstSet:
            print i, "->",a.FirstSet[i]
        print "Follow Set:"
        for i in a.FollowSet:
            print i, "->",a.FollowSet[i]
        print "Predict Set:"
        for i in a.FollowSet:
            print i, "->",a.PredictSet[i]
        """
        DISPLAYTABLE(BUILDTABLE(a),a)

    else:
        print "!help! this proram is uses command line input"
        print
        print "!help! try                    /> python GrammarAnalizer.py <filename>"
        print "!help! sometimes windows uses /> GrammarAnalizer.py <filename>"

    pass

if __name__ == '__main__':
    main()

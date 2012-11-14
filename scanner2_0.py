#-------------------------------------------------------------------------------
# Name:        scanner2.py
# Purpose:
# This function takes a filename for the argument and then returns a list of
# Micro Launguage tokens
#
# Pre: valid filename for Micro Launguage code file
#
# Post: List of touples of form (token, vaule) in order they appear in file
#       Token and value will be equal if they are not ID or INTLITERAL
#       Final list entry will equal SCANEOF if there are no errors
#
# Author:      Joshua Underwood
#
# Created:     22/08/2012
#
# Licence:     GPLv3 or latter
#-------------------------------------------------------------------------------
import sys

InputString = ""

# (state,  (Letter Digit Blank +   -   =  :   ,  ;   (    )   _  /t /n OTHR))
MICROLAUNGUAGETABLE = [
( 0,       (1     ,2    ,3    ,14 ,4 ,99 ,6 ,17 ,18 ,19 ,20 ,99,3 ,3 , 99)),
( 1,       (1     ,1    ,11   ,11 ,11,11 ,11,11 ,11 ,11 ,11 ,1,11,11 , 99)),
( 2,       (12    ,2    ,12   ,12 ,12,12 ,12,12 ,12 ,12 ,12 ,12,12,12, 99)),
( 3,       (13    ,13   ,3    ,13 ,13,13 ,13,13 ,13 ,13 ,13 ,13, 3, 3, 99)),
( 4,       (21    ,21   ,21   ,21 ,5 ,21 ,21,21 ,21 ,21 ,21 ,99,21,21, 99)),
( 5,       (5     ,5    ,5    ,5  ,5 ,5  ,5 ,5  ,5  ,5  ,5  ,5 ,5 ,15, 5)),
( 6,       (99    ,99   ,99   ,99 ,99,16 ,99,99 ,99 ,99 ,99 ,99,99,99, 99)),
( 7),
( 8),
( 9),
( 10),
( 11, "ID"),
( 12, "INTLITERAL"),
( 13, " "),
( 14, "PLUSOP"),
( 15, "--"),
( 16, "ASSIGNOP"),
( 17, "COMMA"),
( 18, "SEMICOLON"),
( 19, "LPAREN"),
( 20, "RPAREN"),
( 21, "MINUSOP"),
( 99, "ERROR"),
]
tokens = [
"BEGIN", "END", "READ", "WRITE", "ID", "INTLITERAL",
"LPAREN", "RPAREN", "SEMICOLON", "COMMA", "ASSIGNOP",
"PLUSOP", "MINUSOP", "SCANEOF",
"EQUALITYOP", "EXPONENTIATIONOP",
]

LETTER = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
DIGIT = "0123456789"
BLANK = " "
PLUS = "+"
MINUS = "-"
EQUALS = "="
COLON = ":"
COMMA = ","
SEMICOLON = ";"
LPAREN = "("
RPAREN = ")"
UNDERSCORE = "_"
TAB = "\t"
EOL = "\r\n"
OTHER = '!@#$%^&*{}|"?><,./\'[]\\'

def CurrentChar():
    if len(InputString)<1: return " "
    return InputString[0]

def ConsumeChar():
    global InputString
    InputString = InputString[1:]

def NextState(state, Char):
    #is the table for moves from state to state. It stores the next state to visit.
    if Char in LETTER: return MICROLAUNGUAGETABLE[state][1][0]
    if Char in DIGIT: return MICROLAUNGUAGETABLE[state][1][1]
    if Char in BLANK: return MICROLAUNGUAGETABLE[state][1][2]
    if Char in PLUS: return MICROLAUNGUAGETABLE[state][1][3]
    if Char in MINUS: return MICROLAUNGUAGETABLE[state][1][4]
    if Char in EQUALS: return MICROLAUNGUAGETABLE[state][1][5]
    if Char in COLON: return MICROLAUNGUAGETABLE[state][1][6]
    if Char in COMMA: return MICROLAUNGUAGETABLE[state][1][7]
    if Char in SEMICOLON: return MICROLAUNGUAGETABLE[state][1][8]
    if Char in LPAREN: return MICROLAUNGUAGETABLE[state][1][9]
    if Char in RPAREN: return MICROLAUNGUAGETABLE[state][1][10]
    if Char in UNDERSCORE: return MICROLAUNGUAGETABLE[state][1][11]
    if Char in TAB: return MICROLAUNGUAGETABLE[state][1][12]
    if Char in EOL: return MICROLAUNGUAGETABLE[state][1][13]
    #if Char in OTHER
    else: return MICROLAUNGUAGETABLE[state][1][14]

def Action(State, ChrrentChar):
    if State > 10:
        if State == 99: return "Error"
        if State > 13:
            if State != 21: ConsumeChar()
            return "HaltNoAppend"
        return "HaltAppend"
    if State == 1 or State == 2 or State == 3:
        return "MoveAppend"
    if State == 4 or State == 5 or State == 6:
        return "MoveNoAppend"
    print "!error! /Action/> Reached end of /Action/"

def LookupCode(State, TokenText):
    if TokenText in tokens:
        return TokenText
    return MICROLAUNGUAGETABLE[State][1]

def Scanner ():
    if len(InputString) < 1: return ("SCANEOF", "SCANEOF")
    State = NextState(0, CurrentChar())
    TokenText = "" #Null string
    while len(InputString) > 0:
        action = Action(State, CurrentChar())
        if action == "Error": #=> ?? Do lexical error recovery
            print "!error! /Scanner/> invalid token at", TokenText
            ConsumeChar()
            return Scanner()
        elif action == "MoveAppend": #=>
            TokenText += CurrentChar()
            ConsumeChar()
            State = NextState(State, CurrentChar())
        elif action == "MoveNoAppend": # =>
            ConsumeChar()
            State = NextState(State, CurrentChar())
        elif action == "HaltNoAppend": # =>
            tokenType = LookupCode(State, TokenText)
            #ConsumeChar()
            if tokenType == "--": return Scanner()
            return (tokenType, tokenType)
        elif action == "HaltAppend": # =>
            tokenType = LookupCode(State, TokenText)
            if tokenType == " ": return Scanner()
            return (tokenType, TokenText)
        #end if-else switch
    #end while
    #print "!error! /Scanner/> reached end of file without token."
    return ("SCANEOF", "SCANEOF")

#test driver for scan function
def main():
    if len(sys.argv) == 2:

        global InputString
        try:
            f = open(sys.argv[1], 'rU') #Open file for reading with Uniform new line
        except:
            print "!error! /main/>Invalid filename"
            return

        InputString = str(f.read())
        f.close()

        token_list = []

        while len(InputString) > 0:
            token_list.append(Scanner())
            #print token_list

        if len(token_list) > 0:
            # print token_list #uncomment to show touple list
            for token in token_list:
                if token[0] != token[1]:
                    print token[0],"",token[1]
                else:
                    print token[0]
        if token_list[-1][0] != "SCANEOF":
            print "There was an error, did not reach end of file"
    else:
        print "!help! this program is uses command line input"
        print
        print "!help! try                    /> python scanner.py <filename>"
        print "!help! sometimes windows uses /> scanner.py <filename>"


    pass


if __name__ == '__main__':
    main()


"""
tokens = [
"BEGIN", "END", "READ", "WRITE", "ID", "INTLITERAL",
"LPAREN", "RPAREN", "SEMICOLON", "COMMA", "ASSIGNOP",
"PLUSOP", "MINUSOP", "SCANEOF",
"EQUALITYOP", "EXPONENTIATIONOP",
]


symbols = [ "BEGIN", "END", "READ", "WRITE", "ID", "[\d]",
"(",")",";",",",":=",
"+","-","$",
"=", "**",
]
comment = ["--",]

leagalIDnames = ["_", ]

InputString = ""
"""

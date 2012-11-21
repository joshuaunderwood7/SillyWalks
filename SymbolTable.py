#-------------------------------------------------------------------------------
# Name:        SymbolTable.py
# Purpose:     This module stores symbols (vaiables) for code generation
#              to meet requirements for homework 10.
#
# Author:      Joshua Underwood
#
# Created:     19/11/2012
# Copyright:   (c) Joshua 2012
# Licence:     GPLv3 or latter
#-------------------------------------------------------------------------------

_initilized = False

_scope = -1
_string_space = ""
_hash_table = []
HASTABLESIZE = 7

#the general memory location for the variables. not yet implemented.
_memory_location = 0;
_word_length = 4;

VERBOSE = False

class record:
#This is a structure to hold the scope, offset and length in string space,
#and the memory offset of a stored symbol.
    def __init__(self, _length, _offset, _scope, pointer):
        self.length = _length
        self.offset = _offset
        self.scope = _scope
        self.pointer = pointer 

def initilize(_initial_offset, _bit_length = 32):
#set up hash table to keep track of symbols
#they will be placed at "memory locations" starting with the initial offset
#optionally, the bit length can be set, defaults to 32
    global _scope, _hash_table, _string_space, _word_length, _memory_location
    global _initilized
    _string_space = ""
    _scope = -1
    for i in range(0, HASTABLESIZE):
        _hash_table.append(list())
    _memory_location = 0;
    _word_length = _bit_length/8
    _initilized = True

def setVerbose(_bool):
#Set the verbose for more output from this module
    global VERBOSE
    VERBOSE = _bool

def newScope():
#sets new scope for symbol
    global _scope
    _scope += 1

def clearScope():
#clears current scope symbols from table and string space
#returns scope to previous level, this means that the scoping is dynamic
    global _hash_table, _scope, _string_space, _word_length, _memory_location
    for bucket in _hash_table:
        if len(bucket) > 0:
            if bucket[-1].scope == _scope:
                #print len(_string_space)
                #print  _string_space[:len(_string_space) - bucket[-1].length]
                _string_space = _string_space[:len(_string_space) - bucket[-1].length]
                _memory_location -= _word_length
                bucket.pop()
    _scope -= 1

def enterSymbol(symbol):
#enter a symbol into the current scope.
#symbol must be of token tuple type (ID, <symbol name>)
    global _scope, _hash_table, _string_space, _memory_location, _word_length
    length = len(symbol[1])
    offset = len(_string_space)
    scope = _scope
    pointer = _memory_location
    _hash_table[HASH(symbol[1])].append(record(length, offset, scope, pointer))
    _string_space += symbol[1]
    _memory_location += _word_length
    
def getPointer(symbol):
#retrieve a symbol's pointer. returns None if symbol does not exist
#symbol must be of token tuple type (ID, <symbol name>)
    global _scope, _hash_table, _string_space
    global _memory_location, _word_length, VERBOSE
    hash_index = HASH(symbol[1])
    if len(_hash_table[hash_index]) == 0: 
        return None
    for i in range(1, 1 + len(_hash_table[hash_index])):
        rec = _hash_table[hash_index][-i]
        if _string_space[rec.offset:(rec.offset+rec.length)] == symbol[1]:
            if rec.scope == _scope:
                return _hash_table[hash_index][-i].pointer
    if VERBOSE: 
        print "/Error/SymbolTable/getPointer/ symbol does not exist"
    return None

def getLocationString(symbol):
#retrieve string representation. returns None if symbol does not exist
#symbol must be of token tuple type (ID, <symbol name>)
    return_string = getPointer(symbol)
    if return_string != None: 
        return_string = "["+str(return_string)+"]"
        return return_string
    else:
        return None
    
    
def HASH(_string_input):
#pre:  takes a string input
#post: returns a number between 0 and HASTABLESIZE
    hash_result = ord(_string_input[0]) * ord(_string_input[-1])
    for letter in _string_input[1:]:
        hash_result += ord(letter)
        hash_result << 2
    return (hash_result % HASTABLESIZE)

def display():
    for bucket in _hash_table:
        print "Bucket:"
        if len(bucket) > 0:
            for rec in bucket:
                print "   symbol: " + _string_space[rec.offset:(rec.offset+rec.length)], "   \t",
            print
            for rec in bucket:
                print "   offset:", rec.offset, "\t", "\t",
            print
            for rec in bucket:
                print "   length:", rec.length, "\t", "\t",
            print
            for rec in bucket:
                print "    scope:", rec.scope, "\t", "\t",
            print
        else:
            print "  Empty."

def main():
    initilize(0)
    newScope()
    a = ["ID", "temp&1"]
    enterSymbol(a)
    newScope()
    a = ["ID", "temp&2"]
    enterSymbol(a)
    newScope()
    a = ["ID", "temp&3"]
    enterSymbol(a)

    display()
    
    clearScope()
    print
    
    
    display()

"""
    from pprint import pprint; pprint(_hash_table)
    for c in"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
        _hash_table[HASH(c)].append(c)
    c = "HASH_TABLE"
    _hash_table[HASH(c)].append(c)
    c = "pies"
    _hash_table[HASH(c)].append(c)
    c = "cast"
    _hash_table[HASH(c)].append(c)
    c = "cats"
    _hash_table[HASH(c)].append(c)

    from pprint import pprint; pprint(_hash_table)
    pass
"""
if __name__ == '__main__':
    main()

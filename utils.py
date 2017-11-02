#!/usr/bin/env python2
import sys

"""itobl
Converts an integer to a byte list

@param {Int} value - integer value
@return {ByteList} Byte List created
"""
def itobl(value):
    hexValue = hex(value)
    cutHexValue = hexValue[2:]
    byteList = list(cutHexValue.decode("hex"))
    return byteList

"""htobl
Converts a hex value (with or without the '0x') to a ByteList

@param {Hex} value - hex value (does not need to be an even value)
@return {ByteList} Byte List created
"""
def htobl(value):
    #Removes 0x if exists
    if value[1] == 'x':
        value = value[2:]
    #Adds 0 to beginning if an odd number of values
    if len(value) % 2 == 1:
        value = '0'+value

    byteList = list(value.decode("hex"))
    return byteList

"""bltoh
Converts a byte list to a hex number with the '0x'

@param {ByteList} value - list of byte characters
@return {Hex} Hex value created
"""
def bltoh(value):
    binaryStr = ''
    byteString = ''.join(str(s) for s in value)
    for char in byteString:
        binaryStr += '{0:08b}'.format(ord(char))
    intValue = int(binaryStr, 2)
    hexValue = hex(intValue)
    return hexValue

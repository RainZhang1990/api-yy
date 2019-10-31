__author__ = 'zeewell'
#
# Converts any integer into a base [BASE] number. I have chosen 62
# as it is meant to represent the integers using all the alphanumeric
# characters
#
# decode()  takes the base 62 key, as a string, and turns it back into an integer
# encode() takes an integer and turns it into the base 62 string
#
import math


BASE = 62

bit_char = ('y', '4', '8', 'a', 'b', '1', 'z', 'M', 'V', 'H',
            '6', 'f', 'o', 'p', 'R', 'P', 'X', 'q', 'c', 'G',
            '3', 'h', 'l', 'E', '0', 'v', 'T', 's', 'm', 'B',
            'j', 'k', 'n', 'W', 'w', 'I', 'O', 'F', 'e', 'N',
            'S', '5', '7', '2', 'g', 'i', 'A', 'K', 'J', 'u',
            '9', 'D', 'Z', 't', 'r', 'd', 'x', 'C', 'L', 'Q',
            'U', 'Y')


def encode(integer):
    """
    Turn an integer [integer] into a base [BASE] number
    in string representation
    """

    # we won't step into the while if integer is 0
    # so we just solve for that case here
    if integer == 0:
        return _turn_chr(0)

    string = ''
    while integer > 0:
        integer, remainder = divmod(integer, BASE)
        string = _turn_chr(remainder) + string
    return string


def decode(string):
    """
    Turn the base [BASE] number [key] into an integer
    """
    int_sum = 0
    reversed_string = string[::-1]
    for idx, char in enumerate(reversed_string):
        int_sum += _turn_ord(char) * int(math.pow(BASE, idx))
    return int_sum


def _turn_ord(char):
    """
    Turns a digit [char] in character representation
    from the number system with base [BASE] into an integer.
    """
    try:
        index = bit_char.index(char)
        return index
    except ValueError as e:
        raise ValueError("%s is not a valid character" % char)


def _turn_chr(integer):
    """
    Turns an integer [integer] into digit in base [BASE]
    as a character representation.
    """
    if integer < 62:
        return bit_char[integer]
    else:
        raise ValueError("%d is not a valid integer in the range of base %d" % (integer, BASE))

if __name__ == '__main__':
    labels(encode(9007199254740992))

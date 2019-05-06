#!/usr/bin/python3

from functools import reduce
 
# constants used in the multGF2 function
mask1 = mask2 = polyred = None
 
def setGF2(degree, irPoly):
    """Define parameters of binary finite field GF(2^m)/g(x)
       - degree: extension degree of binary field
       - irPoly: coefficients of irreducible polynomial g(x)
    """
    global mask1, mask2, polyred
    mask1 = mask2 = 1 << degree
    mask2 -= 1
    if sum(irPoly) <= len(irPoly):
        polyred = reduce(lambda x, y: (x << 1) + y, irPoly[1:])    
    else:
        polyred = poly2Int(irPoly[1:]) 
         
def multGF2(p1, p2):
    """Multiply two polynomials in GF(2^m)/g(x)"""
    p = 0
    while p2:
        if p2 & 1:
            p ^= p1
        p1 <<= 1
        if p1 & mask1:
            p1 ^= polyred
        p2 >>= 1
    return p & mask2
 
#=============================================================================
#                        Auxiliary formatting functions
#=============================================================================
def int2Poly(bInt):
    """Convert a "big" integer into a "high-degree" polynomial"""
    exp = 0
    poly = []
    while bInt:
        if bInt & 1:
            poly.append(exp)
        exp += 1
        bInt >>= 1
    return poly[::-1]
 
def poly2Int(hdPoly):
    """Convert a "high-degree" polynomial into a "big" integer"""
    bigInt = 0
    for exp in hdPoly:
        bigInt += 1 << exp
    return bigInt
 
def i2P(sInt):
    """Convert a "small" integer into a "low-degree" polynomial"""
    return [(sInt >> i) & 1 for i in reversed(range(sInt.bit_length()))]
 
def p2I(ldPoly):
    """Convert a "low-degree" polynomial into a "small" integer"""
    return reduce(lambda x, y: (x << 1) + y, ldPoly)
 
def ldMultGF2(p1, p2):
    """Multiply two "low-degree" polynomials in GF(2^n)/g(x)"""
    return multGF2(p2I(p1), p2I(p2))
 
def hdMultGF2(p1, p2):
    """Multiply two "high-degree" polynomials in GF(2^n)/g(x)"""
    return multGF2(poly2Int(p1), poly2Int(p2))
 
if __name__ == "__main__":
    # Define binary field GF(2^8)/x^8 + x^4 + x^3 + x + 1
    setGF2(8, [1, 0, 0, 0, 1, 1, 0, 1, 1])
     
    # Alternative way to define GF(2^8)/x^8 + x^4 + x^3 + x + 1
    setGF2(8, i2P(0b100011011))
     
    # Check if (x)(x^7 + x^2 + x + 1) == x^4 + x^2 + 1
    assert ldMultGF2([1, 0], [1, 0, 0, 0, 0, 1, 1, 1]) == p2I([1, 0, 1, 0, 1])

    print(int2Poly(hdMultGF2([2,0], [44,6,4,1])))

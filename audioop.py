# fake audioop compatibility for Python 3.13

def add(a, b, width=None): return a
def mul(a, factor, width=None): return a
def avg(a, b, width=None): return a
def rms(a, width=None): return 0
def max(a, width=None): return 0
def avgpp(a, width=None): return 0
def cross(a, b, width=None): return 0
def tomono(a, width, lfac, rfac): return a
def tostereo(a, width, lfac, rfac): return a
def getsample(a, width, i): return 0
def bias(a, width, bias): return a
def lin2lin(a, inwidth, outwidth): return a
def ratecv(a, width, nchannels, inrate, outrate, state, weightA=1, weightB=0): return a, None

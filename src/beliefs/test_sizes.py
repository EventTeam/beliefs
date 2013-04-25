
def choose(n, k):
    """
    A fast way to calculate binomial coefficients by Andrew Dalke (contrib).
    """
    if 0 <= k <= n:
        ntok = 1
        ktok = 1
        for t in xrange(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    else:
        return 0

def factorial(n, start=1):
    result = 1
    assert start <= n
    for i in xrange(start, abs(n)+1):
        result *= i
    if n >= 0:
        return result
    else:
        return -result

def binomial(n, k, klow=1):
    """binomial(n, k): return the binomial coefficient (n k)."""
    if k < 0 or k > n: return 0
    if k == 0 or k == n: return 1
    return factorial(n) // (factorial(k) * factorial(n-k))

def binomial_range2(n, k_low, k_high):
    assert k_low <= k_high
    return sum([binomial(n, i) for i in range(k_low, k_high+1)])

def binomial_range(n, k_low, k_high):
    """ Takes advantage of Pascal's proof to cut the number
    of operations in half when the difference is even """
    assert k_low <= k_high
    diff = k_high - k_low 
    if diff % 2 != 0 or diff == 0:
        return sum([binomial(n, i) for i in range(k_low, k_high+1)])
    else: 
        return sum([binomial(n+1, i+1) for i in range(k_low, k_high+1, 2)])

def binomial_range3(n, k_low, k_high):
    """
    nCk = n! / k!(n-k)!
    nCk + nC(k-1) = (n+1)! / k!(n-k+1)!

    Therefore...

    \sum_{k=i}^{j}\binom{N}{k} = \frac{(N + j - i)!}{j!(N-i)!}
    """
    diff = k_high - k_low 
    print "%iC%i - %iC%i => %iC%i" % (n, k_low, n, k_high, n+diff, k_high)
    return binomial(n+diff, k_high)

    print "NUM", factorial(n+diff)
    print "DENOM", factorial(k_high), factorial(n-k_low), 
    print "=", factorial(k_high) * factorial(n-k_low)
    if k_low > k_high or k_high < 0 or k_high > n: return 0
    #if k_high == 0 or k_high == n: return 1
    return factorial(n+diff) // (factorial(k_high) * factorial(n-k_low))

    #return sum([binomial(n, i) for i in range(k_low, k_high+1)])

"""
Generate a powerset within certain bounds

From highest to lowest
"""

# target bounds
tlow, thigh = 0, 999999999

# distractor bounds
dlow, dhigh = 1, 999999999

# size of context set
cs = 6

# number of referents (singletons)
t = 5 

# number of distractors
d = cs - t

targets = range(t)
import itertools
import timeit

def powersetr(t, low, high):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(range(t))
    return itertools.chain.from_iterable(itertools.combinations(s, r) 
            for r in reversed(xrange(low, high)))

low = max(0, tlow) - 1
high = min([t+ 1,  thigh, t-(dlow+1)])
print "low",low, "high", high
print binomial_range(t,1,4) #  35 
print binomial_range2(t,1,4) #  35 
print "\n"
print binomial_range(t,2,3) # 20
print binomial_range2(t,2,3) # 20
print binomial_range(t,3,3) # 10
print binomial_range2(t,3,3) # 10

print binomial_range(3,1,3)
print binomial_range2(3,1,3)
#print timeit.Timer('choose(10,5)', setup='from __main__ import choose, binomial').timeit()  # 7.2sec
#print timeit.Timer('binomial(10,5)', setup='from __main__ import choose, binomial').timeit()  # 7.2sec
print timeit.Timer('binomial_range(t,low,high)', setup='from __main__ import binomial_range, t, low, high').timeit()  # 7.2sec
print timeit.Timer('binomial_range2(t,low,high)', setup='from __main__ import binomial_range2, t, low, high').timeit()  # 7.2sec
#print timeit.Timer('len(list(powersetr(t,low,high)))', setup='from __main__ import powersetr, t, low, high').timeit() # 104 sec
##print timeit.Timer('powersetr([0,1,2,3,4,5,6,7,8])', setup='from __main__ import powersetr').timeit()


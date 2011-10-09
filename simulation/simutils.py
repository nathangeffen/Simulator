from math import exp, log

def proportion(values):
    return len(list(filter(lambda x: x, values))) / len(values)

def mean(values):
    return sum(values) / len(values)

def median(values):
    values = sorted(values)
    length = len(values)
        
    if length == 0:
        raise ValueError("median() arg is an empty sequence")
    elif length == 1:
        return values[0]
    elif length % 2 == 0:
        return (values[length//2] + values[length//2+1]) / 2
    else:
        return values[length // 2 + 1]
    
def normalise_compounded_proportion(proportion, 
                                    time_period_from,
                                    time_period_to):
    print ("In ncp")
    n = time_period_from / time_period_to
    c = proportion + 1.0 
    print ("Debug: ", proportion, n, c, exp(log(c)/n) - 1)
    # x^n = c ; we must solve for x
    # n*ln(x) = ln(c)
    # ln(x) = ln(c)/n
    # x = exp(ln(c)/n)   
    # Finally subtract the 1 that was added in the previous statement 
    return exp(log(c)/n) - 1



def normalise_linear_proportion(proportion, 
                                time_period_from,
                                time_period_to):
    return proportion / (time_period_from / time_period_to) 


ncp = normalise_compounded_proportion
nlp = normalise_linear_proportion

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

def get_precursor_mz(exact_mass, precursor_type):
    # these are just taken from what was present in the massbank .msp file for those missing the exact mass
    d = {'[M-H]-': -1.007276,
         '[M+H]+': 1.007276,
         '[M+H-H2O]+': 1.007276 - ((1.007276 * 2) + 15.9949)
         }

    try:

        return exact_mass + d[precursor_type]
    except KeyError as e:
        print(e)
        return False


def line_count(fn):
    with open(fn) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
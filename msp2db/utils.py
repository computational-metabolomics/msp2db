def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

def get_precursor_mz(exact_mass, precursor_type):
    """ Calculate precursor mz based on exact mass and precursor type

    Args:
        exact_mass (float): exact mass of compound of interest
        precursor_type (str): Precursor type (currently only works with '[M-H]-', '[M+H]+' and '[M+H-H2O]+'

    Return:
          neutral mass of compound
    """

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
    """ Get line count of file

    Args:
        fn (str): Path to file

    Return:
          Number of lines in file (int)
    """

    with open(fn) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def get_blank_dict(d):
    """ Remove values from dictionary

    Args:
        d (dict): any dictionary

    Return:
          dictionary with blank values
    """
    return {k: '' for k in d.keys()}
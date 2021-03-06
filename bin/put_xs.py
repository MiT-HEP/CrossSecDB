#! /usr/bin/python

"""
Usage:

  put_xs.py [--comments=COMMENTS] SOURCE SAMPLE XSEC [SAMPLE XSEC [SAMPLE XSEC]]]

Put the cross sections for a sample or list of samples into the central database.
The comments flag is optional. The SOURCE parameter is not.
Remeber that arguments with spaces should be in quotes.

To add a sample with uncertainties, place a '+-' inside of the XSEC argument.

By default, the my.cnf configuration file is a centrally maintained one.
To point to your own file, set the environment variable $XSECCONF to the location.

Also by default, the samples are read off of the 13 TeV table.
To change energies, set the environment variable $ENERGY to something different.

Examples:

  put_xs.py "Source is uncertain" example_sample 10.0 example_with_uncertainty 10.0+-2.0
  XSECCONF=$HOME/my.cnf ENERGY=8 put_xs.py --comments="This is old, I know" "My memory" sample_i_want_to_store_elsewhere 0.5

Author:

  Daniel Abercrombie <dabercro@mit.edu>
"""

import os
import sys

from CrossSecDB.inserter import put_xsec

if __name__ == '__main__':

    if len(sys.argv) < 4 or sys.argv[1] in ['-h', '--help']:
        print __doc__
        exit(0)

    # Get the comments, if there
    comments = '='.join(sys.argv.pop(1).split('=')[1:]) \
        if sys.argv[1].startswith('--comments=') else ''

    # Get the source
    source = sys.argv[1]

    # Get the samples, cross sections, and uncertainties

    samples = sys.argv[2::2]

    xs = []
    unc = []
    for xs_arg in sys.argv[3::2]:
        splitted = xs_arg.split('+-')
        xs.append(float(splitted[0]))

        if len(splitted) > 1:
            unc.append(float(splitted[1]))
        else:
            unc.append(0.0)

    # Finally, get the energy
    energy = int(os.environ.get('ENERGY', 13))

    put_xsec(samples, xs, source, comments, energy=energy, uncertainties=unc)

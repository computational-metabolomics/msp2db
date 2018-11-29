#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals, print_function
import argparse
import os
from .parse import LibraryData
from .db import create_db


def main():
    p = argparse.ArgumentParser(prog='PROG',
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                description='''Convert msp to SQLite or MySQL database''',
                                epilog='''--------------''')

    p.add_argument('-msp_pth', dest='msp_pth', help='path to the MSP file (or directory of msp files)', required=True)

    p.add_argument('-name', dest='name', help='name of the database', required=True)
    p.add_argument('-source', dest='source', help='Name of data source (e.g. MassBank, LipidBlast)', required=True)
    p.add_argument('-o', dest='out_dir', help='out directory for SQLite database', required=False)
    p.add_argument('-t', dest='type', help='database type [mysql, sqlite]', required=False, default='sqlite')
    p.add_argument('-dt', dest='dt', help='delete tables', action='store_true')
    p.add_argument('-mslevel', dest='mslevel', help='ms level of fragmentation if not detailed in msp file',
                   required=False)
    p.add_argument('-chunk', dest='chunk', help='Chunks of spectra to parse data (useful to control memory usage)', default=200)
    p.add_argument('-schema', dest='schema', help='Type of schema used (by default can use Massbank style or MSP or mona style'
                                                  'msp', default='mona')

    p.add_argument('-msp_file', dest='msp_file', help='(deprecated, please use msp_pth)', required=False)
    args = p.parse_args()

    if args.type == 'sqlite':

        if not os.path.exists(args.out_dir):
            os.makedirs(args.out_dir)

        db_pth = os.path.join(args.out_dir, args.name + '.db')
        if not os.path.exists(db_pth) or args.dt:
            create_db(db_pth)

    else:
        if args.dt:
            create_db(file_pth=None)

        db_pth = None

    if args.msp_file:
        print('msp_file is now deprecated please use msp_pth')
        return

    if not args.mslevel:
        args.mslevel = 0

    if args.chunk:
        libdata = LibraryData(msp_pth=args.msp_pth,

                              db_pth=db_pth if db_pth else None,
                              db_type=args.type,

                              source=args.source,
                              mslevel=args.mslevel,
                              schema=args.schema,
                              chunk=int(args.chunk))
    else:
        libdata = LibraryData(msp_pth=args.msp_pth,

                              db_pth=db_pth if db_pth else None,
                              db_type=args.type,

                              source=args.source,
                              schema=args.schema,
                              mslevel=args.mslevel)
        libdata.insert_data()


if __name__ == '__main__':
    main()
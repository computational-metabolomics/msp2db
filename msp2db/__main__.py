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

    p.add_argument('-m', '--msp_pth', dest='msp_pth', help='path to the MSP file (or directory of msp files)', required=True)
    p.add_argument('-s', '--source', dest='source', help='Name of data source (e.g. MassBank, LipidBlast)', required=True)
    p.add_argument('-o', '--out_pth', dest='out_pth', help='file path for SQLite database', required=False)
    p.add_argument('-t', '--db_type', dest='type', help='database type [mysql, sqlite]', required=False, default='sqlite')
    p.add_argument('-d', '--delete_tables',  dest='dt', help='delete tables', action='store_true')
    p.add_argument('-l', '--mslevel', dest='mslevel', help='ms level of fragmentation if not detailed in msp file', required=False)
    p.add_argument('-c', '--chunk', dest='chunk', help='Chunks of spectra to parse data (useful to control memory usage)', default=200)
    p.add_argument('-x', '--schema', dest='schema', help='Type of schema used (by default is "mona" msp style but can use "massbank" style', default='mona')

    args = p.parse_args()

    if args.type == 'sqlite':
        db_pth = args.out_pth
        if not os.path.exists(db_pth) or args.dt:
            create_db(db_pth)

    else:
        if args.dt:
            create_db(file_pth=None)

        db_pth = None



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
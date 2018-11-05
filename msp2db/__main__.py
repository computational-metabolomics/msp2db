#!/usr/bin/env python
from __future__ import absolute_import, unicode_literals, print_function
import argparse
from .msp2db import LibraryData


def main():
    p = argparse.ArgumentParser(prog='PROG',
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                description='''Convert msp to SQLite or MySQL database''',
                                epilog='''--------------''')

    p.add_argument('-msp_file', dest='msp_file', help='path to the MSP file', required=True)
    p.add_argument('-name', dest='name', help='name of the database', required=True)
    p.add_argument('-source', dest='source', help='Name of data source (e.g. MassBank, LipidBlast)', required=True)
    p.add_argument('-o', dest='out_dir', help='out directory', required=False)
    p.add_argument('-t', dest='type', help='database type [mysql, sqlite]', required=True)
    p.add_argument('-dt', dest='dt', help='delete tables', action='store_true')
    p.add_argument('-mslevel', dest='mslevel', help='ms level of fragmentation if not detailed in msp file',
                   required=False)
    p.add_argument('-chunk', dest='chunk', help='Memory efficient chunks to parse data')

    args = p.parse_args()

    if args.type == 'sqlite':

        if not os.path.exists(args.out_dir):
            os.makedirs(args.out_dir)

        db_pth = os.path.join(args.out_dir, args.name + '.db')
        if not os.path.exists(db_pth) or args.dt:
            create_db(db_pth, db_type=args.type, db_name=args.name)

    else:
        if args.dt:
            create_db(file_pth=None, db_type=args.type, db_name=args.name)

        db_pth = None

    if args.type == 'django_mysql':
        d_form = True
    else:
        d_form = False

    print(db_pth, args.dt)

    if not args.mslevel:
        args.mslevel = 0

    if args.chunk:
        libdata = LibraryData(msp_pth=args.msp_file,
                              name=args.name,
                              db_pth=db_pth if db_pth else None,
                              db_type=args.type,
                              d_form=d_form,
                              source=args.source,
                              mslevel=args.mslevel,
                              chunk=int(args.chunk))
    else:
        libdata = LibraryData(msp_pth=args.msp_file,
                              name=args.name,
                              db_pth=db_pth if db_pth else None,
                              db_type=args.type,
                              d_form=d_form,
                              source=args.source,
                              mslevel=args.mslevel)
        libdata.insert_data()


if __name__ == '__main__':
    main()
#!/bin/env python

"""
parseboards.py
jlazear
2013-07-31

Parsing boards.txt files.

"""
import os
from numpy import *
from types import StringTypes
from HKEBinaryFile import HKEBinaryFile


def parse_boards_file(f):
    if not isinstance(f, StringTypes):
        f = f.name

    boards = {'description': None, 'dewar': None,
              'temperature': {'address': None, 'channel': None},
              'boards': {}}

    with open(f, 'r') as fi:
        board = {}
        for line in fi:
            line = line.strip()
            if line.startswith('BOARD,'):
                if board:
                    addr = board['address']
                    boards['boards'][addr] = board
                board = {'registers': {}}
                addr, btype, name = parse_board_line(line)
                board['address'] = addr
                board['type'] = btype
                board['name'] = name
            elif line.startswith('REGISTER,'):
                rtype, ch, name = parse_register_line(line)
                rdict = board['registers']
                subdict = {}
                subdict['type'] = rtype
                subdict['channel'] = ch
                subdict['name'] = name
                rdict[ch] = subdict
            elif line.startswith('#DESCRIPTION, '):
                desc = parse_description_line(line)
                boards['description'] = desc
            elif line.startswith('#DEWAR, '):
                dewar = parse_dewar_line(line)
                boards['dewar'] = dewar
            elif line.startswith('#TBOARD, '):
                tregister = parse_tregister_line(line)
                boards['temperature']['address'] = tregister
            elif line.startswith('#TCHANNEL, '):
                tchannel = parse_tchannel_line(line)
                boards['temperature']['channel'] = tchannel
    return boards

def parse_board_line(line):
    line = line.replace(',', '', 3)     # Remove commas
    sline = line.split(' ', 3)
    addr, btype, name = sline[1:]
    addr = int(addr, 16)
    btype = btype.lower()
    return addr, btype, name

def parse_register_line(line):
    line = line.replace(',', '', 3)     # Remove commas
    sline = line.split(' ', 3)
    rtype, ch, name = sline[1:]
    ch = int(ch[3:])
    name = name[5:]
    return rtype, ch, name

def parse_description_line(line):
    sline = line.split(', ', 1)
    return sline[1]

def parse_dewar_line(line):
    sline = line.split(', ', 1)
    return sline[1]

def parse_tregister_line(line):
    sline = line.split(', ', 1)
    return int(sline[1], 16)

def parse_tchannel_line(line):
    sline = line.split(', ', 1)
    return int(sline[1])

def construct_register_name(boardsdict, address, rtype='Demod'):
    board = boardsdict[address]
    name = board['name']
    btype = board['type']
    typedict = {'tread_standard': 'TRead_Standard',
                'tread_lr': 'TRead_LR',
                'tread_diode': 'TRead_Diode',
                'dspid': 'DSPID',
                'pmaster': 'PMaster',
                'analog_in': 'Analog_In',
                'analog_out': 'Analog_Out'}
    btype = typedict[btype]

    rstring = '{name} ({addr}-{btype}): {rtype}'.format(name=name,
                                                        addr=address,
                                                        btype=btype,
                                                        rtype=rtype)
    return rstring

def save_board_file(boardsdict, f, eol='\r\n'):
    if not isinstance(f, StringTypes):
        f = f.name

    with open(f, 'w') as fi:
        desc = boardsdict['description']
        if desc is None:
            desc = ''
        dewar = boardsdict['dewar']
        if dewar is None:
            dewar = ''
        tdict = boardsdict['temperature']
        if tdict['address'] is None:
            tboard = ''
        else:
            tboard = "{0:X}".format(tdict['address'])
        if tdict['channel'] is None:
            tchannel = ''
        else:
            tchannel = int(tdict['channel'])
        linestr = "#{0}, {1}" + eol
        fi.write(linestr.format('DESCRIPTION', desc))
        fi.write(linestr.format('DEWAR', dewar))
        fi.write(linestr.format('TBOARD', tboard))
        fi.write(linestr.format('TCHANNEL', tchannel))
        fi.write(eol)

        towrite = ("# Available board types: PMASTER, DSPID, TREAD_STANDARD,"
                   " TREAD_LR, TREAD_HR, TREAD_DIODE, ANALOG_IN, ANALOG_OUT")
        fi.write(towrite + eol + eol)

        boardstr = "BOARD, {addr:X}, {type}, {name}" + eol
        regstr = "\tREGISTER, {type}, CH={ch}, NAME={name}" + eol

        for i, board in boardsdict['boards'].items():
            addr = board['address']
            t = board['type'].upper()
            name = board['name']

            fi.write(boardstr.format(addr=addr, type=t, name=name))

            for i, register in board['registers'].items():
                ch = register['channel']
                name = register['name']
                t = register['type']

                fi.write(regstr.format(type=t, ch=ch, name=name))
            fi.write(eol)

def generate_from_datafile(fname, outname=None, eol='\r\n', verbose=False,
                           overwrite=False):
    if isinstance(fname, StringTypes):
        f = HKEBinaryFile(fname)
    else:
        f = fname

    filename = os.path.abspath(f.filename)

    if outname is None:
        fn, ext = os.path.splitext(filename)
        outname = fn + '_boards.txt'

    # Abort if file already exists and overwrite flag is False
    if (not overwrite) and os.path.exists(outname):
        return False

    boardsdict = {}
    header = f.header
    bds = header.boarddescriptions
    for bd in bds:
        addr = bd.address
        t = bd.boardtype.lower()
        name = bd.description
        rdict = {}
        try:
            rd = bd.registers['Demod']
            for i, chtag in enumerate(rd.chtags):
                if chtag:
                    chdict = {'channel': i, 'name': chtag, 'type': 'Demod'}
                    rdict[i] = chdict
        except KeyError:
            pass
        bddict = {'address': addr, 'name': name, 'type': t,
                  'registers': rdict}
        boardsdict[addr] = bddict

    boards = {'description': None, 'dewar': None,
              'temperature': {'address': None, 'channel': None},
              'boards': boardsdict}

    save_board_file(boards, f=outname, eol=eol)

    if verbose:
        msgstr = "Created boards file {b} corresponding to data file {d}"
        toprint = msgstr.format(b=outname, d=filename)
        print toprint

    return outname


#! /usr/bin/env python
#
# This is a utility application that lets the user explore a NITF file interactively
# on the console

import readline
import shlex
import pydoc
from geocal import *
from geocal.nitf import *

version="%prog July 7, 2017"
usage="""Usage:
  explore_nitf.py [-hvc COMMAND] <nitf_file>

Options:
  -h --help     Print this message
  -v --version  Print program version
  -c COMMAND    Run program executing command, command needs to be a single string

This is a utility application that lets the user explore a NITF file interactively 
on the console   
       
"""

helpString = '''Usage Example:

list seg
list image
list des
list tre
list tre file
list tre image
list tre image 1
        
summary
summary file
summary image
summary image 1
        
print file
print image
print image 1
print text
print text 1
print des
print des 1
print tre file
print tre image
print tre image 1
print tre image 1(image_index) 1(tre_index)

data 10000(offset) 50(size)
data image 1(index) 0(offset) 100(size)
'''

def listTRESegment(segment, p=False):
    if (hasattr(segment, 'tre_list') == True):
        for a in range(len(segment.tre_list)):
            print("%d: %s" % (a, segment.tre_list[a].cetag_value()))
            if (p == True):
                print(segment.tre_list[a])

def listTREFile(f, p=False):
    for a in range(len(f.tre_list)):
        print("%d: %s" % (a, f.tre_list[a].cetag_value()))
        if (p == True):
            print(f.tre_list[a])

def listImageSegments(f):
    for a in range(len(f.image_segment)):
        print("%d: %s" % (a, f.image_segment[a].subheader.iid1))

def listTextSegments(f):
    for a in range(len(f.text_segment)):
        print("%d: %s" % (a, f.text_segment[a].subheader.txtitl))

def listDESSegments(f):
    for a in range(len(f.des_segment)):
        print("%d: %s" % (a, f.des_segment[a].subheader.desid))

def processTRE(f, param, p):
    # List all TREs that are used in this NITF file
    if (len(param) == 0):
        listTREFile(f)
        for i in f.image_segment + f.graphic_segment + f.text_segment + f.des_segment + f.res_segment:
            listTRESegment(i, p)

    # List all TREs that are used at the file level
    elif (param[0] == "file"):
        listTREFile(f, p)

    # List TREs in Image Segments
    elif (param[0] == "image"):
        #Print/List all TREs for all image segments
        if (len(param) == 1):
            for i in f.image_segment:
                listTRESegment(i, p)
        #Print/List all TREs for a particular image segment
        else:
            index = int(param[1])
            if (index < len(f.image_segment)):
                if ((len(param) == 3)):
                    treIndex = int(param[2])
                    if (treIndex < len(f.image_segment[index].tre_list)):
                        print (f.image_segment[index].tre_list[treIndex])
                    else:
                        print ("Select TRE Index 0 - %d" % (len(f.image_segment[index].tre_list) - 1))
                else:
                    listTRESegment(f.image_segment[index], p)
            else:
                print("Select Image Segment Index 0 - %d" % (len(f.image_segment) - 1))

def processCommand(line):
    cmd, args = line[0], line[1:]

    if cmd == 'help':
        print(helpString)

    elif cmd == 'list':
        if (len(args) == 0):
            print ("seg image text des tre")
            return

        tar, param = args[0], args[1:]

        if (tar == 'seg'):
            print ("Image Segments:")
            listImageSegments(f)
            # print("Graphic Segments")
            # for i in f.graphic_segment:
            #    print(i.subheader.iid1)
            print("Text Segments:")
            listTextSegments(f)
            print("DESs:")
            listDESSegments(f)
            # print("RESs:")
            # for i in f.res_segment:
            #    print(i.subheader.iid1)
        elif (tar == 'image'):
            listImageSegments(f)
        elif (tar == 'text'):
            listTextSegments(f)
        elif (tar == 'des'):
            listDESSegments(f)
        elif (tar == 'tre'):
            processTRE(f, param, False)

    elif cmd == 'summary':
        # print(f.summary())
        print("Summary functionality not yet implemented")

    elif cmd == 'print':
        tar, param = args[0], args[1:]

        if (len(args) == 0):
            print ("tre seg file")
            return

        if (tar == 'file'):
            pydoc.pager(str(f))
        elif (tar == 'image' or tar == 'text' or tar == 'des'):
            segs = vars(f)[tar + '_segment']
            if (len(param) == 0):
                output = ""
                for seg in segs:
                    output += str(seg)
                pydoc.pager(output)
            else:
                index = int(param[0])
                if (index < len(segs)):
                    pydoc.pager(str(segs[index]))
                else:
                    print("Select %s Segments 0 - %d" % (tar, len(segs) - 1))
        elif (tar == 'tre'):
            processTRE(f, param, True)

    elif cmd == 'data':
        print("Data functionality not yet implemented")

    else:
        print('Unknown command: {}'.format(cmd))

a = docopt_simple(usage, version=version)
f = NitfFile(a.nitf_file)

command = a.args['-c']
print(type(command))
if (type(command) == str):
    processCommand(command.split(' '))
else:
    print('Enter a command to do something, e.g. `list tre`.')
    print('To get help, enter `help`.')

    while True:
        line = shlex.split(input('> '))
        if len(line) == 0:
            continue

        cmd = line[0]
        if cmd == 'exit':
            break
        else:
            processCommand(line)
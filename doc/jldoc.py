#!/usr/bin/env python
# This program extracts comments and code from julia
# source code from standard input and outputs a sphinx rst file.

import sys
from collections import defaultdict

def funcname(line):
    f = line.split()
    i = f[1].find('{')
    if i >= 0:
        return f[1][:i]
    i = f[1].index('(')
    return f[1][:i]

def typename(line):
    return line.split()[1]

def modulename(line):
    return line.split()[1]

def constname(line):
    return line.split()[1]

def printtitle(title, c='-'):
    print(title)
    print(c*len(title))

def printfunc(funcdocs):
    for sig, doc in funcdocs:
        print(".. function::", sig[len("function"):])
        print(''.join(doc))

def printcode(lines):
    print(".. code-block:: julia\n")
    for line in lines:
        print("\t%s" % line, end='')
    print("")

def printmodule(name, comments):
    synopsis = ''
    if len(comments) > 0:
        synopsis = comments[0].strip()
        comments = comments[1:]
    printtitle(name+' --- '+synopsis, '=')
    print('')
    print('.. module:: ', name)
    if synopsis != '':
        print('\t:synopsis: ', synopsis)
    print(''.join(comments))

def main():
    print(".. This file was auto-generated using jldoc.py.")
    print("   DO NOT EDIT THIS FILE.")
    print("   Edit the original Julia source code with the documentation.")
    print("")
    comments = []
    funcdoc = defaultdict(list)
    funclist = []
    typedoc = defaultdict(list)
    typelist = []
    constants = []
    while True:
        line = sys.stdin.readline()
        if line == '':
            break
        if line.startswith('#'):
            if line[1] == ' ':
                comments.append(line[2:])
            else:
                comments.append(line[1:])
        elif line.startswith('function'):
            name = funcname(line)
            if name not in funclist:
                funclist.append(name)
            funcdoc[name].append((line, comments))
            comments = []
        elif line.startswith('const'):
            if constname(line)[0] != '_':
                constants.append(line)
            comments = []
        elif line.startswith('module'):
            printmodule(modulename(line), comments)
            comments = []
        elif line.startswith('export'):
            printtitle("Exports")
            printcode([line])
            comments = []
        elif line.startswith('type'):
            name = typename(line)
            typelist.append(name)
            while True:
                s = line.strip()
                if line.startswith('end') or s.startswith('function') \
                        or (s != '' and s[0].isupper()):
                    typedoc[name].append("end\n")
                    break
                if s != '' and s[0] != '_':
                    typedoc[name].append(line)
                line = sys.stdin.readline()
                if line == '':
                    break
            comments = []
        else:
            comments = []

    printtitle("Constants")
    printcode(constants)

    for name in typelist:
        printtitle("Type " + name)
        printcode(typedoc[name])
        printfunc(funcdoc[name])

    for name in funclist:
        if name in typelist or name[0] == '_':
            continue
        printtitle("Function " + name)
        printfunc(funcdoc[name])

if __name__ == '__main__':
    main()

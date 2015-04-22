#! /usr/bin/python

import logging
import sys, os;
import re;
from argparse import ArgumentParser

logger = logging.getLogger('MIPSGENERATER')

reRuleRightQuote = re.compile("\[")

#
# regs are dict of dict
#
class InstFormat:

    def __init__(self): 
        print "initialize." 
        self.__instName = ''
        self.__regs = []
        self.__maxHex = 0
        self.__minHex = 0
        self.__instCode = ''

    def addReg(self, reg=dict()):
        self.__regs.append(reg)

    def addInstName(self, name = ""):
        self.__instName = name

    def getRegs(self):
        return self.__regs

    def reorganize(self):
        sortList = {}
        for i in range (0, len(self.__regs)):
            sortList.update({self.__regs[i].get('pos'):i})

        newRegs = []
        totaloffset = 0;
        instCode = self.__instCode
        for i in sorted(sortList.keys()):
            reg = self.__regs[sortList[i]]

            pos = reg.get('pos');
            regname = reg.get('regname')

            pos = pos - totaloffset;

            reg.update({'pos':pos})

            totaloffset += len(regname) - 1
            instCode = instCode.replace(regname, 'x')

            newRegs.append(reg)
        self.__regs = newRegs

        logger.debug("Organized regs :" + str(newRegs))

        logger.debug("Reg length is: " + str(len(instCode)))
        maxCode = instCode
        minCode = instCode

        logger.debug("MaxCode is " + maxCode)
        logger.debug("MinCode is " + minCode)
        for i in range(0, len(self.__regs)):
            reg = self.__regs[i]
            pos = reg.get('pos')
            width = reg.get('width')
            maxCode = maxCode[:pos] + '1' * width + maxCode[pos + width:]
            minCode = minCode[:pos] + '0' * width + minCode[pos + width:]
            logger.debug("MaxCode is " + maxCode)
            logger.debug("MinCode is " + minCode)

    def setCode(self, instCode = ''):
        self.__instCode = instCode


def setLogLevel():
    logger.setLevel(logging.DEBUG)
    hdr = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s]: %(funcName)s: %(levelname)s: %(message)s')
    hdr.setFormatter(formatter)
    logger.addHandler(hdr)

def checkLeftQuoteInCode(instCode = str('')):
    pos = []
    reRuleLeftQuote = re.compile("\[")
    matches = reRuleLeftQuote.finditer(instCode)
    for i in matches:
        pos.append(i.start())

    return pos

def checkRightQuoteInCode(instCode = str('')):
    pos = []
    reRuleLeftQuote = re.compile("\]")
    matches = reRuleLeftQuote.finditer(instCode)
    for i in matches:
        pos.append(i.start())

    return pos

# Return left and right quote position
def checkInQuote(leftQ = [], rightQ = [], pos = 0):
    for i in range(0, leftQ.__len__()):
        logger.debug("check " + str(pos) + " in " + str(leftQ[i]) + ":" + str(rightQ[i]))
        if pos > leftQ[i] and pos < rightQ[i]:
            return [leftQ[i], rightQ[i]]
    return []

def decodeInsts(instline = str('')):
    logger.debug(instline)
    instline = instline.strip()

    if not instline.__contains__(';'):
        logger.debug('Not a valid inst line')
        return -1

    if instline[0] == '#':
        logger.debug('Got quote line')
        return -1

    hasQuote = 0

    insts = instline.split(';')
    instFormat = insts[0].strip()
    instCode = insts[1].strip()

    leftQ = []
    rightQ = []

    leftQ = checkLeftQuoteInCode(instCode)
    if leftQ.__len__() > 0:
        hasQuote = 1

    if hasQuote == 1:
        rightQ = checkRightQuoteInCode(instCode)

        if leftQ.__len__() != rightQ.__len__():
            print "Bad quote! Instruction code not valid!"
            return -1

    inst = InstFormat()

    if instFormat.find(' ') > 0:
        instName = instFormat[0:instFormat.find(' ')]
        instLast = instFormat[instFormat.find(' '):]
    else:
        instName = instFormat
        instLast = ''

    logger.debug("instName: " + instName)
    inst.addInstName(instName)

    instLast = instLast.replace(' ', '')
    instLasts = re.split(',|\(|\)', instLast)

    logger.debug("InstLasts are: " + str(instLasts))
    for i in range(0, instLasts.__len__()):
        if instLasts[i] == '':
            continue;

        reg = {}

        search = instLasts[i]
        regname = search

        if hasQuote == 1:
            ret = checkInQuote(leftQ, rightQ, instCode.find(instLasts[i]))
            if ret.__len__() > 0:
                search = instCode[ret[0]:ret[1] + 1]
                regname = search
                search = search.replace('[', '\[')
                search = search.replace(']', '\]')

        logger.debug("search is " + search);
        match = re.search(' *' + search, instCode)
        width = match.end() - match.start() - len(search) + 1

        reg.update({'regname':regname})
        reg.update({'width':width})
        reg.update({'pos':match.start()})

        logger.debug("add reg" + str(reg))
        inst.addReg(reg)

    inst.setCode(instCode)
    inst.reorganize()

def openInstFile(filename=""):
    logger.debug("File name is: " + filename)
    if not os.path.isfile(filename):
        print 'Not a file'
        return -1;
    ifile = open(filename, 'r')
    fileContent = ifile.read();
    instlines = fileContent.split('\n')

    for i in range(0, instlines.__len__()):
        decodeInsts(instlines[i])

if __name__ == '__main__':
    print "Into main function"
    p = ArgumentParser(usage=sys.argv[0] + ' it is usage tip',
            description='this is a test')  
    p.add_argument('--file', default=" ", type=str,
            help='the first argument')  
    
    setLogLevel()
    args = p.parse_args()  
    openInstFile(args.file)

#! /usr/bin/python

import logging
import sys, os;
import re;
from argparse import ArgumentParser

logger = logging.getLogger('MIPSGENERATER')

#
# regs are dict of dict
#
class InstFormat:
    """
    Keyword arguments:
    __instName - Instruction Name
    __regs - Registers name and position
        regs format:
           regname
    __maxHex = 0
    __minHex = 0
    __instCode = ''
    """

    REGNAME="regName"
    REGPOS="regPos"
    REGWIDTH="regWidth"
    IDPOS="idPos"
    IDWIDTH="idWidth"
    IDVALUE="idValue"

    def __init__(self):
        logger.debug("Initialize InstFormat")
        self.__instName = ''
        self.__regs = []
        self.__instId = []
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
        """
        Sort regs by position and generate common codes.
        """
        sortList = {}
        for i in range (0, len(self.__regs)):
            sortList.update({self.__regs[i].get(InstFormat.REGPOS):i})

        newRegs = []
        totaloffset = 0;
        instCode = self.__instCode
        for i in sorted(sortList.keys()):
            reg = self.__regs[sortList[i]]

            pos = reg.get(InstFormat.REGPOS);
            regname = reg.get(InstFormat.REGNAME)

            pos = pos - totaloffset;

            reg.update({InstFormat.REGPOS:pos})

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
        newInstIds = []
        id_pos = 0

        for i in range(0, len(self.__regs)):
            reg = self.__regs[i]
            pos = reg.get(InstFormat.REGPOS)
            width = reg.get(InstFormat.REGWIDTH)

            maxCode = maxCode[:pos] + '1' * width + maxCode[pos + width:]
            minCode = minCode[:pos] + '0' * width + minCode[pos + width:]

            if (pos - id_pos) > 0:
                instId = dict()
                instId.update({InstFormat.IDPOS:id_pos})
                instId.update({InstFormat.IDWIDTH:(pos - id_pos)})
                instId.update({InstFormat.IDVALUE:instCode[id_pos:pos]})
                newInstIds.append(instId)
                logger.debug("InstID = " + str(id_pos) + ":" + str(pos - id_pos) + ":" + instCode[id_pos:pos])

            id_pos = pos + width

            logger.debug("MaxCode is " + maxCode)
            logger.debug("MinCode is " + minCode)

        if (id_pos < len(instCode)):
            instId = dict()
            instId.update({InstFormat.IDPOS:id_pos})
            instId.update({InstFormat.IDWIDTH:(len(instCode) - id_pos)})
            instId.update({InstFormat.IDVALUE:instCode[id_pos:len(instCode)]})
            newInstIds.append(instId)
            logger.debug("InstID = " + str(id_pos) + ":" + str(len(instCode) - id_pos) + ":" + instCode[id_pos:len(instCode)])

        self.__instId = newInstIds

        self.__maxHex = maxCode
        self.__minHex = minCode

    def setCode(self, instCode = ''):
        self.__instCode = instCode

    def getInstName(self):
        return self.__instName

    def getRegs(self):
        return self.__regs

    def getMaxHex(self):
        return self.__maxHex

    def getMinHex(self):
        return self.__minHex

    def getInstCode(self):
        return self.__instCode


def setLogLevel(level = 0):
    logger.setLevel(level)
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
    reRuleRightQuote = re.compile("\]")
    matches = reRuleRightQuote.finditer(instCode)
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

        pure_search = search = instLasts[i]
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
        width = match.end() - match.start() - len(pure_search) + 1

        reg.update({InstFormat.REGNAME:regname})
        reg.update({InstFormat.REGWIDTH:width})
        reg.update({InstFormat.REGPOS:match.start()})

        logger.debug("add reg" + str(reg))
        inst.addReg(reg)

    inst.setCode(instCode)
    inst.reorganize()

    return inst

def showAllInsts(insts = []):
    for i in range(0, len(insts)):
        inst = insts[i]

        logger.info("All instructions messages:")
        logger.info(inst.getInstName())
        logger.info(inst.getMaxHex())
        logger.info(inst.getMinHex())
        logger.info(inst.getInstCode())
        regs = inst.getRegs()
        for j in range(0, len(regs)):
            reg = regs[j]
            regname = reg.get(InstFormat.REGNAME)
            regpos = reg.get(InstFormat.REGPOS)
            regwidth = reg.get(InstFormat.REGWIDTH)
            logger.info("regname: " + regname)
            logger.info("regpos: " + str(regpos))
            logger.info("regwidth: " + str(regwidth))
            logger.info("----------")

        logger.info("")

def openInstFile(filename=""):
    logger.debug("File name is: " + filename)
    if not os.path.isfile(filename):
        print 'Not a file'
        return -1;
    ifile = open(filename, 'r')
    fileContent = ifile.read();

    return fileContent

def do_main(filename):
    fileContent = openInstFile(filename)

    instlines = fileContent.split('\n')

    insts = []

    for i in range(0, instlines.__len__()):
        inst = decodeInsts(instlines[i]);

        if inst != -1:
            insts.append(inst)

    showAllInsts(insts)


if __name__ == '__main__':
    logger.debug("Into main function")
    debugLevel = 0

    p = ArgumentParser(usage=sys.argv[0] + ' it is usage tip',
            description='this is a test')
    p.add_argument('--file', default=" ", type=str,
            help='the first argument')
    p.add_argument('-d', default=0, type=int, nargs='?', help='set debug level')

    args = p.parse_args()

    if args.d == None:
        debugLevel = logging.DEBUG

    setLogLevel(debugLevel)

    do_main(args.file)


/*
 * Class Instruction
 */

var InstType = {
    num: 0,
    gpr: 1,
    fpr: 2,
};

var InstCode = {
    createNew: function(type, value, pos, width) {
        var instCode = {};

        instCode.type = type;
        instCode.value = value;
        instCode.pos = pos;
        instCode.width = width;

        return instCode;
    }
};

var Instruction = {
    createNew: function(instFormat, instCode, encodeRule, decodeRule, mask, filter) {
        var instruction = {};

        instruction.instFormat = instFormat;
        instruction.instCode = instCode;
        instruction.encodeRule = encodeRule;

        instruction.decodeRule = decodeRule;
        instruction.mask = mask;
        instruction.filter = filter;

        return instruction;
    }
};

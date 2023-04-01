import threading

class IF_ID_Pipeline_Registers:
    def __init__(self):
        self.instruction_word = 0
        self.nextPC = 0
        self.isEnd = False
        self.isfree = False
        self.lock = threading.Condition()

    def getInfo(self):
        return {
            "instruction_word":self.instruction_word,
            "nextPC":self.nextPC,
            "isEnd":self.isEnd
        }


class ID_EX_Pipeline_Registers:
    def __init__(self):
        self.operand1 = 0
        self.operand2 = 0
        self.op1 = 0
        self.op2 = 0
        self.rd = 0
        self.rs1 = 0
        self.rs2 = 0
        self.immB = 0
        self.immJ = 0
        self.immI = 0
        self.immS = 0
        self.immU = 0
        self.nextPC = 0

        self.op2Select = 0
        self.ALUOp = ""
        self.operation = ""
        self.MemOp = ""
        self.Mem_b_h_w = ""
        self.resultSelect = 0
        self.RFWrite = False
        self.branchTargetSelect = 0
        self.isBranch = 0
        self.isEnd = False
        self.isfree = False
        self.lock = threading.Condition()

    def getInfo(self):
        return {
            "operand1": self.operand1,
            "operand2": self.operand2,
            "op1": self.op1,
            "op2": self.op2,
            "rd": self.rd,
            "rs1": self.rs1,
            "rs2": self.rs2,
            "immB": self.immB,
            "immJ": self.immJ,
            "immI": self.immI,
            "immS": self.immS,
            "immU": self.immU,
            "nextPC": self.nextPC,
            "op2Select": self.op2Select,
            "ALUOp": self.ALUOp,
            "operation": self.operation,
            "MemOp": self.MemOp,
            "Mem_b_h_w": self.Mem_b_h_w,
            "resultSelect": self.resultSelect,
            "RFWrite": self.RFWrite,
            "branchTargetSelect": self.branchTargetSelect,
            "isBranch": self.isBranch,
            "isEnd": self.isEnd
        }




class EX_MEM_Pipeline_Registers:
    def __init__(self):
        self.nextPC = 0
        self.ALUResult = 0
        self.branchTargetAddress = 0
        self.immU = 0
        self.pc_immU = 0
        self.op2 = 0
        self.rd = 0

        self.isBranch = 0
        self.MemOp = "-1"
        self.Mem_b_h_w = ""
        self.RFWrite = False
        self.resultSelect = 0
        self.isEnd = False
        self.isfree = False
        self.lock = threading.Condition()

    def getInfo(self):
        return {
            "nextPC": self.nextPC,
            "ALUResult": self.ALUResult,
            "branchTargetAddress": self.branchTargetAddress,
            "immU": self.immU,
            "pc_immU": self.pc_immU,
            "op2": self.op2,
            "rd": self.rd,
            "isBranch": self.isBranch,
            "MemOp": self.MemOp,
            "Mem_b_h_w": self.Mem_b_h_w,
            "RFWrite": self.RFWrite,
            "resultSelect": self.resultSelect,
            "isEnd": self.isEnd
        }

class MEM_WB_Pipeline_Registers:
    def __init__(self):
        self.nextPC = 0
        self.ALUResult = 0
        self.immU = 0
        self.pc_immU = 0
        self.loadData = 0
        self.rd = 0

        self.RFWrite = False
        self.resultSelect = 0
        self.isEnd = False
        self.isfree = False
        self.lock = threading.Condition()

    def getInfo(self):
        return {
            "nextPC": self.nextPC,
            "ALUResult": self.ALUResult,
            "immU": self.immU,
            "pc_immU": self.pc_immU,
            "loadData": self.loadData,
            "rd": self.rd,
            "RFWrite": self.RFWrite,
            "resultSelect": self.resultSelect,
            "isEnd": self.isEnd
        }



        
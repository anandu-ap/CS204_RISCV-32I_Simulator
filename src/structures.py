

class IF_ID_Pipeline_Registers:
    def __init__(self):
        self.instruction_word = 0
        self.nextPC = 0
        self.isEnd = False
        self.isStall = True
        self.branchTaken = True
        self.PC = 0
        self.predictedPC = 0
        self.isEmpty = True

    def getInfo(self):
        return {
            "instruction_word":self.instruction_word,
            "nextPC":self.nextPC,
            "isEnd":self.isEnd,
            "isStall":self.isStall,
            "branchTaken":self.branchTaken,
            "PC":self.PC,
            "predictedPC":self.predictedPC
        }
    
    def flush(self):
        self.instruction_word = 0
        self.nextPC = 0
        self.isEnd = False
        self.isStall = True
        self.branchTaken = True
        self.PC = 0
        self.predictedPC = 0
        self.isEmpty = True


class ID_EX_Pipeline_Registers:
    def __init__(self):
        self.operand1 = 0
        self.operand2 = 0
        self.op1 = 0
        self.op2 = 0
        self.rd = 32
        self.rs1 = 32
        self.rs2 = 32
        self.immB = 0
        self.immJ = 0
        self.immI = 0
        self.immS = 0
        self.immU = 0
        self.nextPC = 0
        self.PC = 0
        self.predictedPC = 0

        self.op2Select = 0
        self.ALUOp = "-1"
        self.operation = ""
        self.MemOp = ""
        self.Mem_b_h_w = ""
        self.resultSelect = 0
        self.RFWrite = False
        self.branchTargetSelect = 0
        self.isBranch = 0
        self.isEnd = False
        self.isStall = True
        self.branchTaken = True
        self.isEmpty = True

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
            "isEnd": self.isEnd,
            "isStall":self.isStall,
            "branchTaken":self.branchTaken,
            "PC":self.PC,
            "predictedPC":self.predictedPC
        }
    
    def flush(self):
        self.operand1 = 0
        self.operand2 = 0
        self.op1 = 0
        self.op2 = 0
        self.rd = 32
        self.rs1 = 32
        self.rs2 = 32
        self.immB = 0
        self.immJ = 0
        self.immI = 0
        self.immS = 0
        self.immU = 0
        self.nextPC = 0
        self.PC = 0
        self.predictedPC = 0

        self.op2Select = 0
        self.ALUOp = "-1"
        self.operation = ""
        self.MemOp = ""
        self.Mem_b_h_w = ""
        self.resultSelect = 0
        self.RFWrite = False
        self.branchTargetSelect = 0
        self.isBranch = 0
        self.isEnd = False
        self.isStall = True
        self.branchTaken = True
        self.isEmpty = True




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
        self.isStall = True
        self.isEmpty = True
        
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
            "isEnd": self.isEnd,
            "isStall":self.isStall
        }
    
    def flush(self):
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
        self.isStall = True
        self.isEmpty = True

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
        self.isStall = True
        self.isEmpty = True

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
            "isEnd": self.isEnd,
            "isStall":self.isStall
        }
    
    def flush(self):
        self.nextPC = 0
        self.ALUResult = 0
        self.immU = 0
        self.pc_immU = 0
        self.loadData = 0
        self.rd = 0

        self.RFWrite = False
        self.resultSelect = 0
        self.isEnd = False
        self.isStall = True
        self.isEmpty = True

class BTB:
    def __init__(self):
        self.buff = {}

    def addNewPC(self, pc, target_address, isTaken):
        self.buff[pc] = (target_address, isTaken)
    
    def updateisTaken(self, pc, isTaken):
        prediction = self.buff[pc][1]
        if (isTaken):
            if (prediction < 3):
                prediction += 1
        else:
            if (prediction > 0):
                prediction -= 1

        self.buff[pc] = (self.buff[pc][0], prediction)

    def updateTargetAddr(self, pc, tarAddr):
        self.buff[pc] = (tarAddr, 3)
    
    def hasPC(self, pc):
        if pc in self.buff:
            return True
        return False
    
    def getTargetAddress(self, pc):
        return self.buff[pc]
    
    def reset(self):
        self.buff = {}

    



        



        
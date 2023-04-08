

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

    def printContents(self):
        print("\nIF_ID_Pipeline_Registers\n")

        print(f"instruction word:{self.instruction_word}")
        print(f"nextPC: {self.nextPC}")
        print(f"isEnd: {self.isEnd}")
        print(f"isStall: {self.isStall}")
        print(f"branchTaken: {self.branchTaken}")
        print(f"currentPC: {self.PC}")
        print(f"predictedPC: {self.predictedPC}")
        print(f"isEmpty: {self.isEmpty}")

        print("\n")

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

    def printContents(self):
        print("\nID_EX_Pipeline_Registers\n")

        print(f"operand1:{self.operand1}")
        print(f"operand2: {self.operand2}")
        print(f"op1: {self.op1}")
        print(f"op2: {self.op2}")
        print(f"rd: {self.rd}")
        print(f"rs1: {self.rs1}")
        print(f"rs2: {self.rs2}")
        print(f"immB: {self.immB}")
        print(f"immJ: {self.immJ}")
        print(f"immI: {self.immI}")
        print(f"immS: {self.immS}")
        print(f"immU: {self.immU}")
        print(f"nextPC: {self.nextPC}")
        print(f"PC: {self.PC}")
        print(f"predictedPC: {self.predictedPC}")
        
        print(f"op2Select: {self.op2Select}")
        print(f"ALUOp: {self.ALUOp}")
        print(f"operation: {self.operation}")
        print(f"MemOp: {self.MemOp}")
        print(f"Mem_b_h_w: {self.Mem_b_h_w}")
        print(f"resultSelect: {self.resultSelect}")
        print(f"RFWrite: {self.RFWrite}")
        print(f"branchTargetSelect: {self.branchTargetSelect}")
        print(f"isBranch: {self.isBranch}")
        print(f"isEnd: {self.isEnd}")
        print(f"isStall: {self.isEnd}")
        print(f"branchTaken: {self.branchTaken}")
        print(f"isEmpty: {self.isEmpty}")

    
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
        self.PC = 0

        self.isBranch = 0
        self.MemOp = "-1"
        self.Mem_b_h_w = ""
        self.RFWrite = False
        self.resultSelect = 0
        self.op2Select = 0
        self.isEnd = False
        self.isStall = True
        self.isEmpty = True

    def printContents(self):
        print("\nEX_MEM_Pipeline_Registers\n")

        print(f"nextPC: {self.nextPC}")
        print(f"ALUResult: {self.ALUResult}")
        print(f"branchTargetAddress: {self.branchTargetAddress}")
        print(f"immU: {self.immU}")
        print(f"pc_immU: {self.pc_immU}")
        print(f"op2: {self.op2}")
        print(f"rd: {self.rd}")

        print(f"isBranch: {self.isBranch}")
        print(f"MemOp: {self.MemOp}")
        print(f"Mem_b_h_w: {self.Mem_b_h_w}")
        print(f"RFWrite: {self.RFWrite}")
        print(f"resultSelect: {self.resultSelect}")
        print(f"op2Select : {self.op2Select}")
        print(f"isEnd: {self.isEnd}")
        print(f"isStall: {self.isStall}")
        print(f"isEmpty: {self.isEmpty}")

        
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
            "op2Select": self.op2Select,
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
        self.PC = 0

        self.RFWrite = False
        self.MemOp = "-1"
        self.resultSelect = 0
        self.isEnd = False
        self.isStall = True
        self.isEmpty = True

    def printContents(self):
        print("\nMEM_WB_Pipeline_Registers\n")

        print(f"nextPC: {self.nextPC}")
        print(f"ALUResult: {self.ALUResult}")
        print(f"immU: {self.immU}")
        print(f"pc_immU: {self.pc_immU}")
        print(f"loadData: {self.loadData}")
        print(f"rd: {self.rd}")

        print(f"RFWrite: {self.RFWrite}")
        print(f"MemOp: {self.MemOp}")
        print(f"resultSelect: {self.resultSelect}")
        print(f"isEnd: {self.isEnd}")
        print(f"isStall: {self.isStall}")
        print(f"isEmpty: {self.isEmpty}")

    def getInfo(self):
        return {
            "nextPC": self.nextPC,
            "ALUResult": self.ALUResult,
            "immU": self.immU,
            "pc_immU": self.pc_immU,
            "loadData": self.loadData,
            "rd": self.rd,
            "RFWrite": self.RFWrite,
            "MemOp": self.MemOp,
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

    def copy(self, target_buffer):
        self.nextPC = target_buffer.nextPC
        self.ALUResult = target_buffer.ALUResult
        self.immU = target_buffer.immU
        self.pc_immU = target_buffer.pc_immU
        self.loadData = target_buffer.loadData
        self.rd = target_buffer.rd

        self.RFWrite = target_buffer.RFWrite
        self.MemOp = target_buffer.MemOp
        self.resultSelect = target_buffer.resultSelect
        self.isEnd = target_buffer.isEnd
        self.isStall = target_buffer.isStall
        self.isEmpty = target_buffer.isEmpty

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

    
class Stats:
    def __init__(self):
        self.cycles = 0
        self.instructions = 0
        self.CPI = 0
        self.data_transfers = 0
        self.ALU_ins = 0
        self.control_ins = 0
        self.stalls = 0
        self.data_hazards = 0
        self.control_hazards = 0
        self.branch_mispredictions = 0
        self.stalls_data_hazards = 0
        self.stalls_control_hazards = 0
    
    def calculateCPI(self):
        self.CPI = self.cycles/self.instructions
    
    def printToFile(self):
        out_file = open("stats.mem", 'w')

        out_file.write(f"Cycles : {self.cycles}\n\n")
        out_file.write(f"Total instructions executed = {self.instructions}\n\n")
        out_file.write(f"CPI = {self.CPI}\n\n")
        out_file.write(f"Number of data transfer = {self.data_transfers}\n\n")
        out_file.write(f"Number of ALU instructions executed = {self.ALU_ins}\n\n")
        out_file.write(f"Number of Control instructions executed = {self.control_ins}\n\n")
        out_file.write(f"Number of stalls = {self.stalls}\n\n")
        out_file.write(f"Number of data hazards = {self.data_hazards}\n\n")
        out_file.write(f"Number of control hazards = {self.control_hazards}\n\n")
        out_file.write(f"Number of branch mispredictions = {self.branch_mispredictions}\n\n")
        out_file.write(f"Number of stalls due to data hazards = {self.stalls_data_hazards}\n\n")
        out_file.write(f"Number of stalls due to control hazards = {self.stalls_control_hazards}\n\n")

        out_file.close()

        
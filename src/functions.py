

class ALU:
    
    def __init__(self, control, op1, op2):
        self.ALUOp = control
        self.operand1 = op1
        self.operand2 = op2 
    
    def compute(self):
        result = 0
        if self.ALUOp == "add":
            result = self.fun_add()
        elif self.ALUOp == "sub":
            result = self.fun_sub()
        elif self.ALUOp == "xor":
            result = self.fun_xor()
        elif self.ALUOp == "or":
            result = self.fun_or()
        elif self.ALUOp == "and":
            result = self.fun_and()
        elif self.ALUOp == "sll":
            result = self.fun_sll()
        elif self.ALUOp == "srl":
            result = self.fun_srl()
        elif self.ALUOp == "sra":
            result = self.fun_sra()
        elif self.ALUOp == "slt":
            result = self.fun_slt()
        elif self.ALUOp == "beq":
            result = self.fun_beq()
        elif self.ALUOp == "bne":
            result = self.fun_bne()
        elif self.ALUOp == "blt":
            result = self.fun_blt()
        elif self.ALUOp == "bge":
            result = self.fun_bge()
        else:
            print("Some error occured")
            result = 0
        return (result & 0xFFFFFFFF)
    
    def fun_add(self):
        return self.operand1+self.operand2
    
    def fun_sub(self):
        return self.operand1-self.operand2
    
    def fun_xor(self):
        return self.operand1 ^ self.operand2
    
    def fun_or(self):
        return self.operand1 | self.operand2
    
    def fun_and(self):
        return self.operand1 & self.operand2
    
    def fun_sll(self):
        return self.operand1 << self.operand2
    
    def fun_srl(self):
        return self.operand1 >> self.operand2
    
    def fun_sra(self):
        # mask = (1 << (32 - self.operand2)) - 1
        return self.operand1 >> self.operand2
    
    def fun_slt(self):
        return 1 if self.operand1 < self.operand2 else 0
    
    def fun_beq(self):
        return 1 if self.operand1 == self.operand2 else 0
    
    def fun_bne(self):
        return 1 if self.operand1 != self.operand2 else 0
    
    def fun_blt(self):
        return 1 if self.operand1 < self.operand2 else 0
    
    def fun_bge(self):
        if (self.operand1 & 0x80000000) != 0:
            self.operand1 = -1 * (2**32 - self.operand1)
        if (self.operand2 & 0x80000000) != 0:
            self.operand2 = -1 * (2**32 - self.operand2)
        return 1 if self.operand1 >= self.operand2 else 0
    
class Message:
    def __init__(self, operation, rd, rs1, rs2, operand1, operand2, immB, immJ, immU):
        self.operation = operation
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.operand1 = operand1
        self.operand2 = operand2
        self.immB = immB
        self.immJ = immJ
        self.immU = immU

    def printMsg(self):
        if (self.operation == "add" or self.operation == "sub" or self.operation == "xor" or self.operation == "or" or self.operation == "and" or self.operation == "sll" or self.operation == "srl" or self.operation == "sra" or self.operation == "slt"):
            self.printMsgR()
        elif (self.operation == "addi" or self.operation == "xori" or self.operation == "ori" or self.operation == "andi" or self.operation == "slli" or self.operation == "srli" or self.operation == "srai" or self.operation == "slti"):
            self.printMsgI()
        elif (self.operation == "lb" or self.operation == "lh" or self.operation == "lw"):
            self.printMsgLoad()
        elif (self.operation == "sb" or self.operation == "sh" or self.operation == "sw"):
            self.printMsgStore()
        elif (self.operation == "beq" or self.operation == "bne" or self.operation == "blt" or self.operation == "bge"):
            self.printMsgB()
        elif (self.operation == "jal"):
            self.printMsgJ()
        elif (self.operation == 'jalr'):
            self.printMsgJalr()
        elif (self.operation == "lui" or self.operation == "auipc"):
            self.printMsgU()
        else:
            print("Some error happened")

    def printMsgR(self):
        print(f"DECODE: {self.operation} x{self.rd}, x{self.rs1}, x{self.rs2}. Read registers x{self.rs1} = {self.operand1}, x{self.rs2} = {self.operand2}")
        # print(f"DECODE: Read registers x{self.rs1} = {self.operand1}, x{self.rs2} = {self.operand2}")
    
    def printMsgI(self):
        print(f"DECODE: {self.operation} x{self.rd}, x{self.rs1}, {self.operand2}. Read registers x{self.rs1} = {self.operand1}")
        # print(f"DECODE: Read registers x{self.rs1} = {self.operand1}")
    
    def printMsgLoad(self):
        print(f"DECODE: {self.operation} x{self.rd}, {self.operand2}(x{self.rs1}). Read registers x{self.rs1} = {self.operand1}")
        # print(f"DECODE: Read registers x{self.rs1} = {self.operand1}")

    def printMsgStore(self):
        print(f"DECODE: {self.operation} x{self.rs2}, {self.operand2}(x{self.rs1}). Read registers x{self.rs1} = {self.operand1}, x{self.rs2} = {self.operand2}")
        # print(f"DECODE: Read registers x{self.rs1} = {self.operand1}, x{self.rs2} = {self.operand2}")

    def printMsgB(self):
        print(f"DECODE: {self.operation} x{self.rs1}, x{self.rs2}, {self.immB}. Read registers x{self.rs1} = {self.operand1}, x{self.rs2} = {self.operand2}")
        # print(f"DECODE: Read registers x{self.rs1} = {self.operand1}, x{self.rs2} = {self.operand2}")

    def printMsgJ(self):
        print(f"DECODE: {self.operation} x{self.rd}, {self.immJ}")
    
    def printMsgJalr(self):
        print(f"DECODE: {self.operation} x{self.rd}, {self.operand2}(x{self.rs1}). Read registers x{self.rs1} = {self.operand1}")
        # print(f"DECODE: Read registers x{self.rs1} = {self.operand1}")

    def printMsgU(self):
        print(f"DECODE: {self.operation} x{self.rd}, {self.immU}")

    
    

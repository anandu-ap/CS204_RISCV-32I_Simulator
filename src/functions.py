

class ALU:
    
    def __init__(self, control, op1, op2):
        self.ALUOp = control
        self.operand1 = op1
        self.operand2 = op2 
    
    def compute(self):
        result = 0
        if self.ALUOp == 0:
            result = self.fun_add()
        elif self.ALUOp == 1:
            result = self.fun_sub()
        elif self.ALUOp == 2:
            result = self.fun_xor()
        elif self.ALUOp == 3:
            result = self.fun_or()
        elif self.ALUOp == 4:
            result = self.fun_and()
        elif self.ALUOp == 5:
            result = self.fun_sll()
        elif self.ALUOp == 6:
            result = self.fun_srl()
        elif self.ALUOp == 7:
            result = self.fun_sra()
        elif self.ALUOp == 8:
            result = self.fun_slt()
        elif self.ALUOp == 9:
            result = self.fun_beq()
        elif self.ALUOp == 10:
            result = self.fun_bne()
        elif self.ALUOp == 11:
            result = self.fun_blt()
        elif self.ALUOp == 12:
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
        self.operation = self.reverseMap(operation)
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.operand1 = operand1
        self.operand2 = operand2
        self.immB = immB
        self.immJ = immJ
        self.immU = immU

    def reverseMap(self, operation):
        if (operation == 0):
            return "add"
        elif (operation == 1):
            return "sub"
        elif (operation == 2):
            return "xor"
        elif (operation == 3):
            return "or"
        elif (operation == 4):
            return "and"
        elif (operation == 5):
            return "sll"
        elif (operation == 6):
            return "srl"
        elif (operation == 7):
            return "sra"
        elif (operation == 8):
            return "slt"
        elif (operation == 9):
            return "addi"
        elif (operation == 10):
            return "xori"
        elif (operation == 11):
            return "ori"
        elif (operation == 12):
            return "andi"
        elif (operation == 13):
            return "slli"
        elif (operation == 14):
            return "srrli"
        elif (operation == 15):
            return "slti"
        elif (operation == 16):
            return "lb"
        elif (operation == 17):
            return "lh"
        elif (operation == 18):
            return "lw"
        elif (operation == 19):
            return "sb"
        elif (operation == 20):
            return "sh"
        elif (operation == 21):
            return "sw"
        elif (operation == 22):
            return "beq"
        elif (operation == 23):
            return "bne"
        elif (operation == 24):
            return "blt"
        elif (operation == 25):
            return "bge"
        elif (operation == 26):
            return "jal"
        elif (operation == 27):
            return "jalr"
        elif (operation == 28):
            return "lui"
        elif (operation == 29):
            return "auipc"
        return ""

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

    
    

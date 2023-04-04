import functions
import structures as st

"""
The project is developed as part of Computer Architecture class
Project Name: Functional Simulator for subset of RISCV Processor

Developer's Name: Anandu A P
Developer's Email id: 2019csb1069@iitrpr.ac.in
Date:
""" 


""""  myRISCVSim.py
 Purpose of this file: implementation file for myRISCVSim
"""

# Register file
X = [0]*32
# flags
# memory

data_MEM = {}
ins_MEM = {}

PC = 0
clock = 0

# intermediate datapath signals
instruction_word = 0
operand1 = 0
operand2 = 0
op1 = 0
op2 = 0
rd = 0
rs1 = 0
rs2 = 0
immB = 0
immJ = 0
immI = 0
immS = 0
immU = 0
ALUResult = 0
loadData = 0
finalResult = 0
branchTargetAddress = 0
nextPC = 0
pc_immU = 0

# intermideate control path signals
isExit = False
op2Select = 0
ALUOp = ""
operation = ""
MemOp = ""
Mem_b_h_w = ""
resultSelect = 0
RFWrite = False
branchTargetSelect = 0
isBranch = 0

isEnd = False
stall = 0
PC_on_missprediction = 0
isFlush = False
isLastIns = False
stallUp = -1

IF_ID_buff = st.IF_ID_Pipeline_Registers()
ID_EX_buff = st.ID_EX_Pipeline_Registers()
EX_MEM_buff = st.EX_MEM_Pipeline_Registers()
MEM_WB_buff = st.MEM_WB_Pipeline_Registers()

btb = st.BTB()

out_file = open("out.txt", "w")


def run_riscvsim():
    global out_file, PC, clock, isFlush, PC_on_missprediction, IF_ID_buff, ID_EX_buff, isExit, isLastIns

    while(isExit == False):
        write_back2()
        mem2()
        execute2()
        decode1()
        fetch1()

        clock += 1
        # out_file.write("clock cycle : " + clock + "-------------------------------------------------------------------------------------------------\n")
        print("clock cycle : ", clock)
        print("-------------------------------------------------------------------------------------------------\n")

        if (isFlush):
            PC = PC_on_missprediction
            isLastIns = False
            IF_ID_buff.flush()
            ID_EX_buff.flush()
            isFlush = False

        if (isLastIns and IF_ID_buff.isStall and ID_EX_buff.isStall and EX_MEM_buff.isStall and MEM_WB_buff.isStall):
            isExit = True
    swi_exit()


    # while(True):
    #     fetch()
    #     decode()
    #     execute()
    #     mem()
    #     write_back()
        
    #     clock += 1
    #     print("clock cycle : ", clock)


# it is used to set the reset values
# reset all registers and memory content to 0
def reset_proc():
    global X, PC, data_MEM, ins_MEM, IF_ID_buff, ID_EX_buff, EX_MEM_buff, MEM_WB_buff, btb

    PC = 0

    for i in range(32):
        X[i] = 0
    X[2] = int('0x7FFFFFFC', 16)

    data_MEM = {}
    ins_MEM = {}

    IF_ID_buff.flush()
    ID_EX_buff.flush()
    EX_MEM_buff.flush()
    MEM_WB_buff.flush()

    btb.reset()




# load_program_memory reads the input memory, and pupulates the instruction 
# memory
def load_program_memory(file_name):
    global ins_MEM
    with open(file_name, "r") as fp:
        i = 0
        for line in fp:
            # address, ins = map(lambda x: int(x, 16), line.split())
            ins = int(line.strip()[2:], 16)
            write_word(ins_MEM, i, ins)
            i += 4


# writes the data memory in "data_out.mem" file
def write_data_memory():
    # TODO
    global data_MEM, X
    with open("data_out.mem", "w") as fp:
        for key, value in sorted(data_MEM.items()):
            value = value & 0xffffffff
            fp.write(f"0x{key:08x} 0x{value:08x}\n")


# should be called when instruction is swi_exit
def swi_exit():
    write_data_memory()
    print("Completed writting data to data_out.mem")
    print("Program finished")
    exit(0)

# reads from the instruction memory and updates the instruction register
def fetch():
    global ins_MEM, PC, instruction_word, isExit, nextPC

    instruction_word = read_word(PC, ins_MEM)
    print(f"FETCH:Fetch instruction 0x{instruction_word:08x} from address 0x{hex(PC)}")

    nextPC = PC + 4

def fetch1():
    global out_file, stallUp, isLastIns, stall, ins_MEM, PC, instruction_word, isExit, nextPC, IF_ID_buff, isEnd

    if (stall > 1 and stall < stallUp):
        print("FETCH: stall")
        # out_file.write("FETCH:")
        stall -= 1
        return
    
    if (stall == 1):
        stall -= 1

    # if (isEnd):
    #     print("FETCH: No Operation")
    if (isLastIns):
        print("FETCH: No Operation end")

    else:
        instruction_word = read_word(PC, ins_MEM)
        print(f"FETCH:Fetch instruction 0x{instruction_word:08x} from address {hex(PC)}")

        if (stall == stallUp):
                print("stall")
                stall -= 1
                return
    
        if (instruction_word == int('0xEF000011', 16)):
            isLastIns = True
            IF_ID_buff.flush()
            # isEnd = True
            # IF_ID_buff.isEnd = True

        else:
            nextPC = PC + 4
            IF_ID_buff.PC = PC

            if (btb.hasPC(PC)):
                tar = btb.getTargetAddress(PC)
                if (tar[1] > 1):
                    PC = tar[0]
                    IF_ID_buff.branchTaken = True
                else:
                    PC = nextPC
                    IF_ID_buff.branchTaken = False
            else:
                PC = nextPC
                IF_ID_buff.branchTaken = False
                
            IF_ID_buff.instruction_word = instruction_word
            IF_ID_buff.nextPC = nextPC
            IF_ID_buff.isStall = False
            IF_ID_buff.predictedPC = PC


    

# reads the instruction register, reads operand1, operand2 from register file, decides the operation to be performed in execute stage
def decode():
    global rd, rs1, rs2, op1, op2, operand1, operand2,op2Select, instruction_word, X, MemOp,Mem_b_h_w, operation, resultSelect, RFWrite, immB, immI, immJ, immS, immU, branchTargetSelect, resultSelect, ALUOp, isExit

    # checking if the instruction is swi_exit
    if (instruction_word == int('0xEF000011', 16)):
        swi_exit()


    instruction_in_binary = bin(instruction_word)[2:].zfill(32)
    opcode = instruction_in_binary[25:32]

  
    if (opcode == "0110011"):
        # R type

        fun7 = instruction_in_binary[0:7]
        fun3 = instruction_in_binary[17:20]

        rd = int(instruction_in_binary[20:25], 2)
        rs1 = int(instruction_in_binary[12:17], 2)
        rs2 = int(instruction_in_binary[7:12], 2)

        operand1 = X[rs1]
        op2 = X[rs2]
        op2Select = 0
        resultSelect = 4
        MemOp = "-1"
        RFWrite = True

        if (fun3 == "000" and fun7 == "0000000"):
            operation = "add"
            ALUOp = "add"
        elif (fun3 == "000" and fun7 == "0100000"):
            operation = "sub"
            ALUOp = "sub"
        elif (fun3 == "100" and "0000000"):
            operation = "xor"
            ALUOp = "xor"
        elif (fun3 == "110" and fun7 == "0000000"):
            operation = "or"
            ALUOp = "or"
        elif (fun3 == "111" and fun7 == "0000000"):
            operation = "and"
            ALUOp = "and"
        elif (fun3 == "001" and fun7 == "0000000"):
            operation = "sll"
            ALUOp = "sll"
        elif (fun3 == "101" and fun7 == "0000000"):
            operation = "srl"
            ALUOp = "srl"
        elif (fun3 == "101" and fun7 == "0100000"):
            operation = "sra"
            ALUOp = "sra"
        elif (fun3 == "010" and fun7 == "0000000"):
            operation = "slt"
            ALUOp = "slt"
        else:
            print("Instruction not supported")
            swi_exit()

        
    elif (opcode == "0010011"):
        # I type (addi, ori, andi)

        fun3 = instruction_in_binary[17:20]

        rd = int(instruction_in_binary[20:25], 2)
        rs1 = int(instruction_in_binary[12:17], 2)

        operand1 = X[rs1]
        if (instruction_in_binary[0] == '1'):
            immI = int(instruction_in_binary[0:12], 2) - 2**12
        else:
            immI = int(instruction_in_binary[0:12], 2)

        op2Select = 1
        resultSelect = 4
        MemOp = "-1"
        RFWrite = True

        if (fun3 == "000"):
            operation = "addi"
            ALUOp = "add"
        elif (fun3 == "100"):
            operation = "xori"
            ALUOp = "xor"
        elif (fun3 == "110"):
            operation = "ori"
            ALUOp = "or"
        elif (fun3 == "111"):
            operation = "andi"
            ALUOp = "and"
        elif (fun3 == "001"):
            operation = "slli"
            ALUOp = "sll"
        elif (fun3 == "101"):
            # if (instruction_in_binary[0:7] == "000000"):
            #     operation = "srli"
            #     ALUOp = "srl"
            # else:
            #     operation = "srai"
            #     ALUOp = "sra"
            operation = "srli"
            ALUOp = "srl"
        elif (fun3 == "010"):
            operation = "slti"
            ALUOp = "slt"
        else:
            print("Instruction not supported")
            swi_exit()

        
    elif (opcode == "0000011"):
        # I type (lb, lh, lw)
        fun3 = instruction_in_binary[17:20]

        rd = int(instruction_in_binary[20:25], 2)
        rs1 = int(instruction_in_binary[12:17], 2)

        operand1 = X[rs1]
        if (instruction_in_binary[0] == '1'):
            immI = int(instruction_in_binary[0:12], 2) - 2**12
        else:
            immI = int(instruction_in_binary[0:12], 2)

        op2Select = 1
        resultSelect = 3
        MemOp = "r"
        RFWrite = True
        ALUOp = "add"

        if (fun3 == "000"):
            operation = "lb"
            Mem_b_h_w = "b"
        elif (fun3 == "001"):
            operation = "lh"
            Mem_b_h_w = "h"
        elif (fun3 == "010"):
            operation = "lw"
            Mem_b_h_w = "w"
        else:
            print("Instruction not supported")
            swi_exit()

        
    elif (opcode == "0100011"):
        # S type
        fun3 = instruction_in_binary[17:20]

        rs1 = int(instruction_in_binary[12:17], 2)
        rs2 = int(instruction_in_binary[7:12], 2)
        

        operand1 = X[rs1]
        op2 = X[rs2]

        imm = instruction_in_binary[0:7] + instruction_in_binary[20:25]
        if (imm[0] == '1'):
            immS = int(imm, 2) - 2**12
        else:
            immS = int(imm, 2)
        
        op2Select = 2
        MemOp = "w"
        RFWrite = False
        ALUOp = "add"

        if (fun3 == "000"):
            operation = "sb"
            Mem_b_h_w = "b"
        elif (fun3 == "001"):
            operation = "sh"
            Mem_b_h_w = "h"
        elif (fun3 == "010"):
            operation = "sw"
            Mem_b_h_w = "w"
        else:
            print("Instruction not supported")
            swi_exit()


    elif (opcode == "1100011"):
        # B type
        fun3 = instruction_in_binary[17:20]

        rs1 = int(instruction_in_binary[12:17], 2)
        rs2 = int(instruction_in_binary[7:12], 2)
        

        operand1 = X[rs1]
        op2 = X[rs2]

        imm = instruction_in_binary[0] + instruction_in_binary[24] + instruction_in_binary[1:7] + instruction_in_binary[20:24] + "0"
        if (imm[0] == '1'):
            immB = int(imm, 2) - 2**13
        else:
            immB = int(imm, 2)
        
        op2Select = 0
        branchTargetSelect = 0
        MemOp = "-1"
        RFWrite = False

        if (fun3 == "000"):
            operation = "beq"
            ALUOp = "beq"
        elif (fun3 == "001"):
            operation = "bne"
            ALUOp = "bne"
        elif (fun3 == "100"):
            operation = "blt"
            ALUOp = "blt"
        elif (fun3 == "101"):
            operation = "bge"
            ALUOp = "bge"
        else:
            print("Instruction not supported")
            swi_exit()

    elif (opcode == "1101111"):
        # J type
        fun3 = instruction_in_binary[17:20]

        rd = int(instruction_in_binary[20:25], 2)

        imm = instruction_in_binary[0] + instruction_in_binary[12:20] + instruction_in_binary[11] + instruction_in_binary[1:11] + "0"
        if (imm[0] == '1'):
            immJ = int(imm, 2) - 2**21
        else:
            immJ = int(imm, 2)
        
        branchTargetSelect = 1
        resultSelect = 0
        MemOp = "-1"
        RFWrite = True
        ALUOp = "-1"
        operation = "jal"

    elif (opcode == "1100111"):
        # I type (jalr)
        fun3 = instruction_in_binary[17:20]

        rd = int(instruction_in_binary[20:25], 2)
        rs1 = int(instruction_in_binary[12:17], 2)

        operand1 = X[rs1]
        if (instruction_in_binary[0] == '1'):
            immI = int(instruction_in_binary[0:12], 2) - 2**12
        else:
            immI = int(instruction_in_binary[0:12], 2)

        resultSelect = 0
        op2Select = 1
        MemOp = "-1"
        RFWrite = True
        ALUOp = "add"

        if (fun3 == "000"):
            operation = "jalr"
        else:
            print("Instruction not supported")
            swi_exit()
        
    elif (opcode == "0110111"):
        # U type (lui)
        fun3 = instruction_in_binary[17:20]

        rd = int(instruction_in_binary[20:25], 2)

        immU = int(instruction_in_binary[0:20] + "000000000000", 2)
        
        resultSelect = 1
        MemOp = "-1"
        RFWrite = True
        operation = "lui"
        ALUOp = "-1"

    elif (opcode == "0010111"):
        # U type (auipc)
        fun3 = instruction_in_binary[17:20]

        rd = int(instruction_in_binary[20:25], 2)

        immU = int(instruction_in_binary[0:20] + "000000000000", 2)
        
        resultSelect = 2
        MemOp = "-1"
        RFWrite = True
        operation = "auipc"
        ALUOp = "-1"

    else:
        print("Instruction not supported")
        swi_exit()
    
    # selecting the operand2 based on op2Select
    if (op2Select == 0):
        operand2 = op2
    elif (op2Select == 1):
        operand2 = immI
    else:
        operand2 = immS

    msg = functions.Message(operation, rd, rs1, rs2, operand1, operand2, immB, immJ, immU)
    msg.printMsg()
    
    
def decode1():
    global stallUp, stall, IF_ID_buff, ID_EX_buff, rd, rs1, rs2, op1, op2, operand1, operand2,op2Select, instruction_word, X, MemOp,Mem_b_h_w, operation, resultSelect, RFWrite, immB, immI, immJ, immS, immU, branchTargetSelect, resultSelect, ALUOp, isExit

    if (stall > 1):
        print("DECODE: stall")
        return
    
    bufferInfo = IF_ID_buff.getInfo()

    if (bufferInfo["isStall"]):
        print("DECODE: stall")
        ID_EX_buff.isStall = True
        return

    # if (bufferInfo["isEnd"]):
    #     print("DECODE: No Operation")
    #     ID_EX_buff.isEnd = True
    #     return

    instruction_in_binary = bin(bufferInfo["instruction_word"])[2:].zfill(32)
    opcode = instruction_in_binary[25:32]

    fun7 = instruction_in_binary[0:7]
    fun3 = instruction_in_binary[17:20]

    rd = int(instruction_in_binary[20:25], 2)
    rs1 = int(instruction_in_binary[12:17], 2)
    rs2 = int(instruction_in_binary[7:12], 2)

    if (instruction_in_binary[0] == '1'):
        immI = int(instruction_in_binary[0:12], 2) - 2**12
    else:
        immI = int(instruction_in_binary[0:12], 2)

    imm = instruction_in_binary[0:7] + instruction_in_binary[20:25]
    if (imm[0] == '1'):
        immS = int(imm, 2) - 2**12
    else:
        immS = int(imm, 2)

    imm = instruction_in_binary[0] + instruction_in_binary[24] + instruction_in_binary[1:7] + instruction_in_binary[20:24] + "0"
    if (imm[0] == '1'):
        immB = int(imm, 2) - 2**13
    else:
        immB = int(imm, 2)
    
    immU = int(instruction_in_binary[0:20] + "000000000000", 2)
    
    imm = instruction_in_binary[0] + instruction_in_binary[12:20] + instruction_in_binary[11] + instruction_in_binary[1:11] + "0"
    if (imm[0] == '1'):
        immJ = int(imm, 2) - 2**21
    else:
        immJ = int(imm, 2)

  
    if (opcode == "0110011"):
        # R type
        op2Select = 0
        resultSelect = 4
        MemOp = "-1"
        RFWrite = True

        if (fun3 == "000" and fun7 == "0000000"):
            operation = "add"
            ALUOp = "add"
        elif (fun3 == "000" and fun7 == "0100000"):
            operation = "sub"
            ALUOp = "sub"
        elif (fun3 == "100" and "0000000"):
            operation = "xor"
            ALUOp = "xor"
        elif (fun3 == "110" and fun7 == "0000000"):
            operation = "or"
            ALUOp = "or"
        elif (fun3 == "111" and fun7 == "0000000"):
            operation = "and"
            ALUOp = "and"
        elif (fun3 == "001" and fun7 == "0000000"):
            operation = "sll"
            ALUOp = "sll"
        elif (fun3 == "101" and fun7 == "0000000"):
            operation = "srl"
            ALUOp = "srl"
        elif (fun3 == "101" and fun7 == "0100000"):
            operation = "sra"
            ALUOp = "sra"
        elif (fun3 == "010" and fun7 == "0000000"):
            operation = "slt"
            ALUOp = "slt"
        else:
            print("Instruction not supported")
            swi_exit()

        
    elif (opcode == "0010011"):
        # I type (addi, ori, andi)

        op2Select = 1
        resultSelect = 4
        MemOp = "-1"
        RFWrite = True

        if (fun3 == "000"):
            operation = "addi"
            ALUOp = "add"
        elif (fun3 == "100"):
            operation = "xori"
            ALUOp = "xor"
        elif (fun3 == "110"):
            operation = "ori"
            ALUOp = "or"
        elif (fun3 == "111"):
            operation = "andi"
            ALUOp = "and"
        elif (fun3 == "001"):
            operation = "slli"
            ALUOp = "sll"
        elif (fun3 == "101"):
            # if (instruction_in_binary[0:7] == "000000"):
            #     operation = "srli"
            #     ALUOp = "srl"
            # else:
            #     operation = "srai"
            #     ALUOp = "sra"
            operation = "srli"
            ALUOp = "srl"
        elif (fun3 == "010"):
            operation = "slti"
            ALUOp = "slt"
        else:
            print("Instruction not supported")
            swi_exit()

        
    elif (opcode == "0000011"):
        # I type (lb, lh, lw)

        op2Select = 1
        resultSelect = 3
        MemOp = "r"
        RFWrite = True
        ALUOp = "add"

        if (fun3 == "000"):
            operation = "lb"
            Mem_b_h_w = "b"
        elif (fun3 == "001"):
            operation = "lh"
            Mem_b_h_w = "h"
        elif (fun3 == "010"):
            operation = "lw"
            Mem_b_h_w = "w"
        else:
            print("Instruction not supported")
            swi_exit()

        
    elif (opcode == "0100011"):
        # S type
        
        op2Select = 2
        MemOp = "w"
        RFWrite = False
        ALUOp = "add"

        if (fun3 == "000"):
            operation = "sb"
            Mem_b_h_w = "b"
        elif (fun3 == "001"):
            operation = "sh"
            Mem_b_h_w = "h"
        elif (fun3 == "010"):
            operation = "sw"
            Mem_b_h_w = "w"
        else:
            print("Instruction not supported")
            swi_exit()


    elif (opcode == "1100011"):
        # B type
        op2Select = 0
        branchTargetSelect = 0
        MemOp = "-1"
        RFWrite = False

        if (fun3 == "000"):
            operation = "beq"
            ALUOp = "beq"
        elif (fun3 == "001"):
            operation = "bne"
            ALUOp = "bne"
        elif (fun3 == "100"):
            operation = "blt"
            ALUOp = "blt"
        elif (fun3 == "101"):
            operation = "bge"
            ALUOp = "bge"
        else:
            print("Instruction not supported")
            swi_exit()

    elif (opcode == "1101111"):
        # J type (jal)
        
        branchTargetSelect = 1
        resultSelect = 0
        MemOp = "-1"
        RFWrite = True
        ALUOp = "-1"
        operation = "jal"


    elif (opcode == "1100111"):
        # I type (jalr)
        
        resultSelect = 0
        op2Select = 1
        MemOp = "-1"
        RFWrite = True
        ALUOp = "add"

        if (fun3 == "000"):
            operation = "jalr"
        else:
            print("Instruction not supported")
            swi_exit()
        
    elif (opcode == "0110111"):
        # U type (lui)
        
        resultSelect = 1
        MemOp = "-1"
        RFWrite = True
        operation = "lui"
        ALUOp = "-1"

    elif (opcode == "0010111"):
        # U type (auipc)
        
        resultSelect = 2
        MemOp = "-1"
        RFWrite = True
        operation = "auipc"
        ALUOp = "-1"

    else:
        print("Error! Instruction not supported\nexiting the program")
        swi_exit()
    
    # Condition for data dependency
    if (stall == 0 and ALUOp != "-1" and ID_EX_buff.RFWrite == True and (rs1 == ID_EX_buff.rd or (rs2 == ID_EX_buff.rd and op2Select == 0))):
        print("DECODE: stall1")
        stall = 4
        stallUp = 4
        # ID_EX_buff.isStall = True
        ID_EX_buff.flush()
        return
    
    if (stall == 0 and ALUOp != "-1" and EX_MEM_buff.RFWrite == True and (rs1 == EX_MEM_buff.rd or (rs2 == EX_MEM_buff.rd and op2Select == 0))):
        print("DECODE: stall2")
        stall = 3
        stallUp = 3
        # ID_EX_buff.isStall = True
        ID_EX_buff.flush()
        return
    
    if (stall == 0 and ALUOp != "-1" and MEM_WB_buff.RFWrite == True and (rs1 == MEM_WB_buff.rd or (rs2 == MEM_WB_buff.rd and op2Select == 0))):
        print("DECODE: stall3")
        stall = 2
        stallUp = 2
        # ID_EX_buff.isStall = True
        ID_EX_buff.flush()
        return
    
    
    operand1 = X[rs1]
    op2 = X[rs2]
    
    # selecting the operand2 based on op2Select
    if (op2Select == 0):
        operand2 = op2
    elif (op2Select == 1):
        operand2 = immI
    else:
        operand2 = immS

    msg = functions.Message(operation, rd, rs1, rs2, operand1, operand2, immB, immJ, immU)
    msg.printMsg()

    ID_EX_buff.ALUOp = ALUOp
    ID_EX_buff.branchTargetSelect = branchTargetSelect
    ID_EX_buff.immB = immB
    ID_EX_buff.immI = immI
    ID_EX_buff.immJ = immJ
    ID_EX_buff.immS = immS
    ID_EX_buff.immU = immU
    ID_EX_buff.isBranch = isBranch
    ID_EX_buff.Mem_b_h_w = Mem_b_h_w
    ID_EX_buff.MemOp = MemOp
    ID_EX_buff.nextPC = bufferInfo["nextPC"]
    ID_EX_buff.op1 = op1
    ID_EX_buff.op2 = op2
    ID_EX_buff.op2Select = op2Select
    ID_EX_buff.operand1 = operand1
    ID_EX_buff.operand2 = operand2
    ID_EX_buff.operation = operation
    ID_EX_buff.rd = rd
    ID_EX_buff.resultSelect = resultSelect
    ID_EX_buff.RFWrite = RFWrite
    ID_EX_buff.rs1 = rs1
    ID_EX_buff.rs2 = rs2
    ID_EX_buff.isStall = False
    ID_EX_buff.branchTaken = IF_ID_buff.branchTaken
    ID_EX_buff.PC = bufferInfo["PC"]
    ID_EX_buff.predictedPC = bufferInfo["predictedPC"]


  
# executes the operations based on ALUOp
def execute():
    global PC, rd, op2, pc_immU, operand1, operand2, instruction_word, X, MemOp, operation, RFWrite, ALUResult, ALUOp, isBranch, immU, branchTargetSelect, branchTargetAddress

    
    if (ALUOp != "-1"):
        ALUUnit = functions.ALU(ALUOp, operand1, operand2)
        ALUResult = ALUUnit.compute()
        print(f"EXECUTE: {ALUOp} 0x{operand1:08x} and 0x{operand2:08x}")
    else:
        print(f"EXECUTE: No ALU operation")

    if (branchTargetSelect == 0):
        branchTargetAddress = PC + immB
    else:
        branchTargetAddress = PC + immJ
    
    if (operation == "beq" or operation == "bne" or operation == "blt" or operation == "bge"):
        if (ALUResult == 1):
            isBranch = 1
        else:
            isBranch = 0
    elif (operation == "jal"):
        isBranch = 1
    elif (operation == "jalr"):
        isBranch = 2
    else:
        isBranch = 0

    pc_immU = PC + immU


def execute2():
    global btb, isFlush, PC_on_missprediction, ID_EX_buff, EX_MEM_buff, ALUResult, isBranch, branchTargetAddress

    bufferInfo = ID_EX_buff.getInfo()

    if (bufferInfo["isStall"]):
        print("EXECUTE: stall")
        # EX_MEM_buff.isStall = True
        EX_MEM_buff.flush()
        return


    # if (bufferInfo["isEnd"]):
    #     print("EXECUTE: No Operation")
    #     EX_MEM_buff.isEnd = True
    #     return


    if (bufferInfo["ALUOp"] != "-1"):
        ALUUnit = functions.ALU(bufferInfo["ALUOp"], bufferInfo["operand1"], bufferInfo["operand2"])
        ALUResult = ALUUnit.compute()
        print(f"EXECUTE: {bufferInfo['ALUOp']} 0x{bufferInfo['operand1']:08x} and 0x{bufferInfo['operand2']:08x}")
    else:
        print(f"EXECUTE: No ALU operation")

    if (bufferInfo["branchTargetSelect"] == 0):
        branchTargetAddress = bufferInfo["nextPC"] - 4 + bufferInfo["immB"]
    else:
        branchTargetAddress = bufferInfo["nextPC"] - 4 + bufferInfo["immJ"]
        
    
    if (bufferInfo["operation"] == "beq" or bufferInfo["operation"] == "bne" or bufferInfo["operation"] == "blt" or bufferInfo["operation"] == "bge"):
        if (not btb.hasPC(bufferInfo["PC"])):
            print("EXECUTE:Hiiiiiiiiiiiiiiiiiiiiiiiiii\n")
            btb.addNewPC(bufferInfo["PC"], branchTargetAddress, 1)
        if (ALUResult == 1):
            isBranch = 1
            if (not ID_EX_buff.branchTaken):
                isFlush = True
                PC_on_missprediction = branchTargetAddress
                btb.updateisTaken(bufferInfo["PC"], True)
        else:
            isBranch = 0
            if (ID_EX_buff.branchTaken):
                isFlush = True
                PC_on_missprediction = ID_EX_buff.nextPC
                btb.updateisTaken(bufferInfo["PC"], False)
                
    elif (bufferInfo["operation"] == "jal"):
        isBranch = 1
        if (not btb.hasPC(bufferInfo["PC"])):
            btb.addNewPC(bufferInfo["PC"], branchTargetAddress, 3)

        if (not ID_EX_buff.branchTaken):
            isFlush = True
            PC_on_missprediction = branchTargetAddress
            btb.updateisTaken(bufferInfo["PC"], True)

    elif (bufferInfo["operation"] == "jalr"):
        isBranch = 2
        if (not btb.hasPC(bufferInfo["PC"])):
            btb.addNewPC(bufferInfo["PC"], ALUResult, 3)

        if (not bufferInfo["predictedPC"] == ALUResult):
            isFlush = True
            PC_on_missprediction = ALUResult
            btb.updateisTaken(bufferInfo["PC"], True)
    else:
        isBranch = 0

    pc_immU = bufferInfo["nextPC"] - 4 + bufferInfo["immU"]

    EX_MEM_buff.nextPC = bufferInfo["nextPC"]
    EX_MEM_buff.ALUResult = ALUResult
    EX_MEM_buff.branchTargetAddress = branchTargetAddress
    EX_MEM_buff.isBranch = isBranch
    EX_MEM_buff.Mem_b_h_w = bufferInfo["Mem_b_h_w"]
    EX_MEM_buff.MemOp = bufferInfo["MemOp"]
    EX_MEM_buff.op2 = bufferInfo["op2"]
    EX_MEM_buff.immU = bufferInfo["immU"]
    EX_MEM_buff.pc_immU = pc_immU
    EX_MEM_buff.rd = bufferInfo["rd"]
    EX_MEM_buff.resultSelect = bufferInfo["resultSelect"]
    EX_MEM_buff.RFWrite = bufferInfo["RFWrite"]
    EX_MEM_buff.isStall = False

    



# perform the memory operation
def mem():
    global data_MEM, MemOp, ALUResult, Mem_b_h_w, loadData, op2

    if (MemOp == "r"):
        if (Mem_b_h_w == "b"):
            loadData = read_byte(ALUResult, data_MEM)
        elif (Mem_b_h_w == "h"):
            loadData = read_half_word(ALUResult, data_MEM)
        else:
            loadData = read_word(ALUResult, data_MEM)
        print(f"MEMORY: READ 0x{loadData:08x} from address 0x{ALUResult:08x}")

    elif (MemOp == "w"):
        if (Mem_b_h_w == "b"):
            write_byte(data_MEM, ALUResult, op2)
        elif (Mem_b_h_w == "h"):
            write_half_word(data_MEM, ALUResult, op2)
        else:
            write_word(data_MEM, ALUResult, op2)
        print(f"MEMORY: WRITE 0x{op2:08x} to address 0x{ALUResult:08x}")
        
    else:
        print("MEMORY: No memory operation")


def mem2():
    global EX_MEM_buff, MEM_WB_buff, data_MEM, MemOp, ALUResult, Mem_b_h_w, loadData, op2

    bufferInfo = EX_MEM_buff.getInfo()

    if (bufferInfo["isStall"]):
        print("MEMORY: stall")
        # MEM_WB_buff.isStall = True
        MEM_WB_buff.flush()
        return
    
    # if (bufferInfo["isEnd"]):
    #     print("MEMORY: No Operation")
    #     MEM_WB_buff.isEnd = True
    #     return
    

    
    if (bufferInfo["MemOp"] == "r"):
        if (bufferInfo["Mem_b_h_w"] == "b"):
            loadData = read_byte(bufferInfo["ALUResult"], data_MEM)
        elif (bufferInfo["Mem_b_h_w"] == "h"):
            loadData = read_half_word(bufferInfo["ALUResult"], data_MEM)
        else:
            loadData = read_word(bufferInfo["ALUResult"], data_MEM)
        print(f"MEMORY: READ 0x{loadData:08x} from address 0x{bufferInfo['ALUResult']:08x}")

    elif (bufferInfo["MemOp"] == "w"):
        if (bufferInfo["Mem_b_h_w"] == "b"):
            write_byte(data_MEM, bufferInfo["ALUResult"], bufferInfo["op2"])
        elif (bufferInfo["Mem_b_h_w"] == "h"):
            write_half_word(data_MEM, bufferInfo["ALUResult"], bufferInfo["op2"])
        else:
            write_word(data_MEM, bufferInfo["ALUResult"], bufferInfo["op2"])
        print(f"MEMORY: WRITE 0x{bufferInfo['op2']:08x} to address 0x{bufferInfo['ALUResult']:08x}")
        
    else:
        print("MEMORY: No memory operation")

    MEM_WB_buff.ALUResult = bufferInfo["ALUResult"]
    MEM_WB_buff.immU = bufferInfo["immU"]
    MEM_WB_buff.pc_immU = bufferInfo["pc_immU"]
    MEM_WB_buff.loadData = loadData
    MEM_WB_buff.nextPC = bufferInfo["nextPC"]
    MEM_WB_buff.rd = bufferInfo["rd"]
    MEM_WB_buff.resultSelect = bufferInfo["resultSelect"]
    MEM_WB_buff.RFWrite = bufferInfo["RFWrite"]
    MEM_WB_buff.isStall = False





# writes the results back to register file
def write_back():
    global PC, immU, loadData, ALUResult, RFWrite, resultSelect, rd, X, nextPC, pc_immU

    if (RFWrite):
        if (rd != 0):
            if (resultSelect == 0):
                X[rd] = nextPC
                print(f"WRITEBACK: WRITE 0x{nextPC:08x} to x{rd}")
            elif (resultSelect == 1):
                X[rd] = immU
                print(f"WRITEBACK: WRITE 0x{immU:08x} to x{rd}")
            elif (resultSelect == 2):
                X[rd] = pc_immU
                print(f"WRITEBACK: WRITE 0x{pc_immU:08x} to x{rd}")
            elif (resultSelect == 3):
                X[rd] = loadData
                print(f"WRITEBACK: WRITE 0x{loadData:08x} to x{rd}")
            else:
                X[rd] = ALUResult
                print(f"WRITEBACK: WRITE 0x{ALUResult:08x} to x{rd}")
        else:
            print("WRITEBACK: Destination register x0. operation ignored")
    else:
        print("WRITEBACK: No operation")



def write_back2():
    global isExit, MEM_WB_buff, PC, immU, loadData, ALUResult, RFWrite, resultSelect, rd, X, nextPC, pc_immU

    bufferInfo = MEM_WB_buff.getInfo()

    if (bufferInfo["isStall"]):
        print("WRITEBACK: stall")
        return

    # if (bufferInfo["isEnd"]):
    #     print("WRITEBACK: No Operation")
    #     isExit = True
    #     return

    if (bufferInfo["RFWrite"]):
        if (bufferInfo["rd"] != 0):
            if (bufferInfo["resultSelect"] == 0):
                X[bufferInfo["rd"]] = bufferInfo["nextPC"]
                print(f"WRITEBACK: WRITE 0x{bufferInfo['nextPC']:08x} to x{bufferInfo['rd']}")
            elif (bufferInfo["resultSelect"] == 1):
                X[bufferInfo["rd"]] = bufferInfo["immU"]
                print(f"WRITEBACK: WRITE 0x{bufferInfo['immU']:08x} to x{bufferInfo['rd']}")
            elif (bufferInfo["resultSelect"] == 2):
                X[bufferInfo["rd"]] = bufferInfo["pc_immU"]
                print(f"WRITEBACK: WRITE 0x{bufferInfo['pc_immU']:08x} to x{bufferInfo['rd']}")
            elif (bufferInfo["resultSelect"] == 3):
                X[bufferInfo["rd"]] = bufferInfo["loadData"]
                print(f"WRITEBACK: WRITE 0x{bufferInfo['loadData']:08x} to x{bufferInfo['rd']}")
            else:
                X[bufferInfo["rd"]] = bufferInfo["ALUResult"]
                print(f"WRITEBACK: WRITE 0x{bufferInfo['ALUResult']:08x} to x{bufferInfo['rd']}")
        else:
            print("WRITEBACK: Destination register x0. operation ignored")
    else:
        print("WRITEBACK: No operation")



def read_word(address, mem):
    if (address % 4 == 0):
        return mem.get(address, 0)
    elif (address % 4 == 1):
        data1 = mem.get(address-1, 0)
        data2 = mem.get(address+3, 0)
        data1 = data1 & 0xFFFFFF00
        data1 = (data1 >> 8) & 0x00FFFFFF
        data2 = data2 & 0x000000FF
        data2 = data2 << 24
        return data1 + data2
    elif (address % 4 == 2):
        data1 = mem.get(address-2, 0)
        data2 = mem.get(address+2, 0)
        data1 = data1 & 0xFFFF0000
        data1 = (data1 >> 16) & 0x0000FFFF
        data2 = data2 & 0x0000FFFF
        data2 = data2 << 16
        return data1 + data2
    else:
        data1 = mem.get(address-3, 0)
        data2 = mem.get(address+1, 0)
        data1 = data1 & 0xFF000000
        data1 = (data1 >> 24) & 0x000000FF
        data2 = data2 & 0x00FFFFFF
        data2 = data2 << 8
        return data1 + data2

def read_half_word(address, mem):
    if (address % 4 == 0):
        data1 = mem.get(address, 0)
        data1 = data1 & 0x0000FFFF
        data1 = data1 << 16
        data1 = data1 >> 16
        return data1 
    elif (address % 4 == 1):
        data1 = mem.get(address-1, 0)
        data1 = data1 & 0x00FFFF00
        data1 = data1 << 8
        data1 = data1 >> 16
        return data1 
    elif (address % 4 == 2):
        data1 = mem.get(address-2, 0)
        data1 = data1 & 0xFFFF0000
        data1 = data1 >> 16
        return data1 
    else:
        data1 = mem.get(address-3, 0)
        data2 = mem.get(address+1, 0)
        data1 = data1 & 0xFF000000
        data1 = data1 >> 24
        data1 = data1 & 0x000000FF
        data2 = data2 & 0x000000FF
        data2 = data2 << 8
        data = data1 + data2
        data = (data << 16) >> 16
        return data

def read_byte(address, mem):
    if (address % 4 == 0):
        data1 = mem.get(address, 0)
        data1 = data1 & 0x000000FF
        data1 = (data1 << 24) >> 24
        return data1 
    elif (address % 4 == 1):
        data1 = mem.get(address-1, 0)
        data1 = data1 & 0x0000FF00
        data1 = (data1 << 16) >> 24
        return data1 
    elif (address % 4 == 2):
        data1 = mem.get(address-2, 0)
        data1 = data1 & 0x00FF0000
        data1 = (data1 << 8) >> 24
        return data1 
    else:
        data1 = mem.get(address-3, 0)
        data1 = data1 & 0xFF000000
        data1 = data1 >> 24
        return data1 

def write_word(mem, address, data):
    if (address % 4 == 0):
        mem[address] = data
    elif (address % 4 == 1):
        data1 = mem.get(address-1, 0)
        data2 = mem.get(address+3, 0)
        data2 = data2 & 0xFFFFFF00
        data2 = data2 + ((data >> 24) & 0x000000FF)
        data1 = data1 & 0x000000FF
        data1 = data1 + ((data << 8) & 0xFFFFFF00)
        mem[address-1] = data1
        mem[address+3] = data2
    elif (address % 4 == 2):
        data1 = mem.get(address-2, 0)
        data2 = mem.get(address+2, 0)
        data2 = data2 & 0xFFFF0000
        data2 = data2 + ((data >> 16) & 0x0000FFFF)
        data1 = data1 & 0x0000FFFF
        data1 = data1 + ((data << 16) & 0xFFFF0000)
        mem[address-2] = data1
        mem[address+2] = data2
    else:
        data1 = mem.get(address-3, 0)
        data2 = mem.get(address+1, 0)
        data2 = data2 & 0xFF000000
        data2 = data2 + ((data >> 8) & 0x00FFFFFF)
        data1 = data1 & 0x00FFFFFF
        data1 = data1 + ((data << 24) & 0xFF000000)
        mem[address-3] = data1
        mem[address+1] = data2

def write_half_word(mem, address, data):
    if (address % 4 == 0):
        data1 = mem.get(address, 0)
        data1 = data1 & 0xFFFF0000
        data1 = data1 + (data & 0x0000FFFF)
        mem[address] = data1
    elif (address % 4 == 1):
        data1 = mem.get(address-1, 0)
        data1 = data1 & 0xFF0000FF
        data1 = data1 + ((data << 8) & 0x00FFFF00)
        mem[address-1] = data1
    elif (address % 4 == 2):
        data1 = mem.get(address-2, 0)
        data1 = data1 & 0x0000FFFF
        data1 = data1 + ((data << 16) & 0xFFFF0000)
        mem[address-2] = data1
    else: 
        data1 = mem.get(address-3, 0)
        data2 = mem.get(address+1, 0)
        data1 = data1 & 0x00FFFFFF
        data1 = data1 + ((data << 24) & 0xFF000000)
        data2 = data2 & 0xFFFFFF00
        data2 = data2 + ((data >> 8) & 0x000000FF)
        mem[address-3] = data1
        mem[address+1] = data2

def write_byte(mem, address, data):
    if (address % 4 == 0):
        data1 = mem.get(address, 0)
        data1 = data1 & 0xFFFFFF00
        data1 = data1 + (data & 0x000000FF)
        mem[address] = data1
    elif (address % 4 == 1):
        data1 = mem.get(address-1, 0)
        data1 = data1 & 0xFFFF00FF
        data1 = data1 + ((data << 8) & 0x0000FF00)
        mem[address-1] = data1
    elif (address % 4 == 2):
        data1 = mem.get(address-2, 0)
        data1 = data1 & 0xFF00FFFF
        data1 = data1 + ((data << 16) & 0x00FF0000)
        mem[address-2] = data1
    else:
        data1 = mem.get(address-3, 0)
        data1 = data1 & 0x00FFFFFF
        data1 = data1 + ((data << 24) & 0xFF000000)
        mem[address-3] = data1


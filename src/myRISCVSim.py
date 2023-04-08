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

# input knobs
knob1 = False
knob2 = False
knob3 = False
knob4 = False
knob5 = 0
PC_of_target_ins = -1


# inter stage buffers
IF_ID_buff = st.IF_ID_Pipeline_Registers()
ID_EX_buff = st.ID_EX_Pipeline_Registers()
EX_MEM_buff = st.EX_MEM_Pipeline_Registers()
MEM_WB_buff = st.MEM_WB_Pipeline_Registers()

# temporary buffer to copy contents of MEM_WB_buff
temp_MEM_WB_buff = st.MEM_WB_Pipeline_Registers()

# Branch Target buffer
btb = st.BTB()

stats = st.Stats()


def run_riscvsim():
    global stats, PC, clock, isFlush, PC_on_missprediction, IF_ID_buff, ID_EX_buff, EX_MEM_buff, MEM_WB_buff,isExit, isLastIns, knob1

    if (knob1):
        # in case of pipelined implemetation
        while(isExit == False):
            write_back_p()
            if (MEM_WB_buff.PC == PC_of_target_ins):
                MEM_WB_buff.printContents()
            mem_p()
            if (EX_MEM_buff.PC == PC_of_target_ins):
                MEM_WB_buff.printContents()
            execute_p()
            if (ID_EX_buff.PC == PC_of_target_ins):
                ID_EX_buff.printContents()
            decode_p()
            if (IF_ID_buff.PC == PC_of_target_ins):
                IF_ID_buff.printContents()
            fetch_p()

            clock += 1
            print("clock cycle : ", clock)

            if (knob3):
                print_RF()
            
            if (knob4):
                IF_ID_buff.printContents()
                ID_EX_buff.printContents()
                EX_MEM_buff.printContents()
                MEM_WB_buff.printContents()
            print("-------------------------------------------------------------------------------------------------\n")

            if (isFlush):
                PC = PC_on_missprediction
                isLastIns = False
                IF_ID_buff.flush()
                ID_EX_buff.flush()
                isFlush = False

            if (isLastIns and IF_ID_buff.isStall and ID_EX_buff.isStall and EX_MEM_buff.isStall and MEM_WB_buff.isStall):
                isExit = True
    else:
        # in case of non pipelined implementation
        while(True):
            fetch_np()
            if (isExit):
                break
            decode_np()
            if (isExit):
                break
            execute_np()
            mem_np()
            write_back_np()
        
            clock += 1
            print("clock cycle : ", clock)
            print("-------------------------------------------------------------------------------------------------\n")

    stats.cycles = clock
    #call the exit method        
    swi_exit()

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
    global ins_MEM, PC_of_target_ins

    with open(file_name, "r") as fp:
        i = 0
        for line in fp:
            if (i/4 == knob5-1):
                PC_of_target_ins = i
            # address, ins = map(lambda x: int(x, 16), line.split())
            ins = int(line.strip()[2:], 16)
            write_word(ins_MEM, i, ins)
            i += 4


# to store the input data from the user
def load_data_memory(data):
    global data_MEM

    index1 = int("0x10001000", 16)
    index2 = int("0x10002000", 16)
    for i in range(len(data)):
        write_word(data_MEM, index1+i*4, data[i])
        write_word(data_MEM, index2+i*4, data[i])


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
    global stats
    write_data_memory()
    stats.calculateCPI()
    stats.printToFile()
    # write_ins_memory()
    print("Completed writting data to data_out.mem")
    print("Program finished")
    exit(0)

def print_RF():
    global X

    print("\nRegister File\n")
    for i in range(32):
        print(f"X{i} : 0x{X[i]:08x}")


# reads from the instruction memory and updates the instruction register
def fetch_np():
    global ins_MEM, PC, instruction_word, isExit, nextPC

    instruction_word = read_word(PC, ins_MEM)
    print(f"FETCH:Fetch instruction 0x{instruction_word:08x} from address 0x{hex(PC)}")

    # checking if the instruction is swi_exit
    if (instruction_word == int('0xEF000011', 16)):
        isExit = True


    nextPC = PC + 4

def fetch_p():
    global stats, stallUp, isLastIns, stall, ins_MEM, PC, instruction_word, isExit, nextPC, IF_ID_buff, isEnd

    if (stall > 1 and stall < stallUp):
        print("FETCH: stalled")
        # out_file.write("FETCH:")
        stall -= 1
        return
    
    if (stall == 1):
        stall -= 1

    # if (isEnd):
    #     print("FETCH: No Operation")
    if (isLastIns):
        print("FETCH: Already fetched last instruction")

    else:
        instruction_word = read_word(PC, ins_MEM)
        print(f"FETCH:Fetch instruction 0x{instruction_word:08x} from address 0x{PC:08x}")

        if (stall == stallUp):
                print("stalled")
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

            # stats.instructions += 1

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
def decode_np():
    global stats, isBranch, rd, rs1, rs2, op1, op2, operand1, operand2,op2Select, instruction_word, X, MemOp,Mem_b_h_w, operation, resultSelect, RFWrite, immB, immI, immJ, immS, immU, branchTargetSelect, resultSelect, ALUOp, isExit

    instruction_in_binary = bin(instruction_word)[2:].zfill(32)
    opcode = instruction_in_binary[25:32]

    fun7 = instruction_in_binary[0:7]
    fun3 = instruction_in_binary[17:20]

    rd = int(instruction_in_binary[20:25], 2)
    rs1 = int(instruction_in_binary[12:17], 2)
    rs2 = int(instruction_in_binary[7:12], 2)

    isBranch = 0

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
        MemOp = 0
        RFWrite = True

        if (fun3 == "000" and fun7 == "0000000"):
            operation = 0
            ALUOp = 0
        elif (fun3 == "000" and fun7 == "0100000"):
            operation = 1
            ALUOp = 1
        elif (fun3 == "100" and "0000000"):
            operation = 2
            ALUOp = 2
        elif (fun3 == "110" and fun7 == "0000000"):
            operation = 3
            ALUOp = 3
        elif (fun3 == "111" and fun7 == "0000000"):
            operation = 4
            ALUOp = 4
        elif (fun3 == "001" and fun7 == "0000000"):
            operation = 5
            ALUOp = 5
        elif (fun3 == "101" and fun7 == "0000000"):
            operation = 6
            ALUOp = 6
        elif (fun3 == "101" and fun7 == "0100000"):
            operation = 7
            ALUOp = 7
        elif (fun3 == "010" and fun7 == "0000000"):
            operation = 8
            ALUOp = 8
        else:
            print("Instruction not supported")
            swi_exit()

        
    elif (opcode == "0010011"):
        # I type (addi, ori, andi)

        op2Select = 1
        resultSelect = 4
        MemOp = 0
        RFWrite = True

        if (fun3 == "000"):
            operation = 9
            ALUOp = 0
        elif (fun3 == "100"):
            operation = 10
            ALUOp = 2
        elif (fun3 == "110"):
            operation = 11
            ALUOp = 3
        elif (fun3 == "111"):
            operation = 12
            ALUOp = 4
        elif (fun3 == "001"):
            operation = 13
            ALUOp = 5
        elif (fun3 == "101"):
            # if (instruction_in_binary[0:7] == "000000"):
            #     operation = "srli"
            #     ALUOp = "srl"
            # else:
            #     operation = "srai"
            #     ALUOp = "sra"
            operation = 14
            ALUOp = 6
        elif (fun3 == "010"):
            operation = 15
            ALUOp = 8
        else:
            print("Instruction not supported")
            swi_exit()

        
    elif (opcode == "0000011"):
        # I type (lb, lh, lw)

        op2Select = 1
        resultSelect = 3
        MemOp = 1
        RFWrite = True
        ALUOp = 0

        if (fun3 == "000"):
            operation = 16
            Mem_b_h_w = 0
        elif (fun3 == "001"):
            operation = 17
            Mem_b_h_w = 1
        elif (fun3 == "010"):
            operation = 18
            Mem_b_h_w = 2
        else:
            print("Instruction not supported")
            swi_exit()

        
    elif (opcode == "0100011"):
        # S type
        
        op2Select = 2
        MemOp = 2
        RFWrite = False
        ALUOp = 0

        if (fun3 == "000"):
            operation = 19
            Mem_b_h_w = 0
        elif (fun3 == "001"):
            operation = 20
            Mem_b_h_w = 1
        elif (fun3 == "010"):
            operation = 21
            Mem_b_h_w = 2
        else:
            print("Instruction not supported")
            swi_exit()


    elif (opcode == "1100011"):
        # B type
        op2Select = 0
        branchTargetSelect = 0
        MemOp = 0
        RFWrite = False

        stats.control_ins += 1

        if (fun3 == "000"):
            operation = 22
            ALUOp = 9
        elif (fun3 == "001"):
            operation = 23
            ALUOp = 10
        elif (fun3 == "100"):
            operation = 24
            ALUOp = 11
        elif (fun3 == "101"):
            operation = 25
            ALUOp = 12
        else:
            print("Instruction not supported")
            swi_exit()

    elif (opcode == "1101111"):
        # J type (jal)
        
        branchTargetSelect = 1
        resultSelect = 0
        MemOp = 0
        RFWrite = True
        ALUOp = 15
        operation = 26
        isBranch = 1

        stats.control_ins += 1


    elif (opcode == "1100111"):
        # I type (jalr)
        
        resultSelect = 0
        op2Select = 1
        MemOp = 0
        RFWrite = True
        ALUOp = 0
        isBranch = 2

        stats.control_ins += 1

        if (fun3 == "000"):
            operation = 27
        else:
            print("Instruction not supported")
            swi_exit()
        
    elif (opcode == "0110111"):
        # U type (lui)
        
        resultSelect = 1
        MemOp = 0
        RFWrite = True
        operation = 28
        ALUOp = 15

    elif (opcode == "0010111"):
        # U type (auipc)
        
        resultSelect = 2
        MemOp = 0
        RFWrite = True
        operation = 29
        ALUOp = 15

    else:
        print("Instruction not supported")
        isExit = True
    
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
    
    
def decode_p():
    global stats, stallUp, isBranch, stall, IF_ID_buff, ID_EX_buff, rd, rs1, rs2, op1, op2, operand1, operand2,op2Select, instruction_word, X, MemOp,Mem_b_h_w, operation, resultSelect, RFWrite, immB, immI, immJ, immS, immU, branchTargetSelect, resultSelect, ALUOp, isExit

    if (stall > 1):
        print("DECODE: stalled")
        ID_EX_buff.flush()
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
        MemOp = 0
        RFWrite = True

        if (fun3 == "000" and fun7 == "0000000"):
            operation = 0
            ALUOp = 0
        elif (fun3 == "000" and fun7 == "0100000"):
            operation = 1
            ALUOp = 1
        elif (fun3 == "100" and "0000000"):
            operation = 2
            ALUOp = 2
        elif (fun3 == "110" and fun7 == "0000000"):
            operation = 3
            ALUOp = 3
        elif (fun3 == "111" and fun7 == "0000000"):
            operation = 4
            ALUOp = 4
        elif (fun3 == "001" and fun7 == "0000000"):
            operation = 5
            ALUOp = 5
        elif (fun3 == "101" and fun7 == "0000000"):
            operation = 6
            ALUOp = 6
        elif (fun3 == "101" and fun7 == "0100000"):
            operation = 7
            ALUOp = 7
        elif (fun3 == "010" and fun7 == "0000000"):
            operation = 8
            ALUOp = 8
        else:
            print("Instruction not supported")
            swi_exit()

        
    elif (opcode == "0010011"):
        # I type (addi, ori, andi)

        op2Select = 1
        resultSelect = 4
        MemOp = 0
        RFWrite = True

        if (fun3 == "000"):
            operation = 9
            ALUOp = 0
        elif (fun3 == "100"):
            operation = 10
            ALUOp = 2
        elif (fun3 == "110"):
            operation = 11
            ALUOp = 3
        elif (fun3 == "111"):
            operation = 12
            ALUOp = 4
        elif (fun3 == "001"):
            operation = 13
            ALUOp = 5
        elif (fun3 == "101"):
            # if (instruction_in_binary[0:7] == "000000"):
            #     operation = "srli"
            #     ALUOp = "srl"
            # else:
            #     operation = "srai"
            #     ALUOp = "sra"
            operation = 14
            ALUOp = 6
        elif (fun3 == "010"):
            operation = 15
            ALUOp = 8
        else:
            print("Instruction not supported")
            swi_exit()

        
    elif (opcode == "0000011"):
        # I type (lb, lh, lw)

        op2Select = 1
        resultSelect = 3
        MemOp = 1
        RFWrite = True
        ALUOp = 0

        if (fun3 == "000"):
            operation = 16
            Mem_b_h_w = 0
        elif (fun3 == "001"):
            operation = 17
            Mem_b_h_w = 1
        elif (fun3 == "010"):
            operation = 18
            Mem_b_h_w = 2
        else:
            print("Instruction not supported")
            swi_exit()

        
    elif (opcode == "0100011"):
        # S type
        
        op2Select = 2
        MemOp = 2
        RFWrite = False
        ALUOp = 0

        if (fun3 == "000"):
            operation = 19
            Mem_b_h_w = 0
        elif (fun3 == "001"):
            operation = 20
            Mem_b_h_w = 1
        elif (fun3 == "010"):
            operation = 21
            Mem_b_h_w = 2
        else:
            print("Instruction not supported")
            swi_exit()


    elif (opcode == "1100011"):
        # B type
        op2Select = 0
        branchTargetSelect = 0
        MemOp = 0
        RFWrite = False

        if (fun3 == "000"):
            operation = 22
            ALUOp = 9
        elif (fun3 == "001"):
            operation = 23
            ALUOp = 10
        elif (fun3 == "100"):
            operation = 24
            ALUOp = 11
        elif (fun3 == "101"):
            operation = 25
            ALUOp = 12
        else:
            print("Instruction not supported")
            swi_exit()

    elif (opcode == "1101111"):
        # J type (jal)
        
        branchTargetSelect = 1
        resultSelect = 0
        MemOp = 0
        RFWrite = True
        ALUOp = 15
        operation = 26
        isBranch = 1


    elif (opcode == "1100111"):
        # I type (jalr)
        
        resultSelect = 0
        op2Select = 1
        MemOp = 0
        RFWrite = True
        ALUOp = 0
        isBranch = 2

        if (fun3 == "000"):
            operation = 27
        else:
            print("Instruction not supported")
            swi_exit()
        
    elif (opcode == "0110111"):
        # U type (lui)
        
        resultSelect = 1
        MemOp = 0
        RFWrite = True
        operation = 28
        ALUOp = 15

    elif (opcode == "0010111"):
        # U type (auipc)
        
        resultSelect = 2
        MemOp = 0
        RFWrite = True
        operation = 29
        ALUOp = 15

    else:
        print("Instruction not supported")
        isExit = True
    # Condition for data dependency
    # print("DP Var : stall = ", stall, " ALUOp: ", ALUOp, " IDEXBuff.RFWrite: ", ID_EX_buff.RFWrite, " rs1: ", rs1, " rs2: ", rs2, " op2select: ", op2Select)
    if ( not knob2):
        # if (stall == 0 and ALUOp != "-1" and ID_EX_buff.RFWrite == True and (rs1 == ID_EX_buff.rd or (rs2 == ID_EX_buff.rd and op2Select == 0) or (rs2 == ID_EX_buff.rd and MemOp == "w"))):
        #     print("DECODE: stall1")
        #     stall = 3
        #     stallUp = 3
        #     # ID_EX_buff.isStall = True
        #     ID_EX_buff.flush()
        #     return
    
        if (stall == 0 and ALUOp != 15 and EX_MEM_buff.RFWrite == True and (rs1 == EX_MEM_buff.rd or (rs2 == EX_MEM_buff.rd and op2Select == 0) or (rs2 == EX_MEM_buff.rd and MemOp == 2))):
            print("DECODE: stall2")
            stall = 3
            stallUp = 3
            # ID_EX_buff.isStall = True
            ID_EX_buff.flush()
            stats.stalls += 2
            stats.data_hazards += 1
            stats.stalls_data_hazards += 2
            return
    
        if (stall == 0 and ALUOp != 15 and MEM_WB_buff.RFWrite == True and (rs1 == MEM_WB_buff.rd or (rs2 == MEM_WB_buff.rd and op2Select == 0) or (rs2 == ID_EX_buff.rd and MemOp == 2))):
            print("DECODE: stall3")
            stall = 2
            stallUp = 2
            # ID_EX_buff.isStall = True
            ID_EX_buff.flush()
            stats.stalls += 1
            stats.data_hazards += 1
            stats.stalls_data_hazards += 1
            return
    
    # if (stall == 0 and ID_EX_buff.MemOp == 'r' and ALUOp != '-1' and (ID_EX_buff.rd == rs1 or (rs2 == ID_EX_buff.rd and op2Select == 0))):
    #     print("DECODE: stall3")
    #     stall = 2
    #     stallUp = 2
    #     # ID_EX_buff.isStall = True
    #     ID_EX_buff.flush()
    #     return    
    
    if (stall == 0 and ID_EX_buff.MemOp == 1 and (ID_EX_buff.rd == rs1 or ID_EX_buff.rd == rs2)):
        print("DECODE: stalled")
        stall = 2
        stallUp = 2
        #TODO
        stats.data_hazards += 1
        stats.stalls += 1
        stats.stalls_data_hazards += 1
        # ID_EX_buff.flush()
        # stats.instructions -= 1
        return
    
    operand1 = X[rs1]
    op1 = X[rs1]
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
    ID_EX_buff.op2Select = op2Select
    ID_EX_buff.RFWrite = RFWrite
    ID_EX_buff.rs1 = rs1
    ID_EX_buff.rs2 = rs2
    ID_EX_buff.isStall = False
    ID_EX_buff.branchTaken = IF_ID_buff.branchTaken
    ID_EX_buff.PC = bufferInfo["PC"]
    ID_EX_buff.predictedPC = bufferInfo["predictedPC"]

  
# executes the operations based on ALUOp
def execute_np():
    global stats, PC, rd, op2, pc_immU, operand1, operand2, instruction_word, X, MemOp, operation, RFWrite, ALUResult, ALUOp, isBranch, immU, branchTargetSelect, branchTargetAddress

    # performing the ALU operation
    if (ALUOp != 15):
        ALUUnit = functions.ALU(ALUOp, operand1, operand2)
        ALUResult = ALUUnit.compute()
        print(f"EXECUTE: {ALUOp} 0x{operand1:08x} and 0x{operand2:08x}")
        stats.ALU_ins += 1
    else:
        print(f"EXECUTE: No ALU operation")

    # computing branch target address
    if (branchTargetSelect == 0):
        branchTargetAddress = PC + immB
    else:
        branchTargetAddress = PC + immJ
    
    # deciding whether branch is taken or not
    if (operation == 22 or operation == 23 or operation == 24 or operation == 25):
        if (ALUResult == 1):
            isBranch = 1
        else:
            isBranch = 0

    # update PC 
    if (isBranch == 0):
        PC = nextPC
    elif (isBranch == 1):
        PC = branchTargetAddress
    else:
        PC = ALUResult

    # computing value of PC + immU    
    pc_immU = PC + immU

    


def execute_p():
    global stats, btb, isFlush, PC_on_missprediction, ID_EX_buff, EX_MEM_buff, ALUResult, isBranch, branchTargetAddress, stall, stallUp

    bufferInfo = ID_EX_buff.getInfo()

    if (bufferInfo["isStall"]):
        print("EXECUTE: stall")
        # EX_MEM_buff.isStall = True
        EX_MEM_buff.flush()
        return
    
    # print("rs1: ", bufferInfo["rs1"], "     rs2: ", bufferInfo["rs2"])
    ex_operand1 = bufferInfo["operand1"]
    ex_operand2 = 0
    ex_rs2_value = bufferInfo["op2"]

    has_data_dependency = 0

    if (knob2):
        f_rs1 = 0
        f_rs2 = 0

        # if (stall == 0 and EX_MEM_buff.MemOp == 'r' and (EX_MEM_buff.rd == bufferInfo["rs1"] or EX_MEM_buff.rd == bufferInfo["rs2"])):
        #     stall = 2
        #     stallUp = 2
        #     return
    
        if (EX_MEM_buff.RFWrite and EX_MEM_buff.rd != 0 and EX_MEM_buff.rd == bufferInfo["rs1"] and EX_MEM_buff.MemOp != 1):
            f_rs1 = 1
            # ex_operand1 = EX_MEM_buff.ALUResult
        elif (temp_MEM_WB_buff.RFWrite and temp_MEM_WB_buff.rd != 0 and temp_MEM_WB_buff.rd == bufferInfo["rs1"]):
            f_rs1 = 2
            if (temp_MEM_WB_buff.MemOp == 1):
                f_alu_mem = 1
                f_rs1 = 3
        else:
            pass
        if (EX_MEM_buff.RFWrite and EX_MEM_buff.rd != 0 and EX_MEM_buff.rd == bufferInfo["rs2"] and EX_MEM_buff.MemOp != 1):
            # ex_rs2_value = EX_MEM_buff.ALUResult
            f_rs2 = 1
            
        elif (temp_MEM_WB_buff.RFWrite and temp_MEM_WB_buff.rd != 0 and temp_MEM_WB_buff.rd == bufferInfo["rs2"]):
            f_rs2 = 2
            if (temp_MEM_WB_buff.MemOp == 1):
                f_alu_mem = 1
                f_rs2 = 3
        else:
            pass

        if (f_rs1 == 0):
            ex_operand1 = bufferInfo["op1"]
        elif (f_rs1 == 1):
            ex_operand1 = EX_MEM_buff.ALUResult
            has_data_dependency = 1
        elif (f_rs1 == 2):
            ex_operand1 = temp_MEM_WB_buff.ALUResult
            has_data_dependency = 1
        else:
            ex_operand1 = temp_MEM_WB_buff.loadData
            has_data_dependency = 1


        
        if (f_rs2 == 0):
            ex_rs2_value = bufferInfo["op2"]
        elif (f_rs2 == 1):
            ex_rs2_value = EX_MEM_buff.ALUResult
            has_data_dependency = 1
        elif (f_rs2 == 2):
            ex_rs2_value = temp_MEM_WB_buff.ALUResult
            has_data_dependency = 1
        else:
            ex_rs2_value = temp_MEM_WB_buff.loadData
            has_data_dependency = 1



    if (bufferInfo["op2Select"] == 0):
        ex_operand2 = ex_rs2_value
        if (knob2 and has_data_dependency == 1):
            stats.data_hazards += 1
    elif (bufferInfo["op2Select"] == 1):
        ex_operand2 = bufferInfo["immI"]
    else:
        ex_operand2 = bufferInfo["immS"]


    if (bufferInfo["ALUOp"] != 15):
        ALUUnit = functions.ALU(bufferInfo["ALUOp"], ex_operand1, ex_operand2)
        ALUResult = ALUUnit.compute()
        print(f"EXECUTE: {bufferInfo['ALUOp']} 0x{ex_operand1:08x} and 0x{ex_operand2:08x}")
        stats.ALU_ins += 1
    else:
        print(f"EXECUTE: No ALU operation")

    if (bufferInfo["branchTargetSelect"] == 0):
        branchTargetAddress = bufferInfo["nextPC"] - 4 + bufferInfo["immB"]
    else:
        branchTargetAddress = bufferInfo["nextPC"] - 4 + bufferInfo["immJ"]
        
    
    if (bufferInfo["operation"] == 22 or bufferInfo["operation"] == 23 or bufferInfo["operation"] == 24 or bufferInfo["operation"] == 25):
        if (not btb.hasPC(bufferInfo["PC"])):
            btb.addNewPC(bufferInfo["PC"], branchTargetAddress, 1)
        if (ALUResult == 1):
            isBranch = 1
            if (not ID_EX_buff.branchTaken):
                isFlush = True
                PC_on_missprediction = branchTargetAddress
                btb.updateisTaken(bufferInfo["PC"], True)
                stats.branch_mispredictions += 1
                stats.stalls_control_hazards += 2
                # stats.instructions -= 2
        else:
            isBranch = 0
            if (ID_EX_buff.branchTaken):
                isFlush = True
                PC_on_missprediction = ID_EX_buff.nextPC
                btb.updateisTaken(bufferInfo["PC"], False)
                stats.branch_mispredictions += 1
                stats.stalls_control_hazards += 2
                # stats.instructions -= 2

        stats.control_ins += 1
        stats.control_hazards += 1
                
    elif (bufferInfo["operation"] == 26):
        isBranch = 1
        if (not btb.hasPC(bufferInfo["PC"])):
            btb.addNewPC(bufferInfo["PC"], branchTargetAddress, 3)

        if (not ID_EX_buff.branchTaken):
            isFlush = True
            PC_on_missprediction = branchTargetAddress
            stats.branch_mispredictions += 1
            stats.stalls_control_hazards += 2
            # stats.instructions -= 2
        stats.control_ins += 1

    elif (bufferInfo["operation"] == 27):
        isBranch = 2
        if (not btb.hasPC(bufferInfo["PC"])):
            btb.addNewPC(bufferInfo["PC"], ALUResult, 3)

        if (bufferInfo["predictedPC"] != ALUResult):
            isFlush = True
            PC_on_missprediction = ALUResult
            btb.updateTargetAddr(bufferInfo["PC"], ALUResult)
            stats.branch_mispredictions += 1
            stats.stalls_control_hazards += 2
            # stats.instructions -= 2
        stats.control_ins += 1
    else:
        isBranch = 0

    pc_immU = bufferInfo["nextPC"] - 4 + bufferInfo["immU"]

    EX_MEM_buff.nextPC = bufferInfo["nextPC"]
    EX_MEM_buff.ALUResult = ALUResult
    EX_MEM_buff.branchTargetAddress = branchTargetAddress
    EX_MEM_buff.isBranch = isBranch
    EX_MEM_buff.Mem_b_h_w = bufferInfo["Mem_b_h_w"]
    EX_MEM_buff.MemOp = bufferInfo["MemOp"]
    # EX_MEM_buff.op2 = bufferInfo["op2"]
    EX_MEM_buff.op2 = ex_rs2_value
    EX_MEM_buff.immU = bufferInfo["immU"]
    EX_MEM_buff.pc_immU = pc_immU
    EX_MEM_buff.rd = bufferInfo["rd"]
    EX_MEM_buff.resultSelect = bufferInfo["resultSelect"]
    EX_MEM_buff.RFWrite = bufferInfo["RFWrite"]
    EX_MEM_buff.isStall = False

    stats.instructions += 1

# perform the memory operation
def mem_np():
    global stats, data_MEM, MemOp, ALUResult, Mem_b_h_w, loadData, op2

    if (MemOp == 1):
        if (Mem_b_h_w == 0):
            loadData = read_byte(ALUResult, data_MEM)
        elif (Mem_b_h_w == 1):
            loadData = read_half_word(ALUResult, data_MEM)
        else:
            loadData = read_word(ALUResult, data_MEM)
        print(f"MEMORY: READ 0x{loadData:08x} from address 0x{ALUResult:08x}")

        stats.data_transfers += 1

    elif (MemOp == 2):
        if (Mem_b_h_w == 0):
            write_byte(data_MEM, ALUResult, op2)
        elif (Mem_b_h_w == 1):
            write_half_word(data_MEM, ALUResult, op2)
        else:
            write_word(data_MEM, ALUResult, op2)
        print(f"MEMORY: WRITE 0x{op2:08x} to address 0x{ALUResult:08x}")
        stats.data_transfers += 1
        
    else:
        print("MEMORY: No memory operation")

def mem_p():
    global stats, temp_MEM_WB_buff, EX_MEM_buff, MEM_WB_buff, data_MEM, MemOp, ALUResult, Mem_b_h_w, loadData, op2

    bufferInfo = EX_MEM_buff.getInfo()

    if (bufferInfo["isStall"]):
        print("MEMORY: stalled")
        # MEM_WB_buff.isStall = True
        MEM_WB_buff.flush()
        return
    
    # if (bufferInfo["isEnd"]):
    #     print("MEMORY: No Operation")
    #     MEM_WB_buff.isEnd = True
    #     return
    
    if (knob2):
        
        if (bufferInfo["MemOp"] == 2 and MEM_WB_buff.RFWrite and MEM_WB_buff.rd == bufferInfo["rd"]):
            if (MEM_WB_buff.MemOp == 1):
                bufferInfo["op2"] = MEM_WB_buff.loadData
            else:
                bufferInfo["op2"] = MEM_WB_buff.ALUResult
            stats.data_hazards += 1
    
    if (bufferInfo["MemOp"] == 1):
        if (bufferInfo["Mem_b_h_w"] == 0):
            loadData = read_byte(bufferInfo["ALUResult"], data_MEM)
        elif (bufferInfo["Mem_b_h_w"] == 1):
            loadData = read_half_word(bufferInfo["ALUResult"], data_MEM)
        else:
            loadData = read_word(bufferInfo["ALUResult"], data_MEM)
        print(f"MEMORY: READ 0x{loadData:08x} from address 0x{bufferInfo['ALUResult']:08x}")

        stats.data_transfers += 1

    elif (bufferInfo["MemOp"] == 2):
        if (bufferInfo["Mem_b_h_w"] == 0):
            write_byte(data_MEM, bufferInfo["ALUResult"], bufferInfo["op2"])
        elif (bufferInfo["Mem_b_h_w"] == 1):
            write_half_word(data_MEM, bufferInfo["ALUResult"], bufferInfo["op2"])
        else:
            write_word(data_MEM, bufferInfo["ALUResult"], bufferInfo["op2"])
        print(f"MEMORY: WRITE 0x{bufferInfo['op2']:08x} to address 0x{bufferInfo['ALUResult']:08x}")
        
        stats.data_transfers += 1
    else:
        print("MEMORY: No memory operation")

    temp_MEM_WB_buff.copy(MEM_WB_buff)

    MEM_WB_buff.ALUResult = bufferInfo["ALUResult"]
    MEM_WB_buff.immU = bufferInfo["immU"]
    MEM_WB_buff.pc_immU = bufferInfo["pc_immU"]
    MEM_WB_buff.loadData = loadData
    MEM_WB_buff.nextPC = bufferInfo["nextPC"]
    MEM_WB_buff.rd = bufferInfo["rd"]
    MEM_WB_buff.resultSelect = bufferInfo["resultSelect"]
    MEM_WB_buff.RFWrite = bufferInfo["RFWrite"]
    MEM_WB_buff.MemOp = bufferInfo["MemOp"]
    MEM_WB_buff.isStall = False



# writes the results back to register file
def write_back_np():
    global stats, PC, immU, loadData, ALUResult, RFWrite, resultSelect, rd, X, nextPC, pc_immU

    stats.instructions += 1

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

def write_back_p():
    global stats, isExit, MEM_WB_buff, PC, immU, loadData, ALUResult, RFWrite, resultSelect, rd, X, nextPC, pc_immU

    bufferInfo = MEM_WB_buff.getInfo()

    if (bufferInfo["isStall"]):
        print("WRITEBACK: stall")
        return

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


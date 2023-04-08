import myRISCVSim as m

def main():
    fileName = input("Enter the file name: ")

    knob1 = False
    knob2 = False
    knob3 = False
    knob4 = False
    knob5 = 0
 
    knob1 = True if input("Pipelined(yes/no) (default: no): ") == "yes" else False

    if (knob1):
        knob2 = True if input("enable data forwarding (yes/no) (default: no): ") == "yes" else False
        knob3 = True if input("Enable/disable printing values in the register file at the end of each cycle (default: no): ") == "yes" else False
        knob4 = True if input("Enable/disable printing information in the pipeline registers at the end of each cycle (default: no): ") else False
        
        try:
            num = int(input("Enable Knob4 for a specific instruction: "))
            if num <= 0:
                knob5 = 0
            else:
                knob5 = num
        except ValueError:
            knob5 = 0
        
        

    # Reset the processor
    m.reset_proc()

    m.knob1 = knob1
    m.knob2 = knob2
    m.knob3 = knob3
    m.knob4 = knob4
    m.knob5 = knob5

    # Load the program memory
    m.load_program_memory(fileName)

    # data = [int(i) for i in input().split(" ")]
    # m.load_data_memory(data)

    # Run the simulator
    m.run_riscvsim()

if __name__ == '__main__':
    main()
















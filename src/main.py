import myRISCVSim as m

def main():
    fileName = input("Enter the file name: ")

    a = input("Pipelined(yes/no) (default: no): ")
    isPipelined = True if a == "yes" else False

    b = input("enable data forwarding (yes/no) (default: no): ")
    isDF = True if b == "yes" else False


    # Reset the processor
    m.reset_proc()

    # Load the program memory
    m.load_program_memory(fileName)

    # data = [int(i) for i in input().split(" ")]
    # m.load_data_memory(data)

    m.isPipelined = isPipelined
    m.hasDataForwarding = isDF
    
    # Run the simulator
    m.run_riscvsim()

if __name__ == '__main__':
    main()
















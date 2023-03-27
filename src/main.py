import myRISCVSim as m

def main():
    fileName = input("Enter the file name: ")
    # Reset the processor
    m.reset_proc()

    # Load the program memory
    m.load_program_memory(fileName)

    # Run the simulator
    m.run_riscvsim()

if __name__ == '__main__':
    main()


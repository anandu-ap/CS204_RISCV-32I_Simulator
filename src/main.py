import myRISCVSim as m
import tkinter as tk

def run_simulator():
    global input_field
    # Get the file name from the input field
    filename = input_field.get()

    # Reset the processor
    m.reset_proc()

    # Load the program memory
    m.load_program_memory(filename)

    # Run the simulator
    m.run_riscvsim()

def main():
    global input_field
    root = tk.Tk()

    # Set the window size and make it non-resizable
    root.geometry("500x500")
    root.resizable(False, False)

    # Create the input field and label
    input_label = tk.Label(root, text="Enter file name:")
    input_label.pack()
    input_field = tk.Entry(root)
    input_field.pack()

    # Create the "Run" button
    run_button = tk.Button(root, text="Run", command=run_simulator)
    run_button.pack()

    # Start the main event loop
    root.mainloop()


if __name__ == '__main__':
    main()


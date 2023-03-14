with open("bs.mem", "r") as f:
    hex_list = [int(line.strip(), 16) for line in f]

with open("bs2.mem", "w") as fp:
    for i in range(len(hex_list)):
        fp.write(f"{hex(i*4)} 0x{hex_list[i]:08x}\n")




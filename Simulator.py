import sys

input_file = sys.argv[1]
output_file = sys.argv[2]

extra_file = None
if len(sys.argv) > 3:
    extra_file = sys.argv[3]

f = open(input_file, "r")
lines = f.readlines()
f.close()

instructions = []
for l in lines:
    l = l.strip()
    if l != "":
        instructions.append(l)

regs = []
for i in range(32):
    regs.append(0)

regs[2] = 0x0000017C   # stack pointer

memory = {}

for i in range(32):
    addr = 0x00010000 + i * 4
    memory[addr] = 0

for i in range(32):
    addr = 0x00000100 + i * 4
    memory[addr] = 0

PC = 0
output_lines = []

def to_bin(val):
    val = val & 0xFFFFFFFF
    binary = bin(val)[2:]

    while len(binary) < 32:
        binary = "0" + binary

    return binary

def sign_ext(val, bits):
    if val & (1 << (bits - 1)):
        val = val - (1 << bits)
    return val

def to_signed(val):
    val = val & 0xFFFFFFFF
    if (val >> 31) == 1:
        val = val - (2 ** 32)
    return val

def mask32(val):
    return val & 0xFFFFFFFF

def check_memory_access(addr, rs1, pc):

    # address kaha fall kra ha
    data_start = 0x00010000
    data_end = 0x0001007F
    stack_start = 0x00000100
    stack_end = 0x0000017F

    in_data = (addr >= data_start and addr <= data_end)
    in_stack = (addr >= stack_start and addr <= stack_end)

    if not in_data and not in_stack:
        print("Error: memory out of bounds at pc:", pc)
        return False

    if rs1 == 2 and not in_stack:
        print("Error: illegal stack memory access at pc:", pc)
        return False

    if rs1 != 2 and in_stack:
        print("Error: accessing stack memory without sp at pc:", pc)
        return False

    if addr % 4 != 0:
        print("Error: unaligned memory access at pc:", pc)
        return False

    return True

error_found = False

while True:

    index = PC // 4

    if index < 0 or index >= len(instructions):
        print("PC out of range:", PC)
        break

    instr = instructions[index]
    opcode = instr[25:32]
    halt = False

    if opcode == "0110011":

        funct7 = instr[0:7]
        rs2 = int(instr[7:12], 2)
        rs1 = int(instr[12:17], 2)
        funct3 = instr[17:20]
        rd = int(instr[20:25], 2)

        v1 = regs[rs1]
        v2 = regs[rs2]

        result = 0

        if funct3 == "000":
            if funct7 == "0000000":
                result = mask32(v1 + v2)
            elif funct7 == "0100000":
                result = mask32(v1 - v2)

        elif funct3 == "001":
            result = mask32(v1 << (v2 & 31))

        elif funct3 == "010":
            if to_signed(v1) < to_signed(v2):
                result = 1
            else:
                result = 0

        elif funct3 == "011":
            if (v1 & 0xFFFFFFFF) < (v2 & 0xFFFFFFFF):
                result = 1
            else:
                result = 0

        elif funct3 == "100":
            result = mask32(v1 ^ v2)

        elif funct3 == "101":
            if funct7 == "0000000":
                result = mask32(v1 >> (v2 & 31))

        elif funct3 == "110":
            result = mask32(v1 | v2)

        elif funct3 == "111":
            result = mask32(v1 & v2)

        if rd != 0:
            regs[rd] = result

        PC = PC + 4

    elif opcode == "0010011":

        imm_bits = instr[0:12]
        imm_number = int(imm_bits, 2)
        imm = sign_ext(imm_number, 12)

        rs1 = int(instr[12:17], 2)
        funct3 = instr[17:20]
        rd = int(instr[20:25], 2)

        result = 0

        if funct3 == "000":
            result = mask32(regs[rs1] + imm)

        elif funct3 == "011":
            rs1_unsigned = regs[rs1] & 0xFFFFFFFF
            imm_unsigned = imm & 0xFFFFFFFF

            if rs1_unsigned < imm_unsigned:
                result = 1
            else:
                result = 0

        if rd != 0:
            regs[rd] = result

        PC = PC + 4
    elif opcode == "0000011":

        imm_bits = instr[0:12]
        imm_number = int(imm_bits, 2)
        imm = sign_ext(imm_number, 12)

        rs1 = int(instr[12:17], 2)
        rd = int(instr[20:25], 2)

        base = regs[rs1]
        offset = imm
        addr = mask32(base + offset)

        if not check_memory_access(addr, rs1, PC):
            error_found = True
            break

        val = memory.get(addr, 0)

        if rd != 0:
            regs[rd] = val

        PC = PC + 4

    elif opcode == "1100111":

        imm_bits = instr[0:12]
        imm_number = int(imm_bits, 2)
        imm = sign_ext(imm_number, 12)

        rs1 = int(instr[12:17], 2)
        rd = int(instr[20:25], 2)

        base = regs[rs1]
        offset = imm
        target = mask32(base + offset)

        target = target & 0xFFFFFFFE

        if rd != 0:
            return_addr = mask32(PC + 4)
            regs[rd] = return_addr

        PC = target

    elif opcode == "0100011":

        upper_bits = instr[0:7]
        lower_bits = instr[20:25]
        imm_bits = upper_bits + lower_bits
        imm_number = int(imm_bits, 2)
        imm = sign_ext(imm_number, 12)

        rs1 = int(instr[12:17], 2)
        rs2 = int(instr[7:12], 2)

        base = regs[rs1]
        offset = imm
        addr = mask32(base + offset)

        if not check_memory_access(addr, rs1, PC):
            error_found = True
            break

        value = regs[rs2] & 0xFFFFFFFF
        memory[addr] = value

        PC = PC + 4

    elif opcode == "1100011":

        bit_12 = instr[0]
        bit_11 = instr[24]
        bits_10_to_5 = instr[1:7]
        bits_4_to_1 = instr[20:24]
        bit_0 = '0'

        imm_bits = bit_12 + bit_11 + bits_10_to_5 + bits_4_to_1 + bit_0
        imm_number = int(imm_bits, 2)
        imm = sign_ext(imm_number, 13)

        rs1 = int(instr[12:17], 2)
        rs2 = int(instr[7:12], 2)
        funct3 = instr[17:20]

        v1 = regs[rs1]
        v2 = regs[rs2]

        s1 = to_signed(v1)
        s2 = to_signed(v2)

        take = False

        if funct3 == "000":
            take = (v1 == v2)
        elif funct3 == "001":
            take = (v1 != v2)
        elif funct3 == "100":
            take = (s1 < s2)
        elif funct3 == "101":
            take = (s1 >= s2)
        elif funct3 == "110":
            take = ((v1 & 0xFFFFFFFF) < (v2 & 0xFFFFFFFF))
        elif funct3 == "111":
            take = ((v1 & 0xFFFFFFFF) >= (v2 & 0xFFFFFFFF))

        if funct3 == "000" and rs1 == 0 and rs2 == 0 and imm == 0:
            halt = True

        if take:
            PC = mask32(PC + imm)
        else:
            PC = PC + 4

    elif opcode == "0110111":

        imm = int(instr[0:20], 2)
        rd = int(instr[20:25], 2)

        if rd != 0:
            regs[rd] = mask32(imm << 12)

        PC = PC + 4

    elif opcode == "0010111":

        imm = int(instr[0:20], 2)
        rd = int(instr[20:25], 2)

        if rd != 0:
            regs[rd] = mask32(PC + (imm << 12))

        PC = PC + 4

    elif opcode == "1101111":

        bit_20 = instr[0]
        bits_19_to_12 = instr[12:20]
        bit_11 = instr[11]
        bits_10_to_1 = instr[1:11]
        bit_0 = '0'

        imm_bits = bit_20 + bits_19_to_12 + bit_11 + bits_10_to_1 + bit_0
        imm_number = int(imm_bits, 2)
        imm = sign_ext(imm_number, 21)

        rd = int(instr[20:25], 2)

        if rd != 0:
            return_addr = mask32(PC + 4)
            regs[rd] = return_addr

        PC = mask32(PC + imm)

    else:
        print("Unknown opcode:", opcode)
        break
    regs[0] = 0

    line = "0b" + to_bin(PC)
    for r in regs:
        line = line + " 0b" + to_bin(r)

    output_lines.append(line)

    if opcode == "1100011" and halt:
        break

if not error_found:
    for i in range(32):
        addr = 0x00010000 + i * 4
        val = memory.get(addr, 0)

        # address ko 8 digit hex mein convert
        addr_hex = format(addr, '08X')

        # value ko 32-bit binary mein convert
        val_binary = to_bin(val)

        # dono jod ke line banao
        line = "0x" + addr_hex + ":0b" + val_binary

        output_lines.append(line)

f = open(output_file, "w")
for l in output_lines:
    f.write(l + "\n")
f.close()

print("Done, output saved in", output_file)
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
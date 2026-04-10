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
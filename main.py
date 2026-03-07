import sys

input_file = sys.argv[1]
output_file = sys.argv[2]

f = open(input_file, "r")
lines = f.readlines()
f.close()

error_found = False

instr_type = {
    "R": ["add", "sub", "slt", "sltu", "xor", "sll", "srl", "or", "and"],
    "I": ["lw", "addi", "sltiu", "jalr"],
    "S": ["sw"],
    "B": ["beq", "bne", "blt", "bge", "bltu", "bgeu"],
    "U": ["lui", "auipc"],
    "J": ["jal"]
}

all_instructions = [
    "add","addi","and","auipc","beq","bge","bgeu",
    "blt","bltu","bne","jal","jalr","lui","lw",
    "or","sll","slt","sltiu","sltu","srl","sub","sw","xor"
]

instr_to_type = {}                                     #mapping kr rha h instruction ko uske type se 
for t in instr_type:
    for inst in instr_type[t]:
        instr_to_type[inst] = t

registers = {
    "zero": "00000","ra":"00001","sp":"00010","gp":"00011","tp":"00100",
    "t0":"00101","t1":"00110","t2":"00111","s0":"01000","fp":"01000",
    "s1":"01001","a0":"01010","a1":"01011","a2":"01100","a3":"01101",
    "a4":"01110","a5":"01111","a6":"10000","a7":"10001","s2":"10010",
    "s3":"10011","s4":"10100","s5":"10101","s6":"10110","s7":"10111",
    "s8":"11000","s9":"11001","s10":"11010","s11":"11011","t3":"11100",
    "t4":"11101","t5":"11110","t6":"11111",
}

opcodes={
    "add":"0110011","sub":"0110011","slt":"0110011","sltu":"0110011",
    "xor":"0110011","sll":"0110011","srl":"0110011","or":"0110011","and":"0110011",
    "sw":"0100011",
    "lui":"0110111",
    "auipc":"0010111",
    "beq":"1100011","bne":"1100011","blt":"1100011",
    "bge":"1100011","bltu":"1100011","bgeu":"1100011"
}

funct3={
    "add":"000","sub":"000","sll":"001","slt":"010","sltu":"011",
    "xor":"100","srl":"101","or":"110","and":"111",
    "sw":"010",
    "beq":"000","bne":"001","blt":"100",
    "bge":"101","bltu":"110","bgeu":"111"
}

funct7={
    "add":"0000000","sub":"0100000","sll":"0000000","slt":"0000000","sltu":"0000000",
    "xor":"0000000","srl":"0000000","or":"0000000","and":"0000000",
}

last_instruction = ""                                  

for line in reversed(lines):            #reverse order me ja rha h lines ko read krne ke liye taki last instruction mil jaye
    line = line.strip()

    if line == "":
        continue

    if ":" in line:
        parts = line.split(":")
        if parts[1].strip() != "":
            last_instruction = parts[1].strip()
            break
    else:
        last_instruction = line
        break

check_line = last_instruction.replace(",", " ")
check_parts = check_line.split()

if len(check_parts) != 4 or check_parts[0] != "beq" or check_parts[1] != "zero" or check_parts[2] != "zero":        #ye check kr rha h ki last instruction virtual halt instruction hai ya nahi
    print("ERROR: Missing virtual halt instruction")
    sys.exit()

labels = {}
pc = 0

for line_num, line in enumerate(lines,1):                        #line_num 1 se start hoga taki error messages me line number sahi aaye
    line = line.strip()   

    if line == "":
        continue

    if ":" in line:
        label = line.split(":")[0]             #ye label ko find kr rha h line se

        if label in labels:
            print(f"ERROR line {line_num}: Duplicate label '{label}'")
            error_found = True
        else:
            labels[label] = pc                #ye label ke address ko store kr rha h labels dictionary me

        if line.split(":")[1].strip() != "":
            pc += 4

    else:
        pc += 4

output = []
pc = 0

for line_num, line in enumerate(lines,1):

    line = line.strip()

    if line == "":
        continue

    if line.endswith(":"):
        continue

    if ":" in line:
        line = line.split(":")[1].strip()

    line = line.replace(",", " ")
    parts = line.split()

    if len(parts) == 0:
        continue

    instr = parts[0]

    if instr not in all_instructions:
        print(f"ERROR line {line_num}: Unknown instruction '{instr}'")
        error_found = True
        continue

    t = instr_to_type[instr]

    if t == "U":
        if len(parts) < 3:
            print(f"ERROR line {line_num}: Missing operands")
            error_found = True
            continue

        rd = parts[1]

        if rd not in registers:
            print(f"ERROR line {line_num}: Invalid register '{rd}'")
            error_found = True
            continue

        imm = int(parts[2],16)

        rd_bin = registers[rd]
        imm_bin = bin(imm)[2:].zfill(20)

        binary = imm_bin + rd_bin + opcodes[instr]

        output.append(binary)

    elif t == "S":

        if len(parts) < 3:
            print(f"ERROR line {line_num}: Missing operands")
            error_found = True
            continue

        rs2 = parts[1]
        st = parts[2]

        imm = int(st.split("(")[0])
        rs1 = st.split("(")[1][:-1]

        if rs1 not in registers or rs2 not in registers:
            print(f"ERROR line {line_num}: Invalid register")
            error_found = True
            continue

        if imm < -2048 or imm > 2047:
            print(f"ERROR line {line_num}: Immediate out of range")
            error_found = True
            continue

        rs1_bin = registers[rs1]
        rs2_bin = registers[rs2]

        imm_bin = bin((1<<12)+imm if imm<0 else imm)[2:].zfill(12)

        imm1 = imm_bin[0:7]
        imm2 = imm_bin[7:12]

        binary = imm1 + rs2_bin + rs1_bin + funct3[instr] + imm2 + opcodes[instr]

        output.append(binary)

    elif t == "B":

        if len(parts) < 4:
            print(f"ERROR line {line_num}: Missing operands")
            error_found = True
            continue

        rs1 = parts[1]
        rs2 = parts[2]
        label = parts[3]

        if label.lstrip("-").isdigit():
            offset = int(label)

        else:
            if label not in labels:
                print(f"ERROR line {line_num}: Undefined label '{label}'")
                error_found = True
                continue

            label_address = labels[label]
            offset = label_address - pc

        if offset < -4096 or offset > 4094:
            print(f"ERROR line {line_num}: Branch offset out of range")
            error_found = True
            continue

        imm = offset // 2

        rs1_bin = registers[rs1]
        rs2_bin = registers[rs2]

        if imm >= 0:
            imm_bin = bin(imm)[2:].zfill(13)
        else:
            imm = (1<<13) + imm
            imm_bin = bin(imm)[2:]

        imm_12 = imm_bin[0]
        imm_10_5 = imm_bin[2:8]
        imm_4_1 = imm_bin[8:12]
        imm_11 = imm_bin[1]

        imm_31_25 = imm_12 + imm_10_5
        imm_11_7 = imm_4_1 + imm_11

        binary = (
            imm_31_25 +
            rs2_bin +
            rs1_bin +
            funct3[instr] +
            imm_11_7 +
            opcodes[instr]
        )

        output.append(binary)

    pc += 4

if error_found == False:
    file = open(output_file, "w")

    for line in output:
        file.write(line + "\n")

    file.close()

    print("\nDone! Output saved to output.bin")
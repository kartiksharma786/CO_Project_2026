import sys

input_file = sys.argv[1]
output_file = sys.argv[2]

f = open(input_file, "r")
lines = f.readlines()                                   
f.close()

error_f = False

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

instr_to_type = {}
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
    "bge":"1100011","bltu":"1100011","bgeu":"1100011",
    "lw":"0000011",
    "addi":"0010011",
    "sltiu":"0010011",
    "jalr":"1100111",
    "jal":"1101111"
}

funct3={
    "add":"000","sub":"000","sll":"001","slt":"010","sltu":"011",
    "xor":"100","srl":"101","or":"110","and":"111",
    "sw":"010",
    "beq":"000","bne":"001","blt":"100",
    "bge":"101","bltu":"110","bgeu":"111",
    "lw":"010",
    "addi":"000",
    "sltiu":"011",
    "jalr":"000"
}

funct7={
    "add":"0000000","sub":"0100000","sll":"0000000","slt":"0000000","sltu":"0000000",
    "xor":"0000000","srl":"0000000","or":"0000000","and":"0000000",
}

lst_instruc = ""

for line in reversed(lines):                                    #line ko reverse order me read karenge taki last instruction mile             
    line = line.strip()

    if line == "":
        continue

    if ":" in line:
        parts = line.split(":")
        if parts[1].strip() != "":
            lst_instruc = parts[1].strip()                              #agar label ke baad instruction hai to use lst_instruc me store karenge
            break
    else:
        lst_instruc = line
        break

check_line = lst_instruc.replace(",", " ")                              #last instruction me se comma hata kar uske parts dekhenge
check_parts = check_line.split()

if len(check_parts) < 4 or check_parts[0] != "beq" or check_parts[1] != "zero" or check_parts[2] != "zero":      #last instruction beq zero zero hona chahiye
    print("ERROR: Missing virtual HALT")
    sys.exit()

labels = {}
pc = 0

for line_num, line in enumerate(lines,1):                                       #line ko reverse order me read karenge taki labels ke addresses mile
    line = line.strip()

    if line == "":
        continue

    if ":" in line:
        label=line.split(":")[0]

        if label in labels:
            print(f"ERROR line {line_num}: duplicate label '{label}'")                      #agar label pehle se available hai to error
            error_f = True
        else:
            labels[label] = pc

        if line.split(":")[1].strip()!= "":
            pc += 4
    else:
        pc += 4

output = []
pc = 0

for line_num, line in enumerate(lines,1):                       #abhi jo line read karenge usko process karenge taki binary code generate ho sake
    line = line.strip()
    if line == "":
        continue
    if line.endswith(":"):
        continue
    if ":" in line:
        line = line.split(":")[1].strip()

    line = line.replace(",", " ")
    parts = line.split()

    if len(parts) == 0:                     #agar line me sirf label hai to usko skip karenge
        continue

    instr = parts[0]

    if instr not in all_instructions:                       #agar instruction unknown hai to error
        if instr in labels:
            print(f"ERROR line {line_num}: Label '{instr}' used as instruction")
        else:
            print(f"ERROR line {line_num}: Unknown instruction '{instr}'")                  
        error_f = True
        continue

    t = instr_to_type[instr]                #instruction ke type ke hisab se usko process karenge taki binary code generate ho sake

    if t == "U":                                                            #U-type instructions 
        if len(parts) != 3:
            print(f"ERROR line {line_num}: missing operands")
            error_f = True
            continue

        rd = parts[1]

        if rd not in registers:
            print(f"ERROR line {line_num}: invalid register '{rd}'")
            error_f = True
            continue
        try:
            imm = int(parts[2],0)
        except:
            print(f"ERROR line {line_num}: invalid immediate")
            error_f = True
            continue

        rd_bin = registers[rd]
        i_bin = bin(imm & ((1<<20)-1))[2:].zfill(20)                                    #immediate ko 20 bit me convert karenge (negative ke liye 2's complement)

        binary = i_bin + rd_bin + opcodes[instr]
        output.append(binary)

    elif t == "S":                                              #S-type instructions                
        if len(parts) != 3:
            print(f"ERROR line {line_num}: missing operands")
            error_f = True
            continue

        rs2 = parts[1]
        st = parts[2]

        try:
            imm = int(st.split("(")[0])
            rs1 = st.split("(")[1][:-1]
        except:
            print(f"ERROR line {line_num}: invalid memory format")
            error_f = True
            continue

        if rs1 not in registers or rs2 not in registers:
            print(f"ERROR line {line_num}: invalid register")
            error_f = True
            continue

        if imm < -2048 or imm > 2047:
            print(f"ERROR line {line_num}: immediate out of range")
            error_f = True
            continue

        rs1_bin = registers[rs1]
        rs2_bin = registers[rs2]
        i_bin = bin((1<<12)+imm if imm<0 else imm)[2:].zfill(12)                                #immediate ko 12 bit me convert karenge (negative ke liye 2's complement)

        binary = i_bin[0:7] + rs2_bin + rs1_bin + funct3[instr] + i_bin[7:] + opcodes[instr]
        output.append(binary)

    elif t == "R":                                                           #R-type instructions
        if len(parts) != 4:
            print(f"ERROR line {line_num}: r-type requires 3 arguments")
            error_f = True
            continue

        rd  = parts[1]
        rs1 = parts[2]
        rs2 = parts[3]

        if rd not in registers or rs1 not in registers or rs2 not in registers:
            print(f"ERROR line {line_num}: invalid register")
            error_f = True
            continue

        binary = funct7[instr] + registers[rs2] + registers[rs1] + funct3[instr] + registers[rd] + opcodes[instr]
        output.append(binary)

    elif t == "I":                                                             #I-type instructions 
        if instr == "lw" and len(parts) != 3:
            print(f"ERROR line {line_num}: lw requires 2 arguments")
            error_f = True
            continue
        elif instr != "lw" and len(parts) != 4:
            print(f"ERROR line {line_num}: i-type requires 3 arguments")
            error_f = True
            continue

        rd = parts[1]
        if rd not in registers:
            print(f"ERROR line {line_num}: invalid register")
            error_f = True
            continue

        if instr == "lw":
            st = parts[2]
            imm = int(st.split("(")[0])
            rs1 = st.split("(")[1][:-1]
        else:
            rs1  = parts[2]
            imm  = int(parts[3])

        if rs1 not in registers:
            print(f"ERROR line {line_num}: invalid register")
            error_f = True
            continue

        if imm < -2048 or imm > 2047:
            print(f"ERROR line {line_num}: immediate out of range")
            error_f = True
            continue

        i_bin = bin((1<<12)+imm if imm<0 else imm)[2:].zfill(12)                                            #immediate ko 12 bit me convert karenge (negative ke liye 2's complement)
        binary = i_bin + registers[rs1] + funct3[instr] + registers[rd] + opcodes[instr]                    #I-type instructions ke format ke hisab se binary code generate karenge
        output.append(binary)

    elif t == "B":                                                            #B-type instructions
        if len(parts) != 4:
            print(f"ERROR line {line_num}: missing operands")
            error_f = True
            continue

        rs1 = parts[1]
        rs2 = parts[2]
        label = parts[3]

        if rs1 not in registers or rs2 not in registers:
            print(f"ERROR line {line_num}: invalid register")
            error_f = True
            continue

        if label in labels:
            offset = labels[label] - pc
        else:
            try:
                offset = int(label)
            except ValueError:
                print(f"ERROR line {line_num}: undefined label '{label}'")
                error_f = True
                continue

        if offset < -4096 or offset > 4094:
            print(f"ERROR line {line_num}: branch offset out of range")                 #branch offset -4096 se chhota ya 4094 se bada nahi hona chahiye 
            error_f = True
            continue

        imm = offset 
        i_bin = bin((1<<13)+imm if imm<0 else imm)[2:].zfill(13)                        #branch offset ko 13 bit me convert karenge (negative ke liye 2's complement)

        binary = i_bin[0] + i_bin[2:8] + registers[rs2] + registers[rs1] + funct3[instr] + i_bin[8:12] + i_bin[1] + opcodes[instr]                      #B-type instructions ke format ke hisab se binary code generate karenge
        output.append(binary)

    elif t == "J":                                                      #J-type instructions                                        
        if len(parts) != 3:
            print(f"ERROR line {line_num}: j-type requires rd label")
            error_f = True
            continue

        rd = parts[1]
        label = parts[2]

        if rd not in registers:
            print(f"ERROR line {line_num}: invalid register")
            error_f = True
            continue

        if label not in labels:
            print(f"ERROR line {line_num}: undefined label '{label}'")
            error_f = True
            continue

        offset = labels[label] - pc
        imm = offset 
        i_bin = bin((1<<21)+imm if imm<0 else imm)[2:].zfill(21)                            #jump offset ko 21 bit me convert karenge (negative ke liye 2's complement)

        binary = i_bin[0] + i_bin[10:20] + i_bin[9] + i_bin[1:9] + registers[rd] + opcodes[instr]                   #J-type instructions ke format ke hisab se binary code generate karenge
        output.append(binary)

    pc += 4

if error_f == False:
    file = open(output_file, "w")
    for line in output:
        file.write(line + "\n")
    file.close()
    print("\nDone!: Output saved to output.bin")
instr_type = {
    "R": ["add", "sub", "slt", "sltu", "xor", "sll", "srl", "or", "and"],
    "I": ["lw", "addi", "sltiu", "jalr"],
    "S": ["sw"],
    "B": ["beq", "bne", "blt", "bge", "bltu", "bgeu"],
    "U": ["lui", "auipc"],
    "J": ["jal"]
}

instruction_types_list = list(instr_type.keys())

all_instructions = [
    "add", "addi", "and", "auipc", "beq", "bge", "bgeu",
    "blt", "bltu", "bne", "jal", "jalr", "lui", "lw",
    "or", "sll", "slt", "sltiu", "sltu",
    "srl", "sub", "sw", "xor"
]



instr_to_type = {}
for t, insts in instr_type.items():
    for inst in insts:
        instr_to_type[inst] = t




with open("instruction.asm", "r") as f:
    lines = f.readlines()




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
    "auipc":"0010111"
}

funct3={
    "add":"000","sub":"000","sll":"001","slt":"010","sltu":"011",
    "xor":"100","srl":"101","or":"110","and":"111",

    
    "sw":"010"
}

funct7={
    "add":"0000000","sub":"0100000","sll":"0000000","slt":"0000000","sltu":"0000000",
    "xor":"0000000","srl":"0000000","or":"0000000","and":"0000000",
}




output = []

for line_num, line in enumerate(lines, 1):

    line = line.strip()
    if line == "":
        continue

    line = line.replace(",", " ")
    parts = line.split()

    instr = parts[0]

    
    if instr not in all_instructions:
        print(f"ERROR line {line_num}: Unknown instruction '{instr}'")
        continue

    
    t = instr_to_type[instr]

    if t=="U":

        if len(parts) != 3:
            print(f"ERROR line {line_num}: U-type requires rd imm12")
            continue

        rd=parts[1]

        if rd not in registers:
            print(f"ERROR line {line_num}: Invalid register in '{line}'")
            continue

        rd_bin=registers[rd]

        st=""
        for i in parts[2]:
            st+= i

        for i in st[2:len(st)]:
            if i in "0123456789":
                continue
            elif i in "abcdef".upper():
                continue
            else:
                print(f"ERROR line {line_num}: Invalid immediate value in '{line}'")
                continue

        imm=int(st[2:len(st)],16)

        bin=""
        while imm>0:
            bin=str(imm%2)+bin
            imm//=2

        

        rbin=bin

        while len(rbin)<20:
            rbin="0"+rbin

        op=opcodes[instr]

        binary=rbin+rd_bin+op
        output.append(binary)

        print(f"Line {line_num}: {binary}")


    
    
    
    elif t=="S":

        if len(parts) != 3:
            print(f"ERROR line {line_num}: S-type requires rs2 imm(rs1)")
            continue

        rs2=parts[1]

        if rs2 not in registers:
            print(f"ERROR line {line_num}: Invalid register in '{line}'")
            continue    

        rs2_bin=registers[rs2]

        st=""
        for i in parts[2]:
            st+= i

        imm=st.split("(")[0]
        imm=int(imm)

        bin=""

        # FIX 1 → imm = 0 case handle
        if imm >= 0:

            while imm>0:
                bin=str(imm%2)+bin
                imm//=2

            rbin=bin

            while len(rbin)<12:
                rbin="0"+rbin
        
            imm1=rbin[0:7]
            imm2=rbin[7:12]

            rs1=""
            for i in st.split("(")[1]:
                rs1+=i

            rs1=rs1[:-1]

            if rs1 not in registers:
                print(f"ERROR line {line_num}: Invalid register in '{line}'")
                continue

            rs1_bin=registers[rs1]

            op=opcodes[instr]
            f3=funct3[instr]

            binary=imm1+rs2_bin+rs1_bin+f3+imm2+op

            output.append(binary)

            print(f"Line {line_num}: {binary}")

        elif imm < 0:

            x = -imm

            while x > 0:
                bin = str(x % 2) + bin
                x //= 2

            rbin = bin

            while len(rbin) < 12:
                rbin = "0" + rbin

            
            inv = ""
            for i in rbin:
                if i == "0":
                    inv += "1"
                else:
                    inv += "0"

            rbin = inv

            
            carry = 1
            temp = ""

            for i in rbin[::-1]:
                if i == "1" and carry == 1:
                    temp = "0" + temp
                elif i == "0" and carry == 1:
                    temp = "1" + temp
                    carry = 0
                else:
                    temp = i + temp

            rbin = temp

            while len(rbin) < 12:
                rbin = "0" + rbin


            imm1 = rbin[0:7]
            imm2 = rbin[7:12]

            rs1 = ""
            for i in st.split("(")[1]:
                rs1 += i

            rs1 = rs1[:-1]

            if rs1 not in registers:
                print(f"ERROR line {line_num}: Invalid register in '{line}'")
                continue

            rs1_bin = registers[rs1]

            op = opcodes[instr]
            f3 = funct3[instr]

            binary = imm1 + rs2_bin + rs1_bin + f3 + imm2 + op

            output.append(binary)

            print(f"Line {line_num}: {binary}")



with open("output.bin", "w") as out:
    for b in output:
        out.write(b + "\n")

print("\nDone! Output saved to output.bin")
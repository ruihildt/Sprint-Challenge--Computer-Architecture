"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        
        # 256 byte RAM
        self.ram = [0] * 256

        # Register (R0 - R7)
        self.register = [0] * 8

        # Program Counter
        self.pc = self.register[0]

        # Instruction Register
        self.ir = None

        # Stack Pointer 
        self.sp = 7 # Stack pointer R7

        # Flag register
        self.fl = 0b00000000
        
        self.halted = False

        # set up branchtable
        self.branchtable = {
            LDI: self.handle_ldi,
            PRN: self.handle_prn,
            HLT: self.handle_hlt,
            ADD: self.handle_add,
            CMP: self.handle_cmp,
            MUL: self.handle_mul,
            PUSH: self.handle_push,
            POP: self.handle_pop,
            CALL: self.handle_call,
            RET: self.handle_ret,
            JMP: self.handle_jmp
        }

    def handle_jmp(self, a, b):
        self.pc = self.register[a]

    def handle_hlt(self, a, b):
        self.halted = True

    def handle_ldi(self, a, b):
        self.register[a] = b
        self.pc += 3
    
    def handle_prn(self, a, b):
        print(self.register[a])
        self.pc += 2

    def handle_mul(self, a, b):
        self.alu("MUL", a, b)
        self.pc += 3
    
    def handle_add(self, a, b):
        self.alu("ADD", a, b)
        self.pc += 3

    def handle_cmp(self, a, b):
        self.alu("CMP", a, b)
        self.pc += 3

    def handle_pop(self, a, b):
        val = self.ram[self.register[self.sp]]

        # POP
        self.register[a] = val
        self.register[self.sp] += 1
        self.pc += 2

    def handle_push(self, a, b):
        val = self.register[a]

        # PUSH
        self.register[self.sp] -= 1
        self.ram[self.register[self.sp]] = val
        self.pc += 2

    def handle_call(self, a, b):
        self.register[self.sp] -= 1
        self.ram[self.register[self.sp]] = self.pc + 2

        self.pc = self.register[a]
    
    def handle_ret(self, a, b):
        self.pc = self.ram[self.register[self.sp]]
        self.register[self.sp] += 1

    def load(self, filename):
        """Load a program into memory."""

        if filename[-4:] != ".ls8":
            full_filename = f"examples/{filename}.ls8"
        else: full_filename = f"examples/{filename}"
        try:
            address = 0
            with open(full_filename) as f:
                for line in f:
                    # deal with comments
                    # split before and after any comment symbol '#'
                    comment_split = line.split("#")

                    # convert the pre-comment portion (to the left) from binary to a value
                    # extract the first part of the split to a number variable
                    # and trim whitespace
                    num = comment_split[0].strip()

                    # ignore blank lines / comment only lines
                    if len(num) == 0:
                        continue

                    # set the number to an integer of base 2
                    value = int(num, 2)
                    # print the value in binary and in decimal
                    # print(f"{value:08b}: {value:d}")
                    
                    # add the value in to the memory at the index of address
                    self.ram[address] = value

                    # increment the address
                    address += 1


        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def ram_read(self, location):
        """Read avalue stored at specified address."""
        return self.ram[location]

    def ram_write(self, location, value):
        """Writes value to RAM at the address specified."""
        self.ram[location] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        elif op == "MUL":
            self.register[reg_a] *= self.register[reg_b]
        elif op == "CMP":
            if self.register[reg_a] < self.register[reg_b]:
                self.fl = 0b00000100
            elif self.register[reg_a] > self.register[reg_b]:
                self.fl = 0b00000010
            else:
                self.fl = 0b00000001
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        
        while not self.halted:
            self.ir = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            self.branchtable[self.ir](operand_a, operand_b)
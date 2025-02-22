class InstructionDecoder:
    
    @staticmethod
    def decode(instruction: int) -> dict:
        opcode = (instruction >> 26) & 0x3F
        rs = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F
        rd = (instruction >> 11) & 0x1F
        shamt = (instruction >> 6) & 0x1F
        funct = instruction & 0x3F
        imm = instruction & 0xFFFF
        address = instruction & 0x3FFFFFF

        if imm & 0x8000:  # تمديد الإشارة
            imm = imm - 0x10000

        return {
            'opcode': opcode,
            'rs': rs,
            'rt': rt,
            'rd': rd,
            'shamt': shamt,
            'funct': funct,
            'immediate': imm,
            'address': address,
            'type': InstructionDecoder.get_instruction_type(opcode, funct),
            'mnemonic': InstructionDecoder.get_instruction_name(opcode, funct)
        }

    @staticmethod
    def get_instruction_type(opcode: int, funct: int) -> str:
        if opcode == 0:
            return 'R'
        elif opcode in [0x02, 0x03]:
            return 'J'
        else:
            return 'I'

    @staticmethod
    def get_instruction_name(opcode: int, funct: int) -> str:
        r_type_map = {
            0x20: 'ADD', 0x22: 'SUB', 0x24: 'AND', 0x25: 'OR', 0x27: 'NOR',
            0x26: 'XOR', 0x2A: 'SLT', 0x2B: 'SGT', 0x00: 'SLL', 0x02: 'SRL'
        }
        i_type_map = {
            0x23: 'LW', 0x2B: 'SW', 0x04: 'BEQ', 0x05: 'BNE', 0x08: 'ADDI',
            0x0D: 'ORI', 0x0E: 'XORI', 0x01: 'BLTZ_BGEZ'
        }
        j_type_map = {0x02: 'J', 0x03: 'JAL'}

        if opcode == 0:
            return r_type_map.get(funct, 'UNKNOWN')
        elif opcode in j_type_map:
            return j_type_map[opcode]
        elif opcode == 0x01:
            return 'BLTZ' if funct == 0 else 'BGEZ'
        else:
            return i_type_map.get(opcode, 'UNKNOWN')

from mips_pipline.enums.ProcessorSignals import Stages, InstructionTypes,RegisterTypes, Instruction

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

        if imm & 0x8000:  
            imm = imm - 0x10000

        return {
            RegisterTypes.opcode.value: opcode,
            RegisterTypes.rs.value: rs,
            RegisterTypes.rt.value: rt,
            RegisterTypes.rd.value: rd,
            RegisterTypes.shamt.value: shamt,
            RegisterTypes.funct.value: funct,
            RegisterTypes.immediate.value: imm,
            RegisterTypes.address.value: address,
            RegisterTypes.type.value: InstructionDecoder.get_instruction_type(opcode, funct),
            RegisterTypes.mnemonic.value: InstructionDecoder.get_instruction_name(opcode, funct)
        }

    @staticmethod
    def get_instruction_type(opcode: int, funct: int) -> str:
        if opcode == 0:
            return InstructionTypes.R.value
        elif opcode in [0x02, 0x03]:
            return InstructionTypes.J.value
        else:
            return InstructionTypes.I.value

    @staticmethod
    def get_instruction_name(opcode: int, funct: int) -> str:
        r_type_map = {
            0x20: Instruction.ADD.value, 0x22: Instruction.SUB.value, 
            0x24: Instruction.AND.value, 0x25: Instruction.OR.value, 
            0x27: Instruction.NOR.value, 0x2A: Instruction.SLT.value, 
            0x26: Instruction.XOR.value, 0x2B: Instruction.SGT.value, 
            0x00: Instruction.SLL.value, 0x02: Instruction.SRL.value,
        }
        i_type_map = {
            0x23: Instruction.LW.value, 0x2B: Instruction.SW.value,
            0x0D: Instruction.ORI.value, 0x0E: Instruction.XORI.value,
            0x01: Instruction.BLTZ_BGEZ.value, 0x04: Instruction.BEQ.value,
            0x05: Instruction.BNE.value, 0x08: Instruction.ADDI.value,
        }
        j_type_map = {0x02: Instruction.J.value, 0x03: Instruction.JAL.value}

        if opcode == 0:
            return r_type_map.get(funct, Instruction.UNKNOWN.value)
        elif opcode in j_type_map:
            return j_type_map[opcode]
        elif opcode == 0x01:
            return Instruction.BLTZ.value if funct == 0 else Instruction.BGEZ.value
        else:
            return i_type_map.get(opcode, Instruction.UNKNOWN.value)
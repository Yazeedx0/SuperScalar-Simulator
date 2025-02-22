from enum import Enum



class InstructionTypes(Enum):
  R = "R"
  I = "I"
  J = "J"

class RegisterTypes (Enum):
  mnemonic = "mnemonic"
  type = "type"
  opcode = "opcode"
  rt = "rt"
  rd = "rd"
  rs = "rs"
  shamt = "shamt"
  immediate = "immediate"
  address = "address"
  decoded = "decoded"
  funct = "funct"
  mem_result = "mem_result"
  alu_result = "alu_result"
  jump_address = "jump_address"
  branch_taken = "branch_taken"
  decoded_instruction = "decoded_instruction"
  raw_instruction = "raw_instruction"
  program_counter = "program_counter"

        
class Stages(Enum):
  IF = "IF"
  ID = "ID"
  EX = "EX"
  MEM = "MEM"
  WB = "WB"
  EX_MEM = "EX_MEM"
  MEM_WB = "MEM_WB"

class Instruction(Enum):
  ADD = "ADD"
  SUB = "SUB"
  AND = "AND"
  OR = "OR"
  NOR = "NOR"
  XOR = "XOR"
  SLT = "SLT"
  SGT = "SGT"
  SLL = "SLL"
  SRL = "SRL"
  ADDI = "ADDI"
  XORI = "XORI"
  ORI = "ORI"
  LW = "LW"
  SW = "SW"
  BNE = "BNE"
  BLTZ = "BLTZ"
  BGEZ = "BGEZ"
  BEQ = "BEQ"
  JAL = "JAL"
  J = "J"
  NOP = "NOP"
  BLTZ_BGEZ = "BLTZ_BGEZ"
  UNKNOWN = "UNKNOWN"

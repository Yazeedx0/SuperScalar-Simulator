from enum import Enum

# Defines the three basic MIPS instruction formats
class InstructionTypes(Enum):
    R = "R"  # Register format instructions (e.g., ADD, SUB)
    I = "I"  # Immediate format instructions (e.g., ADDI, LW)
    J = "J"  # Jump format instructions (e.g., J, JAL)

# Contains all possible fields and signals that can be associated with an instruction
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

# Represents the five pipeline stages in the MIPS processor
class Stages(Enum):
    IF = "IF"      # Instruction Fetch
    ID = "ID"      # Instruction Decode
    EX = "EX"      # Execute
    MEM = "MEM"    # Memory Access
    WB = "WB"      # Write Back
    EX_MEM = "EX_MEM"  # Pipeline register between EX and MEM stages
    MEM_WB = "MEM_WB"  # Pipeline register between MEM and WB stages

# Supported MIPS instruction set
class Instruction(Enum):
    # Arithmetic and Logic Instructions
    ADD = "ADD"    # Add
    SUB = "SUB"    # Subtract
    AND = "AND"    # Logical AND
    OR = "OR"      # Logical OR
    NOR = "NOR"    # Logical NOR
    XOR = "XOR"    # Logical XOR
    
    # Comparison Instructions
    SLT = "SLT"    # Set if Less Than
    SGT = "SGT"    # Set if Greater Than
    
    # Shift Instructions
    SLL = "SLL"    # Shift Left Logical
    SRL = "SRL"    # Shift Right Logical
    
    # Immediate Instructions
    ADDI = "ADDI"  # Add Immediate
    XORI = "XORI"  # XOR Immediate
    ORI = "ORI"    # OR Immediate
    
    # Memory Instructions
    LW = "LW"      # Load Word
    SW = "SW"      # Store Word
    
    # Branch Instructions
    BNE = "BNE"    # Branch if Not Equal
    BLTZ = "BLTZ"  # Branch if Less Than Zero
    BGEZ = "BGEZ"  # Branch if Greater Than or Equal to Zero
    BEQ = "BEQ"    # Branch if Equal
    
    # Jump Instructions
    JAL = "JAL"    # Jump and Link
    J = "J"        # Jump
    
    # Special Instructions
    NOP = "NOP"    # No Operation
    BLTZ_BGEZ = "BLTZ_BGEZ"  # Combined BLTZ/BGEZ instruction
    UNKNOWN = "UNKNOWN"       # Unknown/Invalid instruction

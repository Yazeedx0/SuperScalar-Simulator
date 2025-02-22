import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class PipelineStage:
    """Represents a single pipeline stage with support for multiple instructions."""
    def __init__(self, name: str, width: int = 2):
        self.name = name
        self.instructions: List[Optional[int]] = [None] * width  
        self.details: List[Dict] = [{}] * width
        self.stalled = False

class InstructionDecoder:
    """Advanced instruction decoder for MIPS-like architecture."""
    @staticmethod
    def decode(instruction: int) -> Dict:
        opcode = (instruction >> 26) & 0x3F
        rs = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F
        rd = (instruction >> 11) & 0x1F
        shamt = (instruction >> 6) & 0x1F
        funct = instruction & 0x3F
        imm = instruction & 0xFFFF
        address = instruction & 0x3FFFFFF

        if imm & 0x8000:  # Sign extension
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

class ComprehensivePipelineProcessor:
    """Superscalar MIPS Pipeline Simulator with Dual-Issue Capability"""
    def __init__(self, memory_size: int = 4096, register_count: int = 32, issue_width: int = 2):
        self.memory = [0] * memory_size
        self.registers = [0] * register_count
        self.issue_width = issue_width

        self.stages = {
            'IF': PipelineStage('Instruction Fetch', self.issue_width),
            'ID': PipelineStage('Instruction Decode', self.issue_width),
            'EX': PipelineStage('Execute', self.issue_width),
            'MEM': PipelineStage('Memory Access', self.issue_width),
            'WB': PipelineStage('Write Back', self.issue_width)
        }

        self.pc = 0
        self.cycle_count = 0
        self.instruction_count = 0
        self.program: List[int] = []

        self.forwarding = {
            'EX_MEM': [None] * self.issue_width,
            'MEM_WB': [None] * self.issue_width
        }
        self.stall = False

    def set_registers(self, initial_values: Dict[int, int]):
        for reg, value in initial_values.items():
            if 0 <= reg < len(self.registers) and reg != 0:
                self.registers[reg] = value

    def fetch_stage(self) -> List[Optional[int]]:
        stage = self.stages['IF']
        instructions = []
        for _ in range(self.issue_width):
            if self.pc < len(self.program):
                instructions.append(self.program[self.pc])
                self.pc += 1
            else:
                instructions.append(None)
        stage.instructions = instructions
        stage.details = [{'program_counter': self.pc - len(instructions) + i, 'raw_instruction': hex(instr)} if instr is not None else {} for i, instr in enumerate(instructions)]
        logger.info(f"Fetch Stage - Instructions: {[hex(instr) if instr is not None else 'None' for instr in instructions]}")
        return instructions

    def decode_stage(self, instructions: List[Optional[int]]) -> List[Optional[Dict]]:
        stage = self.stages['ID']
        decoded_instructions = [InstructionDecoder.decode(instr) if instr is not None else None for instr in instructions]
        stage.instructions = [decoded['mnemonic'] if decoded else None for decoded in decoded_instructions]
        stage.details = [{'decoded_instruction': decoded} if decoded else {} for decoded in decoded_instructions]
        return decoded_instructions

    def execute_stage(self, decoded_instructions: List[Optional[Dict]]) -> List[Optional[Dict]]:
        stage = self.stages['EX']
        results = []
        branch_taken = False
        jump_address = None
        
        for decoded in decoded_instructions:
            if decoded is None:
                results.append(None)
                continue

            instr_type = decoded['type']
            mnemonic = decoded['mnemonic']
            rs_val = self.get_register_value(decoded['rs'])
            rt_val = self.get_register_value(decoded['rt'])
            rd = decoded.get('rd', None)
            shamt = decoded.get('shamt', 0)
            imm = decoded['immediate']
            address = decoded.get('address', None)

            result = None

            if instr_type == 'R':
                if mnemonic == 'ADD': result = rs_val + rt_val
                elif mnemonic == 'SUB': result = rs_val - rt_val
                elif mnemonic == 'AND': result = rs_val & rt_val
                elif mnemonic == 'OR': result = rs_val | rt_val
                elif mnemonic == 'NOR': result = ~(rs_val | rt_val) & 0xFFFFFFFF
                elif mnemonic == 'XOR': result = rs_val ^ rt_val
                elif mnemonic == 'SLT': result = 1 if rs_val < rt_val else 0
                elif mnemonic == 'SGT': result = 1 if rs_val > rt_val else 0
                elif mnemonic == 'SLL': result = rt_val << shamt
                elif mnemonic == 'SRL': result = (rt_val & 0xFFFFFFFF) >> shamt
            elif instr_type == 'I':
                if mnemonic == 'ADDI': result = rs_val + imm
                elif mnemonic == 'ORI': result = rs_val | (imm & 0xFFFF)
                elif mnemonic == 'XORI': result = rs_val ^ (imm & 0xFFFF)
                elif mnemonic in ['LW', 'SW']: result = rs_val + imm
                elif mnemonic == 'BEQ' and rs_val == rt_val:
                    branch_taken = True
                    jump_address = self.pc + imm
                elif mnemonic == 'BNE' and rs_val != rt_val:
                    branch_taken = True
                    jump_address = self.pc + imm
                elif mnemonic == 'BLTZ' and rs_val < 0:
                    branch_taken = True
                    jump_address = self.pc + imm
                elif mnemonic == 'BGEZ' and rs_val >= 0:
                    branch_taken = True
                    jump_address = self.pc + imm
            elif instr_type == 'J':
                if mnemonic == 'J':
                    jump_address = address
                    branch_taken = True
                elif mnemonic == 'JAL':
                    self.registers[31] = self.pc
                    jump_address = address
                    branch_taken = True

            if branch_taken and jump_address is not None:
                self.pc = jump_address
                self.flush_pipeline()

            results.append({
                'alu_result': result,
                'decoded': decoded,
                'branch_taken': branch_taken,
                'jump_address': jump_address
            })

        stage.instructions = [decoded['mnemonic'] if decoded else None for decoded in decoded_instructions]
        stage.details = results
        return results

    def memory_stage_func(self, execute_data: List[Optional[Dict]]) -> List[Optional[Dict]]:
        stage = self.stages['MEM']
        mem_results = []
        for data in execute_data:
            if data is None or 'decoded' not in data:
                mem_results.append(None)
                continue

            decoded = data['decoded']
            if 'mnemonic' not in decoded:
                mem_results.append(None)
                continue
            
            alu_result = data.get('alu_result')  # Fixed: Changed data.get['alu_result'] to data.get('alu_result')
            mnemonic = decoded['mnemonic']
            mem_result = alu_result

            if mnemonic == 'LW' and alu_result is not None and 0 <= alu_result < len(self.memory):
                mem_result = self.memory[alu_result]
            elif mnemonic == 'SW' and alu_result is not None and 0 <= alu_result < len(self.memory):
                self.memory[alu_result] = self.registers[decoded['rt']]

            mem_results.append({
                'mem_result': mem_result,
                'decoded': decoded,
                'alu_result': alu_result
            })

        stage.instructions = [
            data['decoded']['mnemonic'] if data and 'decoded' in data and 'mnemonic' in data['decoded'] else None
            for data in execute_data
        ]
        stage.details = mem_results
        return mem_results

    def write_back_stage_func(self, memory_data: List[Optional[Dict]]):
        stage = self.stages['WB']

        for data in memory_data:
            
            if data is None or 'decoded' not in data or 'mnemonic' not in data ['decoded']:
                continue

            decoded = data['decoded']
            mnemonic = decoded['mnemonic']
            alu_result = data.get('alu_result')
            mem_result = data.get('mem_result')
            rd = decoded.get('rd', None)
            rt = decoded.get('rt', None)

            if mnemonic in ['ADD', 'SUB', 'AND', 'OR', 'NOR', 'XOR', 'SLT', 'SGT', 'SLL', 'SRL'] and rd != 0 and alu_result is not None:
                self.registers[rd] = alu_result
            elif mnemonic in ['ADDI', 'ORI', 'XORI'] and rt != 0 and alu_result is not None:
                self.registers[rt] = alu_result
            elif mnemonic == 'LW' and rt != 0 and mem_result is not None:
                self.registers[rt] = mem_result
            elif mnemonic == 'JAL' and data.get('jump_address') is not None:
                self.registers[31] = self.pc

        stage.instructions = [
            data ['decoded']['mnemonic'] if data and 'decoded' in data and 'mnemonic' in data ['decoded'] else None
            for data in memory_data
        ]
        stage.details = memory_data if memory_data else [{}] * self.issue_width
    def get_register_value(self, reg_num: int) -> int:
        for fwd in self.forwarding['EX_MEM'] + self.forwarding['MEM_WB']:
            if fwd and 'rd' in fwd and fwd['rd'] == reg_num and reg_num != 0:
                return fwd['value']
        return self.registers[reg_num]

    def detect_data_hazard(self, decoded_instructions: List[Optional[Dict]]) -> bool:
        for i, decoded in enumerate(decoded_instructions):
            if decoded is None:
                continue
            src_regs = self.get_source_registers(decoded)
            for stage_name in ['EX', 'MEM']:
                for prev_instr in self.stages[stage_name].details:
                    if prev_instr and 'decoded' in prev_instr:
                        prev_rd = prev_instr['decoded'].get('rd') or prev_instr['decoded'].get('rt')
                        if prev_rd in src_regs and prev_rd != 0:
                            return True
            for j in range(i + 1, len(decoded_instructions)):
                if decoded_instructions[j]:
                    dst = decoded_instructions[j].get('rd') or decoded_instructions[j].get('rt')
                    if dst in src_regs and dst != 0:
                        return True
        return False

    def get_source_registers(self, decoded: Dict) -> List[int]:
        instr_type = decoded['type']
        mnemonic = decoded['mnemonic']
        if instr_type == 'R':
            return [decoded['rs'], decoded['rt']]
        elif instr_type == 'I':
            src = [decoded['rs']]
            if mnemonic in ['BEQ', 'BNE', 'SW']:
                src.append(decoded['rt'])
            return src
        return []

    def flush_pipeline(self):
        for stage in self.stages.values():
            stage.instructions = [None] * self.issue_width
            stage.details = [{}] * self.issue_width

    def run_pipeline_cycle(self):
        self.cycle_count += 1
        cycle_info = f"\n--- Cycle {self.cycle_count} ---"

        self.write_back_stage_func(self.stages['MEM'].details)
        mem_data = self.memory_stage_func(self.stages['EX'].details)
        ex_data = self.execute_stage([d.get('decoded_instruction') if d else None for d in self.stages['ID'].details])
        decoded_instructions = self.decode_stage(self.stages['IF'].instructions)

        hazard = self.detect_data_hazard(decoded_instructions)
        if hazard:
            logger.info(f"{cycle_info}\nData hazard detected. Stalling pipeline.")
            self.flush_pipeline()
            stall_info = "STALL: Inserted bubble (NOP)"
            fetched_instructions = [None] * self.issue_width  # Insert NOPs
        else:
            fetched_instructions = self.fetch_stage()
            stall_info = "NO STALL"

        # Update forwarding paths
        self.forwarding['MEM_WB'] = self.forwarding['EX_MEM']
        self.forwarding['EX_MEM'] = [
            None if not data else {
                'rd': data['decoded'].get('rd') or data['decoded'].get('rt'),
                'value': data.get('alu_result')
            } for data in self.stages['EX'].details
        ]

        # Convert integers to hex strings for IF stage, keep strings for others
        pipeline_details = [
            f"{name}: {', '.join([hex(instr) if isinstance(instr, int) else (instr if instr else 'NOP') for instr in stage.instructions])}"
            for name, stage in self.stages.items()
        ]
        logger.info(f"{cycle_info}\n{' | '.join(pipeline_details)} | {stall_info}")
        self.print_clock_cycle()

    def print_clock_cycle(self):
        logger.info(f"Clock Cycle: {self.cycle_count}")

    def simulate(self, program: List[int], max_cycles: int = 100):
        self.program = program
        logger.info("=== Superscalar Pipeline Simulation Started ===")
        while self.pc < len(self.program) or any(any(instr is not None for instr in stage.instructions) for stage in self.stages.values()):
            if self.cycle_count >= max_cycles:
                logger.warning("Maximum cycle count reached.")
                break
            self.run_pipeline_cycle()
        logger.info("=== Superscalar Pipeline Simulation Ended ===")
        self.print_registers()
        logger.info(f"Total Cycles: {self.cycle_count}")

    def print_registers(self):
        logger.info("\nFinal Register States:")
        for i in range(len(self.registers)):
            logger.info(f"${i}: {self.registers[i]}")

# Example Usage
if __name__ == "__main__":
    sample_program = [
        0x34020000,  # ORI $2 , $0, 0x0
        0x2014000A,  # ADDI $20, $0, 0xA
        0x383F0001,  # XORI $31, $0, 0x1
        0x30050000,  # ANDI $5 , $0, 0x0
        0x8CA00000,  # LW $10, 0x0($5)
        0x8CAF0000,  # LW $15, 0x0($5)
        0x20420001,  # ADDI $2, $2, 1
        0x0252402B,  # SGT $25, $20, $2
        0x17A00009,  # BNE $25, $31, END
        0x8CB00000,  # LW $16, 0x0($5)
        0x02CA502B,  # SGT $26, $16, $10
        0x11C00003,  # BEQ $26, $0, MIN
        0x020A5025,  # OR $10, $16, $0
        0x08000007,  # J LOOP
        0x02CF682A,  # SLT $27, $16, $15
        0x11E0FFF9,  # BEQ $27, $0, LOOP
        0x020F8020,  # ADD $15, $16, $0
        0x08000007,  # J LOOP
        0x00000000,  # NOP
    ]

    processor = ComprehensivePipelineProcessor()
    initial_registers = {2: 0, 20: 10, 31: 1, 5: 0}
    processor.set_registers(initial_registers)
    processor.memory[:10] = [0x10, 0xF, 0x5, 0x9, 0x20, 0x19, 0x4, 0x1E, 0x9, 0xB]
    processor.simulate(sample_program, max_cycles=100)

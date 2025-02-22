import logging
from typing import List, Dict, Optional
from mips_pipline.PipelineStage import PipelineStage
from mips_pipline.InstructionDecoder import InstructionDecoder
from mips_pipline.enums.ProcessorSignals import Stages, InstructionTypes, RegisterTypes, Instruction

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class ComprehensivePipelineProcessor:
    def __init__(self, memory_size: int = 4096, register_count: int = 32, issue_width: int = 2):
        self.memory = [0] * memory_size
        self.registers = [0] * register_count
        self.issue_width = issue_width

        self.stages = {
            Stages.IF.value: PipelineStage('Instruction Fetch', self.issue_width),
            Stages.ID.value: PipelineStage('Instruction Decode', self.issue_width),
            Stages.EX.value: PipelineStage('Execute', self.issue_width),
            Stages.MEM.value: PipelineStage('Memory Access', self.issue_width),
            Stages.WB.value: PipelineStage('Write Back', self.issue_width)
        }

        self.pc = 0
        self.cycle_count = 0
        self.instruction_count = 0
        self.program: List[int] = []

        self.forwarding = {
            Stages.EX_MEM.value: [None] * self.issue_width,
            Stages.MEM_WB.value: [None] * self.issue_width
        }
        self.stall = False

    def set_registers(self, initial_values: Dict[int, int]):
        for reg, value in initial_values.items():
            if 0 <= reg < len(self.registers) and reg != 0:
                self.registers[reg] = value

    def fetch_stage(self) -> List[Optional[int]]:
        stage = self.stages[Stages.IF.value]
        instructions = []
        for _ in range(self.issue_width):
            if self.pc < len(self.program):
                instructions.append(self.program[self.pc])
                self.pc += 1
            else:
                instructions.append(None)
        stage.instructions = instructions
        stage.details = [
            {RegisterTypes.program_counter.value: self.pc - len(instructions) + i, RegisterTypes.raw_instruction.value: hex(instr)}
            if instr is not None else {} for i, instr in enumerate(instructions)
        ]
        logger.info(f"Fetch Stage - Instructions: {[hex(instr) if instr is not None else 'None' for instr in instructions]}")
        return instructions

    def decode_stage(self, instructions: List[Optional[int]]) -> List[Optional[Dict]]:
        stage = self.stages[Stages.ID.value]
        decoded_instructions = [
            InstructionDecoder.decode(instr) if instr is not None else None for instr in instructions
        ]
        stage.instructions = [
            decoded[RegisterTypes.mnemonic.value] if decoded else None 
            for decoded in decoded_instructions
        ]
        stage.details = [{RegisterTypes.decoded_instruction.value: decoded} if decoded else {} for decoded in decoded_instructions]
        return decoded_instructions

    def execute_stage(self, decoded_instructions: List[Optional[Dict]]) -> List[Optional[Dict]]:
        stage = self.stages[Stages.EX.value]
        results = []
        branch_taken = False
        jump_address = None

        for decoded in decoded_instructions:
            if decoded is None:
                results.append(None)
                continue

            instr_type = decoded[RegisterTypes.type.value]
            mnemonic = decoded[RegisterTypes.mnemonic.value]
            rs_val = self.get_register_value(decoded[RegisterTypes.rs.value])
            rt_val = self.get_register_value(decoded[RegisterTypes.rt.value])
            rd = decoded.get(RegisterTypes.rd.value, None)
            shamt = decoded.get(RegisterTypes.shamt.value, 0)
            imm = decoded[RegisterTypes.immediate.value]
            address = decoded.get(RegisterTypes.address.value, None)

            result = None

            if instr_type == InstructionTypes.R.value:
                if mnemonic == Instruction.ADD.value: result = rs_val + rt_val
                elif mnemonic == Instruction.SUB.value: result = rs_val - rt_val
                elif mnemonic == Instruction.AND.value: result = rs_val & rt_val
                elif mnemonic == Instruction.OR.value: result = rs_val | rt_val
                elif mnemonic == Instruction.NOR.value: result = ~(rs_val | rt_val) & 0xFFFFFFFF
                elif mnemonic == Instruction.XOR.value: result = rs_val ^ rt_val
                elif mnemonic == Instruction.SLT.value: result = 1 if rs_val < rt_val else 0
                elif mnemonic == Instruction.SGT.value: result = 1 if rs_val > rt_val else 0
                elif mnemonic == Instruction.SLL.value: result = rt_val << shamt
                elif mnemonic == Instruction.SRL.value: result = (rt_val & 0xFFFFFFFF) >> shamt
            elif instr_type == InstructionTypes.I.value:
                if mnemonic == Instruction.ADDI.value: result = rs_val + imm
                elif mnemonic == Instruction.ORI.value: result = rs_val | (imm & 0xFFFF)
                elif mnemonic == Instruction.XORI.value: result = rs_val ^ (imm & 0xFFFF)
                elif mnemonic in [Instruction.LW.value, Instruction.SW.value]: result = rs_val + imm
                elif mnemonic == Instruction.BEQ.value and rs_val == rt_val:
                    branch_taken = True
                    jump_address = self.pc + imm
                elif mnemonic == Instruction.BNE.value and rs_val != rt_val:
                    branch_taken = True
                    jump_address = self.pc + imm
                elif mnemonic == Instruction.BLTZ.value and rs_val < 0:
                    branch_taken = True
                    jump_address = self.pc + imm
                elif mnemonic == Instruction.BGEZ.value and rs_val >= 0:
                    branch_taken = True
                    jump_address = self.pc + imm
            elif instr_type == InstructionTypes.J.value:
                if mnemonic == InstructionTypes.J.value:
                    jump_address = address
                    branch_taken = True
                elif mnemonic == Instruction.JAL.value:
                    self.registers[31] = self.pc
                    jump_address = address
                    branch_taken = True

            if branch_taken and jump_address is not None:
                self.pc = jump_address
                self.flush_pipeline()

            results.append({
                RegisterTypes.alu_result.value: result,
                RegisterTypes.decoded.value: decoded,
                RegisterTypes.branch_taken.value: branch_taken,
                RegisterTypes.jump_address.value: jump_address
            })

        stage.instructions = [decoded[RegisterTypes.mnemonic.value] if decoded else None for decoded in decoded_instructions]
        stage.details = results
        return results

    def memory_stage_func(self, execute_data: List[Optional[Dict]]) -> List[Optional[Dict]]:
        stage = self.stages[Stages.MEM.value]
        mem_results = []
        for data in execute_data:
            if data is None or RegisterTypes.decoded.value not in data:
                mem_results.append(None)
                continue

            decoded = data[RegisterTypes.decoded.value]
            if RegisterTypes.mnemonic.value not in decoded:
                mem_results.append(None)
                continue

            alu_result = data.get(RegisterTypes.alu_result.value)
            mnemonic = decoded[RegisterTypes.mnemonic.value]
            mem_result = alu_result

            if mnemonic == Instruction.LW.value and alu_result is not None and 0 <= alu_result < len(self.memory):
                mem_result = self.memory[alu_result]
            elif mnemonic == Instruction.SW.value and alu_result is not None and 0 <= alu_result < len(self.memory):
                self.memory[alu_result] = self.registers[decoded[RegisterTypes.rt.value]]

            mem_results.append({
                RegisterTypes.mem_result.value: mem_result,
                RegisterTypes.decoded.value: decoded,
                RegisterTypes.alu_result.value: alu_result
            })

        stage.instructions = [
            data[RegisterTypes.decoded.value][RegisterTypes.mnemonic.value] if data and RegisterTypes.decoded.value in data and RegisterTypes.mnemonic.value in data[RegisterTypes.decoded.value] else None
            for data in execute_data
        ]
        stage.details = mem_results
        return mem_results

    def write_back_stage_func(self, memory_data: List[Optional[Dict]]):
        stage = self.stages[Stages.WB.value]

        for data in memory_data:
            if data is None or RegisterTypes.decoded.value not in data or RegisterTypes.mnemonic.value not in data[RegisterTypes.decoded.value]:
                continue

            decoded = data[RegisterTypes.decoded.value]
            mnemonic = decoded[RegisterTypes.mnemonic.value]
            alu_result = data.get(RegisterTypes.alu_result.value)
            mem_result = data.get(RegisterTypes.mem_result.value)
            rd = decoded.get(RegisterTypes.rd.value, None)
            rt = decoded.get(RegisterTypes.rt.value, None)

            if mnemonic in [Instruction.ADD.value, Instruction.SUB.value, Instruction.AND.value, Instruction.OR.value, Instruction.NOR.value, Instruction.XOR.value, Instruction.SLT.value, Instruction.SGT.value, Instruction.SLL.value, Instruction.SRL.value] and rd != 0 and alu_result is not None:
                self.registers[rd] = alu_result
            elif mnemonic in [Instruction.ADDI.value, Instruction.ORI.value, Instruction.XORI.value] and rt != 0 and alu_result is not None:
                self.registers[rt] = alu_result
            elif mnemonic == Instruction.LW.value and rt != 0 and mem_result is not None:
                self.registers[rt] = mem_result
            elif mnemonic == Instruction.JAL.value and data.get(RegisterTypes.jump_address.value) is not None:
                self.registers[31] = self.pc

        stage.instructions = [
            data[RegisterTypes.decoded.value][RegisterTypes.mnemonic.value] if data and RegisterTypes.decoded.value in data and RegisterTypes.mnemonic.value in data[RegisterTypes.decoded.value] else None
            for data in memory_data
        ]
        stage.details = memory_data if memory_data else [{}] * self.issue_width

    def get_register_value(self, reg_num: int) -> int:
        for fwd in self.forwarding[Stages.EX_MEM.value] + self.forwarding[Stages.MEM_WB.value]:
            if fwd and RegisterTypes.rd.value in fwd and fwd[RegisterTypes.rd.value] == reg_num and reg_num != 0:
                return fwd['value']
        return self.registers[reg_num]

    def detect_data_hazard(self, decoded_instructions: List[Optional[Dict]]) -> bool:
        for i, decoded in enumerate(decoded_instructions):
            if decoded is None:
                continue
            src_regs = self.get_source_registers(decoded)
            for stage_name in [Stages.EX.value, Stages.MEM.value]:
                for prev_instr in self.stages[stage_name].details:
                    if prev_instr and RegisterTypes.decoded.value in prev_instr:
                        prev_rd = prev_instr[RegisterTypes.decoded.value].get(RegisterTypes.rd.value) or prev_instr[RegisterTypes.decoded.value].get(RegisterTypes.rt.value)
                        if prev_rd in src_regs and prev_rd != 0:
                            return True
            for j in range(i + 1, len(decoded_instructions)):
                if decoded_instructions[j]:
                    dst = decoded_instructions[j].get(RegisterTypes.rd.value) or decoded_instructions[j].get(RegisterTypes.rt.value)
                    if dst in src_regs and dst != 0:
                        return True
        return False

    def get_source_registers(self, decoded: dict) -> list:
        instr_type = decoded[RegisterTypes.type.value]
        mnemonic = decoded[RegisterTypes.mnemonic.value]
        if instr_type == InstructionTypes.R.value:
            return [decoded[RegisterTypes.rs.value], decoded[RegisterTypes.rt.value]]
        elif instr_type == InstructionTypes.I.value:
            src = [decoded[RegisterTypes.rs.value]]
            if mnemonic in [Instruction.BEQ.value, Instruction.BNE.value, Instruction.SW.value]:
                src.append(decoded[RegisterTypes.rt.value])
            return src
        return []

    def flush_pipeline(self):
        for stage in self.stages.values():
            stage.instructions = [None] * self.issue_width
            stage.details = [{}] * self.issue_width

    def run_pipeline_cycle(self):
        self.cycle_count += 1
        cycle_info = f"\n---- Cycle {self.cycle_count} ----"

        self.write_back_stage_func(self.stages[Stages.MEM.value].details)
        mem_data = self.memory_stage_func(self.stages[Stages.EX.value].details)
        ex_data = self.execute_stage([d.get(RegisterTypes.decoded_instruction.value) if d else None for d in self.stages[Stages.ID.value].details])
        decoded_instructions = self.decode_stage(self.stages[Stages.IF.value].instructions)

        hazard = self.detect_data_hazard(decoded_instructions)
        if hazard:
            logger.info(f"{cycle_info}\nData hazard detected. Stalling pipeline.")
            self.flush_pipeline()
            stall_info = "STALL: Inserted bubble (NOP)"
            fetched_instructions = [None] * self.issue_width  # Insert NOPs
        else:
            fetched_instructions = self.fetch_stage()
            stall_info = "NO STALL"

        self.forwarding[Stages.MEM_WB.value] = self.forwarding[Stages.EX_MEM.value]
        self.forwarding[Stages.EX_MEM.value] = [
            None if not data else {
                RegisterTypes.rd.value: data[RegisterTypes.decoded.value].get(RegisterTypes.rd.value) or data[RegisterTypes.decoded.value].get(RegisterTypes.rt.value),
                'value': data.get(RegisterTypes.alu_result.value)
            } for data in self.stages[Stages.EX.value].details
        ]

        pipeline_details = [
            f"{name}: {', '.join([hex(instr) if isinstance(instr, int) else (instr if instr else Instruction.NOP.value) for instr in stage.instructions])}"
            for name, stage in self.stages.items()
        ]
        logger.info(f"{cycle_info}\n{' | '.join(pipeline_details)} | {stall_info}")
        self.print_clock_cycle()

    def print_clock_cycle(self):
        logger.info(f"Clock Cycle: {self.cycle_count}")

    def simulate(self, program: List[int], max_cycles: int = 100):
        self.program = program
        logger.info("====== Superscalar Pipeline Simulation Started =====")
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

from typing import Dict, List
from prettytable import PrettyTable
from mips_pipline.enums.ProcessorSignals import RegisterTypes, Stages, Instruction
import logging

class PipelineLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def print_cycle_header(self, cycle_num: int):
        self.logger.info("\n" + "="*50)
        self.logger.info(f"CYCLE {cycle_num}")
        self.logger.info("="*50)

    def print_pipeline_stages(self, stages: Dict):
        table = PrettyTable()
        table.field_names = ["Stage", "Slot 0", "Slot 1"]
        table.align = "l"
        
        for stage_name, stage in stages.items():
            instr_slots = [
                str(instr) if instr else Instruction.NOP.value 
                for instr in stage.instructions
            ]
            table.add_row([stage_name, instr_slots[0], instr_slots[1]])
            
        self.logger.info("\nPipeline State:")
        self.logger.info(table)

    def print_stage_details(self, stage_details: Dict):
        table = PrettyTable()
        table.field_names = ["Stage", "Details"]
        table.align = "l"
        
        for stage_name, details in stage_details.items():
            formatted_details = self._format_stage_details(details)
            table.add_row([stage_name, formatted_details])
            
        self.logger.info("\nStage Details:")
        self.logger.info(table)

    def print_register_state(self, registers: List[int]):
        # MIPS Register Groups
        register_groups = {
            "Zero": [("$zero", 0)],
            "Function Arguments": [("$a"+str(i), i+4) for i in range(4)],
            "Function Results": [("$v"+str(i), i+2) for i in range(2)],
            "Temporaries": [("$t"+str(i), i+8) for i in range(10)],
            "Saved Temporaries": [("$s"+str(i), i+16) for i in range(8)],
            "Special Purpose": [
                ("$gp", 28),  # Global Pointer
                ("$sp", 29),  # Stack Pointer
                ("$fp", 30),  # Frame Pointer
                ("$ra", 31)   # Return Address
            ]
        }

        table = PrettyTable()
        table.field_names = ["Group", "Register", "Number", "Value (Hex)", "Value (Dec)"]
        table.align = "l"
        
        for group_name, regs in register_groups.items():
            for reg_name, reg_num in regs:
                value = registers[reg_num]
                if reg_num == 0 or value != 0:  # Always show $zero and non-zero registers
                    table.add_row([
                        group_name,
                        reg_name,
                        f"${reg_num}",
                        f"0x{value:08x}",
                        str(value)
                    ])
            # Add separator between groups
            if any(registers[reg_num] != 0 for _, reg_num in regs):
                table.add_row(["-"*15, "-"*10, "-"*5, "-"*10, "-"*10])

        self.logger.info("\nRegister State:")
        self.logger.info(table)

    def print_hazard_info(self, hazard_detected: bool, forwarding_info: Dict):
        table = PrettyTable()
        table.field_names = ["Type", "Status"]
        table.align = "l"
        
        table.add_row(["Hazard", "Detected - Pipeline Stalled" if hazard_detected else "None"])
        
        forwarding_status = []
        for stage, forwards in forwarding_info.items():
            for fwd in forwards:
                if fwd:
                    forwarding_status.append(
                        f"{stage}: R{fwd.get(RegisterTypes.rd.value)} = {fwd.get('value')}"
                    )
        
        table.add_row(["Forwarding", "\n".join(forwarding_status) if forwarding_status else "None"])
        
        self.logger.info("\nHazard and Forwarding Information:")
        self.logger.info(table)

    def print_statistics(self, stats: Dict):
        table = PrettyTable()
        table.field_names = ["Metric", "Value"]
        table.align = "l"
        
        for metric, value in stats.items():
            table.add_row([metric, value])
            
        self.logger.info("\nSimulation Statistics:")
        self.logger.info(table)

    def _format_stage_details(self, details: List[Dict]) -> str:
        formatted = []
        for slot_num, detail in enumerate(details):
            if detail:
                formatted.append(f"Slot {slot_num}:")
                for key, value in detail.items():
                    if key != RegisterTypes.decoded.value:
                        formatted.append(f"  {key}: {value}")
        return "\n".join(formatted) if formatted else "No details"

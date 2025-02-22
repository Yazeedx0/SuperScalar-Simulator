import logging
from typing import Dict, List
from tabulate import tabulate
from datetime import datetime

class SimulationReportGenerator:
    def __init__(self):
        self.program_info = []
        self.cycle_data = []
        self.start_time = datetime.now()
        
    def add_program_info(self, program: List[int]):
        self.program_info = [hex(instr) for instr in program]
        
    def add_cycle_data(self, cycle: int, stages: Dict, registers: Dict, hazards: Dict):
        self.cycle_data.append({
            'cycle': cycle,
            'stages': stages,
            'registers': registers,
            'hazards': hazards
        })
        
    def generate_report(self) -> str:
        report = []
        
        # Header
        report.append("=" * 80)
        report.append("MIPS Superscalar Pipeline Simulation Report")
        report.append(f"Generated: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80 + "\n")
        
        # Program Information
        report.append("1. Program Information")
        report.append("-" * 20)
        report.append("Instructions:")
        for i, instr in enumerate(self.program_info):
            report.append(f"{i:4d}: {instr}")
        report.append("")
        
        # Simulation Summary
        report.append("2. Simulation Summary")
        report.append("-" * 20)
        report.append(f"Total Cycles: {len(self.cycle_data)}")
        report.append(f"Instructions Executed: {len(self.program_info)}")
        report.append(f"CPI: {len(self.cycle_data)/len(self.program_info):.2f}")
        report.append("")
        
        # Cycle-by-Cycle Analysis
        report.append("3. Cycle-by-Cycle Analysis")
        report.append("-" * 20)
        for cycle_info in self.cycle_data:
            report.append(f"\nCycle {cycle_info['cycle']}:")
            
            # Pipeline Stages
            stage_data = []
            for stage, instructions in cycle_info['stages'].items():
                instr_str = ', '.join([str(i) if i else 'NOP' for i in instructions])
                stage_data.append([stage, instr_str])
            report.append(tabulate(stage_data, headers=['Stage', 'Instructions'], tablefmt='grid'))
            
            # Hazards
            if cycle_info['hazards']['data_hazards']:
                report.append("* Data Hazard Detected")
        
        # Register State
        report.append("\n4. Final Register State")
        report.append("-" * 20)
        final_registers = self.cycle_data[-1]['registers']
        reg_data = [[f"R{i}", hex(val)] for i, val in final_registers.items()]
        report.append(tabulate(reg_data, headers=['Register', 'Value'], tablefmt='grid'))
        
        # Performance Metrics
        report.append("\n5. Performance Metrics")
        report.append("-" * 20)
        # Count actual hazard stalls by looking at consecutive cycles
        hazard_cycles = 0
        for i in range(len(self.cycle_data)):
            if self.cycle_data[i]['hazards']['data_hazards']:
                # Check if this hazard actually caused a stall
                # by looking at the pipeline stages
                stages = self.cycle_data[i]['stages']
                if any('NOP' in str(instr) for stage, instrs in stages.items() for instr in instrs):
                    hazard_cycles += 1

        total_instructions = len(self.program_info)
        ideal_cycles = total_instructions / 2  # Due to 2-way superscalar
        actual_cycles = len(self.cycle_data)
        
        # Calculate efficiency considering superscalar capability
        theoretical_max_throughput = total_instructions
        actual_throughput = total_instructions / actual_cycles
        pipeline_efficiency = (actual_throughput / 2) * 100  # Divide by 2 for 2-way superscalar

        report.append(f"Hazard Stalls: {hazard_cycles}")
        report.append(f"Ideal Cycles (no hazards): {ideal_cycles:.1f}")
        report.append(f"Actual Cycles: {actual_cycles}")
        report.append(f"Pipeline Efficiency: {pipeline_efficiency:.2f}%")
        report.append(f"Instructions Per Cycle (IPC): {actual_throughput:.2f}")
        
        return "\n".join(report)


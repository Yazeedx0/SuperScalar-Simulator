import logging
from typing import Dict, List
from tabulate import tabulate
from datetime import datetime
from fpdf import FPDF
import os

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        # Define colors
        self.primary_color = (40, 120, 180)
        self.secondary_color = (70, 130, 180)
        self.light_gray = (245, 245, 245)
        self.dark_gray = (80, 80, 80)
        
        # Try to use Montserrat if available, otherwise fall back to Arial
        base_path = os.path.dirname(os.path.dirname(__file__))
        font_path = f'{base_path}/assets/fonts/Montserrat-Regular.ttf'
        try:
            self.add_font('Montserrat', '', font_path, uni=True)
            self.add_font('Montserrat', 'B', f'{base_path}/assets/fonts/Montserrat-Bold.ttf', uni=True)
            self.default_font = 'Montserrat'
        except RuntimeError:
            self.default_font = 'Arial'
        
    def header(self):
        # Modern header design
        self.set_fill_color(*self.primary_color)
        self.rect(0, 0, 210, 35, 'F')
        
        # Title
        self.set_font(self.default_font, 'B', 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'Risk - V Superscalar Simulation', 0, 1, 'C')
        
        # Subtitle
        self.set_font(self.default_font, '', 12)
        self.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.default_font, '', 8)
        self.set_text_color(*self.dark_gray)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font(self.default_font, 'B', 16)
        self.set_fill_color(*self.secondary_color)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, title, 0, 1, 'L', True)
        self.ln(5)

    def create_table(self, headers, data, col_widths=None, data_font=None):
        if data_font is None:
            data_font = self.default_font
        
        self.set_fill_color(*self.light_gray)
        self.set_text_color(*self.dark_gray)
        self.set_font(self.default_font, 'B', 10)
        
        # Headers
        for i, header in enumerate(headers):
            width = col_widths[i] if col_widths else self.get_string_width(header) + 10
            self.cell(width, 8, header, 1, 0, 'C', True)
        self.ln()
        
        # Data with subtle tint for alternate rows
        self.set_font(data_font, '', 10)
        for i, row in enumerate(data):
            self.set_fill_color(240, 248, 255) if i % 2 else self.set_fill_color(255, 255, 255)  # Alice Blue for alternate rows
            for j, cell in enumerate(row):
                width = col_widths[j] if col_widths else self.get_string_width(str(cell)) + 10
                self.cell(width, 8, str(cell), 1, 0, 'L', True)
            self.ln()

class SimulationReportGenerator:
    def __init__(self):
        self.program_info = []
        self.cycle_data = []
        self.start_time = datetime.now()
        self.pdf = PDFReport()
        
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
        report.append("Risk- V : MIPS Superscalar Pipeline Simulation Report")
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
        # Count actual hazard stalls
        hazard_cycles = 0
        for i in range(len(self.cycle_data)):
            if self.cycle_data[i]['hazards']['data_hazards']:
                stages = self.cycle_data[i]['stages']
                if any('NOP' in str(instr) for stage, instrs in stages.items() for instr in instrs):
                    hazard_cycles += 1

        total_instructions = len(self.program_info)
        ideal_cycles = total_instructions / 2  # Due to 2-way superscalar
        actual_cycles = len(self.cycle_data)
        
        theoretical_max_throughput = total_instructions
        actual_throughput = total_instructions / actual_cycles
        pipeline_efficiency = (actual_throughput / 2) * 100  # Divide by 2 for 2-way superscalar

        report.append(f"Hazard Stalls: {hazard_cycles}")
        report.append(f"Ideal Cycles (no hazards): {ideal_cycles:.1f}")
        report.append(f"Actual Cycles: {actual_cycles}")
        report.append(f"Pipeline Efficiency: {pipeline_efficiency:.2f}%")
        report.append(f"Instructions Per Cycle (IPC): {actual_throughput:.2f}")
        
        return "\n".join(report)

    def generate_pdf(self, filename: str):
        """Generate a beautifully formatted PDF report"""
        self.pdf.add_page()
        
        # Program Information Section
        self.pdf.chapter_title('1. Program Information')
        headers = ['Index', 'Instruction']
        data = [[f"{i:04d}", instr] for i, instr in enumerate(self.program_info[:20])]
        self.pdf.create_table(headers, data, [30, 160], data_font='Courier')  # Use Courier for instructions
        self.pdf.ln(10)

        # Performance Analysis Section
        self.pdf.chapter_title('2. Performance Analysis')
        metrics = [
            ['Total Cycles', str(len(self.cycle_data))],
            ['Instructions', str(len(self.program_info))],
            ['CPI', f"{len(self.cycle_data)/len(self.program_info):.2f}"],
            ['Efficiency', f"{(len(self.program_info)/(len(self.cycle_data)*2))*100:.1f}%"]
        ]
        self.pdf.create_table(['Metric', 'Value'], metrics, [95, 95])
        self.pdf.ln(10)

        # Pipeline Analysis Section
        self.pdf.chapter_title('3. Pipeline Stages Analysis')
        for i, cycle_info in enumerate(self.cycle_data[:15]):
            # Cycle header with modern styling
            self.pdf.set_fill_color(200, 220, 240)  # Light blue for cycle header
            self.pdf.set_font(self.pdf.default_font, 'B', 12)
            self.pdf.cell(0, 8, f"Cycle {cycle_info['cycle']}", 0, 1, 'L', True)
            self.pdf.ln(2)
            
            # Stage information
            stage_data = []
            for stage, instructions in cycle_info['stages'].items():
                instr_str = ', '.join([str(i) if i else 'NOP' for i in instructions])
                stage_data.append([stage, instr_str])
            self.pdf.create_table(['Stage', 'Instructions'], stage_data, [40, 150])
            
            # Hazard warning with icon
            if cycle_info['hazards']['data_hazards']:
                self.pdf.set_text_color(200, 0, 0)
                self.pdf.set_font(self.pdf.default_font, 'B', 10)
                self.pdf.cell(0, 6, '⚠ Data Hazard Detected', 0, 1, 'L')
            self.pdf.ln(5)  # Increased spacing after each cycle

        # Final Register State Section
        self.pdf.chapter_title('4. Final Register State')
        final_registers = self.cycle_data[-1]['registers']
        reg_data = [[f"R{i}", hex(val)] for i, val in final_registers.items()]
        self.pdf.create_table(['Register', 'Value'], reg_data, [95, 95], data_font='Courier')  # Use Courier for values
        self.pdf.ln(10)

        # Detailed Performance Metrics Section
        self.pdf.chapter_title('5. Detailed Performance Metrics')
        total_cycles = len(self.cycle_data)
        total_instructions = len(self.program_info)
        cpi = total_cycles / total_instructions
        ipc = total_instructions / total_cycles
        hazard_stalls = sum(1 for cycle in self.cycle_data if cycle['hazards']['data_hazards'] and any('NOP' in str(instr) for stage in cycle['stages'].values() for instr in stage))
        ideal_cycles = total_instructions / 2  # 2-way superscalar
        pipeline_efficiency = (ipc / 2) * 100  # Theoretical max IPC is 2
        metrics = [
            ['Total Cycles', str(total_cycles)],
            ['Total Instructions', str(total_instructions)],
            ['Cycles Per Instruction (CPI)', f"{cpi:.2f}"],
            ['Instructions Per Cycle (IPC)', f"{ipc:.2f}"],
            ['Hazard Stalls', str(hazard_stalls)],
            ['Ideal Cycles (no hazards)', f"{ideal_cycles:.1f}"],
            ['Pipeline Efficiency', f"{pipeline_efficiency:.1f}%"]
        ]
        self.pdf.create_table(['Metric', 'Value'], metrics, [120, 70])
        
        self.pdf.output(filename)
from mips_pipline.ComprehensivePipelineProcessor import ComprehensivePipelineProcessor
from mips_pipline.SimulationReportGenerator import SimulationReportGenerator

def main():
    # Create processor instance with default configuration
    processor = ComprehensivePipelineProcessor(
        memory_size=4096,
        register_count=32,
        issue_width=2
    )

    # Test program with all instruction types
    program = [
        # Arithmetic operations
        0x00430820,  # add  r1, r2, r3
        0x00A62022,  # sub  r4, r5, r6
        0x00E83820,  # add  r7, r7, r8
        0x012A5022,  # sub  r10, r9, r10
]

    # Initialize registers with test values
    initial_registers = {
        2: 10,      # R2 = 10
        3: 20,      # R3 = 20
        5: 50,      # R5 = 50
        6: 30,      # R6 = 30
        7: 15,      # R7 = 15
        8: 0xFF,    # R8 = 255
        9: 0xF0,    # R9 = 240
        10: 0x55,   # R10 = 85
        11: 0x0F,   # R11 = 15
        12: 0xF0,   # R12 = 240
        31: 0x100   # R31 = 256
    }
    processor.set_registers(initial_registers)

    # Initialize memory values for testing load/store
    processor.store_word(0, 0x12345678)  # For testing lw
    
    # Run simulation and generate both text and PDF reports
    report_generator = SimulationReportGenerator()
    processor.simulate(program, max_cycles=30, report_generator=report_generator)
    
    # Generate PDF report
    report_generator.generate_pdf('simulation_report.pdf')

if __name__ == "__main__":
    main()

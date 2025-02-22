from mips_pipline.ComprehensivePipelineProcessor import ComprehensivePipelineProcessor
from mips_pipline.SimulationReportGenerator import SimulationReportGenerator

def main():
    # Create processor instance with default configuration
    processor = ComprehensivePipelineProcessor(
        memory_size=4096,
        register_count=32,
        issue_width=2
    )

    # Example program - simple arithmetic operations
    # ADD R1, R2, R3    # R1 = R2 + R3
    # SUB R4, R5, R6    # R4 = R5 - R6
    # AND R7, R8, R9    # R7 = R8 & R9
    # OR  R10, R11, R12 # R10 = R11 | R12
    program = [
        0x00430820,  # ADD R1, R2, R3
        0x00A62022,  # SUB R4, R5, R6
        0x01093824,  # AND R7, R8, R9
        0x016C5025   # OR  R10, R11, R12
    ]

    # Initialize some register values for testing
    initial_registers = {
        2: 10,   # R2 = 10
        3: 20,   # R3 = 20
        5: 50,   # R5 = 50
        6: 30,   # R6 = 30
        8: 0xFF, # R8 = 255
        9: 0xF0, # R9 = 240
        11: 0x0F,# R11 = 15
        12: 0xF0 # R12 = 240
    }
    processor.set_registers(initial_registers)

    # Create report generator
    report_generator = SimulationReportGenerator()

    # Run simulation
    processor.simulate(program, max_cycles=20, report_generator=report_generator)

if __name__ == "__main__":
    main()

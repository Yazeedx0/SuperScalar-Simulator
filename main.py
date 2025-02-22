from mips_pipline.ComprehensivePipelineProcessor import ComprehensivePipelineProcessor
from mips_pipline.SimulationReportGenerator import SimulationReportGenerator

def main():
    # Create processor instance with default configuration
    processor = ComprehensivePipelineProcessor(
        memory_size=4096,
        register_count=32,
        issue_width=2
    )

    # Test program with comprehensive instruction set
    program = [
        # Arithmetic operations
        0x00430820,  # add  r1, r2, r3       # R1 = R2 + R3
        0x00A62022,  # sub  r4, r5, r6       # R4 = R5 - R6
        0x20070005,  # addi r7, r0, 5        # R7 = R0 + 5
        
        # Logical operations
        0x00C84024,  # and  r8, r6, r8       # R8 = R6 & R8
        0x00E94825,  # or   r9, r7, r9       # R9 = R7 | R9
        0x00065080,  # sll  r10, r6, 2       # R10 = R6 << 2
        0x000B5842,  # srl  r11, r11, 1      # R11 = R11 >> 1
        
        # Memory operations
        0x8C0C0000,  # lw   r12, 0(r0)      # R12 = MEM[R0 + 0]
        0xAC0D0004,  # sw   r13, 4(r0)      # MEM[R0 + 4] = R13
        
        # Branch and jump operations
        0x10A60002,  # beq  r5, r6, 2        # if(R5==R6) PC+=8
        0x00430820,  # add  r1, r2, r3       # (might be skipped)
        0x14A60002,  # bne  r5, r6, 2        # if(R5!=R6) PC+=8
        0x00C84024,  # and  r8, r6, r8       # (might be skipped)
        0x08000000,  # j    0                # jump to address 0
    ]

    # Initialize registers with test values
    initial_registers = {
        2: 10,       # R2 = 10
        3: 20,       # R3 = 20
        5: 50,       # R5 = 50
        6: 30,       # R6 = 30
        7: 15,       # R7 = 15
        8: 0xFF,     # R8 = 255
        9: 0xF0,     # R9 = 240
        10: 0x55,    # R10 = 85
        11: 0x0F,    # R11 = 15
        12: 0xF0,    # R12 = 240
        13: 0xAA,    # R13 = 170
        31: 0x100    # R31 = 256
    }
    processor.set_registers(initial_registers)

    # Initialize memory with test values
    processor.store_word(0, 0x12345678)  # For testing lw
    processor.store_word(4, 0x87654321)  # For testing lw/sw
    
    # Create report generator and run simulation
    report_generator = SimulationReportGenerator()
    processor.simulate(program, max_cycles=50, report_generator=report_generator)
    
    # Generate PDF report
    report_generator.generate_pdf('simulation_report.pdf')
    print("Report generated: simulation_report.pdf")

if __name__ == "__main__":
    main()

from mips_pipline.ComprehensivePipelineProcessor import ComprehensivePipelineProcessor



def main():
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

if __name__ == "__main__":
    main()


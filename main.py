from mips_pipline.ComprehensivePipelineProcessor import ComprehensivePipelineProcessor
from mips_pipline.ReportGenerator import ReportGenerator
import os
import sys
from io import StringIO

def main():
    try:
        # Capture console output
        old_stdout = sys.stdout
        console_output = StringIO()
        sys.stdout = console_output

        # Get absolute path for current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create output directory
        output_dir = os.path.join(current_dir, "output")
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created output directory: {output_dir}")
        except Exception as e:
            print(f"Error creating output directory: {e}")
            # Fallback to current directory
            output_dir = current_dir
            
        # Set the full path for the report file
        report_path = os.path.join(output_dir, "simulation_report.pdf")
        print(f"Will save report to: {report_path}")
        
        # Create report generator with full path
        report_generator = ReportGenerator(report_path)
        
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
        
        # Store initial state
        report_generator.add_register_state(dict(enumerate(processor.registers)))
        report_generator.add_memory_state(processor.memory[:])
        
        # Run simulation
        processor.simulate(sample_program, max_cycles=100, report_generator=report_generator)
        
        # Store final state
        report_generator.add_register_state(dict(enumerate(processor.registers)))
        report_generator.add_memory_state(processor.memory[:])
        
        # Restore stdout and get console output
        sys.stdout = old_stdout
        report_generator.add_log(console_output.getvalue())
        console_output.close()
        
        # Generate the final report
        report_generator.generate_report()
        print(f"Report generated successfully at: {report_path}")
        
    except Exception as e:
        print(f"Error in simulation: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()




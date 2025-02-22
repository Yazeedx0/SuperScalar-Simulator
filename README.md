# Superscalar MIPS Processor Simulator

A sophisticated Python-based simulator for a superscalar MIPS processor that implements advanced pipelining concepts, hazard detection, and instruction-level parallelism.

## 🌟 Features

### Core Architecture
- **Superscalar Execution**: Supports dual-issue (2-way) instruction execution
- **Five-Stage Pipeline**: Implements IF, ID, EX, MEM, and WB stages
- **Hazard Handling**: 
  - Dynamic data hazard detection
  - Pipeline stalling mechanism
  - Data forwarding support
- **Full MIPS Instruction Support**:
  - R-type: ADD, SUB, AND, OR, NOR, XOR, SLT, SGT, SLL, SRL
  - I-type: ADDI, ORI, XORI, LW, SW, BEQ, BNE, BLTZ, BGEZ
  - J-type: J, JAL

### Simulation Features
- **Detailed Execution Tracking**: Cycle-by-cycle pipeline state visualization
- **Performance Metrics**: CPI, pipeline efficiency, stall analysis
- **Rich Reporting**: Comprehensive simulation reports with:
  - Pipeline state history
  - Register file contents
  - Memory state changes
  - Hazard detection events
  - Data forwarding operations

## 🛠 Technical Architecture

### Core Components

#### 1. Pipeline Stages (`PipelineStage.py`)
- Implements individual pipeline stages with configurable width
- Manages instruction flow and stage-specific operations
- Handles stall propagation and bubble insertion

#### 2. Instruction Decoder (`InstructionDecoder.py`)
- Decodes 32-bit MIPS instructions into components
- Extracts opcodes, operands, and immediate values
- Identifies instruction types and operations

#### 3. Pipeline Processor (`ComprehensivePipelineProcessor.py`)
- Main simulation engine
- Implements the superscalar pipeline logic
- Manages hazard detection and handling
- Coordinates between different pipeline stages

#### 4. Simulation Reporter (`SimulationReportGenerator.py`)
- Generates detailed execution reports
- Tracks performance metrics
- Provides cycle-by-cycle analysis

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- Required packages: `tabulate`, `prettytable`

### Installation

```bash
# Clone the repository
git clone https://github.com/Yazeedx0/SuperScalar-Simulator
cd Superscalar simulator

# Install dependencies
pip install -r requirements.txt
```

### Running the Simulator

1. Basic Usage:
```python
from mips_pipline.ComprehensivePipelineProcessor import ComprehensivePipelineProcessor
from mips_pipline.SimulationReportGenerator import SimulationReportGenerator

# Create processor instance
processor = ComprehensivePipelineProcessor(
    memory_size=4096,
    register_count=32,
    issue_width=2
)

# Define your MIPS program (example)
program = [
    0x00430820,  # add  r1, r2, r3
    0x00A62022,  # sub  r4, r5, r6
    # Add more instructions...
]

# Initialize registers (optional)
initial_registers = {
    2: 10,  # R2 = 10
    3: 20,  # R3 = 20
    # Add more register values...
}
processor.set_registers(initial_registers)

# Run simulation with reporting
report_generator = SimulationReportGenerator()
processor.simulate(program, max_cycles=30, report_generator=report_generator)
```

## 📊 Simulation Output

The simulator provides detailed output including:

1. **Cycle-by-Cycle Pipeline State**:
```
---- Cycle 1 ----
IF: 0x00430820, 0x00A62022 | ID: NOP, NOP | EX: NOP, NOP | MEM: NOP, NOP | WB: NOP, NOP | NO STALL
```

2. **Register State Updates**:
```
Register State:
+----------+----------+--------+-------------+-----------+
| Group    | Register | Number | Value (Hex) | Value (Dec)|
+----------+----------+--------+-------------+-----------+
| Zero     | $zero    | $0     | 0x00000000 | 0         |
| Function | $a0      | $4     | 0x00000014 | 20        |
...
```

3. **Hazard Detection**:
```
Hazard and Forwarding Information:
+----------+-------------------------+
| Type     | Status                 |
+----------+-------------------------+
| Hazard   | Detected - Pipeline... |
| Forward  | EX->ID: R5 = 0x20      |
```

## 🔧 Advanced Configuration

### Processor Configuration
```python
processor = ComprehensivePipelineProcessor(
    memory_size=8192,      # Larger memory
    register_count=32,     # Standard MIPS register file
    issue_width=2         # Dual-issue superscalar
)
```

### Memory Initialization
```python
# Initialize specific memory locations
processor.store_word(0, 0x12345678)
processor.store_word(4, 0x87654321)
```

## 📊 Reporting System

The simulator provides comprehensive reporting capabilities through both PDF and text-based formats.

### PDF Reports
Generated PDF reports include:
- Professional header with simulation title and timestamp
- Program information with instruction listing
- Performance analysis metrics
- Detailed pipeline stages analysis
- Hazard detection events
- Clean, modern design with tables and color-coding

### Text-Based Reports
Includes detailed information about:
- Cycle-by-cycle pipeline state
- Register contents
- Hazard detection
- Performance metrics

### Using the Report Generator
```python
from mips_pipline.SimulationReportGenerator import SimulationReportGenerator

# Create report generator
report_gen = SimulationReportGenerator()

# Add program information
report_gen.add_program_info(program)

# Add cycle data during simulation
report_gen.add_cycle_data(
    cycle=current_cycle,
    stages=pipeline_stages,
    registers=register_state,
    hazards=hazard_info
)

# Generate text report
text_report = report_gen.generate_report()
print(text_report)

# Generate PDF report
report_gen.generate_pdf("simulation_report.pdf")
```

### Report Metrics
The reports include crucial performance metrics:
- Total execution cycles
- Instructions executed
- CPI (Cycles Per Instruction)
- Pipeline efficiency
- Hazard stall count
- Actual vs. ideal cycle comparison
- Instructions Per Cycle (IPC)

## 📝 Instruction Format Support

### R-Type Instructions
- Format: `opcode (6) | rs (5) | rt (5) | rd (5) | shamt (5) | funct (6)`
- Example: `ADD rd, rs, rt` → `0x00430820`

### I-Type Instructions
- Format: `opcode (6) | rs (5) | rt (5) | immediate (16)`
- Example: `ADDI rt, rs, imm` → `0x20040005`

### J-Type Instructions
- Format: `opcode (6) | address (26)`
- Example: `J target` → `0x08000000`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- MIPS Architecture References
- Computer Architecture Textbooks
- Open Source Community
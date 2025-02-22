# Superscalar MIPS Simulator

A Python-based simulator for a superscalar MIPS processor that models pipeline stages, hazard detection, and instruction-level parallelism.

## Features

- Superscalar execution with configurable issue width
- Five-stage pipeline implementation (IF, ID, EX, MEM, WB)
- Support for R-type, I-type, and J-type MIPS instructions
- Data hazard detection and handling
- Branch prediction and control hazard handling
- Memory and register file simulation
- Detailed cycle-by-cycle execution logging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/superscalar-mips-simulator.git
cd superscalar-mips-simulator
```

2. Ensure you have Python 3.7+ installed
3. Install dependencies (if any):
```bash
pip install -r requirements.txt
```

## Usage

Run the simulator using the main script:

```bash
python main.py
```

The simulator will execute the sample program defined in `main.py` and display the pipeline stages for each clock cycle.

Example output:
```
====== Superscalar Pipeline Simulation Started =====
---- Cycle 1 ----
IF: 0x34020000, 0x2014000a | ID: NOP, NOP | EX: NOP, NOP | MEM: NOP, NOP | WB: NOP, NOP | NO STALL
Clock Cycle: 1

---- Cycle 2 ----
IF: 0x383f0001, 0x30050000 | ID: 0x34020000, 0x2014000a | EX: NOP, NOP | MEM: NOP, NOP | WB: NOP, NOP | NO STALL
Clock Cycle: 2
...
```

## File Structure

```
superscalar-mips-simulator/
├── mips_pipeline/
│   ├── __init__.py
│   ├── ComprehensivePipelineProcessor.py
│   ├── InstructionDecoder.py
│   ├── PipelineStage.py
│   └── enums/
│       └── ProcessorSignals.py
├── main.py
└── README.md
```

## Implementation Details

The simulator implements the following key components:

- **Pipeline Stages**: IF (Instruction Fetch), ID (Instruction Decode), EX (Execute), MEM (Memory Access), and WB (Write Back)
- **Hazard Detection**: Detects and handles data hazards through stalling
- **Superscalar Execution**: Processes multiple instructions per cycle
- **Memory System**: Simulates main memory and register file
- **MIPS Instructions**: Supports major MIPS instruction types including arithmetic, logical, memory, and control instructions

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

Please ensure your code follows the existing style and includes appropriate tests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

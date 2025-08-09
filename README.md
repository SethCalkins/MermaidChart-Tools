# MermaidChart-Tools

A comprehensive parser and toolkit for analyzing Mermaid diagrams, with perfect connection counting and linkStyle mapping.

## Features

- **Accurate Connection Parsing**: Counts connections exactly like Mermaid does internally
- **Compound Connection Expansion**: Properly handles `&` expansions (e.g., `A --> B & C & D` becomes 3 connections)
- **Complete Arrow Type Support**: All Mermaid arrow types including labeled arrows
- **Perfect linkStyle Mapping**: Connection indices align perfectly with linkStyle numbers
- **Color and Animation Analysis**: Extracts colors and animation metadata

## Supported Arrow Types

### Basic Arrows
- `-->` - solid arrow
- `==>` - thick arrow
- `-.->` - dotted arrow
- `<-->` - bidirectional solid
- `<==` - bidirectional thick
- `---` - thick line, no arrow

### Special Endpoints  
- `--x` - solid line with x ending
- `x--x` - x on both ends
- `--o` - solid line with circle ending
- `o--o` - circles on both ends
- `x-->` - x start, arrow end
- `o-->` - circle start, arrow end

### Labeled Arrows
- `-- text -->` - labeled arrow
- `-- text ---` - labeled thick line
- `<-- text -->` - labeled bidirectional
- `x-- text --x` - labeled x on both ends
- `o-- text --o` - labeled circles on both ends
- `-. text .->` - labeled dotted arrow
- `== text ==>` - labeled thick arrow

### Special Patterns
- `-- <br> -->` - arrow with line break
- `<-- <br> -->` - bidirectional with line break

## Usage

```bash
python3 mermaid_parser.py diagram.mmd
```

### Output Format

```
Found 157 actual connections and 145 linkStyles
linkStyle range: 0-144

[0] iOS == HTTPS requests ==> FastAPI | color=#D50000 | animation=none
[1] iOS -- User input --> iOSAuth | color=#D50000 | animation=none
[142] LivingPlanService == Trace AI operations ==> Logfire | color=#AA00FF | animation=none
```

## Key Features

### Compound Connection Handling
When Mermaid encounters connections with multiple targets using `&`, it creates individual connections:

```mermaid
A --> B & C & D
```
Creates 3 connections:
- Connection 0: A → B  
- Connection 1: A → C
- Connection 2: A → D

### Perfect Index Alignment
The parser ensures connection indices match linkStyle numbers exactly:
- Connection at index 142 = linkStyle 142
- No gaps or misalignment

### Comprehensive Analysis
- **Connection count**: Total connections found vs linkStyles defined
- **Color mapping**: Extracts stroke colors from linkStyle definitions  
- **Animation detection**: Identifies connection animations
- **Missing linkStyles**: Reports unused linkStyle definitions

## Example Output Analysis

```
Found 157 actual connections and 145 linkStyles
```

This indicates:
- 157 actual connections exist in the diagram
- 145 linkStyle definitions (some connections may not have styles)
- Perfect parsing with compound expansion handled correctly

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/MermaidChart-Tools.git
cd MermaidChart-Tools
```

2. Run the parser:
```bash
python3 mermaid_parser.py your_diagram.mmd
```

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

## License

MIT License - see LICENSE file for details.
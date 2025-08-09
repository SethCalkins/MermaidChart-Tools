#!/usr/bin/env python3
import re
import sys
from collections import defaultdict

if len(sys.argv) < 2:
    print("Usage: python3 mermaid_parser.py <diagram_file>")
    sys.exit(1)

with open(sys.argv[1], encoding="utf-8") as f:
    mermaid_code = f.read()

# --- Extract connections exactly as Mermaid counts them ---
def extract_mermaid_connections(content):
    """Extract all connections exactly as Mermaid counts them, expanding compound connections"""
    connections = []
    
    # Comprehensive skip patterns for non-connection lines
    skip_patterns = [
        'linkStyle', 'classDef', 'class ', 'style ', 'subgraph', 'end',
        '---', 'config:', 'theme:', 'look:', 'layout:', 'flowchart',
        ':::',  # Class assignments
    ]
    
    # All possible arrow patterns Mermaid recognizes (order matters - check more specific first)
    arrow_patterns = [
        '<-- <br> -->',  # bidirectional with line break
        'x-- text --x',  # labeled x on both ends (pattern)
        'o-- text --o',  # labeled circles on both ends (pattern)
        '-- text ---',   # labeled thick line pattern
        '-- text -->',   # labeled arrow pattern
        '<-- text -->',  # labeled bidirectional pattern
        '-- text --x',   # labeled line with x ending
        '-- text --o',   # labeled line with circle ending
        '-. text .->',   # labeled dotted arrow pattern
        '== text ==>',   # labeled thick arrow pattern
        'x--x',         # x on both ends
        'o--o',         # circles on both ends
        '-.->',         # dotted arrow
        '.->',          # dotted arrow variant
        '--x',          # solid line with x ending
        '--o',          # solid line with circle ending
        'x-->',         # x start, arrow end
        'o-->',         # circle start, arrow end
        '<-->',         # bidirectional solid
        '<==',          # bidirectional thick
        '==>',          # thick arrow
        '-->',          # solid arrow
        '<--',          # reverse solid
        '---',          # thick line, no arrow
        '==',           # thick line (no arrow)
        # Pattern with line breaks (less specific, check later)
        '-- <br> -->',  # arrow with line break
    ]
    
    # Process line by line to maintain exact order
    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        original_line = line
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('%'):
            continue
            
        # Skip non-connection lines
        if any(line.startswith(pattern) for pattern in skip_patterns):
            continue
            
        # Check if line contains any arrow pattern
        found_arrow = None
        split_parts = None
        
        # Only try regex patterns for labeled arrows if line doesn't contain compound connections (&)
        if '&' not in line:
            labeled_patterns = [
                (r'(.*?)\s*<--\s+[^-]+\s+-->\s*(.*)', '<-- label -->'),
                (r'(.*?)\s*x--\s+[^-]+\s+--x\s*(.*)', 'x-- label --x'),
                (r'(.*?)\s*o--\s+[^-]+\s+--o\s*(.*)', 'o-- label --o'),
                (r'(.*?)\s*--\s+[^-]+\s+---\s*(.*)', '-- label ---'),
                (r'(.*?)\s*--\s+[^-]+\s+-->\s*(.*)', '-- label -->'),
                (r'(.*?)\s*--\s+[^-]+\s+--x\s*(.*)', '-- label --x'),
                (r'(.*?)\s*--\s+[^-]+\s+--o\s*(.*)', '-- label --o'),
                (r'(.*?)\s*-\.\s+[^-]+\s+\.->\s*(.*)', '-. label .->'),
                (r'(.*?)\s*==\s+[^=]+\s+==>\s*(.*)', '== label ==>'),
            ]
            
            for pattern, arrow_desc in labeled_patterns:
                match = re.match(pattern, line)
                if match:
                    split_parts = [match.group(1).strip(), match.group(2).strip()]
                    found_arrow = arrow_desc
                    break
        
        # If no labeled pattern matched, try literal arrow patterns
        if not found_arrow:
            for arrow in arrow_patterns:
                if arrow in line:
                    found_arrow = arrow
                    split_parts = line.split(arrow, 1)
                    break
                
        if not found_arrow or not split_parts or len(split_parts) != 2:
            continue
            
        parts = split_parts
            
        source_part = parts[0].strip()
        target_part = parts[1].strip()
        
        # Skip if source or target is empty
        if not source_part or not target_part:
            continue
        
        # Check for compound connections (& or &amp;)
        if '&' in target_part:
            # Split by both & and &amp; (HTML encoded)
            targets = re.split(r'\s*(?:&amp;|&)\s*', target_part)
            targets = [t.strip() for t in targets if t.strip()]
            
            # Create individual connection for each target
            for target in targets:
                individual_connection = f"{source_part} {found_arrow} {target}"
                connections.append(individual_connection)
        else:
            # Single connection
            connections.append(line)
    
    return connections

edges = extract_mermaid_connections(mermaid_code)

# --- Extract linkStyle rules ---
linkstyle_pattern = re.compile(
    r'^\s*linkStyle\s+(\d+)\s+(.+)$',
    re.MULTILINE
)

link_styles = {}
for match in re.finditer(linkstyle_pattern, mermaid_code):
    idx = int(match.group(1))
    style_str = match.group(2).strip()
    props = {}
    for prop in style_str.split(","):
        if ":" in prop:
            k, v = prop.split(":", 1)
            props[k.strip()] = v.strip()
    link_styles[idx] = props

# --- Extract animation metadata ---
animation_pattern = re.compile(
    r'^(L_[^\s@]+)@\{\s*animation:\s*([a-z]+)\s*\}',
    re.MULTILINE
)

animations = {}
for match in re.finditer(animation_pattern, mermaid_code):
    edge_id = match.group(1).strip()
    speed = match.group(2).strip()
    animations[edge_id] = speed

# --- Combine data ---
edge_data = []
for idx, edge in enumerate(edges):
    data = {
        "index": idx,
        "edge": edge,
        "style": link_styles.get(idx, {}),
        "animation": None
    }
    # Try to match ID from edge if it has one
    id_match = re.search(r'(L_[^@\s]+)', edge)
    if id_match and id_match.group(1) in animations:
        data["animation"] = animations[id_match.group(1)]
    edge_data.append(data)

# --- Print connection analysis ---
linkstyle_indices = list(link_styles.keys())
print(f"Found {len(edges)} actual connections and {len(linkstyle_indices)} linkStyles")
print(f"linkStyle range: 0-{max(linkstyle_indices) if linkstyle_indices else 0}")
print()

# --- Print all edges with color, style, animation ---
for e in edge_data:
    color = e["style"].get("stroke", "default")
    anim = e["animation"] or "none"
    print(f"[{e['index']}] {e['edge']} | color={color} | animation={anim}")

# --- Show which linkStyles don't have corresponding connections ---
if len(linkstyle_indices) > len(edges):
    print(f"\nWarning: {len(linkstyle_indices) - len(edges)} linkStyles don't have corresponding connections:")
    missing_connections = [idx for idx in sorted(linkstyle_indices) if idx >= len(edges)]
    for idx in missing_connections[:10]:  # Show first 10
        print(f"  linkStyle {idx} => (No corresponding connection)")
    if len(missing_connections) > 10:
        print(f"  ... and {len(missing_connections) - 10} more")
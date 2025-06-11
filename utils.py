#!/usr/bin/env python3
"""
Frame System Utilities
======================

Helper functions and visualizations.
"""

from typing import List, Optional, Dict, Any
import json
from frame_system import Frame, fget


def frame_to_mermaid(frame_name: str, max_depth: int = 2) -> str:
    """
    Generate Mermaid diagram code for a frame.
    
    Args:
        frame_name: Name of the frame to visualize
        max_depth: Maximum depth for inheritance chains
    
    Returns:
        Mermaid diagram code as string
    """
    frame = Frame.get_frame(frame_name)
    if not frame:
        return f"graph LR\n    {frame_name}[Frame not found]"
    
    lines = ["graph TD"]
    lines.append(f'    {frame_name}["{frame_name}<br/>Frame"]')
    lines.append(f'    style {frame_name} fill:#f9f,stroke:#333,stroke-width:4px')
    
    # Add slots
    for slot_name, slot_data in frame.slots.items():
        slot_id = f"{frame_name}_{slot_name}"
        slot_label = f"{slot_name}"
        
        # Add value if present
        value = slot_data.get('value', slot_data.get('default'))
        if value is not None and not callable(value):
            slot_label += f"<br/>= {value}"
        
        lines.append(f'    {slot_id}["{slot_label}"]')
        lines.append(f'    {frame_name} --> {slot_id}')
        
        # Add important facets
        for facet in ['units', 'min', 'max']:
            if facet in slot_data:
                facet_id = f"{slot_id}_{facet}"
                lines.append(f'    {facet_id}["{facet}: {slot_data[facet]}"]')
                lines.append(f'    {slot_id} --> {facet_id}')
                lines.append(f'    style {facet_id} fill:#ffd,stroke:#333,stroke-width:1px')
    
    # Check for prototype/inheritance
    if 'prototype' in frame.slots or 'instance_of' in frame.slots:
        parent = frame.get('prototype') or frame.get('instance_of')
        if parent and max_depth > 1:
            lines.append(f'    {parent}["{parent}<br/>Parent Frame"]')
            lines.append(f'    {parent} -.-> {frame_name}')
            lines.append(f'    style {parent} fill:#9ff,stroke:#333,stroke-width:2px')
    
    return '\n'.join(lines)


def frames_to_dot(frames: Optional[List[str]] = None) -> str:
    """
    Generate Graphviz DOT format for frame visualization.
    
    Args:
        frames: List of frame names to include (None = all frames)
    
    Returns:
        DOT format string
    """
    frames = frames or Frame.all_frames()
    
    lines = ['digraph FrameSystem {']
    lines.append('    rankdir=LR;')
    lines.append('    node [shape=record];')
    
    for frame_name in frames:
        frame = Frame.get_frame(frame_name)
        if not frame:
            continue
        
        # Build node label
        slots_info = []
        for slot_name, slot_data in frame.slots.items():
            value = slot_data.get('value', slot_data.get('default', '?'))
            if not callable(value):
                slots_info.append(f"{slot_name}: {value}")
        
        label = f"{frame_name}|" + "\\n".join(slots_info[:5])  # Limit slots shown
        if len(slots_info) > 5:
            label += f"\\n... +{len(slots_info)-5} more"
        
        lines.append(f'    "{frame_name}" [label="{label}"];')
        
        # Add inheritance edges
        for slot in ['prototype', 'instance_of']:
            if slot in frame.slots:
                parent = frame.get(slot)
                if parent:
                    lines.append(f'    "{parent}" -> "{frame_name}" [style=dashed];')
    
    lines.append('}')
    return '\n'.join(lines)


def find_frames_with_slot(slot_name: str, facet: Optional[str] = None) -> List[str]:
    """
    Find all frames that have a specific slot.
    
    Args:
        slot_name: Name of the slot to search for
        facet: Optional specific facet to check for
    
    Returns:
        List of frame names
    """
    results = []
    
    for frame_name in Frame.all_frames():
        frame = Frame.get_frame(frame_name)
        if frame and slot_name in frame.slots:
            if facet is None or facet in frame.slots[slot_name]:
                results.append(frame_name)
    
    return results


def frame_stats() -> Dict[str, Any]:
    """Get statistics about the frame system."""
    total_frames = len(Frame.all_frames())
    total_slots = 0
    total_facets = 0
    facet_types = {}
    
    for frame_name in Frame.all_frames():
        frame = Frame.get_frame(frame_name)
        if frame:
            total_slots += len(frame.slots)
            for slot_data in frame.slots.values():
                total_facets += len(slot_data)
                for facet_name in slot_data:
                    facet_types[facet_name] = facet_types.get(facet_name, 0) + 1
    
    return {
        'total_frames': total_frames,
        'total_slots': total_slots,
        'total_facets': total_facets,
        'avg_slots_per_frame': total_slots / total_frames if total_frames > 0 else 0,
        'facet_types': facet_types
    }


def export_frames_to_csv(filename: str, frames: Optional[List[str]] = None) -> None:
    """Export frames to CSV format."""
    import csv
    
    frames = frames or Frame.all_frames()
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Frame', 'Slot', 'Facet', 'Value'])
        
        for frame_name in sorted(frames):
            frame = Frame.get_frame(frame_name)
            if frame:
                for slot_name, slot_data in sorted(frame.slots.items()):
                    for facet, value in sorted(slot_data.items()):
                        if not callable(value):
                            writer.writerow([frame_name, slot_name, facet, str(value)])


def validate_frame_schema(frame_name: str, schema: Dict[str, Dict[str, Any]]) -> List[str]:
    """
    Validate a frame against a schema.
    
    Args:
        frame_name: Name of frame to validate
        schema: Dict of slot_name -> {required_facets, types, constraints}
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    frame = Frame.get_frame(frame_name)
    
    if not frame:
        return [f"Frame '{frame_name}' not found"]
    
    for slot_name, requirements in schema.items():
        if 'required' in requirements and requirements['required']:
            if slot_name not in frame.slots:
                errors.append(f"Missing required slot: {slot_name}")
                continue
        
        if slot_name in frame.slots:
            slot_data = frame.slots[slot_name]
            
            # Check required facets
            for facet in requirements.get('required_facets', []):
                if facet not in slot_data:
                    errors.append(f"Slot '{slot_name}' missing required facet: {facet}")
            
            # Check value type
            if 'type' in requirements:
                value = slot_data.get('value')
                expected_type = requirements['type']
                if value is not None and not isinstance(value, expected_type):
                    errors.append(f"Slot '{slot_name}' value has wrong type: "
                                f"expected {expected_type.__name__}, "
                                f"got {type(value).__name__}")
    
    return errors


if __name__ == "__main__":
    # Demo utilities
    from examples import example_basic, example_inheritance
    
    print("Frame System Utilities Demo")
    print("=" * 40)
    
    # Create some frames
    example_basic()
    example_inheritance()
    
    # Show statistics
    stats = frame_stats()
    print("\nFrame System Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Find frames with specific slots
    print("\nFrames with 'color' slot:")
    for frame_name in find_frames_with_slot('color'):
        print(f"  - {frame_name}: {fget(frame_name, 'color')}")
    
    # Generate Mermaid diagram
    print("\nMermaid diagram for 'robot':")
    print(frame_to_mermaid('robot'))
    
    # Export to CSV
    export_frames_to_csv('frames_export.csv')
    print("\nExported frames to frames_export.csv")

#!/usr/bin/env python3
"""
Frame-Based Knowledge Representation System
==========================================

A modern implementation of frame-based KR inspired by FRL.
Compatible with Python 3.6+ on all platforms.
"""

import json
from typing import Any, Dict, Optional, Callable, List


class Frame:
    """A frame is a knowledge structure with slots and facets."""
    
    _frames: Dict[str, 'Frame'] = {}  # Global frame registry
    
    def __init__(self, name: str):
        """Create a new frame with the given name."""
        self.name = name
        self.slots: Dict[str, Dict[str, Any]] = {}
        Frame._frames[name] = self
    
    def add_slot(self, slot_name: str, **facets) -> 'Frame':
        """Add or update a slot with multiple facets."""
        if slot_name not in self.slots:
            self.slots[slot_name] = {}
        self.slots[slot_name].update(facets)
        return self
    
    def get(self, slot_name: str, facet: str = 'value') -> Any:
        """
        Get a facet value from a slot.
        
        Special handling for:
        - 'value' with 'if_needed': Computes value on demand
        - Missing 'value': Falls back to 'default'
        """
        if slot_name not in self.slots:
            return None
        
        slot = self.slots[slot_name]
        
        # Handle computed values
        if facet == 'value' and 'value' not in slot and 'if_needed' in slot:
            computed = slot['if_needed'](self)
            slot['value'] = computed  # Cache the result
            return computed
        
        # Return requested facet or fall back to default
        result = slot.get(facet)
        if result is None and facet == 'value':
            result = slot.get('default')
        
        return result
    
    def put(self, slot_name: str, value: Any, facet: str = 'value') -> 'Frame':
        """
        Set a facet value, triggering demons if present.
        
        Demons triggered:
        - 'if_added': When value facet is modified
        - 'if_removed': When value is set to None
        """
        if slot_name not in self.slots:
            self.slots[slot_name] = {}
        
        old_value = self.slots[slot_name].get(facet)
        self.slots[slot_name][facet] = value
        
        # Trigger demons
        if facet == 'value':
            if value is not None and 'if_added' in self.slots[slot_name]:
                self.slots[slot_name]['if_added'](self, old_value, value)
            elif value is None and 'if_removed' in self.slots[slot_name]:
                self.slots[slot_name]['if_removed'](self, old_value)
        
        return self
    
    def remove_slot(self, slot_name: str) -> bool:
        """Remove a slot from the frame."""
        if slot_name in self.slots:
            del self.slots[slot_name]
            return True
        return False
    
    def describe(self, verbose: bool = False) -> None:
        """Pretty print the frame."""
        print(f"\nFrame: {self.name}")
        print("=" * (len(self.name) + 7))
        
        for slot_name, slot_data in self.slots.items():
            print(f"\n  {slot_name}:")
            for facet, value in sorted(slot_data.items()):
                if callable(value):
                    if verbose:
                        print(f"    {facet}: <function {value.__name__}>")
                    else:
                        print(f"    {facet}: <function>")
                else:
                    print(f"    {facet}: {value}")
    
    def to_dict(self, include_functions: bool = False) -> Dict[str, Any]:
        """Convert frame to dictionary (for serialization)."""
        data = {'name': self.name, 'slots': {}}
        
        for slot_name, slot_data in self.slots.items():
            data['slots'][slot_name] = {}
            for facet, value in slot_data.items():
                if not callable(value) or include_functions:
                    data['slots'][slot_name][facet] = (
                        f"<function {value.__name__}>" if callable(value) else value
                    )
        
        return data
    
    @classmethod
    def get_frame(cls, name: str) -> Optional['Frame']:
        """Retrieve a frame by name."""
        return cls._frames.get(name)
    
    @classmethod
    def all_frames(cls) -> List[str]:
        """Get names of all frames."""
        return list(cls._frames.keys())
    
    @classmethod
    def clear_all(cls) -> None:
        """Clear all frames from the registry."""
        cls._frames.clear()
    
    def __repr__(self) -> str:
        return f"Frame('{self.name}')"


# Convenience functions for FRL-style syntax
def fassert(name: str, **slots) -> Frame:
    """
    Create a frame with slots in FRL style.
    
    Example:
        robot = fassert('robot',
            color={'value': 'red'},
            height={'value': 4.5, 'units': 'feet'}
        )
    """
    frame = Frame(name)
    for slot_name, facets in slots.items():
        if isinstance(facets, dict):
            frame.add_slot(slot_name, **facets)
        else:
            # If not a dict, treat as a simple value
            frame.add_slot(slot_name, value=facets)
    return frame


def fget(frame_name: str, slot_name: str, facet: str = 'value') -> Any:
    """Get a value from a frame."""
    frame = Frame.get_frame(frame_name)
    return frame.get(slot_name, facet) if frame else None


def fput(frame_name: str, slot_name: str, value: Any, facet: str = 'value') -> Any:
    """Put a value in a frame."""
    frame = Frame.get_frame(frame_name)
    if frame:
        frame.put(slot_name, value, facet)
    return value


def fdel(frame_name: str) -> bool:
    """Delete a frame."""
    if frame_name in Frame._frames:
        del Frame._frames[frame_name]
        return True
    return False


# Persistence functions
def save_frames(filename: str, frames: Optional[List[str]] = None) -> None:
    """Save frames to JSON file."""
    data = {}
    frames_to_save = frames or Frame.all_frames()
    
    for name in frames_to_save:
        frame = Frame.get_frame(name)
        if frame:
            data[name] = frame.to_dict()
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved {len(data)} frames to {filename}")


def load_frames(filename: str) -> int:
    """Load frames from JSON file."""
    with open(filename, 'r') as f:
        data = json.load(f)
    
    count = 0
    for name, frame_data in data.items():
        frame = Frame(name)
        for slot_name, facets in frame_data.get('slots', {}).items():
            # Skip function placeholders
            clean_facets = {
                k: v for k, v in facets.items()
                if not (isinstance(v, str) and v.startswith('<function'))
            }
            frame.add_slot(slot_name, **clean_facets)
        count += 1
    
    print(f"Loaded {count} frames from {filename}")
    return count


if __name__ == "__main__":
    print("Frame System v1.0 - Ready!")
    print("Try: help(Frame) or help(fassert)")

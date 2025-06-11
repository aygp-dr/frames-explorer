#!/usr/bin/env python3
"""
Frame System Test Suite
=======================

Run with: python3 test_frames.py
Or with pytest: pytest test_frames.py -v
"""

import sys
import os
import tempfile
import json
from typing import List

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from frame_system import Frame, fassert, fget, fput, fdel, save_frames, load_frames


class TestResults:
    """Simple test result collector."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def assert_equal(self, actual, expected, message=""):
        if actual == expected:
            self.passed += 1
            print(".", end="", flush=True)
        else:
            self.failed += 1
            print("F", end="", flush=True)
            self.errors.append(f"{message}: expected {expected}, got {actual}")
    
    def assert_true(self, condition, message=""):
        self.assert_equal(bool(condition), True, message)
    
    def assert_false(self, condition, message=""):
        self.assert_equal(bool(condition), False, message)
    
    def report(self):
        print(f"\n\nTest Results: {self.passed} passed, {self.failed} failed")
        if self.errors:
            print("\nFailures:")
            for error in self.errors:
                print(f"  - {error}")
        return self.failed == 0


def test_basic_operations(t: TestResults):
    """Test basic frame operations."""
    print("\nTesting basic operations", end="")
    
    # Create frame
    robot = fassert('test-robot', 
        color={'value': 'blue'},
        height={'value': 1.5}
    )
    
    t.assert_equal(fget('test-robot', 'color'), 'blue', "Basic fget")
    t.assert_equal(fget('test-robot', 'height'), 1.5, "Numeric value")
    
    # Update value
    fput('test-robot', 'color', 'red')
    t.assert_equal(fget('test-robot', 'color'), 'red', "Value update")
    
    # Non-existent frame/slot
    t.assert_equal(fget('no-such-frame', 'anything'), None, "Missing frame")
    t.assert_equal(fget('test-robot', 'no-such-slot'), None, "Missing slot")
    
    # Frame registry
    t.assert_true('test-robot' in Frame.all_frames(), "Frame in registry")
    
    # Delete frame
    fdel('test-robot')
    t.assert_false('test-robot' in Frame.all_frames(), "Frame deleted")


def test_facets(t: TestResults):
    """Test facet system."""
    print("\nTesting facets", end="")
    
    sensor = fassert('sensor',
        temperature={
            'value': 22.5,
            'units': 'celsius',
            'min': -50,
            'max': 100,
            'default': 20
        }
    )
    
    t.assert_equal(fget('sensor', 'temperature'), 22.5, "Value facet")
    t.assert_equal(fget('sensor', 'temperature', 'units'), 'celsius', "Units facet")
    t.assert_equal(fget('sensor', 'temperature', 'min'), -50, "Min facet")
    
    # Test default fallback
    sensor.slots['temperature'].pop('value')  # Remove value
    t.assert_equal(fget('sensor', 'temperature'), 20, "Default fallback")


def test_computed_values(t: TestResults):
    """Test if_needed computations."""
    print("\nTesting computed values", end="")
    
    compute_count = 0
    
    def compute_area(frame):
        nonlocal compute_count
        compute_count += 1
        width = frame.get('width', 'value')
        height = frame.get('height', 'value')
        return width * height if width and height else None
    
    rect = fassert('rectangle',
        width={'value': 10},
        height={'value': 5},
        area={'if_needed': compute_area}
    )
    
    # First access computes
    t.assert_equal(fget('rectangle', 'area'), 50, "Computed area")
    t.assert_equal(compute_count, 1, "Computed once")
    
    # Second access uses cached value
    t.assert_equal(fget('rectangle', 'area'), 50, "Cached area")
    t.assert_equal(compute_count, 1, "Still computed once")


def test_demons(t: TestResults):
    """Test active values (demons)."""
    print("\nTesting demons", end="")
    
    changes = []
    
    def track_changes(frame, old_val, new_val):
        changes.append((frame.name, old_val, new_val))
    
    def track_removal(frame, old_val):
        changes.append((frame.name, old_val, None))
    
    device = fassert('device',
        status={
            'value': 'online',
            'if_added': track_changes,
            'if_removed': track_removal
        }
    )
    
    # Test if_added
    fput('device', 'status', 'offline')
    t.assert_equal(len(changes), 1, "Change tracked")
    t.assert_equal(changes[0], ('device', 'online', 'offline'), "Correct change")
    
    # Test if_removed
    fput('device', 'status', None)
    t.assert_equal(len(changes), 2, "Removal tracked")
    t.assert_equal(changes[1][2], None, "Removed value")


def test_persistence(t: TestResults):
    """Test save/load functionality."""
    print("\nTesting persistence", end="")
    
    # Create frames
    config = fassert('config',
        app_name={'value': 'TestApp'},
        version={'value': 1.5},
        features={'value': ['auth', 'api', 'ui']}
    )
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        save_frames(temp_file)
        
        # Verify file contents
        with open(temp_file, 'r') as f:
            data = json.load(f)
        
        t.assert_true('config' in data, "Frame saved")
        t.assert_equal(
            data['config']['slots']['app_name']['value'], 
            'TestApp', 
            "String saved correctly"
        )
        
        # Clear and reload
        Frame.clear_all()
        t.assert_equal(len(Frame.all_frames()), 0, "Frames cleared")
        
        load_frames(temp_file)
        t.assert_equal(fget('config', 'app_name'), 'TestApp', "Frame loaded")
        t.assert_equal(fget('config', 'features'), ['auth', 'api', 'ui'], "List loaded")
        
    finally:
        os.unlink(temp_file)


def test_complex_scenario(t: TestResults):
    """Test a complex real-world scenario."""
    print("\nTesting complex scenario", end="")
    
    # Smart home system
    alerts = []
    
    def temperature_demon(frame, old_val, new_val):
        if new_val > 30:
            alerts.append(f"High temp in {frame.name}: {new_val}°C")
    
    def compute_avg_temp(frame):
        total = 0
        count = 0
        for room_name in ['living-room', 'bedroom', 'kitchen']:
            temp = fget(room_name, 'temperature')
            if temp is not None:
                total += temp
                count += 1
        return total / count if count > 0 else None
    
    # Create rooms
    for room, temp in [('living-room', 22), ('bedroom', 20), ('kitchen', 25)]:
        fassert(room,
            temperature={
                'value': temp,
                'if_added': temperature_demon
            },
            type={'value': 'room'}
        )
    
    # Create house
    house = fassert('smart-house',
        average_temp={'if_needed': compute_avg_temp},
        rooms={'value': ['living-room', 'bedroom', 'kitchen']}
    )
    
    # Test average computation
    avg = fget('smart-house', 'average_temp')
    t.assert_true(abs(avg - 22.333) < 0.01, "Average temperature")
    
    # Trigger alert
    fput('kitchen', 'temperature', 35)
    t.assert_equal(len(alerts), 1, "Alert triggered")
    t.assert_true('High temp' in alerts[0], "Alert message")


def run_tests():
    """Run all tests."""
    t = TestResults()
    
    test_functions = [
        test_basic_operations,
        test_facets,
        test_computed_values,
        test_demons,
        test_persistence,
        test_complex_scenario
    ]
    
    print("Running Frame System Tests")
    print("=" * 40)
    
    for test_func in test_functions:
        Frame.clear_all()  # Fresh start for each test
        test_func(t)
    
    print("\n")
    return t.report()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Frame System Examples
====================

Demonstrations of frame-based knowledge representation.
"""

import time
import random
from frame_system import Frame, fassert, fget, fput, save_frames, load_frames


def example_basic():
    """Basic frame creation and access."""
    print("\n=== Basic Frame Example ===")
    
    # Create a robot frame
    robot = fassert('robot',
        type={'value': 'service-robot'},
        manufacturer={'value': 'Acme Robotics'},
        model={'value': 'ServoBot 3000'},
        height={'value': 1.5, 'units': 'meters'},
        weight={'value': 45, 'units': 'kg'},
        color={'value': 'silver', 'options': ['silver', 'white', 'black']},
        battery={'value': 85, 'units': 'percent', 'min': 0, 'max': 100}
    )
    
    robot.describe()
    
    # Access values
    print(f"\nRobot height: {fget('robot', 'height')} {fget('robot', 'height', 'units')}")
    print(f"Battery level: {fget('robot', 'battery')}%")


def example_computed_values():
    """Demonstrate computed values with if_needed."""
    print("\n=== Computed Values Example ===")
    
    # Temperature sensor with computed Fahrenheit
    def celsius_to_fahrenheit(frame):
        celsius = frame.get('celsius', 'value')
        return celsius * 9/5 + 32 if celsius is not None else None
    
    sensor = fassert('temp-sensor',
        location={'value': 'living-room'},
        celsius={'value': 22},
        fahrenheit={'if_needed': celsius_to_fahrenheit}
    )
    
    print(f"Temperature: {fget('temp-sensor', 'celsius')}°C")
    print(f"Temperature: {fget('temp-sensor', 'fahrenheit')}°F (computed)")
    
    # Update Celsius and get new Fahrenheit
    fput('temp-sensor', 'celsius', 30)
    # Clear cached Fahrenheit
    sensor.slots['fahrenheit'].pop('value', None)
    print(f"\nAfter update: {fget('temp-sensor', 'fahrenheit')}°F")


def example_demons():
    """Demonstrate active values (demons)."""
    print("\n=== Demons (Active Values) Example ===")
    
    # Alert system
    alerts = []
    
    def battery_monitor(frame, old_val, new_val):
        if new_val < 20:
            alert = f"⚠️  LOW BATTERY: {new_val}%"
            alerts.append(alert)
            print(alert)
        elif old_val and old_val < 20 and new_val >= 20:
            alert = "✅ Battery level restored"
            alerts.append(alert)
            print(alert)
    
    device = fassert('laptop',
        model={'value': 'ThinkPad X1'},
        battery={
            'value': 100,
            'units': 'percent',
            'if_added': battery_monitor
        },
        alerts={'if_needed': lambda f: alerts.copy()}
    )
    
    # Simulate battery drain
    print("Simulating battery drain...")
    for level in [80, 50, 19, 15, 10, 25, 90]:
        fput('laptop', 'battery', level)
        time.sleep(0.1)  # Small delay for demo
    
    print(f"\nAll alerts: {fget('laptop', 'alerts')}")


def example_inheritance():
    """Demonstrate prototype-based inheritance."""
    print("\n=== Inheritance Example ===")
    
    # Robot class (prototype)
    robot_class = fassert('robot-prototype',
        category={'value': 'prototype'},
        default_height={'value': 1.5},
        default_weight={'value': 50},
        default_sensors={'value': ['camera', 'lidar', 'ultrasonic']},
        capabilities={'value': ['navigation', 'object-recognition']}
    )
    
    # Helper for inheritance
    def inherit_from(parent_name, slot, facet='value'):
        def getter(frame):
            parent_value = fget(parent_name, f"default_{slot}", facet)
            return parent_value
        return getter
    
    # Create robot instances
    rosie = fassert('rosie',
        prototype={'value': 'robot-prototype'},
        name={'value': 'Rosie'},
        height={'if_needed': inherit_from('robot-prototype', 'height')},
        weight={'value': 45},  # Override
        color={'value': 'red'},
        sensors={'if_needed': inherit_from('robot-prototype', 'sensors')}
    )
    
    c3po = fassert('c3po', 
        prototype={'value': 'robot-prototype'},
        name={'value': 'C-3PO'},
        height={'value': 1.7},  # Override
        weight={'if_needed': inherit_from('robot-prototype', 'weight')},
        color={'value': 'gold'},
        languages={'value': 6000000}
    )
    
    print("Rosie:")
    print(f"  Height: {fget('rosie', 'height')} (inherited)")
    print(f"  Weight: {fget('rosie', 'weight')} (overridden)")
    print(f"  Sensors: {fget('rosie', 'sensors')} (inherited)")
    
    print("\nC-3PO:")
    print(f"  Height: {fget('c3po', 'height')} (overridden)")
    print(f"  Weight: {fget('c3po', 'weight')} (inherited)")
    print(f"  Languages: {fget('c3po', 'languages')} (unique)")


def example_iot_system():
    """Real-world example: IoT device management."""
    print("\n=== IoT System Example ===")
    
    # Device monitoring system
    def check_device_health(frame):
        battery = frame.get('battery', 'value')
        temp = frame.get('temperature', 'value')
        last_seen = frame.get('last_seen', 'value')
        
        if battery and battery < 20:
            return 'critical'
        elif temp and temp > 80:
            return 'warning'
        elif last_seen and (time.time() - last_seen) > 300:
            return 'offline'
        else:
            return 'healthy'
    
    def update_last_seen(frame, old_val, new_val):
        frame.put('last_seen', time.time())
    
    # Create IoT devices
    devices = []
    for i in range(3):
        device = fassert(f'iot-{i}',
            device_type={'value': 'environmental-sensor'},
            location={'value': f'room-{i+1}'},
            battery={'value': random.randint(10, 100), 'units': '%'},
            temperature={'value': random.randint(18, 30), 'units': '°C'},
            humidity={'value': random.randint(30, 70), 'units': '%'},
            last_seen={'value': time.time()},
            health={'if_needed': check_device_health},
            data={
                'value': [],
                'if_added': update_last_seen
            }
        )
        devices.append(f'iot-{i}')
    
    # Simulate some issues
    fput('iot-0', 'battery', 15)  # Low battery
    fput('iot-1', 'temperature', 85)  # High temp
    
    # Status report
    print("IoT Device Status:")
    print("-" * 40)
    for device_name in devices:
        health = fget(device_name, 'health')
        battery = fget(device_name, 'battery')
        temp = fget(device_name, 'temperature')
        location = fget(device_name, 'location')
        
        status_icon = {
            'healthy': '✅',
            'warning': '⚠️ ',
            'critical': '🔴',
            'offline': '📴'
        }.get(health, '❓')
        
        print(f"{status_icon} {device_name} ({location}): "
              f"Battery={battery}%, Temp={temp}°C, Status={health}")


def example_persistence():
    """Demonstrate saving and loading frames."""
    print("\n=== Persistence Example ===")
    
    # Create some frames
    config = fassert('app-config',
        name={'value': 'FrameSystem'},
        version={'value': '1.0'},
        debug={'value': True},
        max_frames={'value': 1000}
    )
    
    user = fassert('current-user',
        username={'value': 'aygp-dr'},
        role={'value': 'admin'},
        preferences={
            'value': {
                'theme': 'dark',
                'notifications': True
            }
        }
    )
    
    print("Original frames:")
    print(f"  Config: {fget('app-config', 'name')} v{fget('app-config', 'version')}")
    print(f"  User: {fget('current-user', 'username')} ({fget('current-user', 'role')})")
    
    # Save frames
    save_frames('frames_backup.json')
    
    # Clear and reload
    Frame.clear_all()
    print(f"\nCleared all frames. Count: {len(Frame.all_frames())}")
    
    load_frames('frames_backup.json')
    print(f"\nAfter loading:")
    print(f"  Config: {fget('app-config', 'name')} v{fget('app-config', 'version')}")
    print(f"  User: {fget('current-user', 'username')} ({fget('current-user', 'role')})")


def run_all_examples():
    """Run all examples in sequence."""
    examples = [
        example_basic,
        example_computed_values,
        example_demons,
        example_inheritance,
        example_iot_system,
        example_persistence
    ]
    
    for example in examples:
        example()
        input("\nPress Enter for next example...")
        Frame.clear_all()  # Clean slate for next example


if __name__ == "__main__":
    print("Frame System Examples")
    print("=" * 50)
    print("\nAvailable examples:")
    print("1. example_basic() - Basic frame operations")
    print("2. example_computed_values() - Lazy computation")
    print("3. example_demons() - Active values")
    print("4. example_inheritance() - Prototype inheritance") 
    print("5. example_iot_system() - Real-world IoT scenario")
    print("6. example_persistence() - Save/load frames")
    print("7. run_all_examples() - Run all examples")
    print("\nRun any example function to see it in action!")

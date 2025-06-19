#!/usr/bin/env python3

import enum # Test the import hook

print("\n\n=== TESTING EXTERNAL HOT RELOAD PATCHING ===")

# Test classes and functions to be patched
class TestClass:
    def __init__(self):
        self.value = 42
        print(f"TestClass initialized with value: {self.value}")
    
    def get_value(self):
        return self.value

def test_function():
    return "Hello from test_function"

# Hot reload patching function
def patch_for_hot_reload(obj, obj_name="unknown"):
    """
    Patch an object's __getattribute__ for hot reload functionality.
    """
    original_getattribute = obj.__getattribute__
    
    def hot_reload_getattribute(self, name):
        print(f"HOT_RELOAD __getattribute__: {name}")
        # Check if class has changed (only for non-special attributes)
        if not name.startswith('_'):
            try:
                cls = self.__class__
                current_checksum = hash(str(cls.__dict__))
                if hasattr(cls, '_hot_reload_checksum') and current_checksum != cls._hot_reload_checksum:
                    print(f"HOT_RELOAD: Class {cls.__name__} has changed, migrating...")
                    # Here we would implement the migration logic
                    cls._hot_reload_checksum = current_checksum
                    if hasattr(cls, '_hot_reload_version'):
                        cls._hot_reload_version += 1
            except:
                pass  # Ignore errors during hot reload check
        
        # Get the original attribute
        return original_getattribute(self, name)
    
    # Replace __getattribute__ for this object
    obj.__getattribute__ = hot_reload_getattribute
    print(f"Patched {obj_name} for hot reload")

obj = TestClass()

print(f"Testing before patching: {obj.value}")
print(f"Testing before patching: {obj.get_value()}")

# Patch all test objects
print("\n=== PATCHING OBJECTS ===")
patch_for_hot_reload(TestClass, "TestClass")

# Create instance and test
print("\n=== TESTING PATCHED OBJECTS ===")

print(f"Created: {obj}")
print(f"Value: {obj.value}")
print(f"Method: {obj.get_value()}")

# Test attribute access (should trigger hot reload check)
print("\n=== TESTING ATTRIBUTE ACCESS ===")
print(f"Value again: {obj.value}")

print("\n=== TEST COMPLETE ===") 
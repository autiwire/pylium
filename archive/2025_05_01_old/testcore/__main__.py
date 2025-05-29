from . import TestCore

TestCore().testfunc()

print(f"TestCore.__module__: {TestCore.__module__}")
print(f"TestCore.__bases__: {TestCore.__bases__}")

print(f"TestCore.is_package(): {TestCore.is_package()}")

print(f"TestCore.is_module(): {TestCore.is_module()}")


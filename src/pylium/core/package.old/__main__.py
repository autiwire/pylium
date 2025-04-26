#from pylium.core.test1.__header__ import Test1

#print(f"Test1 class: {Test1}")

from pylium.core.package import Package

x = Package()
print(f"Created instance: {x}")
print(f"Instance type: {type(x)}")
print(f"Instance test result: {x.test()}")
print("END")



from pylium.core import Package

from .__init__ import Test1

obj = Test1()

print("--- Object ---")
print(obj)

print("--- Component ---")
print(Package.HeaderComponent.__info__())

print("--- Header ---")
print(Package.Header.__info__())

print("--- Test1 ---")
print(Test1.__info__())


# Test: test get_sibling_component
print("--- Test: get_sibling_component ---")
print(Test1.get_sibling_component(Package.Header))
print(Test1.get_sibling_component(Package.Impl))


# Test: create sqlite database from model Test1
print("--- Test: create sqlite database from model Test1 ---")
from sqlmodel import create_engine, SQLModel
engine = create_engine("sqlite:///test1.db", echo=True)
SQLModel.metadata.create_all(engine)



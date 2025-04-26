from pylium.core import Package

from .__init__ import Test1

obj = Test1()

print("--- Object ---")
print(obj)

print("--- Component ---")
print(Package.Component.__info__())

print("--- Header ---")
print(Package.Header.__info__())

print("--- Test1 ---")
print(Test1.__info__())

# Test: create sqlite database from model Test1

from sqlmodel import create_engine, SQLModel

engine = create_engine("sqlite:///test1.db", echo=True)

SQLModel.metadata.create_all(engine)



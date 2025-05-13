from . import Module

from fire import Fire

def main():
    print(Module("test"))

    for m in Module.list():
        print(m)


if __name__ == "__main__":
    main()
from . import Module

def main():
    print(Module("test"))

    for m in Module.list():
        print(m)

    print("cli")
    Module.cli()


if __name__ == "__main__":
    main()
    #Module.cli()
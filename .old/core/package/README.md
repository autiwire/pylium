Pylium package core library.
In Pylium everything is a package, and this is the core library that handles the package management.

Pylium uses PEP-420 to handle the package structure, as Pylium shall be a framework for applications and libraries development.
Pylium packages are located in the `src/pylium/` directory.
Pylium namespace is `pylium`.

*Package Structure*

Everything begins with src/pylium/core/package/ where the base classes for a Pylium package are defined.

- Package entry
    - __init__.py
    - __main__.py

- Header
    - _header.py            # Header file for the package
    - _config.py            # Configuration file for the package
    - _revision.py          # Revision file for the package
    - _todo.py              # Todo file for the package
    - _requirements.py      # Requirements file for the package
    - _tests.py             # Tests file for the package
    - _docs.py              # Docs file for the package

- Compact Header
    - _pylium.py            # Compact header file for the package, can contain all header components

- Implementation
    - _impl.py              # Implementation file for the package

*Subpackage Structure*

Another structure would be a subpackage, which consists of a header files and an implementation file.
E.g. in src/pylium/core/package/ create a subpackage called `subpackage`.

- Package entry
    - subpackage.py

- Header
    - subpackage_header.py
    - subpackage_config.py
    - subpackage_revision.py
    - subpackage_todo.py
    - subpackage_requirements.py
    - subpackage_tests.py
    - subpackage_docs.py

- Compact Header
    - subpackage_pylium.py  

- Implementation    
    - subpackage_impl.py

*Components*

Every header file contains a component of the package and the implementation file contains a component. 
Components are the building blocks of a Pylium package.
Their only job is to ensure consistency of header and implementation structuring.
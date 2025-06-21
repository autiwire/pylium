# Pylium Licensing Information

The Pylium Framework employs a granular licensing model where individual modules and classes
can specify their own licenses through their associated manifest objects.

Please refer to the `__manifest__` attribute within the source code of specific Pylium
components (modules, classes) for detailed licensing information applicable to that
particular part of the framework.

This approach allows for flexibility in licensing different parts of the Pylium
ecosystem. If a specific component does not explicitly state a license in its
manifest, it should be assumed to be under the default or overarching project
license, if one is separately defined for distribution purposes. However, the
primary source of truth for component licensing is its manifest.

## License Inheritance

Pylium's manifest system supports hierarchical licensing. When a new manifest is
created as a child of an existing manifest (e.g., using the `createChild`
method), it inherits the license of its parent by default.

This inheritance can be overridden by explicitly specifying a license for the
child manifest.

The root `__manifest__` of a project (often assigned to a `__project_manifest__`
variable in the project's main `__init__.py`) serves as the ultimate default
license for any component within that project that does not have an overriding
license specified in its own manifest or in an intermediary parent manifest.


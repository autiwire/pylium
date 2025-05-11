from abc import ABCMeta

from logging import getLogger
logger = getLogger(__name__)

# Define the metaclass
class _ModuleMeta(ABCMeta):
    def __str__(cls):
        # logger.debug(f"ModuleMeta __str__ for: {cls.__name__}")

        # This method is called when str(ClassName) is used.
        # It accesses class variables of cls.
        # Ensure these attributes are resolved before str(cls) is called outside of __init_subclass__.
        try:
            # Accessing them might trigger their resolution if accessed for the first time here
            # though __init_subclass__ should have handled it for defined subclasses.
            name = getattr(cls, 'name', cls.__name__) # Fallback to cls.__name__ if 'name' isn't resolved
            type_val = getattr(cls, 'type', 'unknown_type')
            role_val = getattr(cls, 'role', 'unknown_role')
            fqn_val = getattr(cls, 'fqn', 'unknown_fqn')
            version_val = getattr(cls, 'version', 'unknown_version')
            return f"{cls.__name__} (Pylium Class: Name='{name}', Version='{version_val}', Type='{type_val}', Role='{role_val}', FQN='{fqn_val}')"
        except AttributeError:
            # Fallback if attributes aren't set, which shouldn't happen for fully init'd subclasses
            logger.warning(f"ModuleMeta __str__: Attributes not set for {cls.__name__}")
            return super().__str__(cls)

    def __repr__(cls):
        # Similar to __str__ but for repr(ClassName)
        try:
            name = getattr(cls, 'name', cls.__name__)
            return f"<PyliumModuleClass '{name}' (Module: {cls.__module__}.{cls.__name__})>"
        except AttributeError:
            logger.warning(f"ModuleMeta __repr__: Attributes not set for {cls.__name__}")
            return super().__repr__(cls)
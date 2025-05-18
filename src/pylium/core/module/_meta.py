from ._header import _HeaderMeta

from logging import getLogger
logger = getLogger(__name__)

# Define the metaclass
class _ModuleMeta(_HeaderMeta):
    def __str__(cls):
        # logger.debug(f"ModuleMeta __str__ for: {cls.__name__}")

        # This method is called when str(ClassName) is used.
        # It accesses class variables of cls.
        # Ensure these attributes are resolved before str(cls) is called outside of __init_subclass__.
        try:
            return f"{cls.__name__} (PyliumModuleClass {cls.__name__}@{cls.name}^{cls.version} Type={cls.type} Role={cls.role} FQN={cls.fqn})"
        except AttributeError:
            # Fallback if attributes aren't set, which shouldn't happen for fully init'd subclasses
            logger.warning(f"ModuleMeta __str__: Attributes not set for {cls.__name__}")
            return super().__str__(cls)

    def __repr__(cls):
        # Similar to __str__ but for repr(ClassName)
        try:
            return f"<PyliumModuleClass {cls.__name__}@{cls.name}^{cls.version}>"
        except AttributeError:
            logger.warning(f"ModuleMeta __repr__: Attributes not set for {cls.__name__}")
            return super().__repr__(cls)
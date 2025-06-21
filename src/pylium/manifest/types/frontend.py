"""
Frontend type for the manifest.
"""

# Standard library imports
from enum import Flag


class ManifestFrontend(Flag):
    NoFrontend      = 0
    CLI             = 1 << 0
    API             = 1 << 1
    TUI             = 1 << 2
    GUI             = 1 << 3
    Web             = 1 << 4
    All             = CLI | API | TUI | GUI | Web

    def __str__(self):
        # If the flag instance has a specific name (it's a single defined flag or a named combination like 'All')
        if self.name is not None:
            return self.name.lower()
        else:
            # It's an unnamed combination (e.g., CLI | API) or a value like 0 if not directly named.
            decomposed_members = list(self)
            
            if not decomposed_members:
                # This implies self.value is 0, as list(self) for non-zero flags gives its components.
                # Try to find a name for the zero value among defined members.
                if self.value == 0:
                    for member_in_class in self.__class__:
                        if member_in_class.value == 0:
                            return member_in_class.name.lower() # e.g., "nofrontend"
                    return "0" # Default string for 0 if no specific zero-value member like NoFrontend found
                else:
                    # Highly unlikely for Flags: name is None, list() is empty, but value isn't 0.
                    return str(self.value) 

            # For unnamed combinations (e.g. CLI | API), list their lowercase names
            return " | ".join(m.name.lower() for m in decomposed_members)
    
    def __repr__(self):
        cls_name = self.__class__.__name__
        decomposed_members = list(self)

        if not decomposed_members:
            # This typically means self.value == 0 and no canonical member is named for 0.
            if self.value == 0:
                for member_in_class in self.__class__:
                    if member_in_class.value == 0:
                        return f"{cls_name}.{member_in_class.name}" 
                return f"<{cls_name}: 0>" 
            else:
                return f"<{cls_name} value: {self.value}>"

        member_reprs = [f"{cls_name}.{m.name}" for m in decomposed_members]
        return " | ".join(member_reprs)
"""
AI access level type for the manifest.
"""

# Standard library imports
from enum import Flag


# Note: This is a bitmask, so the order of the flags is important
# This is a hint for the AI to use the correct access level,
# mainly used for coding assistance, not for security
# It might work, but AI might completely ignore it
class ManifestAIAccessLevel(Flag):
    NoAccess = 1 << 0
    Read = 1 << 1
    SuggestOnly = 1 << 2
    ForkAllowed = 1 << 3
    Write = 1 << 4
    All = NoAccess | Read | SuggestOnly | ForkAllowed | Write
"""
Part of Dynamic RaceMenu Interface Patcher (DRIP).
Contains Exception classes.

Licensed under Attribution-NonCommercial-NoDerivatives 4.0 International
"""


class InvalidPatchError(Exception):
    """
    For invalid patches (for eg. missing patch.json).
    """


class InvalidSWFFileError(InvalidPatchError):
    """
    For invalid SWF files specified in patch.json.
    """


class UnknownSectionError(InvalidPatchError):
    """
    For unknown patch sections in patch.json.
    """


class BSANotFoundError(Exception):
    """
    For missing RaceMenu BSA.
    """


class FFDecError(Exception):
    """
    For failed FFDec execution.
    """

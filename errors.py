"""This module contains the errors, exceptions, and warnings used."""


class SponsorBlockException(Exception):
    """Base class for all sponsor block exceptions"""


class InferenceException(SponsorBlockException):
    """An exception occurred while predicting sponsor segments"""


class TranscriptError(SponsorBlockException):
    """An exception occurred while retrieving the video transcript"""


class ModelError(SponsorBlockException):
    """Base class for model-related errors"""


class ModelLoadError(ModelError):
    """An exception occurred while loading the model"""

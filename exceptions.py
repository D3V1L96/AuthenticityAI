# intel_providers/exceptions.py

class IntelProviderError(Exception):
    pass

class ProviderUnavailableError(IntelProviderError):
    pass

class AnalysisFailedError(IntelProviderError):
    pass

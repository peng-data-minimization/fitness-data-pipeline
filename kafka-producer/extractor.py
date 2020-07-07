from utils import get_logger
from abc import ABC, abstractmethod
logger = get_logger()


class ActivityExtractor(ABC):
    PROVIDER_NAME = None

    @abstractmethod
    def get_activity(self, id):
        pass

    @abstractmethod
    def get_activities(self):
        pass

    @abstractmethod
    def persist_activity(self, id):
        pass

    @abstractmethod
    def persist_activities(self):
        pass

    @abstractmethod
    def get_activity_ids(self, activities):
        pass

    @classmethod
    def get_provider(cls, provider_name, **kwargs):
        for provider_class in cls.__subclasses__():
            if provider_name == provider_class.PROVIDER_NAME:
                return provider_class(**kwargs)

        raise ActivityExtractorException(
            f"Couldn't find subclass with PROVIDER_NAME '{provider_name}''. "
            f"Available providers are {[provider_class.PROVIDER_NAME for provider_class in cls.__subclasses__()]}",
            status_code=404)


class ActivityExtractorException(Exception):
    def __init__(self, message, error=None, status_code=None):
        self.error = error
        self.message = f'An error occured when trying to extract the fitness data: {message}'
        self.status = status_code if status_code else self._get_status_code()
        logger.error(self.message)
        logger.error(error)
        super().__init__(self.message)

    def _get_status_code(self):
        if isinstance(getattr(self.error, 'status', None), int):
            return self.error.status
        return 500

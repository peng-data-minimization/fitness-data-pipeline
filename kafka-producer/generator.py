from utils import get_logger
from abc import ABC, abstractmethod

logger = get_logger()

class ActivityGenerator(ABC):
    PROVIDER_NAME = None

    @abstractmethod
    def generate_dummy_activity(self):
        pass

    @classmethod
    def get_provider(cls, provider_name, **creds):
        for provider_class in cls.__subclasses__():
            if provider_name == provider_class.PROVIDER_NAME:
                return provider_class(**creds)

        raise Exception(f"Couldn't find subclass with PROVIDER_NAME '{provider_name}'. Available providers are {cls.get_provider_names()}")

    @classmethod
    def get_provider_names(cls):
        return [provider_class.PROVIDER_NAME for provider_class in cls.__subclasses__()]
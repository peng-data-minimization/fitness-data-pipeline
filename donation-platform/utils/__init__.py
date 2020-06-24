import logging.config
import yaml
import os
import json

def get_base_path():
    return os.path.join(os.path.dirname(
        os.path.dirname(os.path.realpath(__file__))))

def get_logger(log_config_path=None):
    if not log_config_path:
        log_config_path = os.path.join(get_base_path(), 'config/logger_config.yml')

    with open(log_config_path, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
        logging.config.dictConfig(config)
        logger = logging.getLogger('default_logger')
        logger.debug('logger initialized.')
    return logger


def get_access_token(provider):
    token_path = os.path.join(get_base_path(), provider.lower() + '-token.json')
    with open(token_path, 'r') as file:
        creds = json.load(file)
        return creds['access_token']
# -*- coding: utf-8 -*-
import os
from exconf.utils import (
    read_yaml,
    get_logger
)

EXCONF_CONFIG_FILE_NAME = 'exconf.yaml'

LOG = get_logger(os.path.basename(__file__))


class ExconfConfig(object):
    vars = {}

    def __init__(self, config_root):
        if not config_root and 'EXCONF_CONFIG_ROOT' in os.environ:
            config_root = os.environ['EXCONF_CONFIG_ROOT']
        if not config_root and EXCONF_CONFIG_FILE_NAME in os.listdir('.'):
            config_root = '.'
        if not config_root:
            raise ValueError("Exconf configuration root not defined. Give -c option, or define "
                             "environment variable EXCONF_CONFIG_ROOT.")
        exconf_config_file_path = os.path.join(config_root, EXCONF_CONFIG_FILE_NAME)
        LOG.debug("Reading Exconf configuration from: {}", exconf_config_file_path)
        self.vars = read_yaml(exconf_config_file_path)

    def __get_service_root_dir(self):
        return os.path.join(self.vars['exconf_configuration_root'],
                            self.vars['services_dir_name'])

    def list_services(self):
        return os.listdir(self.__get_service_root_dir())

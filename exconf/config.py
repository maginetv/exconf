# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import copy
import os
import tempfile

from exconf.utils import (
    read_yaml,
    get_logger,
    read_and_combine_yamls_in_dir,
    recursive_replace_vars,
    list_files_not_seen,
    substitute_vars_until_done,
    parse_filename_var
)

EXCONF_CONFIG_FILE_NAME = 'exconf.yaml'

EXCONF_VAR_SERVICE = 'service'
EXCONF_VAR_ENVIRONMENT = 'environment'
EXCONF_VAR_CONFIG_ROOT = 'exconf_configuration_root'
EXCONF_VAR_SERVICES_DIR = 'services_dir_name'
EXCONF_VAR_TEMPLATES_DIR = 'templates_dir_name'
EXCONF_VAR_ENVIRONMENTS_DIR = 'environments_dir_name'
EXCONF_VAR_STR_TEMPLATE_PREFIX = 'string_template_prefix'
EXCONF_VAR_STR_TEMPLATE_SUFFIX = 'string_template_suffix'
EXCONF_VAR_TEMPLATE_COMMENT_BEGIN = 'template_comment_line_begin'
EXCONF_VAR_TEMPLATE_TYPE = 'template_type'
EXCONF_VAR_FILE_TEMPLATE_PREFIX = 'file_name_template_prefix'
EXCONF_VAR_FILE_TEMPLATE_SUFFIX = 'file_name_template_suffix'
EXCONF_VAR_EXECUTION_COMMAND = 'execution_command'
EXCONF_VAR_EXECUTION_FILE = 'execution_file'

LOG = get_logger(os.path.basename(__file__))


class ExconfConfig(object):
    config_vars = None

    # This is cached resolved variables if you call this multiple times.
    resolved_vars = None

    def __init__(self, config_root):
        self._init_variables(config_root)

    def __get_vars(self):
        """Return the variables resolved, or if not resolved yet, then only the config vars."""
        if self.resolved_vars:
            return self.resolved_vars
        return self.config_vars

    def __get_services_root_dir(self):
        the_dir = os.path.join(self.__get_vars()[EXCONF_VAR_CONFIG_ROOT],
                               self.__get_vars()[EXCONF_VAR_SERVICES_DIR])
        if not os.path.isdir(the_dir):
            raise ValueError("Services directory does not exist: {}".format(the_dir))
        return the_dir

    def __get_templates_root_dir(self):
        the_dir = os.path.join(self.__get_vars()[EXCONF_VAR_CONFIG_ROOT],
                               self.__get_vars()[EXCONF_VAR_TEMPLATES_DIR])
        if not os.path.isdir(the_dir):
            raise ValueError("Templates directory does not exist: {}".format(the_dir))
        return the_dir

    def __get_environments_root_dir(self):
        the_dir = os.path.join(self.__get_vars()[EXCONF_VAR_CONFIG_ROOT],
                               self.__get_vars()[EXCONF_VAR_ENVIRONMENTS_DIR])
        if not os.path.isdir(the_dir):
            raise ValueError("Environments directory does not exist: {}".format(the_dir))
        return the_dir

    def __get_services_root_dir_for_env(self, environment):
        return os.path.join(self.__get_environments_root_dir(),
                            environment,
                            self.__get_vars()[EXCONF_VAR_SERVICES_DIR])

    def _init_variables(self, config_root):
        """Initializes the root configuration variables for this instance."""
        if not config_root and 'EXCONF_CONFIG_ROOT' in os.environ:
            config_root = os.environ['EXCONF_CONFIG_ROOT']
        if not config_root and EXCONF_CONFIG_FILE_NAME in os.listdir('.'):
            config_root = '.'
        if not config_root:
            raise ValueError("Exconf configuration root not defined. Give -c option, or define "
                             "environment variable EXCONF_CONFIG_ROOT.")
        if not EXCONF_CONFIG_FILE_NAME in os.listdir(config_root):
            raise ValueError("No {} file found from configuration root: {}"
                             .format(EXCONF_CONFIG_FILE_NAME, config_root))
        config_root = os.path.abspath(config_root)
        exconf_config_file_path = os.path.join(config_root, EXCONF_CONFIG_FILE_NAME)
        LOG.debug("Reading Exconf configuration from: {}", exconf_config_file_path)
        self.config_vars = read_yaml(exconf_config_file_path)
        self.config_vars[EXCONF_VAR_CONFIG_ROOT] = config_root
        self.resolved_vars = None

    def get_execution_file(self):
        return self.__get_vars()[EXCONF_VAR_EXECUTION_FILE]

    def get_execution_command(self):
        return self.__get_vars()[EXCONF_VAR_EXECUTION_COMMAND]

    def list_services(self):
        the_dir = self.__get_services_root_dir()
        return sorted([f for f in os.listdir(the_dir)
                       if os.path.isdir(os.path.join(the_dir, f))])

    def list_environments(self):
        the_dir = self.__get_environments_root_dir()
        return sorted([f for f in os.listdir(the_dir)
                       if os.path.isdir(os.path.join(the_dir, f))])

    def load_global_variables(self):
        """Loads all the variables found from the environment root.
        These variables apply to all services in all environments.
        """
        return read_and_combine_yamls_in_dir(self.__get_environments_root_dir())

    def load_env_variables(self, environment):
        """Loads all the variables found for the given environment.
        These variables apply to all services in the given environment.
        """
        env_dir = os.path.join(self.__get_environments_root_dir(), environment)
        return read_and_combine_yamls_in_dir(env_dir)

    def load_service_variables(self, service):
        """Loads all the variables found for the given service.
        These variables apply to the given service in all environments.
        """
        service_dir = os.path.join(self.__get_services_root_dir(), service)
        return read_and_combine_yamls_in_dir(service_dir)

    def load_service_variables_for_env(self, service, environment):
        """Loads all the variables found for the given service in given environment."""
        service_dir_for_env = \
            os.path.join(self.__get_services_root_dir_for_env(environment), service)
        return read_and_combine_yamls_in_dir(service_dir_for_env)

    def load_all_variables(self, service, environment, extra_variables=None):
        """Loads all variables for given service in given environment. Resolves and combines
        all variables in specific order, which is also described in the project readme.
        """
        all_vars = copy.deepcopy(self.config_vars)
        all_vars[EXCONF_VAR_SERVICE] = service
        all_vars[EXCONF_VAR_ENVIRONMENT] = environment
        all_vars.update(self.load_global_variables())
        all_vars.update(self.load_env_variables(environment))
        all_vars.update(self.load_service_variables(service))
        all_vars.update(self.load_service_variables_for_env(service, environment))
        if extra_variables:
            all_vars.update(extra_variables)
        return all_vars

    def resolve_variables(self, service, environment, extra_variables=None,
                          require_all_replaced=True):
        """Loads all variables and resolves also the string templates within the variables."""
        all_vars = self.load_all_variables(service, environment, extra_variables)
        self.resolved_vars = recursive_replace_vars(
            all_vars, require_all_replaced,
            all_vars[EXCONF_VAR_TEMPLATE_COMMENT_BEGIN],
            all_vars[EXCONF_VAR_STR_TEMPLATE_PREFIX],
            all_vars[EXCONF_VAR_STR_TEMPLATE_SUFFIX])
        return self.resolved_vars

    def list_template_files(self, service, environment, extra_variables=None, all_vars=None):
        if not all_vars:
            all_vars = self.resolve_variables(service, environment, extra_variables, False)
        if EXCONF_VAR_TEMPLATE_TYPE not in all_vars:
            raise ValueError("Template type (var {}) not defined.".format(EXCONF_VAR_TEMPLATE_TYPE))

        template_type = all_vars[EXCONF_VAR_TEMPLATE_TYPE]
        var_envs = all_vars[EXCONF_VAR_ENVIRONMENTS_DIR]
        var_services = all_vars[EXCONF_VAR_SERVICES_DIR]

        # 1. templates/<template_type>/*
        template_root_dir = os.path.join(self.__get_templates_root_dir(), template_type)
        if not template_type or not os.path.isdir(template_root_dir):
            raise ValueError("Template type '{}' not defined. Expected path: {}"
                             .format(template_type, template_root_dir))
        # 2. templates/<template_type>/environments/<target_environment>/*
        template_env_dir = os.path.join(template_root_dir, var_envs, environment)
        # 3. templates/<template_type>/services/<target_service>/*
        template_services_dir = os.path.join(template_root_dir, var_services, service)
        # 4. templates/<template_type>/environments/<target_environment>/services/<target_service>/*
        template_services_env_dir = os.path.join(template_env_dir, var_services, service)

        seen_file_names = set()
        LOG.debug("Listing template files from: {}", template_services_env_dir)
        all_templates = list_files_not_seen(template_services_env_dir, seen_file_names)
        LOG.debug("Listing template files from: {}", template_services_dir)
        all_templates.extend(list_files_not_seen(template_services_dir, seen_file_names))
        LOG.debug("Listing template files from: {}", template_env_dir)
        all_templates.extend(list_files_not_seen(template_env_dir, seen_file_names))
        LOG.debug("Listing template files from: {}", template_root_dir)
        all_templates.extend(list_files_not_seen(template_root_dir, seen_file_names))
        LOG.info("Found {} template files in total: {}", len(seen_file_names), seen_file_names)
        return all_templates

    def populate_template(self, template_file_path, require_all_replaced=True):
        LOG.debug("Populating template {} from file: {}",
                  os.path.basename(template_file_path), template_file_path)
        data = open(template_file_path).read()
        return substitute_vars_until_done(data, self.__get_vars(), require_all_replaced,
                                          self.__get_vars()[EXCONF_VAR_TEMPLATE_COMMENT_BEGIN],
                                          self.__get_vars()[EXCONF_VAR_STR_TEMPLATE_PREFIX],
                                          self.__get_vars()[EXCONF_VAR_STR_TEMPLATE_SUFFIX])

    def parse_filename_var(self, file_name):
        all_vars = self.__get_vars()
        return parse_filename_var(file_name, all_vars,
                                  all_vars[EXCONF_VAR_FILE_TEMPLATE_PREFIX],
                                  all_vars[EXCONF_VAR_FILE_TEMPLATE_SUFFIX])

    def populate_and_write_template_file(self, template_file_path, target_dir, file_mode=0o640,
                                         require_all_replaced=True):
        if not os.path.isdir(target_dir):
            raise ValueError("Target diretory does not exist: {}".format(target_dir))
        try:
            data = self.populate_template(template_file_path, require_all_replaced)
        except KeyError as err:
            LOG.error("Variable '{}' not defined for template file '{}'"
                      .format(err.args[0], template_file_path))
            LOG.info("Failed creating work directory into dir: {}", target_dir)
            return False

        target_base_name = self.parse_filename_var(os.path.basename(template_file_path))
        target_file_path = os.path.join(target_dir, target_base_name)
        LOG.info("Writing template file: {}", target_file_path)
        open(target_file_path, 'w').write(data)
        os.chmod(target_file_path, file_mode)
        return True

    def prepare_templated_work_dir(self, service, environment, extra_variables=None,
                                   require_all_replaced=True, target_dir=None):
        if not target_dir:
            target_dir = tempfile.mkdtemp()
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir, 0o770)
        LOG.info("Preparing temporary execution dir for service '{}' in env '{}': {}",
                 service, environment, target_dir)
        all_vars = self.resolve_variables(service, environment, extra_variables,
                                          require_all_replaced)
        exec_file_name = self.get_execution_file()

        for file_path in self.list_template_files(service, environment, extra_variables, all_vars):
            file_mode = 0o640
            if os.path.basename(file_path) == exec_file_name:
                file_mode = 0o770
            success = self.populate_and_write_template_file(file_path, target_dir, file_mode,
                                                            require_all_replaced)
            if not success:
                LOG.error("Failed writing template file '{}' into target directory: {}",
                          file_path, target_dir)
                return None

        return os.path.abspath(target_dir)

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
import logbook
import logbook.more
import os
import re
import subprocess
import sys
import yaml

REGEXP_YAML_FILE = '.*\.(yaml|yml)$'


def figure_out_log_level(given_level):
    if isinstance(given_level, str):
        return logbook.lookup_level(given_level.strip().upper())
    else:
        return given_level


def verbosity_level_to_log_level(verbosity):
    if int(verbosity) == 0:
        return 'warning'
    elif int(verbosity) == 1:
        return 'info'
    return 'debug'


def init_logging_stderr(log_level='notset', bubble=False):
    handler = logbook.more.ColorizedStderrHandler(level=figure_out_log_level(log_level),
                                                  bubble=bubble)
    handler.format_string = '{record.time:%Y-%m-%dT%H:%M:%S.%f} ' \
                            '{record.level_name} {record.channel}: {record.message}'
    handler.push_application()


def get_logger(logger_name="magine-services"):
    return logbook.Logger(logger_name)


LOG = get_logger()


def read_yaml(file_path):
    return yaml.load(open(file_path).read())


def call_shell(temp_work_dir, shell_cmd, print_output=True):
    output = []
    LOG.info("Calling shell ({}):\n{}", temp_work_dir, shell_cmd)
    proc = subprocess.Popen(shell_cmd, shell=True, cwd=temp_work_dir,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Poll process for new output until finished
    while True:
        next_line = proc.stdout.readline().decode("utf-8")
        if next_line == '' and proc.poll() is not None:
            break
        output.append(next_line)
        if print_output:
            sys.stdout.write(next_line)
            sys.stdout.flush()

    if proc.returncode != 0:
        LOG.error("Running shell failed with return code: {}", str(proc.returncode))

    return proc.returncode, output


def read_and_combine_yamls_in_dir(the_dir):
    LOG.debug("Loading variables from directory: {}", the_dir)
    all_vars = {}
    if os.path.isdir(the_dir):
        for file_path in files_in_dir(the_dir, REGEXP_YAML_FILE):
            all_vars.update(read_yaml(file_path))
    else:
        LOG.debug("Directory does not exist: {}", the_dir)
    return all_vars


def files_in_dir(the_dir, filter_regexp=None):
    for file_name in sorted(os.listdir(the_dir)):
        if filter_regexp is None or re.match(filter_regexp, file_name):
            file_path = os.path.join(the_dir, file_name)
            yield file_path


def recursive_replace_config_vars(all_vars, require_all_replaced=True, comment_begin='#',
                                  template_prefix='{{', template_suffix='}}'):
    result = copy.deepcopy(all_vars)
    for key in result.keys():
        iterations = 0
        has_changed = True
        while has_changed:
            iterations += 1
            new_value, has_changed = \
                substitute_vars(str(result[key]), result, require_all_replaced,
                                comment_begin, template_prefix, template_suffix)
            if has_changed:
                LOG.debug("Substituted key '{}' to new value:\n'{}'\nfrom old value:\n'{}'",
                          key, new_value, result[key])
            result[key] = new_value
            if iterations > 20:
                LOG.error("Too many recursive calls to variable substitution. Variable: {}", key)
                return None
    return result


def substitute_vars(data, vars, require_all_replaced=True, comment_begin='#',
                    template_prefix='{{', template_suffix='}}'):
    """Just simple string template substitution, like Python string templates etc."""
    output = []
    missing_vars_with_lines = []
    replaced_variables = []
    has_changed = False
    line_num = 0
    for line in data.split('\n'):
        line_num += 1
        if not line.strip().startswith(comment_begin):
            i, j = 0, -1
            while 0 <= i < len(line):
                i = tag_begin = line.find(template_prefix, i)
                if tag_begin >= 0:
                    i = tag_begin + len(template_prefix)
                    j = line.find(template_suffix, i)
                    if j > i:
                        var_name = line[i:j].strip()
                        i = j + len(template_suffix)
                        var_value = vars.get(var_name)
                        if var_value is not None:
                            replaced_variables.append(var_name)
                            line = line[0:tag_begin] + str(var_value) + line[i:]
                            has_changed = True
                        elif require_all_replaced:
                            missing_vars_with_lines.append((line_num, var_name))
        output.append(line)

    LOG.debug("Variables substituted in given data: {}", replaced_variables)
    if missing_vars_with_lines:
        raise ValueError("Cannot replace key(s) in template (line, key_name): {}"
                         .format(missing_vars_with_lines))
    return '\n'.join(output), has_changed

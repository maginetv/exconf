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
REGEXP_INVALID_FILE_NAME_CHARS = '[^-_.A-Za-z0-9]'
MAX_RECURSION_DEPTH = 30


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
    output_lines = []
    LOG.info("Calling shell ({}):\n{}", temp_work_dir, shell_cmd)
    proc = subprocess.Popen(shell_cmd, shell=True, cwd=temp_work_dir,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Poll process for new output until finished
    while True:
        next_line = proc.stdout.readline().decode("utf-8")
        if next_line == '' and proc.poll() is not None:
            break
        output_lines.append(next_line)
        if print_output:
            sys.stdout.write(next_line)
            sys.stdout.flush()

    if proc.returncode != 0:
        LOG.warn("Running shell failed with return code: {}", str(proc.returncode))

    return proc.returncode, output_lines


def read_and_combine_yamls_in_dir(the_dir):
    LOG.debug("Loading variables in YAML files from directory: {}", the_dir)
    all_vars = {}
    if os.path.isdir(the_dir):
        for file_path in files_in_dir(the_dir, REGEXP_YAML_FILE):
            all_vars.update(read_yaml(file_path))
    else:
        LOG.info("Directory does not exist: {}", the_dir)
    return all_vars


def files_in_dir(the_dir, filter_regexp=None):
    for file_name in sorted(os.listdir(the_dir)):
        if filter_regexp is None or re.match(filter_regexp, file_name):
            file_path = os.path.join(the_dir, file_name)
            yield file_path


def list_files_not_seen(source_dir, seen_file_names):
    file_paths = []
    if os.path.isdir(source_dir):
        for x in os.listdir(source_dir):
            x_path = os.path.join(source_dir, x)
            if os.path.isfile(x_path) and x not in seen_file_names:
                seen_file_names.add(x)
                file_paths.append(x_path)
    return file_paths


def recursive_replace_vars(all_vars, require_all_replaced=True, comment_begin='#',
                           template_prefix='{{', template_suffix='}}'):
    result = copy.deepcopy(all_vars)
    for key in all_vars.keys():
        try:
            result[key] = substitute_vars_until_done(
                str(result[key]), all_vars, require_all_replaced,
                comment_begin, template_prefix, template_suffix)
        except RecursionError as err:
            LOG.error("Failed substituting key '{}'. {}", key, err)
            raise err
    return result


def substitute_vars_until_done(data, all_vars, require_all_replaced, comment_begin,
                               template_prefix, template_suffix):
    iterations = 0
    has_changed = True
    while has_changed:
        iterations += 1
        data, has_changed = substitute_vars(data, all_vars, require_all_replaced,
                                            comment_begin, template_prefix, template_suffix)
        if iterations > MAX_RECURSION_DEPTH:
            raise RecursionError("Too many iterations replacing template variables. Check your "
                                 "variables for reference loops, or increase max recursion depth.")
    return data


def substitute_vars(data, vars, require_all_replaced, comment_begin,
                    template_prefix, template_suffix):
    """Just simple string template substitution, like Python string templates etc.

    Provides also line numbers for missing variables so they can be highlighted.
    """
    output = []
    missing_vars_with_lines = []
    replaced_variables = []
    has_changed = False
    line_num = 0
    for line in data.split('\n'):
        line_num += 1
        if not comment_begin or not line.strip().startswith(comment_begin):
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

    if replaced_variables:
        LOG.debug("Variables substituted: {}", replaced_variables)
    if missing_vars_with_lines:
        raise ValueError("Cannot replace key(s) in template (line, key_name): {}"
                         .format(missing_vars_with_lines))
    return '\n'.join(output), has_changed


def parse_filename_var(file_name, all_vars, template_prefix='___', template_suffix='___'):
    while template_prefix in file_name:
        LOG.debug("Parsing string template variable in file name: {}", file_name)
        i = file_name.find(template_prefix)
        j = file_name.find(template_suffix, i + len(template_prefix))
        if j > i:
            filename_var = file_name[i + len(template_prefix):j]
            if filename_var not in all_vars:
                raise ValueError("Invalid file name variable '{}' in file name: {}".format(
                    filename_var, file_name))
            substitute = all_vars[filename_var]
            if re.search(REGEXP_INVALID_FILE_NAME_CHARS, substitute):
                raise ValueError("Invalid file name substitute (var {}): {}"
                                 .format(filename_var, substitute))
            file_name = file_name[:i] + substitute + file_name[j + len(template_suffix):]
            LOG.debug("File name after parsing: {}", file_name)
        else:
            LOG.info("Did not find file name template suffix for parsing: {}", file_name)
            break
    return file_name

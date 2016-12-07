# -*- coding: utf-8 -*-
import subprocess
import sys

import logbook
import logbook.more
import yaml


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
        if next_line == '' and proc.poll() != None:
            break
        output.append(next_line)
        if print_output:
            sys.stdout.write(next_line)
            sys.stdout.flush()

    if proc.returncode != 0:
        LOG.error("Running shell failed with return code: {}", str(proc.returncode))

    return proc.returncode, output

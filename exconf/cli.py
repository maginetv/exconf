#!/usr/bin/env python
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
import click
import json
import os

from exconf.config import ExconfConfig
from exconf.utils import (
    get_logger,
    init_logging_stderr,
    verbosity_level_to_log_level,
)

LOG = get_logger(os.path.basename(__file__))

DEFAULT_CONFIG_ROOT = '.'
VAR_CONFIG_ROOT = 'config_root'


def setup_config_in_context(ctx, config_root):
    ctx.obj[VAR_CONFIG_ROOT] = config_root


def get_config(ctx):
    return ExconfConfig(ctx.obj[VAR_CONFIG_ROOT])


def output(line, color='green'):
    if not line:
        click.echo()
    else:
        click.echo(click.style(str(line), fg=color))


def parse_extra_vars(variables):
    extra_vars = {}
    if variables:
        for var in variables:
            key, value = var.split('=')
            extra_vars[key] = value
    return extra_vars


@click.group(help="Exconf CLI Tool")
@click.option('-v', '--verbose', default=False, count=True,
              help='Give more -v flags to get more verbosity.')
@click.option('-c', '--config-root', default=None, required=False,
              help='Exconf configuration root path. Must contain exconf.yaml')
@click.pass_context
def cli(ctx, verbose, config_root):
    init_logging_stderr(log_level=verbosity_level_to_log_level(verbose))
    LOG.debug("Logging initialized")
    setup_config_in_context(ctx, config_root)


@cli.command('list-services')
@click.pass_context
def list_services(ctx):
    """List all defined services."""
    service_names = get_config(ctx).list_services()
    if not service_names:
        output("No services found", color='yellow')
    for x in service_names:
        output(x)


@cli.command('list-envs')
@click.pass_context
def list_envs(ctx):
    """List all defined environments."""
    env_names = get_config(ctx).list_environments()
    if not env_names:
        output("No environments found", color='yellow')
    for x in env_names:
        output(x)


@cli.command('variables')
@click.option('-s', '--service', help='Service name.', required=True)
@click.option('-e', '--environment', help='Environment name.', required=True)
@click.option('-x', '--extra-var', multiple=True, help='Extra variables, as key=value pairs.')
@click.pass_context
def variables(ctx, service, environment, extra_var):
    """List all variables for given service and environment."""
    cfg = get_config(ctx)
    all_vars = cfg.resolve_variables(service, environment,
                                     parse_extra_vars(extra_var))
    output(json.dumps(all_vars, indent=2, sort_keys=True))


def main():
    cli(obj={})


if __name__ == '__main__':
    main()

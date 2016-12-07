#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
import os

from exconf.config import ExconfConfig
from exconf.utils import (
    get_logger,
    init_logging_stderr,
    verbosity_level_to_log_level,
)

LOG = get_logger(os.path.basename(__file__))

DEFAULT_CONFIG_ROOT = '.'


def setup_config_in_context(ctx, config_root):
    ctx.obj['exconf'] = ExconfConfig(config_root)


def get_config(ctx):
    return ctx.obj['exconf']


def output(line, color='green'):
    if not line:
        click.echo()
    else:
        click.echo(click.style(str(line), fg=color))


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


if __name__ == '__main__':
    cli(obj={})

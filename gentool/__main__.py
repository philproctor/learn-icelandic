#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
import logging
from .data import data
from .svg_cards import svg_cards

log = logging.getLogger()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


if __name__ == '__main__':
    cli.add_command(data)
    cli.add_command(svg_cards)
    cli(prog_name="./gen")

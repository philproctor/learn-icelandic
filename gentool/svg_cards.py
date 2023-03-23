#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
import logging
import yaml
# import drawsvg as draw
from .svgs.cards import SVGCardWriter

log = logging.getLogger()


@click.group()
def svg_cards():
    pass


@svg_cards.command()
def gen_nouns():
    'Generate Noun SVG Cards'
    with open("data/stage-3/nouns.yml", "r") as f:
        content = f.read()
    nouns = yaml.load(content, Loader=yaml.CLoader)
    writer = SVGCardWriter()

    for word, metadata in nouns.items():
        log.info(f"Processing {word}...")
        writer.generate_noun_svg(word, metadata["d"], metadata["f"])

@svg_cards.command()
def gen_verbs():
    'Generate Verb SVG Cards'
    with open("data/stage-3/verbs.yml", "r") as f:
        content = f.read()
    verbs = yaml.load(content, Loader=yaml.CLoader)
    writer = SVGCardWriter()

    for word, metadata in verbs.items():
        log.info(f"Processing {word}...")
        writer.generate_verb_svg(word, metadata["d"], metadata["f"])


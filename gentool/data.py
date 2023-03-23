#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
import logging
import requests
import json
import yaml
from islenska import Bin

log = logging.getLogger()

IS_DICT_DOWNLOAD_URL = "https://kaikki.org/dictionary/Icelandic/kaikki.org-dictionary-Icelandic.json"


@click.group()
def data():
    pass


@data.command()
def stage_0():
    'Download Stage-0 Resources'
    log.info(f"Downloading dictionary from: {IS_DICT_DOWNLOAD_URL}")
    r = requests.get(IS_DICT_DOWNLOAD_URL, allow_redirects=True)
    with open('data/stage-0/isk_dict.json', 'wb') as f:
        f.write(r.content)
    log.info(f"isk_dict.json downloaded")


def process_isk_item(entry):
    pos = entry["pos"]
    if pos not in ["noun", "verb", "adv", "adj"]:
        return None
    if "senses" not in entry:
        return None
    _def = None
    for sense in entry["senses"]:
        if _def == None:
            if "form_of" in sense:
                continue
            if "form-of" in sense.get("tags", []):
                continue
            if "glosses" not in sense:
                continue
            _def = sense["glosses"][0]
    if not _def:
        return None
    word = entry["word"]
    return {
        "t": pos,
        "d": _def,
        "w": word,
    }


@data.command()
def stage_1():
    'Generate Stage-1 Resources'
    results = dict()
    with open('data/stage-0/isk_dict.json', 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            if len(line) < 1:
                continue
            data = json.loads(line)
            res = process_isk_item(data)
            if res:
                word = res["w"]
                del res["w"]
                existing = results.get(word, None)
                if existing:
                    existing.append(res)
                else:
                    results[word] = [res]
    output = yaml.dump(results, allow_unicode=True)
    with open('data/stage-1/dict.yml', "w") as f:
        f.write(output)


def find_word_form_def(word, form, isk_dict):
    if word not in isk_dict:
        return None
    defs = isk_dict[word]
    for d in defs:
        if d["t"] == form:
            return d["d"]
    return None


@data.command()
def stage_2():
    'Generate Stage-2 Resources'

    b = Bin()
    with open("data/stage-0/top5000.txt", "r") as f:
        words = f.readlines()

    with open("data/stage-1/dict.yml", "r") as f:
        dict_content = f.read()

    isk_dict = yaml.load(dict_content, Loader=yaml.CLoader)

    # Load an array from words that are actually icelandic words
    word_matches = []
    bin_ids = set()
    for word in words:
        matchword = word.strip()
        _word, res = b.lookup(matchword)
        if len(res) < 1:
            continue  # Not an icelandic word

        # The following loop presumes lower IDs are more frequent occurrence, not always true
        for cur in res:
            if cur.bin_id not in bin_ids:
                bin_ids.add(cur.bin_id)
                log.info(f"Adding {cur.ord}")
                word_matches.append({
                    "ord": cur.ord,
                    "id": cur.bin_id,
                    "ofl": cur.ofl,
                })

    # Create output dictionaries
    noun_list = dict()
    verb_list = dict()
    adj_list = dict()
    adv_list = dict()
    for word in word_matches:
        ofl = word['ofl']
        del word['ofl']
        ord = word['ord']
        del word['ord']
        if ofl == 'so' and ord not in verb_list:
            _def = find_word_form_def(ord, "verb", isk_dict)
            if not _def:
                continue
            word['d'] = _def
            verb_list[ord] = word
            word['p'] = len(verb_list)
        elif ofl in ['kvk', 'kk', 'hk'] and ord not in noun_list:
            _def = find_word_form_def(ord, "noun", isk_dict)
            if not _def:
                continue
            word['d'] = _def
            noun_list[ord] = word
            word['p'] = len(noun_list)
        elif ofl == "lo" and ord not in adj_list:
            _def = find_word_form_def(ord, "adj", isk_dict)
            if not _def:
                continue
            word['d'] = _def
            adj_list[ord] = word
            word['p'] = len(adj_list)
        elif ofl == "ao" and ord not in adv_list:
            _def = find_word_form_def(ord, "adv", isk_dict)
            if not _def:
                continue
            word['d'] = _def
            adv_list[ord] = word
            word['p'] = len(adv_list)

    for outlist, name in [
        (noun_list, "nouns"),
        (verb_list, "verbs"),
        (adj_list, "adjectives"),
        (adv_list, "adverbs")
    ]:
        output = yaml.dump(outlist, allow_unicode=True)
        log.info(f"Writing {len(outlist)} {name}...")
        with open(f"data/stage-2/{name}.yml", "w") as f:
            f.write(output)


def load_forms(word, typ, bin_id):
    b = Bin()
    forms = b.lookup_variants(word, typ, (), bin_id=bin_id)
    result = dict()
    for part in forms:
        result[part.mark] = part.bmynd
    return result


def gen_nouns():
    with open("data/stage-2/nouns.yml", "r") as f:
        content = f.read()
    nouns = yaml.load(content, Loader=yaml.CLoader)
    for word, metadata in nouns.items():
        bid = metadata["id"]
        del metadata["id"]
        forms = load_forms(word, "no", bid)
        metadata["f"] = {
            "s": {
                "def": {
                    "nom": forms.get("NFETgr", None),
                    "gen": forms.get("EFETgr", None),
                    "dat": forms.get("ÞFETgr", None),
                    "acc": forms.get("ÞGFETgr", None),
                },
                "indef": {
                    "nom": forms.get("NFET", None),
                    "gen": forms.get("EFET", None),
                    "dat": forms.get("ÞFET", None),
                    "acc": forms.get("ÞGFET", None),
                },
            },
            "p": {
                "def": {
                    "nom": forms.get("NFFTgr", None),
                    "gen": forms.get("EFFTgr", None),
                    "dat": forms.get("ÞFFTgr", None),
                    "acc": forms.get("ÞGFFTgr", None),
                },
                "indef": {
                    "nom": forms.get("NFFT", None),
                    "gen": forms.get("EFFT", None),
                    "dat": forms.get("ÞFFT", None),
                    "acc": forms.get("ÞGFFT", None),
                },
            },
        }
    output = yaml.dump(nouns, allow_unicode=True)
    with open(f"data/stage-3/nouns.yml", "w") as f:
        f.write(output)


def gen_verbs():
    with open("data/stage-2/verbs.yml", "r") as f:
        content = f.read()
    verbs = yaml.load(content, Loader=yaml.CLoader)
    for word, metadata in verbs.items():
        bid = metadata["id"]
        del metadata["id"]
        forms = load_forms(word, "so", bid)
        metadata["f"] = {
            "infinitive": forms.get("GM-NH", None),
            "present": {
                "1PS": forms.get("GM-FH-NT-1P-ET", None),
                "2PS": forms.get("GM-FH-NT-2P-ET", None),
                "3PS": forms.get("GM-FH-NT-3P-ET", None),
                "1PP": forms.get("GM-FH-NT-1P-FT", None),
                "2PP": forms.get("GM-FH-NT-2P-FT", None),
                "3PP": forms.get("GM-FH-NT-3P-FT", None),
            },
            "past": {
                "1PS": forms.get("GM-FH-ÞT-1P-ET", None),
                "2PS": forms.get("GM-FH-ÞT-2P-ET", None),
                "3PS": forms.get("GM-FH-ÞT-3P-ET", None),
                "1PP": forms.get("GM-FH-ÞT-1P-FT", None),
                "2PP": forms.get("GM-FH-ÞT-2P-FT", None),
                "3PP": forms.get("GM-FH-ÞT-3P-FT", None),
            },
        }
    output = yaml.dump(verbs, allow_unicode=True)
    with open(f"data/stage-3/verbs.yml", "w") as f:
        f.write(output)


def gen_adverbs():
    with open("data/stage-2/adverbs.yml", "r") as f:
        content = f.read()
    adverbs = yaml.load(content, Loader=yaml.CLoader)
    for word, metadata in adverbs.items():
        del metadata["id"]
    output = yaml.dump(adverbs, allow_unicode=True)
    with open(f"data/stage-3/adverbs.yml", "w") as f:
        f.write(output)


def gen_adjectives():
    with open("data/stage-2/adjectives.yml", "r") as f:
        content = f.read()
    adjectives = yaml.load(content, Loader=yaml.CLoader)
    for word, metadata in adjectives.items():
        del metadata["id"]
    output = yaml.dump(adjectives, allow_unicode=True)
    with open(f"data/stage-3/adjectives.yml", "w") as f:
        f.write(output)


@data.command()
def stage_3():
    'Generate Stage-3 Resources'
    gen_nouns()
    gen_verbs()
    gen_adverbs()
    gen_adjectives()

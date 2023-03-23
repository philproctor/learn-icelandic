#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import drawsvg as draw

log = logging.getLogger()


class SVGCardWriter():
    'Not Thread Safe!'

    def __init__(self):
        self.reset_line_pos()

    def reset_line_pos(self):
        self._line_pos = -((self.height / 2) - self.boundary - self.h1 - 10)

    def advance_line_pos(self, amount):
        self._line_pos += amount

    @property
    def line_pos(self):
        return self._line_pos

    @property
    def width(self):
        return 800

    @property
    def height(self):
        return 600

    @property
    def boundary(self):
        return 10

    @property
    def h1(self):
        return 40

    @property
    def h2(self):
        return 30

    @property
    def h3(self):
        return 24

    @property
    def eighth(self):
        return self.width / 8

    @property
    def right_center(self):
        return (self.width / 4)

    @property
    def left_center(self):
        return -self.right_center

    @property
    def right_boundary(self):
        return (self.width / 2) - self.boundary

    @property
    def left_boundary(self):
        return -self.right_boundary

    @property
    def bottom_boundary(self):
        return (self.height / 2) - self.boundary

    @property
    def top_boundary(self):
        return -self.bottom_boundary

    def start(self):
        self.reset_line_pos()
        self._drawing = draw.Drawing(self.width, self.height, origin='center')
        self.draw(draw.Rectangle(
            -((self.width / 2) - self.boundary), -
            ((self.height / 2) - self.boundary),
            self.width - (self.boundary*2), self.height - (self.boundary*2),
            rx=20, ry=20, stroke="black", fill='#dddddd', stroke_width=2)
        )

    def finish(self, filename: str):
        self._drawing.save_svg(filename)

    def draw(self, obj):
        self._drawing.append(obj)

    def draw_title(self, word: str, ensku_def: str):
        self.draw(draw.Text(word, self.h1, 0, self.line_pos,
                  fill='black', text_anchor='middle'))
        self.advance_line_pos(self.h1 + 10)
        self.draw(draw.Text(ensku_def, self.h2, 0, self.line_pos,
                  fill='black', text_anchor='middle'))
        self.advance_line_pos(self.h2 + 10)

    def draw_columns_header(self, left_text: str, right_text: str):
        self.draw(draw.Text(left_text, self.h2, self.left_center,
                            self.line_pos, fill='black', text_anchor='middle'))
        self.draw(draw.Text(right_text, self.h2, self.right_center,
                            self.line_pos, fill='black', text_anchor='middle'))
        self.draw(draw.Line(0, self.line_pos + 15, 0, self.bottom_boundary -
                            20, stroke='black'))  # vertical divider
        self.draw(draw.Line(self.left_boundary + 30, self.line_pos + 15,
                            self.right_boundary - 30, self.line_pos + 15, stroke='black'))
        self.advance_line_pos(self.h2 + 20)

    def draw_columns_subheader(self, left_text: str, right_text: str):
        self.draw(draw.Text(left_text, self.h3, self.left_center,
                            self.line_pos, fill='black', text_anchor='middle'))
        self.draw(draw.Text(right_text, self.h3, self.right_center,
                            self.line_pos, fill='black', text_anchor='middle'))
        self.advance_line_pos(self.h3 + 10)

    def draw_columns_entry(self, prompt: str, left_text: str, right_text: str):
        self.draw(draw.Text(prompt, self.h3, self.left_center - self.eighth, self.line_pos,
                            fill='black', text_anchor='end', font_style='italic'))
        self.draw(draw.Text(left_text or "", self.h3, self.left_center - self.eighth +
                            10, self.line_pos, fill='black', text_anchor='start', font_weight='bold'))
        self.draw(draw.Text(prompt, self.h3, self.right_center - self.eighth, self.line_pos,
                            fill='black', text_anchor='end', font_style='italic'))
        self.draw(draw.Text(right_text or "", self.h3, self.right_center - self.eighth +
                            10, self.line_pos, fill='black', text_anchor='start', font_weight='bold'))
        self.advance_line_pos(self.h3 + 5)

    def generate_noun_svg(self, word: str, ensku_def: str, forms):
        self.start()
        self.draw_title(word, ensku_def)

        # Articles Header
        self.advance_line_pos(20)
        self.draw_columns_header("singular", "plural")

        # Indefinite Articles
        self.draw_columns_subheader("indef.", "indef.")
        self.draw_columns_entry("nom.", forms["s"]["indef"]["nom"], forms["p"]["indef"]["nom"])
        self.draw_columns_entry("dat.", forms["s"]["indef"]["dat"], forms["p"]["indef"]["dat"])
        self.draw_columns_entry("acc.", forms["s"]["indef"]["acc"], forms["p"]["indef"]["acc"])
        self.draw_columns_entry("gen.", forms["s"]["indef"]["gen"], forms["p"]["indef"]["gen"])

        # Definite Articles
        self.draw(draw.Line(self.left_boundary + 30, self.line_pos + 10,
                            self.right_boundary - 30, self.line_pos + 10, stroke='black'))
        self.advance_line_pos(self.h2 + 20)
        self.draw_columns_subheader("def.", "def.")
        self.draw_columns_entry("nom.", forms["s"]["def"]["nom"], forms["p"]["def"]["nom"])
        self.draw_columns_entry("dat.", forms["s"]["def"]["dat"], forms["p"]["def"]["dat"])
        self.draw_columns_entry("acc.", forms["s"]["def"]["acc"], forms["p"]["def"]["acc"])
        self.draw_columns_entry("gen.", forms["s"]["def"]["gen"], forms["p"]["def"]["gen"])

        self.finish(f'assets/nouns/svg/{word}.svg')

    def generate_verb_svg(self, word: str, ensku_def: str, forms):
        self.start()
        self.draw_title(word, ensku_def)

        # Articles Header
        self.advance_line_pos(20)
        self.draw_columns_header("present", "past")

        # Indefinite Articles
        spacing = 34
        self.advance_line_pos(spacing / 2)
        self.draw_columns_entry("ég", forms["present"]["1PS"], forms["past"]["1PS"])
        self.advance_line_pos(spacing)
        self.draw_columns_entry("þú", forms["present"]["2PS"], forms["past"]["2PS"])
        self.advance_line_pos(spacing)
        self.draw_columns_entry("það", forms["present"]["3PS"], forms["past"]["3PS"])
        self.advance_line_pos(spacing)
        self.draw_columns_entry("við", forms["present"]["1PP"], forms["past"]["1PP"])
        self.advance_line_pos(spacing)
        self.draw_columns_entry("þið", forms["present"]["2PP"], forms["past"]["2PP"])
        self.advance_line_pos(spacing)
        self.draw_columns_entry("þau", forms["present"]["3PP"], forms["past"]["3PP"])

        self.finish(f'assets/verbs/svg/{word}.svg')

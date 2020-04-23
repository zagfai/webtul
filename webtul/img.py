#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Image tools
"""
__author__ = 'Zagfai'
__date__ = '2018-02'

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class BoxWrapper(object):
    """BoxWrapper for Chinese and Alphas text wrapping"""
    def __init__(self, font_path, font_size):
        super(BoxWrapper, self).__init__()
        self.font_path = font_path
        self.font = ImageFont.truetype(font_path, font_size)

    def line_size(self, virtual_line):
        return self.font.getsize(virtual_line)

    def split(self, text):
        words = []
        word_tmp = ''
        for chx in text:
            if ord(chx) > 255:
                if word_tmp:
                    words.append(word_tmp)
                    word_tmp = ''
                words.append(chx)
            else:
                word_tmp += chx

        if word_tmp:
            words.append(word_tmp)
            word_tmp = ''

        # split Alpha words
        split_words = []
        for word in words:
            if len(word) == 1:
                split_words.append(word)
            else:
                split_words.extend(word.split())
        for wordpos, word in enumerate(split_words):
            if len(word) > 1 and wordpos > 0 and \
               len(split_words[wordpos-1]) > 1:
                split_words[wordpos] = ' ' + split_words[wordpos]
        # print(split_words)
        return split_words

    def wrap_as_box(self, text, box_width, color, place='left'):
        words = self.split(text)

        lines = []
        line = ''
        for word in words:
            line_tmp = line + word
            size = self.line_size(line_tmp)
            text_h = size[1]
            if size[0] <= box_width:
                line = line_tmp
            else:
                lines.append(line)
                line = word.strip()
        if line:
            lines.append(line)

        return lines, (box_width, text_h*len(lines)), text_h

    def mkimg(self, text, box_width, color='#000', place='left',
              mode='RGBA', back_color=(255, 255, 255, 0), line_padding=0):

        lines, (w, h), line_h = self.wrap_as_box(text, box_width, color)

        image = Image.new(
                mode, (box_width, h+line_padding*len(lines)), color=back_color)
        draw = ImageDraw.Draw(image)

        x = 0
        y = 0
        for index, line in enumerate(lines):
            draw.text((x, y), line, font=self.font, fill=color)
            y += line_h + line_padding

        return image


if __name__ == "__main__":
    charpath = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
    text = "【以色列钻石交易所：将发行两种数字货币】世界大型交易所之一的以色列钻石交易所宣布，将发行两种数字货币：一种为Carat，定位于广大投资券；另一种为Cut，预计将用于钻石市场专业参与者间的结算。25%的Carat价值将基于交易平台所拥有的钻石。"  # NOQA
    x = BoxWrapper(charpath, 24)
    x.mkimg(text, 390, '#000')

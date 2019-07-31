#!/usr/bin/env python3
#
# This software is licensed under the MIT License
#
# The MIT License
# 
# Copyright (c) 2007 Siddharta Govindaraj. All rights reserved.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 

import os,sys,re
import inspect
from colors import *
from subprocess import call

try:
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont
except:
    try:
        import Image
        import ImageDraw
        import ImageFont
    except:
        print("Install PIL or Pillow please")
        sys.exit(1)

class BadgeImage(object):
    def __init__(self, filename):
        self.debug = False
        self.img = Image.open(filename)
        self.draw = ImageDraw.Draw(self.img)
        self.width = int(self.img.size[0]*0.9)
        self.ttfFontDir = "fonts"
        self.ttfFont = os.path.join(self.ttfFontDir, "Roboto-Medium.ttf")

        self.helloLang = {'en':'HELLO',
                          'de':'HALLO',
                          'fr':'SALUT',
                          'lu':'MOIEN',
                          'pt':'',
                          'es':'HOLA'}

        self.colorSeperator = "#" + triplet(BLACK)
        self.textColorCompany = "#" + "0099ff"
        self.textColorPerson = "#" + triplet(BLACK)
        self.textColorSoi = "#" + triplet(BLACK)
        self.textColorHello = "#" + triplet(BLACK)
        self.textColorColor = "#" + triplet(BLACK)

    def reColor(self,color, srcFile, dstFile):
        call(["convert", "images/badgeTemplate_bw.png", "+level-colors", color + ",white", srcFile, "-compose", "over", "-composite", dstFile])

    def drawAlignedText(self, pos, text, font_color, xtransform, ytransform):
        (font, color) = font_color
        width,height = font.getsize(text)
        xpos = xtransform(pos[0], width)
        ypos = ytransform(pos[1], height)
        if inspect.stack()[1][3] and self.debug == "drawRightAlignedText":
            print(xpos,ypos)
        self.draw.text((xpos, ypos), text, fill=color, font=font)

    def drawCenteredText(self, pos, text, font):
        self.drawAlignedText(pos, text, font, lambda x,w:x-w/2, lambda y,h:y-h/2)

    def drawLeftAlignedText(self, pos, text, font):
        self.drawAlignedText(pos, text, font, lambda x,w:x, lambda y,h:y-h)

    def drawRightAlignedText(self, pos, text, font):
        self.drawAlignedText(pos, text, font, lambda x,w:w+x, lambda y,h:y-h)

    def getFitSize(self, startsize, text):
        size = startsize
        font = ImageFont.truetype(self.ttfFont, int(size))
        textwidth, textheight = font.getsize(text)
        while textwidth > self.width:
            size -= 1
            font = ImageFont.truetype(self.ttfFont, int(size))
            textwidth, textheight = font.getsize(text)
        return size

    def drawPerson(self, name):
        linepos = (self.img.size[0]/2, self.img.size[1]/4)
        line1pos = (self.img.size[0]/2, self.img.size[1]/5)
        line2pos = (self.img.size[0]/2, (self.img.size[1]/5)*2.4)
        fitsize = 36
        size = self.getFitSize(fitsize, name)
        if name.find(" ") >= 0:
            firstname, rest = name.split(" ", 1)
        else:
            firstname, rest = (name, "")
        if size < fitsize and rest != "":
            personFont = ImageFont.truetype(self.ttfFont, int(self.getFitSize(fitsize, firstname)))
            self.drawCenteredText(line1pos, firstname, (personFont, self.textColorPerson))
            personFont = ImageFont.truetype(self.ttfFont, int(self.getFitSize(fitsize, rest)))
            self.drawCenteredText(line2pos, rest, (personFont, self.textColorPerson))
        else:
            personFont = ImageFont.truetype(self.ttfFont, int(self.getFitSize(fitsize, name)))
            self.drawCenteredText(linepos, name, (personFont, self.textColorPerson))

    def drawSoi(self, language, what):
        pos = (self.img.size[0]/2, (self.img.size[1]/4)*3)
        font = ImageFont.truetype(self.ttfFont, int(self.getFitSize(30, name)))
        self.drawCenteredText(pos, what, (font, self.textColorSoi))

    def save(self, filename, doubleSided=True):
        if not doubleSided:
            self.img.save(filename)
            return

        newimg = Image.new("RGB", (self.img.size[0]*2+20, self.img.size[1]), self.colorSeperator)
        newimg.paste(self.img, (0,0))
        newimg.paste(self.img, (self.img.size[0]+20,0))
        newimg.save(filename)

class DataFileReader(object):
    def __init__(self, filename):
        fp = open(filename)
        self.lines = [line[:-1] for line in fp.readlines()]
        fp.close()

    def getData(self):
        for id, line in enumerate(self.lines):
            if re.search('^#', line):
                continue
            if len(line.strip()) != 0:
                name,company,language = line.split(";")
                name = name.title()
            if not company.startswith("*"):
                company = company.title()
            else:
                company = company[1:]
            yield (id, name.title(), company, language)



count = 0
dir = 'people'
reader = DataFileReader("people.csv")
if not os.path.exists(dir):
    os.makedirs(dir)
colorList = []
colorList = [ "GRAY", ]
for id, name, company,language in reader.getData():
    for color in colorList:
        print("Badge ID: {} - Name: {} - What: {} - Color: http://www.colorhexa.com/{}".format(id, name, company, triplet(eval(color))))
        badgeTemplate = "images/badgeTemplate_overlay.png"
        badgeTemplate = "images/badgeTemplate_180x60mm.png"
        badge = BadgeImage(badgeTemplate)
        confBadge = {'LANG': language,
                    'color': "#" + triplet(eval(color)),
                    'what': company}
        #badge.drawHello(confBadge["LANG"])
        # badge.drawColor(confBadge["color"].upper())
        badge.drawPerson(name)
        badge.drawSoi(confBadge["LANG"],confBadge["what"])
        filename = os.path.join(dir, dir + "_badge_" + str(id) + ".png")
        badge.save(filename, False)
        #badge.reColor(color, filename, filename)
    count += 1
print("\n%d badges created" % (count))

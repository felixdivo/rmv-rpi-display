#!/usr/bin/env python3

import time
from threading import RLock
from typing import *

import epd2in9.epd2in9 as epd2in9
from PIL import Image, ImageDraw, ImageFont


class Display2in9:
    PIXEL_CLEAR = 255
    PIXEL_SET = 0
    POS_TIME_1 = (220, 0)
    POS_TIME_2 = (340, 30)

    def __init__(self):
        self.epd = epd2in9.EPD()
        self.epd.init(self.epd.lut_full_update)
        self.epd.Clear(Display2in9.PIXEL_CLEAR)

        self.font = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Semibold.ttf', 19)

        # put an update here
        temp_image = Image.new('1', (epd2in9.EPD_WIDTH, epd2in9.EPD_HEIGHT), Display2in9.PIXEL_CLEAR)
        self.epd.display(self.epd.getbuffer(temp_image))
        time.sleep(2)

        self.epd.init(self.epd.lut_full_update)
        self.image = Image.new('1', (epd2in9.EPD_HEIGHT, epd2in9.EPD_WIDTH), Display2in9.PIXEL_CLEAR)
        self.draw = ImageDraw.Draw(self.image)

        self.periodic_update_image = Image.new('1', (epd2in9.EPD_HEIGHT, epd2in9.EPD_WIDTH), Display2in9.PIXEL_CLEAR)
        self.periodic_update_draw = ImageDraw.Draw(self.periodic_update_image)

        self.lock = RLock()

    def set_lines_of_text(self, data: List[Tuple[float, str, str]]):
        with self.lock:
            # full update
            self.epd.init(self.epd.lut_full_update)

            X0 = 0
            X1 = 50
            X2 = 225
            DY = 20
            Y_LINE = 24
            Y0 = 25  # start point for data on display
            Y_MAX = 127 - DY

            WIDTH = 295
            HEIGHT = 127

            # reset
            self.draw.rectangle(((0, 0), (WIDTH, HEIGHT)), fill=Display2in9.PIXEL_CLEAR)

            self.draw.text((X0, 0), 'Linie', font=self.font, fill=Display2in9.PIXEL_SET)
            self.draw.text((X1, 0), 'Ziel', font=self.font, fill=Display2in9.PIXEL_SET)

            self.draw.line(((X0, Y_LINE), (WIDTH, Y_LINE)), fill=Display2in9.PIXEL_SET, width=1)

            Y = Y0
            for eta_seconds, line, dest in data:
                # do not draw if not enough space is left
                if Y > Y_MAX:
                    break

                eta_minutes = eta_seconds / 60
                self.draw.text((X0, Y), line, font=self.font, fill=Display2in9.PIXEL_SET)
                self.draw.text((X1, Y), dest, font=self.font, fill=Display2in9.PIXEL_SET)
                self.draw.text((X2, Y), f"{eta_minutes:2.0f} min", font=self.font, fill=Display2in9.PIXEL_SET)
                Y += DY

            # draw the time here since the periodic update is shitty as fug
            self.draw.text(Display2in9.POS_TIME_1, time.strftime('%H:%M:%S'), font=self.font,
                           fill=Display2in9.PIXEL_SET)

            self.epd.display(self.epd.getbuffer(self.image))

    def update_time(self):
        # with self.lock:
        ## partial update
        # self.epd.init(self.epd.lut_partial_update)
        #
        # self.periodic_update_draw.rectangle((Display2in9.POS_TIME_1, Display2in9.POS_TIME_2),
        #                                    fill=Display2in9.PIXEL_CLEAR)
        # self.periodic_update_draw.text(Display2in9.POS_TIME_1, time.strftime('%H:%M:%S'), font=self.font,
        #                               fill=Display2in9.PIXEL_SET)
        ##image_section = self.periodic_update_image.crop([*Display2in9.POS_TIME_1, *Display2in9.POS_TIME_2])
        ##self.image.paste(image_section, Display2in9.POS_TIME_1)
        # self.epd.display(self.epd.getbuffer(self.image))

        time.sleep(0.01)

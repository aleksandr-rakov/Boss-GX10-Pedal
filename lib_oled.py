import os
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import config

class SSD1306_Display:

    def __init__(self):

        
        self.disp = Adafruit_SSD1306.SSD1306_128_64(i2c_address=config.i2c_address,rst=0)
            
        self.disp.begin()
        self.disp.clear()
        self.disp.display()

        self.last_text = ''
    
        # Initialise the screen
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        source_dir = os.path.dirname(os.path.realpath(__file__))
        font_path = source_dir + '/fonts/' + config.font

        self.status_font = ImageFont.truetype(font_path, config.status_size)
        self.preset_font = ImageFont.truetype(font_path, config.preset_size)

    def clear_screen(self):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        self.disp.display()

    def display_status(self, status):
        if self.last_text == status:
            return
        else:
            self.last_text = status

        # Clean up return lines
        status = status.replace('\r','')

        self.clear_screen()
        self.draw.text((0, -2), status, font=self.status_font, fill=255)
        self.disp.image(self.image)
        self.disp.display()

    def show_selected_preset(self, preset, name = None, bpm = None):
        if self.last_text == preset:
            return
        else:
            self.last_text = preset

        self.clear_screen()

        self.draw.text((0, 12), preset,
                       font=self.preset_font, fill=255)
        self.disp.image(self.image)
        self.disp.display()


if __name__=='__main__':
    oled=SSD1306_Display()
    oled.display_status('1')


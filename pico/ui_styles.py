from writer_v2 import Writer
import lbaskerv20bold as font1
import lbaskerv20 as font

class MarginWriter(Writer):
    def __init__(self, device, font, margin_left=0, verbose=False):
        super().__init__(device, font, verbose)
        self.margin_left = margin_left

    def _newline(self):
        super()._newline()
        self._getstate().text_col = self.margin_left

def render_modern(epd, text):
    # 1. Top header bar (dark filled box with inverted white text)
    epd.imageblack.fill_rect(0, 0, epd.width, 50, 0x00)
    
    wri_bold = Writer(epd.imageblack, font1, False)
    wri = Writer(epd.imageblack, font, False)

    # Header text
    Writer.set_textpos(epd.imageblack, 17, 20)
    wri_bold.printstring("SEATTLE . NW . OVERCAST", invert=False)

    # Temperature right-aligned
    Writer.set_textpos(epd.imageblack, 17, epd.width - 60)
    wri_bold.printstring("14 F", invert=False)

    # 2. Main body
    # Split text dynamically so it adapts to different poem lengths
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    midpoint = len(lines) // 2 if len(lines) > 1 else 1
    
    black_text = "\n".join(lines[:midpoint]) + "\n"
    red_text = "\n".join(lines[midpoint:]) + "\n" if len(lines) > midpoint else ""

    wri_poem = MarginWriter(epd.imageblack, font, margin_left=45)
    Writer.set_textpos(epd.imageblack, 75, 45)
    wri_poem.printstring(black_text, invert=True)
    
    if red_text:
        wri_red_poem = MarginWriter(epd.imagered, font, margin_left=45)
        # Get the row position after writing black text
        s_black = wri_poem._getstate()
        Writer.set_textpos(epd.imagered, s_black.text_row, 45)
        wri_red_poem.printstring(red_text, invert=True)
        final_row = wri_red_poem._getstate().text_row
    else:
        final_row = wri_poem._getstate().text_row

    # Vertical line separator (adaptive height)
    line_height = final_row - 75
    if line_height < 0:
        line_height = 0
    epd.imageblack.vline(25, 75, line_height, 0x00)
    epd.imageblack.vline(26, 75, line_height, 0x00) # double-thick line

    # 3. Bottom footer
    bottom_y = epd.height - 40
    
    # Small labels using framebuf built-in text (8x8 pixels)
    epd.imageblack.text("WIND", 25, bottom_y - 12, 0x00)
    epd.imageblack.text("HUMIDITY", 100, bottom_y - 12, 0x00)
    epd.imageblack.text("FEELS", 195, bottom_y - 12, 0x00)
    epd.imageblack.text("UPDATED", 265, bottom_y - 12, 0x00)

    # Values using larger font
    Writer.set_textpos(epd.imageblack, bottom_y, 25)
    wri.printstring("12 mph\n", invert=True)
    
    Writer.set_textpos(epd.imageblack, bottom_y, 100)
    wri.printstring("78%\n", invert=True)
    
    Writer.set_textpos(epd.imageblack, bottom_y, 195)
    wri.printstring("6 F\n", invert=True)
    
    Writer.set_textpos(epd.imageblack, bottom_y, 265)
    wri.printstring("06:42\n", invert=True)

def render_broadsheet(epd, text):
    wri_bold = Writer(epd.imageblack, font1, False)
    wri = Writer(epd.imageblack, font, False)

    # 1. Header
    Writer.set_textpos(epd.imageblack, 20, 25)
    wri_bold.printstring("SEATTLE, WA")
    
    epd.imageblack.text("SUNDAY, MARCH 15 . OVERCAST . NW WINDS 12MPH", 25, 45, 0x00)

    Writer.set_textpos(epd.imageblack, 25, epd.width - 60)
    wri_bold.printstring("14 F")

    # Separator line
    epd.imageblack.hline(25, 60, epd.width - 50, 0x00)
    epd.imageblack.hline(25, 61, epd.width - 50, 0x00) # double thick

    # 2. Main body
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    midpoint = len(lines) // 2 if len(lines) > 1 else 1
    
    black_text = "\n".join(lines[:midpoint]) + "\n"
    red_text = "\n".join(lines[midpoint:]) + "\n" if len(lines) > midpoint else ""

    wri_poem = MarginWriter(epd.imageblack, font, margin_left=25)
    Writer.set_textpos(epd.imageblack, 90, 25)
    wri_poem.printstring(black_text)
    
    if red_text:
        wri_red_poem = MarginWriter(epd.imagered, font, margin_left=25)
        s_black = wri_poem._getstate()
        Writer.set_textpos(epd.imagered, s_black.text_row, 25)
        wri_red_poem.printstring(red_text)

    # 3. Bottom footer
    bottom_y = epd.height - 40
    epd.imageblack.hline(25, bottom_y - 15, epd.width - 50, 0x00)
    
    epd.imageblack.text("UPDATED 06:42", 25, bottom_y, 0x00)
    epd.imageblack.text("NEXT REFRESH: 30 MIN", epd.width - 185, bottom_y, 0x00)

def render_minimalist(epd, text):
    wri_bold = Writer(epd.imageblack, font1, False)
    wri = Writer(epd.imageblack, font, False)

    # 1. Header
    Writer.set_textpos(epd.imageblack, 30, 30)
    wri_bold.printstring("18 C")
    
    epd.imageblack.text("RAINY", 100, 40, 0x00)
    
    # Cloud icon using red line art (approximate location right side)
    epd.imagered.ellipse(epd.width - 45, 45, 12, 12, 0x00)
    epd.imagered.ellipse(epd.width - 32, 45, 8, 8, 0x00)
    epd.imagered.hline(epd.width - 57, 45, 20, 0x00)
    epd.imagered.vline(epd.width - 50, 50, 10, 0x00)
    epd.imagered.vline(epd.width - 45, 50, 15, 0x00)
    epd.imagered.vline(epd.width - 40, 50, 10, 0x00)

    # Hairline header divider
    epd.imageblack.hline(30, 80, epd.width - 60, 0x00)

    # 2. Main Body with alternating line colors
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    
    current_y = 100
    for idx, line in enumerate(lines):
        line += "\n"
        if idx % 2 == 0:
            wri_poem = MarginWriter(epd.imageblack, font, margin_left=40)
            Writer.set_textpos(epd.imageblack, current_y, 40)
            wri_poem.printstring(line)
            current_y = wri_poem._getstate().text_row
        else:
            wri_red_poem = MarginWriter(epd.imagered, font1, margin_left=40)
            Writer.set_textpos(epd.imagered, current_y, 40)
            wri_red_poem.printstring(line)
            current_y = wri_red_poem._getstate().text_row

    # Dynamic Red vertical line spanning the height of the poem text
    poem_height = current_y - 100
    epd.imagered.vline(30, 100, poem_height, 0x00)
    epd.imagered.vline(31, 100, poem_height, 0x00)

    # 3. Footer
    bottom_y = epd.height - 35
    
    # Inverted black box for time
    epd.imageblack.fill_rect(30, bottom_y - 3, 40, 15, 0x00)
    epd.imageblack.text("19:44", 32, bottom_y, 0xff)

    # Red location text
    epd.imagered.text("LOC:", epd.width - 130, bottom_y, 0x00)
    epd.imagered.text("LONDON, UK", epd.width - 90, bottom_y, 0x00)


styles_list = [render_modern, render_broadsheet, render_minimalist]

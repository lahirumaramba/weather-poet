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

def _get_time_string(date_str):
    if len(date_str) > 5 and " " in date_str:
        return date_str.split(" ")[-1]
    return date_str

def _get_day_string(date_str):
    # Expects format like "2026-03-17 13:45"
    try:
        if " " in date_str:
            date_part = date_str.split(" ")[0]
            parts = date_part.split("-")
            if len(parts) == 3:
                y = int(parts[0])
                m = int(parts[1])
                d = int(parts[2])
                
                # Zeller's congruence for day of week
                if m < 3:
                    m += 12
                    y -= 1
                k = y % 100
                j = y // 100
                h = (d + 13 * (m + 1) // 5 + k + k // 4 + j // 4 + 5 * j) % 7
                
                days = ["SATURDAY", "SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
                return days[h]
    except Exception:
        pass
    return "UNKNOWN DAY"

def render_modern(epd, data):
    if not isinstance(data, dict):
        text = str(data)
        data = {}
    else:
        text = data.get("text", "")
        
    name = str(data.get("name", "SEATTLE")).upper()
    wind_dir = str(data.get("wind_dir", "NW")).upper()
    condition = str(data.get("condition_text", "OVERCAST")).upper()
    temp = str(data.get("temp_c", "14"))
    
    # 1. Top header bar (dark filled box with inverted white text)
    epd.imageblack.fill_rect(0, 0, epd.width, 50, 0x00)
    
    wri_bold = Writer(epd.imageblack, font1, False)
    wri = Writer(epd.imageblack, font, False)

    # Header text
    Writer.set_textpos(epd.imageblack, 17, 20)
    wri_bold.printstring(f"{name} . {condition}", invert=False)

    # Temperature right-aligned
    Writer.set_textpos(epd.imageblack, 17, epd.width - 60)
    wri_bold.printstring(f"{temp} C", invert=False)

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
    
    wind_kph = str(data.get("wind_kph", "12"))
    feels_like = str(data.get("feelslike_c", "6"))
    last_updated = str(data.get("last_updated", "06:42"))
    time_str = _get_time_string(last_updated)

    # Small labels using framebuf built-in text (8x8 pixels)
    epd.imageblack.text("WIND", 25, bottom_y - 12, 0x00)
    epd.imageblack.text("FEELS", 200, bottom_y - 12, 0x00)
    epd.imageblack.text("UPDATED", 275, bottom_y - 12, 0x00)

    # Values using larger font
    Writer.set_textpos(epd.imageblack, bottom_y, 25)
    wri.printstring(f"{wind_kph}kph\n", invert=True)
    
    Writer.set_textpos(epd.imageblack, bottom_y, 110)
    wri.printstring(f"{wind_dir}\n", invert=True)
    
    Writer.set_textpos(epd.imageblack, bottom_y, 200)
    wri.printstring(f"{feels_like} C\n", invert=True)
    
    Writer.set_textpos(epd.imageblack, bottom_y, 275)
    wri.printstring(f"{time_str}\n", invert=True)

def render_broadsheet(epd, data):
    if not isinstance(data, dict):
        text = str(data)
        data = {}
    else:
        text = data.get("text", "")
        
    name = str(data.get("name", "SEATTLE")).upper()
    country = str(data.get("country", "WA")).upper()
    condition = str(data.get("condition_text", "OVERCAST")).upper()
    temp = str(data.get("temp_c", "14"))
    wind_kph = str(data.get("wind_kph", "12"))
    wind_dir = str(data.get("wind_dir", "NW")).upper()
    last_updated = str(data.get("last_updated", "06:42")).upper()
    feels_like = str(data.get("feelslike_c", "6"))
    time_str = _get_time_string(last_updated)
    day_str = _get_day_string(last_updated)

    wri_bold = Writer(epd.imageblack, font1, False)
    wri = Writer(epd.imageblack, font, False)

    # 1. Header
    Writer.set_textpos(epd.imageblack, 20, 25)
    wri_bold.printstring(f"{name}, {country}")
    
    epd.imageblack.text(f"{day_str} . {wind_dir} WINDS {wind_kph}KPH", 25, 45, 0x00)

    Writer.set_textpos(epd.imageblack, 25, epd.width - 60)
    wri_bold.printstring(f"{temp} C", invert=True)

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
        final_row = wri_red_poem._getstate().text_row
    else:
        final_row = wri_poem._getstate().text_row

    # 3. Bottom footer
    bottom_y = epd.height - 40
    
    epd.imageblack.text(f"{condition}", 25, bottom_y - 30, 0x00)
    
    epd.imageblack.hline(25, bottom_y - 15, epd.width - 50, 0x00)
    
    epd.imageblack.text(f"UPDATED {time_str}", 25, bottom_y, 0x00)
    epd.imageblack.text(f"FEELS: {feels_like} C", epd.width - 200, bottom_y, 0x00)

def render_minimalist(epd, data):
    if not isinstance(data, dict):
        text = str(data)
        data = {}
    else:
        text = data.get("text", "")
        
    name = str(data.get("name", "LONDON")).upper()
    country = str(data.get("country", "UK")).upper()
    condition = str(data.get("condition_text", "RAINY")).upper()
    temp = str(data.get("temp_c", "18"))
    last_updated = str(data.get("last_updated", "19:44"))
    time_str = _get_time_string(last_updated)

    wri_bold = Writer(epd.imageblack, font1, False)
    wri = Writer(epd.imageblack, font, False)

    # 1. Header
    Writer.set_textpos(epd.imageblack, 30, 30)
    wri_bold.printstring(f"{temp} C")
    
    epd.imageblack.text(f"{condition}", 100, 40, 0x00)
    
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
    epd.imageblack.fill_rect(30, bottom_y - 3, 45, 15, 0x00)
    epd.imageblack.text(f"{time_str}", 32, bottom_y, 0xff)

    # Red location text
    country_name = f"{name}, {country}"[:16]
    epd.imagered.text(country_name, epd.width - 145, bottom_y, 0x00)

def render_book(epd, data):
    if not isinstance(data, dict):
        text = str(data)
    else:
        text = data.get("text", "")

    wri = Writer(epd.imageblack, font, False)
    wri_red_bold = Writer(epd.imagered, font1, False)

    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

    # Extract first letter for the drop cap
    first_char = ""
    if lines and len(lines[0]) > 0:
        if lines[0][0] in ["'", '"']:  # Strip existing quotes
            lines[0] = lines[0][1:]
        if len(lines[0]) > 0:
            first_char = lines[0][0]
            lines[0] = lines[0][1:]

    # Estimate height (font is roughly 25px per line with baseline)
    # Using 35 for line spacing to give it an airy, quote-like feel.
    line_spacing = 35
    total_height = len(lines) * line_spacing
    
    start_y = (epd.height - total_height) // 2
    if start_y < 50:
        start_y = 50
        
    current_y = start_y

    # --- Draw decorative book edges and quotation marks ---
    def draw_quote(buf, bx, by):
        # A simple aesthetic large quote shape
        buf.fill_rect(bx, by, 7, 7, 0x00)
        buf.line(bx+7, by+7, bx+2, by+15, 0x00)
        buf.line(bx+6, by+7, bx+1, by+15, 0x00)
        
        buf.fill_rect(bx+12, by, 7, 7, 0x00)
        buf.line(bx+19, by+7, bx+14, by+15, 0x00)
        buf.line(bx+18, by+7, bx+13, by+15, 0x00)

    # Top-Left Bracket and Quote
    epd.imageblack.vline(15, 20, 60, 0x00)
    epd.imageblack.hline(15, 20, 40, 0x00)
    draw_quote(epd.imageblack, 65, 12)
    epd.imageblack.hline(93, 20, 20, 0x00)

    # Bottom-Right Bracket and Quote
    epd.imageblack.vline(epd.width - 15, epd.height - 80, 60, 0x00)
    epd.imageblack.hline(epd.width - 55, epd.height - 20, 40, 0x00)
    draw_quote(epd.imageblack, epd.width - 92, epd.height - 28)
    epd.imageblack.hline(epd.width - 110, epd.height - 20, 10, 0x00)

    for idx, line in enumerate(lines):
        disp_line = line
            
        # Calculate full width for centering
        if idx == 0 and first_char:
            fc_width = wri_red_bold.stringlen(first_char) + 2
            str_width = wri.stringlen(disp_line) + fc_width
        else:
            str_width = wri.stringlen(disp_line)
            
        start_x = (epd.width - str_width) // 2
        if start_x < 0:
            start_x = 0
            
        if idx == 0 and first_char:
            Writer.set_textpos(epd.imagered, current_y, start_x)
            wri_red_bold.printstring(first_char, invert=True)
            
            # Thick red underline to emphasize the drop cap size
            epd.imagered.hline(start_x - 2, current_y + 20, fc_width + 1, 0x00)
            epd.imagered.hline(start_x - 2, current_y + 21, fc_width + 1, 0x00)
            
            start_x += fc_width
            
        wri_poem = MarginWriter(epd.imageblack, font, margin_left=start_x)
        Writer.set_textpos(epd.imageblack, current_y, start_x)
        wri_poem.printstring(disp_line, invert=True)
        current_y += line_spacing

styles_list = [render_book, render_modern, render_broadsheet, render_minimalist]

# *****************************************************************************
# * | File        :	  Pico_ePaper-3.7.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2021-06-01
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from machine import Pin, SPI
import framebuf
import utime

# Display resolution
EPD_WIDTH       = 400
EPD_HEIGHT      = 300

SCK_PIN         = 10
DIN_PIN         = 11
RST_PIN         = 12
DC_PIN          = 8
CS_PIN          = 9
BUSY_PIN        = 13


class Screen(framebuf.FrameBuffer):
    def __init__(self, buffer, width, height):
        self.width = width
        self.height = height
        self.buffer = buffer
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        

class EPD_4in2_B:
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.sck_pin = 1
        self.din_pin = 1
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.flag = 0
        
        self.spi = SPI(1,baudrate=4000_000,sck=Pin(SCK_PIN),mosi=Pin(DIN_PIN))
        # self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        
        
        self.buffer_black = bytearray(self.height * self.width // 8)
        self.buffer_red = bytearray(self.height * self.width // 8)
        self.imageblack = Screen(self.buffer_black, self.width, self.height)
        self.imagered = Screen(self.buffer_red, self.width, self.height)
        
        self.EPD_4IN2B_Init()
        self.EPD_4IN2B_Clear()
        utime.sleep_ms(500)

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    def gpio_init(self):
        self.spi.deinit()
    
    def spi_init(self):
        self.spi = SPI(1,baudrate=4000_000,sck=Pin(SCK_PIN),mosi=Pin(DIN_PIN))
        self.dc_pin = Pin(DC_PIN, Pin.OUT)


    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200) 
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200)


    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def send_data1(self, buf):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytearray(buf))
        self.digital_write(self.cs_pin, 1)

    def send_read(self):
        j = 0x00
        self.sck_pin = Pin(SCK_PIN, Pin.OUT)
        self.din_pin = Pin(DIN_PIN, Pin.IN, Pin.PULL_UP)
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        for i in range(0, 8):
            self.digital_write(self.sck_pin, 0)
            j = j << 1
            if(self.digital_read(self.din_pin) == 1):
                j = j | 0x01
            else:
                j = j & 0xfe
            self.digital_write(self.sck_pin, 1)
        self.digital_write(self.cs_pin, 1)
        return j
        
    def ReadBusy(self):
        print("e-Paper busy")
        if(self.flag == 1):
            while(self.digital_read(self.busy_pin) == 1): 
                self.delay_ms(100) 
        
        else:
            while(self.digital_read(self.busy_pin) == 0): 
                self.delay_ms(100) 
        print("e-Paper busy release")
        
        
    def TurnOnDisplay(self):
        if(self.flag == 1):
            self.send_command(0x22)
            self.send_data(0xF7)	
            self.send_command(0x20)
            self.ReadBusy()
        
        else:
            self.send_command(0x12)
            self.delay_ms(100) 
            self.ReadBusy()
            
    def EPD_4IN2B_Init(self):
        i = 0x00
        self.reset()
        self.send_command(0x2F)
        
        self.delay_ms(100) 
        self.gpio_init()
        i = self.send_read()
        print(i)
        self.spi_init()

        if(i == 0x01):
            self.flag = 1
            self.ReadBusy()
            self.send_command(0x12)
            self.ReadBusy()

            self.send_command(0x3C)
            self.send_data(0x05)	

            self.send_command(0x18)
            self.send_data(0x80)	

            self.send_command(0x11)      
            self.send_data(0x03)

            self.send_command(0x44) 
            self.send_data(0x00)
            self.send_data(self.width//8-1)

            self.send_command(0x45)        
            self.send_data(0x00)
            self.send_data(0x00) 
            self.send_data((self.height-1)%256)    
            self.send_data((self.height-1)//256)

            self.send_command(0x4E)
            self.send_data(0x00)
            self.send_command(0x4F)  
            self.send_data(0x00)    
            self.send_data(0x00)
            self.ReadBusy()

        else:
            self.flag = 0
            self.send_command(0x04)  # POWER_ON
            self.ReadBusy()

            self.send_command(0x00)  # panel setting
            self.send_data(0x0f)

            
    def EPD_4IN2B_Clear(self):
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1

        if(self.flag == 1):
            self.send_command(0x24)
            self.send_data1([0xff] * high * wide)
                    
            self.send_command(0x26)
            self.send_data1([0x00] * high * wide)
        
        else:
            self.send_command(0x10)
            self.send_data1([0xff] * high * wide)
                    
            self.send_command(0x13)
            self.send_data1([0x00] * high * wide)

        self.TurnOnDisplay()
        
    def EPD_4IN2B_Display(self,blackImage,redImage):
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1
        
        if(self.flag == 1):
            self.send_command(0x24)
            self.send_data1(blackImage)
                    
            self.send_command(0x26)
            for j in range(0, high):
                for i in range(0, wide):
                    self.send_data(~redImage[i + j * wide]) 
        
        else:
            self.send_command(0x10)
            self.send_data1(blackImage)
                    
            self.send_command(0x13)
            for j in range(0, high):
                for i in range(0, wide):
                    self.send_data(~redImage[i + j * wide]) 

        self.TurnOnDisplay()
        
        
    def Sleep(self):
        if(self.flag == 1):
            self.send_command(0X10) 
            self.send_data(0x03)
        
        else:
            self.send_command(0X50) 
            self.send_data(0xf7)             
            self.send_command(0X02)
            self.ReadBusy() 
            self.send_command(0X07) 
            self.send_data(0xA5)
    
# if __name__=='__main__':
#     
#     epd = EPD_4in2_B()
#     
#     from writer import Writer
#     
#     import lbaskerv20 as font
#     import esteban20 as font2
#     
#     epd.imageblack.fill(0xff)
#     epd.imagered.fill(0xff)
    
#     print(freesans20.height())
    
#     wri = Writer(epd.imageblack, font, True)
#     Writer.set_textpos(epd.imageblack, 10, 0)  # verbose = False to suppress console output
#     wri.printstring("A whisper of snow, a frigid kiss,\nNorthwest winds in chilling bliss.\nSun obscured, a cloudy hold,\nFourteen Fahrenheit, a winter's scold.\n", True)
#     
#     wri2 = Writer(epd.imageblack, font2, True)
#     Writer.set_textpos(epd.imageblack, 100, 0)  # verbose = False to suppress console output
#     wri2.printstring("A whisper of snow, a frigid kiss,\nNorthwest winds in chilling bliss.\nSun obscured, a cloudy hold,\nFourteen Fahrenheit, a winter's scold.\n", True)
#     wri.printstring('20 Feb 2025\n')
#     wri.printstring('5.48pm')
    
#     start_x = (EPD_WIDTH) // 2
#     start_y = (EPD_HEIGHT) // 2
    
#    wri_red = Writer(epd.imagered, freesans20, True)
#    Writer.set_textpos(epd.imagered, start_x, start_y)  # verbose = False to suppress console output
#    wri_red.printstring("A whisper of snow, a frigid kiss,\nNorthwest winds in chilling bliss.\nSun obscured, a cloudy hold,\nFourteen Fahrenheit, a winter's scold.\n", True)
#     wri_red.printstring('20 Feb 2025\n')
#     wri_red.printstring('5.48pm')
    
#     epd.EPD_4IN2B_Display(epd.buffer_black, epd.buffer_red)
    
#     import network
#     
#     ssid = 'BELL147'
#     password = 'DC76232EE3F1'
#     
#     wlan = network.WLAN(network.STA_IF)
#     wlan.active(True)
#     wlan.connect(ssid, password)
#     
#     import requests
#     
#     url = "https://cdn.weatherapi.com/weather/64x64/night/326.png"
#     response = requests.get(url)
#     #print(response)
#     binary_content = response.content
#     
#     def drawPixel(x, y, color):
#         epd.imageblack.text("Waveshare", 5, 10, 0x00)
#         epd.imageblack.pixel(10 + x, 90 + y, 0x00) 
#         print(x,y,color)
#         if y == 59:
#             epd.EPD_4IN2B_Display(epd.buffer_black,epd.buffer_red)
#         
#     from PNGdecoder import png
#     
#     png(binary_content, callback=drawPixel).render(0, 0)
#     epd.delay_ms(5000)
#     
#     epd.imageblack.fill(0xff)
#     epd.imagered.fill(0xff)
    
#     from logo import icon
#     
#     EPD_WIDTH = 400
#     EPD_HEIGHT = 300
#     
#     # Display the YouTube logo 
#     logo_width = 64 #400
#     logo_height = 64 #300
# 
#     # Calculate the starting point to center the logo
#     start_x = (EPD_WIDTH - logo_width) // 2
#     start_y = (EPD_HEIGHT - logo_height) // 2
# 
#     for y in range(logo_height):
#         for x in range(logo_width):
#             if (icon[y * (logo_width // 8) + (x // 8)] & (128 >> (x % 8))) == False:
#                 epd.imageblack.pixel(start_x + x, start_y + y, 0x00)
# 
#     epd.EPD_4IN2B_Display(epd.buffer_black,epd.buffer_red)
     
    #epd.imageblack.text("Waveshare", 5, 10, 0x00)
    #epd.imagered.text("Pico_ePaper-4.2-B", 5, 40, 0x00)
    #epd.imageblack.text("Raspberry Pico", 5, 70, 0x00)
    #epd.EPD_4IN2B_Display(epd.buffer_black,epd.buffer_red)

#     epd.delay_ms(5000)
#     
#     epd.imageblack.vline(10, 90, 60, 0x00)
#     epd.imagered.vline(90, 90, 60, 0x00)
#     epd.imageblack.hline(10, 90, 80, 0x00)
#     epd.imagered.hline(10, 150, 80, 0x00)
#     epd.imageblack.line(10, 90, 90, 150, 0x00)
#     epd.imagered.line(90, 90, 10, 150, 0x00)
#     epd.EPD_4IN2B_Display(epd.buffer_black,epd.buffer_red)
#     epd.delay_ms(5000)
#     
#     epd.imageblack.rect(10, 180, 50, 80, 0x00)
#     epd.imagered.fill_rect(70, 180, 50, 80, 0x00)
#     epd.EPD_4IN2B_Display(epd.buffer_black,epd.buffer_red)
#     epd.delay_ms(5000)
# 
#     epd.EPD_4IN2B_Clear()
#     epd.Sleep()


#!/usr/bin/env python

import os
import pigpio
import time
import rotary_encoder
from demo_opts import get_device
from luma.core.render import canvas
from luma.core.virtual import viewport
from PIL import ImageFont
from PIL import Image
from mpd import MPDClient

client = MPDClient()               # create client object
client.timeout = 10                # network timeout in seconds (floats allowed), default: None
client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
client.connect("localhost", 6600)  # connect to localhost:6600

device = get_device()
size = (60, 30)
offset = ((device.width - size[0]) // 2, (device.height - size[1]) // 2)
shadow_offset = (offset[0] + 1, offset[1] + 1)
virtualp = viewport(device, width=device.width, height=1000)
virtuals = viewport(device, width=device.width, height=1000)
virtual = viewport(device, width=device.width, height=1000)
playlists=sorted(os.listdir("/var/lib/mpd/playlists"))
artists=[]
global menu
global vol
global display
global menu_l
global menu_r
global menu_p
global menu_s
global pause
global status
global letters
global selected_songs
global selected_letter
global lous_list 
lous_list=[("The Black Keys","El Camino"),("The Black Keys","Brothers"),("The Black Keys","Magic Potion"),("The Cure","Greatest Hits"),
("Joni Mitchell","Clouds"),("I Am Kloot","Sky at Night"),("Paolo Nutini","Sunny Side Up"),("Paolo Nutini","These Streets"),("Amy MacDonald","This Is the Life"),
("Stevie Wonder","Number 1's"),("Everything Everything","Man Alive"),("Elbow","The Seldom Seen Kid"),("Joni Mitchell","Blue"),("Joni Mitchell","Ladies of the Canyon")]
selected_songs=[]
select_letter=[]
display="Main"
menu=0
vol=10
menu_l=0
menu_r=0
menu_p=0
menu_s=0
pause=0
letters=[]
status="on"
stations=["Absolute Radio","Absolute 60's","Absolute 70's","Absolute 80's","Absolute 90's",
"MosaiqueFM DJ","BBC Radio 4","BBC Radio 4 Extra","BBC 6 Music","Cork's 96FM","Main Menu"]
 
class decoder:

#   """Class to decode mechanical rotary encoder pulses."""

   def __init__(self, pi, gpioA, gpioB, callback):

#      """
#      Instantiate the class with the pi and gpios connected to
#      rotary encoder contacts A and B.  The common contact
#      should be connected to ground.  The callback is
#      called when the rotary encoder is turned.  It takes
#      one parameter which is +1 for clockwise and -1 for
#      counterclockwise.
#       """

      self.pi = pi
      self.gpioA = gpioA
      self.gpioB = gpioB
      self.callback = callback

      self.levA = 0
      self.levB = 0

      self.lastGpio = None

      self.pi.set_mode(gpioA, pigpio.INPUT)
      self.pi.set_mode(gpioB, pigpio.INPUT)

      self.pi.set_pull_up_down(gpioA, pigpio.PUD_UP)
      self.pi.set_pull_up_down(gpioB, pigpio.PUD_UP)

      self.cbA = self.pi.callback(gpioA, pigpio.EITHER_EDGE, self._pulse)
      self.cbB = self.pi.callback(gpioB, pigpio.EITHER_EDGE, self._pulse)

   def _pulse(self, gpio, level, tick):

#      """
#      Decode the rotary encoder pulse
#
#      """

      if gpio == self.gpioA:
         self.levA = level
      else:
         self.levB = level;

      if gpio != self.lastGpio: # debounce
         self.lastGpio = gpio

         if   gpio == self.gpioA and level == 1:
            if self.levB == 1:
               self.callback(1)
         elif gpio == self.gpioB and level == 1:
            if self.levA == 1:
               self.callback(-1)

   def cancel(self):

      """
      Cancel the rotary encoder decoder.
      """

      self.cbA.cancel()
      self.cbB.cancel()

if __name__ == "__main__":

   def make_font(name, size):
      font_path = os.path.abspath(os.path.join(
         os.path.dirname(__file__), 'fonts', name))
      return ImageFont.truetype(font_path, size)

   def callback_menu(way):

       global menu
       global menu_r
       global menu_l
       global menu_m
       global menu_p
       global menu_s
       global selected_letter
       if (status=="on"):
          menu += way
          if (display=="Main"):
             if (menu > 1):
                menu=0
             if (menu < 0):
                menu=1
             display_main(menu)
          if (display=="Radio" or display=="PlayR"):
             if (menu > 10):
                menu=0
             if (menu < 0):
                menu=10
             menu_r=menu
             display_radio()    
          if (display=="Letters"):
             if (menu > 11):
                menu=0
             if (menu < 0):
                menu=11
             menu_l=menu
             display_letters()
          if (display=="Playlists"):
             if (menu < 0):
                menu= len(selected_letter)-1
             if (menu == len(selected_letter)):
                menu=0
             menu_p=menu
             display_playlist()
          if (display=="Songs" or display=="PlayS"):
#             print ("menu_s " + str(menu_s) + ": length " + str(len(selected_songs)))
             if (menu < 0):
                menu = len(selected_songs)-1
             if (menu == len(selected_songs)):
                menu = 0
             menu_s=menu
             display_songs()
   def callback_vol(way):

      global vol
#      global menu
      if (status=="on"):
         vol += way
         if (vol>100):
            vol=100
         if (vol<0):
            vol=0
         client.setvol(vol)
         if (display=="Main"):
            display_main(menu)
         if (display=="Radio"):
            display_radio()
         if (display=="PlayR"):
            play_station() 
         if (display=="Letters"):
            display_letters() 
         if (display=="PlayS"):
            play_song()

   def button_menu(gpio, level, tick):
      global display
      global selected_letter
      global selected_songs
      global menu
      global menu_l
      global menu_p
      global menu_s
#      global letters
      if (status=="on"):
         inDisplay = display
         print(inDisplay)
         if (inDisplay=="Main"):
            if (menu==0):
               display="Radio"
               client.clear()
               client.load("radio_stations")
               menu=0 
               display_radio()
            if (menu==1):
               display="Letters"
               menu=0
               display_letters()
         if (inDisplay=="Radio" or inDisplay=="PlayR"):
            if(menu_r==10):
               display="Main"
               menu=0
               display_main(0)
            else:
               display="PlayR"
               client.play(menu_r)
               menu=0
               play_station()
         if (inDisplay=="Letters"):
            if (menu_l==11):
               menu_l=0
               menu=0
               display="Main"
               display_main(1)
            else:
               display="Playlists"
               selected_letter=[]
               create_playlists(letters)
               menu=0
               display_playlist()
         if (inDisplay=="Playlists"):
            print("playlist " + selected_letter[menu_p][1])
            if (selected_letter[menu_p][1] == "Menu"):
               menu_p=0
               menu=0
               display="Letters"
               display_letters()
            else:
               print("loading " + selected_letter[menu_p][0] + " " + selected_letter[menu_p][1]) 
               client.clear()
               album = selected_letter[menu_p][0] + "_" + selected_letter[menu_p][1]
               client.load(album)
               display="Songs"
               selected_songs=[]
               menu=0
               create_songs()
               display_songs()
         if (inDisplay=="Songs" or inDisplay=="PlayS"):
            print("Songs")
            if (selected_songs[menu_s][2] == "Back"):
               print("back " + selected_songs[menu_s][2])
               menu_s=0
               menu=0
               display="Playlists"
               display_playlist()
            else: 
               print("playing " + str(menu_s) + str(selected_songs[menu_s]))
               display="PlayS"
               client.play(menu_s)
               menu=0
               play_song()

   def button_vol(gpio, level, tick):
      global status
      if (status=="off"):
         status="on"
         device.show()
      else :
         status="off"
         client.stop()
         device.hide() 

   def display_main(menu):
#       global vol
       radio_img_path = "/home/pi/luma.examples/examples/images/Radio.png"
       radio_logo = Image.open(radio_img_path).convert("RGBA") \
        .transform(device.size, Image.AFFINE, (1, 0, 0, 0, 1, 0), Image.BILINEAR) \
        .convert("L") \
        .convert(device.mode)


       music_img_path = "/home/pi/luma.examples/examples/images/Music.png"
       music_logo = Image.open(music_img_path).convert("RGBA") \
        .transform(device.size, Image.AFFINE, (1, 0, 0, 0, 1, 0), Image.BILINEAR) \
        .convert("L") \
        .convert(device.mode)


       if (menu==0):	
          with canvas(device) as draw:
             draw.bitmap((0, 0), radio_logo, fill="white")
             draw.text((0,55), "vol " + str(vol) + "%", fill="white",font=font12)

       if (menu==1):
           with canvas(device) as draw:
             draw.bitmap((0, 0), music_logo, fill="white")
             draw.text((0, 55), "vol " + str(vol) + "%", fill="white",font=font12)


   def display_radio():
 #     global menu_r
 #     global stations
      station=stations[menu_r]
      with canvas(device) as draw:
         draw.text((0,5), "select...", fill="white", font=font10)
         draw.text((5,25), station, fill="white", font=font15)

   def play_station():
#      global menu_r  
#      global vol
#      client.play(menu_r)
      station = stations[menu_r]
      with canvas(device) as draw:
         draw.text((0,5), "playing", fill="white", font=font10)
         draw.text((5,25), station, fill="white", font=font15)
         draw.text((0,55), "vol " + str(vol) + "%", fill="white",font=font12)

   def display_letters():
       global letters
       print ("In Letters ")
       if (menu_l==0):
          with canvas(device) as draw:
             draw.multiline_text(offset,"Lou's List", fill="white", align="center", spacing=-1, font=font18)
          letters=["LOU"]
       if (menu_l==1):
          with canvas(device) as draw:
             draw.multiline_text(offset,"A B", fill="white", align="center", spacing=-1, font=font18)
          letters=["A","B"]
       if (menu_l==2):
          with canvas(device) as draw:
             draw.multiline_text(offset,"C D", fill="white", align="center", spacing=-1, font=font18)
          letters=["C","D"]
       if (menu_l==3):
          with canvas(device) as draw:
             draw.multiline_text(offset,"E F G H I", fill="white", align="center", spacing=-1, font=font18)
          letters=["E","F","G","H","I"]
       if (menu_l==4):
          with canvas(device) as draw:
             draw.multiline_text(offset,"J K", fill="white", align="center", spacing=-1, font=font18)
          letters=["J","K"]
       if (menu_l==5):
          with canvas(device) as draw:
             draw.multiline_text(offset,"L M N", fill="white", align="center", spacing=-1, font=font18)
          letters=["L","M","N"]
       if (menu_l==6):
          with canvas(device) as draw:
             draw.multiline_text(offset,"O P Q R", fill="white", align="center", spacing=-1, font=font18)
          letters=["O","P","Q","R"]
       if (menu_l==7):
          with canvas(device) as draw:
             draw.multiline_text(offset,"S", fill="white", align="center", spacing=-1, font=font18)
          letters=["S"]
       if (menu_l==8):
          with canvas(device) as draw:
             draw.multiline_text(offset,"T", fill="white", align="center", spacing=-1, font=font18)
          letters=["T"]
       if (menu_l==9):
          with canvas(device) as draw:
             draw.multiline_text(offset,"U V W", fill="white", align="center", spacing=-1, font=font18)
          letters=["U","V","W"]
       if (menu_l==10):
          with canvas(device) as draw:
             draw.multiline_text(offset,"X Y Z", fill="white", align="center", spacing=-1, font=font18)
          letters=["X","Y","Z"]
       if (menu_l==11):
           with canvas(device) as draw:
             draw.multiline_text(offset,"Main Menu", fill="white", align="center", spacing=-1, font=font10)

   def create_playlists(letters):
      global selected_letter
      if (letters[0]=="LOU"):
         selected_letter = lous_list
      else:
         for file in playlists:
            for letter in letters:
               if file.startswith(letter):
                  l=len(file) 
                  filename = file[:l-4]
                  albumArtist = filename.split('_',1)[0]
                  albumTitle = filename.split('_',1)[1]
 #                 print ("x " + albumArtist)
 #                 print ("x " + albumTitle)
                  selected_letter.append((albumArtist,albumTitle))
      selected_letter.append(("Main","Menu"))

   def display_playlist():
#      print ("dp " + str(menu_p))
      stalbum=selected_letter[menu_p]
      albumArtist = stalbum[0]
      albumTitle = stalbum[1]
      with canvas(device) as draw:
         draw.text((0,5), "select", fill="white", font=font10)
         draw.text((5,18), albumArtist, fill="white", font=font10)
         draw.text((5,30), albumTitle, fill="white", font=font10)
         draw.text((0,55), "vol " + str(vol) + "%", fill="white",font=font12)

   def display_songs():
#      global selected_songs
#      global menu_s
      stalbum=selected_songs[menu_s]
#      print ("ds " + stalbum[1] + " " + stalbum[2])
      albumArtist=stalbum[0]
      albumTitle=stalbum[1]
      albumSong=stalbum[2]
      with canvas(device) as draw:
         draw.text((0,5), "select", fill="white", font=font10)
         draw.text((5,18), albumArtist, fill="white", font=font10)
         draw.text((5,30), albumTitle, fill="white", font=font10)
         draw.text((5,43), albumSong, fill="white", font=font10)
         draw.text((0,55), "vol " + str(vol) + "%", fill="white",font=font12) 

   def create_songs():
      global selected_songs
      albumArtist=""
      albumTitle=""
      for song in client.playlistinfo():
         sts=song["file"]
         albumArtist = sts.split('/',1)[0]
         albumTitle = sts.split('/',-1)[1]
         albumSong = sts.rsplit('/',1)[1].split('.',1)[0]
         artist_in_title = albumSong.split("-",1)
         if len(artist_in_title)>1:
            albumSong = str(menu_s+1) + "- " + artist_in_title[1]
         selected_songs.append((albumArtist,albumTitle,albumSong))
      selected_songs.append((albumArtist,albumTitle,"Back"))

   def play_song():
      print ("play_song " + str(menu_s))
      #change current song for idle but need to loop/while?
      song = client.currentsong()
      stsong=song["file"]
#      print ("song is " + stsong)
      songArtist = stsong.split('/',1)[0]
      songTitle = stsong.rsplit('/',1)[1].split('.',1)[0]
      artist_in_title = songTitle.split("-",1)
      if len(artist_in_title)>1:
         songTitle = str(menu_s+1) + "- " + artist_in_title[1]
      print ("s " + songArtist)
      print ("s " + songTitle)
      with canvas(device) as draw:
         draw.text((0,5), "playing", fill="white", font=font10)
         draw.text((5,20), songArtist, fill="white", font=font10)
         draw.text((5,37), songTitle, fill="white", font=font10)
         draw.text((0,55), "vol " + str(vol) + "%", fill="white",font=font12)

   print(client.mpd_version)             
   pi = pigpio.pi()
   font10 = make_font("/home/pi/luma.examples/examples/fonts/code2000.ttf", 12)
   font12 = make_font("/home/pi/luma.examples/examples/fonts/ProggyTiny.ttf",12)
   font15 = make_font("/home/pi/luma.examples/examples/fonts/code2000.ttf", 15)
   font18 = make_font("/home/pi/luma.examples/examples/fonts/code2000.ttf", 18)
   pi.set_mode(15, pigpio.INPUT)
   pi.set_mode(6, pigpio.INPUT)
   pi.set_mode(9,pigpio.INPUT)
   pi.set_mode(10,pigpio.OUTPUT)
   pi.set_pull_up_down(15, pigpio.PUD_UP)
   pi.set_pull_up_down(6, pigpio.PUD_UP)
#   pi.set_pull_up_down(9,pigpio.PUD_DOWN)
#   pi.write(10,0)
   decoder_menu = rotary_encoder.decoder(pi, 4, 17, callback_menu)
   decoder_vol = rotary_encoder.decoder(pi, 16, 12, callback_vol)
   cb1 =  pi.callback(15, pigpio.FALLING_EDGE,button_menu)
   cb2 =  pi.callback(6, pigpio.FALLING_EDGE,button_vol)
#   cb3 =  pi.callback(9, pigpio.RISING_EDGE,button_on_off)
   display_main(0)
   while True:
      a=1         

   time.sleep(300)

   decoder.cancel()
   client.close()                     # send the close command
   client.disconnect() 
   pi.stop()


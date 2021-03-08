#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pyaudio
import wave
import sys
import librosa, librosa.display
import IPython.display as ipd
import numpy as np
import soundfile as sf
import pygame
import struct
import msvcrt
import math

#INITAILIZE#

# create an audio object
#song onset calculation
x, sr = librosa.load('normal.wav')
onset_frames = librosa.onset.onset_detect(x, sr=sr, delta = 0.2, wait = 5) 
                                                    # delta = threshold to be onset (from mean of amplitude)
                                                    # wait = samples passed before finding another onset

onset_times = librosa.frames_to_time(onset_frames,sr=sr) # tranform the onset position from frames to actual time in the audio

song_length = librosa.get_duration(x,sr=sr)         # get audio length of time
onset_length = len(onset_times)                     # get number of onsets

x_2, sr_2 = librosa.load('easy.wav')
onset_frames_2 = librosa.onset.onset_detect(x_2, sr=sr_2, delta = 0.2, wait = 10)
onset_times_2 = librosa.frames_to_time(onset_frames_2,sr=sr_2)
song_length_2 = librosa.get_duration(x_2,sr=sr_2)
onset_length_2 = len(onset_times_2)

"""
print("Onsets:")
print(onset_times)
print("\nNumber of onsets:")
print(onset_length)
print("\nSong duration:")
print(song_length)

"""


#pygame
pygame.init()
display_width = 800
display_height = 600
black = (0,0,0)
white = (255,255,255)
red = (200,0,0)
green = (0,200,0)
lilac_blue = (176,190,240)
yellow = (255,255,100)
light_green = (193,255,193)
lighter_lilac_blue =(191,245,255)
pink = (205,142,153)
light_pink = (255,182,193)
purple = (128,0,128)


CHUNK = 2048                    #frame per buffer
audioFormat = pyaudio.paInt16   #16 bit int
audioChannel = 1                #number of recording channel
amp = 0

class SoundDetection():
    is_event_handler = True
   
    #initialise
    def __init__(self):
        # recording every frame
        record = pyaudio.PyAudio()
        audioRate = int(record.get_device_info_by_index(0)['defaultSampleRate'])  #rate of your recording
        self.stream = record.open(format=audioFormat, channels=audioChannel, rate=audioRate, input=True, frames_per_buffer=CHUNK)
        self.stream.stop_stream()
        
    #update when called
    def update(self, oldK):
        # reading audio samples
        if self.stream.is_stopped():
            self.stream.start_stream()
        audioDataBuffer = self.stream.read(CHUNK) #sample saved as a buffer
        
        k = max(struct.unpack('2048h', audioDataBuffer)) #unpack buffer with its format, return the maximum turple value to k
        
        
        #calculate amplitude threshold
        if k - oldK > 1500:   #if there's a big jump, recognise as attack of the onset
            onset = 1
            return k, onset
        else:
            onset = 0
            return k, onset


hit = 0
gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('AIST 2010 Project')
clock = pygame.time.Clock()
pause = False


class bar(pygame.sprite.Sprite):
    def __init__(self, display_width, display_height):
        super().__init__()
        # create a plain rectangle for the sprite image

        # find the rectangle that encloses the image
        self.rect = pygame.Rect(display_width-display_width/5,25,display_width/5,display_height)
        self.rect.w = display_width/5
        self.rect.h = display_height
        self.display_width = display_width
        self.display_height = display_height
        self.hit= 0

    def update(self,screen, *args):
        # any code here will happen every time the game loop updates
        self.rect.x=self.rect.x-10
        if self.hit == 1 :
            self.kill()
        pygame.draw.rect(screen, (255, 0, 0), [self.rect.x,25,self.rect.w, self.rect.h])
    # def remove(self, *groups):


def quitgame():
    #pygame.mixer.Sound.stop()
    pygame.quit()
    quit()
 
def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

def button(msg,x,y,w,h,ic,ac,action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(gameDisplay, ac,(x,y,w,h))
        if click[0] == 1 and action != None:
            action()         
    else:
        pygame.draw.rect(gameDisplay, ic,(x,y,w,h))
    smallText = pygame.font.SysFont(None,20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    gameDisplay.blit(textSurf, textRect)

def game_open():
    pygame.mixer.music.stop()
    open = True

    while open:
        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        gameDisplay.fill(yellow)
        largeText = pygame.font.SysFont(None,115)
        TextSurf, TextRect = text_objects('Beat Shouter!',largeText)
        TextRect.center = ((display_width/2),(display_height/2))
        gameDisplay.blit(TextSurf, TextRect)

        button("Play normal!",150,450,100,50,green,(0,255,0),game_loop)
        button("Play easy!",150,510,100,50,green,(0,255,0),game_loop_2)
        button("Quit",550,450,100,50,red,(255,0,0),quitgame)

        pygame.display.update()
        clock.tick(30)

def game_loop():  
    #global pause 
    global score
    global parts
    global amp
    
    test = SoundDetection()
    end = 0
    parts = 0
    score = 0 
    normalColor = lilac_blue
    speakColor = lighter_lilac_blue
    scoreColor = yellow

    bargroup=pygame.sprite.Group()
    pygame.mixer.music.load("normal.wav")
    pygame.mixer.music.play()
    dectectionArea =pygame.Rect(0,25,display_width/4,display_height)
    v=195
    dir = (-1, 0)
    size = 10

    player = pygame.Rect((display_width),25,display_width/12,display_height) 
    player2= pygame.Rect(display_width+ (onset_times[1]-onset_times[0])*v,25,display_width/12,display_height)
    player3= pygame.Rect(display_width+ (onset_times[2]-onset_times[0])*v,25,display_width/12,display_height)
    player4= pygame.Rect(display_width+ (onset_times[3]-onset_times[0])*v,25,display_width/12,display_height)
    player5= pygame.Rect(display_width+ (onset_times[4]-onset_times[0])*v,25,display_width/12,display_height)
    player6= pygame.Rect(display_width+ (onset_times[5]-onset_times[0])*v,25,display_width/12,display_height)
    player7= pygame.Rect(display_width+ (onset_times[6]-onset_times[0])*v,25,display_width/12,display_height)
    player8= pygame.Rect(display_width+ (onset_times[7]-onset_times[0])*v,25,display_width/12,display_height)
    player9= pygame.Rect(display_width+ (onset_times[8]-onset_times[0])*v,25,display_width/12,display_height)
    player10= pygame.Rect(display_width+ (onset_times[9]-onset_times[0])*v,25,display_width/12,display_height)
    player11= pygame.Rect(display_width+ (onset_times[10]-onset_times[0])*v,25,display_width/12,display_height)
    player12= pygame.Rect(display_width+ (onset_times[11]-onset_times[0])*v,25,display_width/12,display_height)

    MOVEEVENT,t = pygame.USEREVENT+1, 50 #note moving speed
    
    pygame.time.set_timer(MOVEEVENT, t)
    pygame.time.set_timer(MOVEEVENT, t)
    
    ADD_BAR = pygame.USEREVENT+2
    pygame.time.set_timer(ADD_BAR, 3000)
    gameExit = False
    while not gameExit:
        for event in pygame.event.get():
            if event.type == MOVEEVENT: # is called every 't' milliseconds
                player.move_ip(*[v*size for v in dir])
                player2.move_ip(*[v*size for v in dir])
                player3.move_ip(*[v*size for v in dir])
                player4.move_ip(*[v*size for v in dir])
                player5.move_ip(*[v*size for v in dir])
                player6.move_ip(*[v*size for v in dir])
                player7.move_ip(*[v*size for v in dir])
                player8.move_ip(*[v*size for v in dir])
                player9.move_ip(*[v*size for v in dir])
                player10.move_ip(*[v*size for v in dir])
                player11.move_ip(*[v*size for v in dir])
                player12.move_ip(*[v*size for v in dir])


            if event.type == ADD_BAR: #notworking
                bargroup.add(bar(display_width, display_height))
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
        bargroup.update(gameDisplay)

        # Draw detection area

        gameDisplay.fill(light_pink) 
        pygame.draw.rect(gameDisplay, normalColor, dectectionArea)
        
        
        #sound detection
        t = pygame.mixer.music.get_pos()
        
        #start next new note
        if (t >= onset_times[parts]*1000+200) and (t < song_length*1000) and (end == 0 or end == 2):
            if parts < onset_length-1:
                parts = parts + 1
            end = 1
        
        #allow current note for recording
        if (t >= (onset_times[parts]*1000)-200) and (t < song_length*1000) and (end == 1):
            end = 0
        k = amp
        amp, hit= test.update(k)
        
        #record hit
        if hit == 1:
            #check if the hit is within the hit-time region
            if (t <= onset_times[parts]*1000+200) and (t>= onset_times[parts]*1000-200) and (t < song_length*1000):
                if end == 0:
                    #print("VALID: +1 mark")
                    score = score + 1
                    end = 2
                    pygame.draw.rect(gameDisplay, scoreColor, dectectionArea)
            else:
                pygame.draw.rect(gameDisplay, speakColor, dectectionArea)
        
        # Draw collision boxes
        pygame.draw.rect(gameDisplay, red, player)
        pygame.draw.rect(gameDisplay, green, player2)
        pygame.draw.rect(gameDisplay, red, player3)
        pygame.draw.rect(gameDisplay, green, player4)
        pygame.draw.rect(gameDisplay, red, player5)
        pygame.draw.rect(gameDisplay, green, player6)
        pygame.draw.rect(gameDisplay, red, player7)
        pygame.draw.rect(gameDisplay, green, player8)
        pygame.draw.rect(gameDisplay, red, player9)
        pygame.draw.rect(gameDisplay, green, player10)
        pygame.draw.rect(gameDisplay, red, player11)
        pygame.draw.rect(gameDisplay, green, player12)
        text = pygame.font.SysFont(None,20)
        TextSurf, ScoreText = text_objects('Score: '+ str(score) ,text)
        ScoreText.topleft = (10,5)
        gameDisplay.blit(TextSurf, ScoreText)
        TextSurf, TimeText = text_objects('Time: '+ str(math.trunc(pygame.mixer.music.get_pos()/1000)) +' s',text)
        TimeText.topleft = (display_width-150,5)
        gameDisplay.blit(TextSurf, TimeText)
        
        TextSurf, HitText = text_objects('next note number: '+ str(parts) ,text)
        HitText.topleft = (300,5)
        gameDisplay.blit(TextSurf, HitText)
        
        TextSurf, MusicText = text_objects('Music: Canon in D' ,text)
        MusicText.topleft = (display_width-200,display_height-40)
        gameDisplay.blit(TextSurf, MusicText)
        
        button("Menu",10,display_height-40,100,display_height-20,green,(0,255,0),game_open)
        TextSurf, MenuText = text_objects('Menu' ,text)
        MenuText.topleft = (40,display_height-25)
        gameDisplay.blit(TextSurf, MenuText)
        
        pygame.display.update()
        clock.tick(60)
        
        
def game_loop_2():  
    #global pause 
    global score
    global parts
    global amp
    
    test = SoundDetection()
    end = 0
    parts = 0
    score = 0 
    normalColor = lilac_blue
    speakColor = lighter_lilac_blue
    scoreColor = yellow

    bargroup=pygame.sprite.Group()
    pygame.mixer.music.load("easy.wav")
    pygame.mixer.music.play()
    dectectionArea =pygame.Rect(0,25,display_width/4,display_height)
    v=200
    dir = (-1, 0)
    size = 10

    player = pygame.Rect((display_width),25,display_width/12,display_height) 
    player2= pygame.Rect(display_width+ (onset_times_2[1]-onset_times_2[0])*v,25,display_width/12,display_height)
    player3= pygame.Rect(display_width+ (onset_times_2[2]-onset_times_2[0])*v,25,display_width/12,display_height)
    player4= pygame.Rect(display_width+ (onset_times_2[3]-onset_times_2[0])*v,25,display_width/12,display_height)
    player5= pygame.Rect(display_width+ (onset_times_2[4]-onset_times_2[0])*v,25,display_width/12,display_height)
    player6= pygame.Rect(display_width+ (onset_times_2[5]-onset_times_2[0])*v,25,display_width/12,display_height)
    player7= pygame.Rect(display_width+ (onset_times_2[6]-onset_times_2[0])*v,25,display_width/12,display_height)
    player8= pygame.Rect(display_width+ (onset_times_2[7]-onset_times_2[0])*v,25,display_width/12,display_height)
    player9= pygame.Rect(display_width+ (onset_times_2[8]-onset_times_2[0])*v,25,display_width/12,display_height)

    MOVEEVENT,t = pygame.USEREVENT+1, 50 #note moving speed
    
    pygame.time.set_timer(MOVEEVENT, t)
    pygame.time.set_timer(MOVEEVENT, t)
    
    ADD_BAR = pygame.USEREVENT+2
    pygame.time.set_timer(ADD_BAR, 3000)
    gameExit = False
    while not gameExit:
        for event in pygame.event.get():
            if event.type == MOVEEVENT: # is called every 't' milliseconds
                player.move_ip(*[v*size for v in dir])
                player2.move_ip(*[v*size for v in dir])
                player3.move_ip(*[v*size for v in dir])
                player4.move_ip(*[v*size for v in dir])
                player5.move_ip(*[v*size for v in dir])
                player6.move_ip(*[v*size for v in dir])
                player7.move_ip(*[v*size for v in dir])
                player8.move_ip(*[v*size for v in dir])
                player9.move_ip(*[v*size for v in dir])


            if event.type == ADD_BAR: #notworking
                bargroup.add(bar(display_width, display_height))
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
        bargroup.update(gameDisplay)

        # Draw detection area

        gameDisplay.fill(light_green) 
        pygame.draw.rect(gameDisplay, normalColor, dectectionArea)
        
        
        #sound detection
        t = pygame.mixer.music.get_pos()
        
        #start next new note
        if (t >= onset_times_2[parts]*1000+200) and (t < song_length_2*1000) and (end == 0 or end == 2):
            if parts < onset_length_2-1:
                parts = parts + 1
            end = 1
        
        #allow current note for recording
        if (t >= (onset_times_2[parts]*1000)-200) and (t < song_length_2*1000) and (end == 1):
            end = 0
        
        k = amp
        amp, hit= test.update(k)
        
        #record hit
        if hit == 1:
            #check if the hit is within the hit-time region
            if (t <= onset_times_2[parts]*1000+200) and (t>= onset_times_2[parts]*1000-200) and (t < song_length_2*1000):
                if end == 0:
                    #print("VALID: +1 mark")
                    score = score + 1
                    end = 2
                    pygame.draw.rect(gameDisplay, scoreColor, dectectionArea)
            else:
                pygame.draw.rect(gameDisplay, speakColor, dectectionArea)
        
        # Draw collision boxes
        pygame.draw.rect(gameDisplay, purple, player)
        pygame.draw.rect(gameDisplay, pink, player2)
        pygame.draw.rect(gameDisplay, purple, player3)
        pygame.draw.rect(gameDisplay, pink, player4)
        pygame.draw.rect(gameDisplay, purple, player5)
        pygame.draw.rect(gameDisplay, pink, player6)
        pygame.draw.rect(gameDisplay, purple, player7)
        pygame.draw.rect(gameDisplay, pink, player8)
        pygame.draw.rect(gameDisplay, purple, player9)
        text = pygame.font.SysFont(None,20)
        TextSurf, ScoreText = text_objects('Score: '+ str(score) ,text)
        ScoreText.topleft = (10,5)
        gameDisplay.blit(TextSurf, ScoreText)
        TextSurf, TimeText = text_objects('Time: '+ str(math.trunc(pygame.mixer.music.get_pos()/1000)) +' s',text)
        TimeText.topleft = (display_width-150,5)
        gameDisplay.blit(TextSurf, TimeText)
        
        TextSurf, HitText = text_objects('next note number: '+ str(parts) ,text)
        HitText.topleft = (300,5)
        gameDisplay.blit(TextSurf, HitText)
        
        TextSurf, MusicText = text_objects('Music: Tanjiro No Uta' ,text)
        MusicText.topleft = (display_width-200,display_height-40)
        gameDisplay.blit(TextSurf, MusicText)
        
        button("Menu",10,display_height-40,100,display_height-20,green,(0,255,0),game_open)
        TextSurf, MenuText = text_objects('Menu' ,text)
        MenuText.topleft = (40,display_height-25)
        gameDisplay.blit(TextSurf, MenuText)
        
        pygame.display.update()
        clock.tick(60)
        

game_open()
game_loop()
game_loop_2()
pygame.quit()
quit()


# In[ ]:





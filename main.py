from machine import Pin,SPI,PWM
import framebuf
import utime
import os
import math

import modlcd

# ============ Start of Drive Code ================
#  == Copy and paste into your code ==
BL = 13  # Pins used for display screen
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

def colour(R,G,B):
# Get RED value
    rp = int(R*31/255) # range 0 to 31
    if rp < 0: rp = 0
    r = rp *8
# Get Green value - more complicated!
    gp = int(G*63/255) # range 0 - 63
    if gp < 0: gp = 0
    g = 0
    if gp & 1:  g = g + 8192
    if gp & 2:  g = g + 16384
    if gp & 4:  g = g + 32768
    if gp & 8:  g = g + 1
    if gp & 16: g = g + 2
    if gp & 32: g = g + 4
# Get BLUE value       
    bp =int(B*31/255) # range 0 - 31
    if bp < 0: bp = 0
    b = bp *256
    colour = r+g+b
    return colour
    
def ring(cx,cy,r,cc):   # Draws a circle - with centre (x,y), radius, colour 
    for angle in range(91):  # 0 to 90 degrees in 2s
        y3=int(r*math.sin(math.radians(angle)))
        x3=int(r*math.cos(math.radians(angle)))
        LCD.pixel(cx-x3,cy+y3,cc)  # 4 quadrants
        LCD.pixel(cx-x3,cy-y3,cc)
        LCD.pixel(cx+x3,cy+y3,cc)
        LCD.pixel(cx+x3,cy-y3,cc)

def hidePlayer(posx, posy, color):
    LCD.fill_rect(posx, posy, 35, 40, color)    

def displayPlayer(posx, posy, color):
    LCD.fill_rect(posx + 10, posy, 5, 5, color)
    LCD.fill_rect(posx + 15, posy, 5, 5, color)
    LCD.fill_rect(posx + 20, posy, 5, 5, color)
    
    LCD.fill_rect(posx + 10, posy + 5, 5, 5, color)
    LCD.fill_rect(posx + 15, posy + 5, 5, 5, color)
    LCD.fill_rect(posx + 20, posy + 5, 5, 5, color)
    
    LCD.fill_rect(posx + 15, posy + 10, 5, 5, color)
    
    LCD.fill_rect(posx + 5, posy + 15, 5, 5, color)
    LCD.fill_rect(posx + 10, posy + 15, 5, 5, color)
    LCD.fill_rect(posx + 15, posy + 15, 5, 5, color)
    LCD.fill_rect(posx + 20, posy + 15, 5, 5, color)
    LCD.fill_rect(posx + 25, posy + 15, 5, 5, color)

    
    LCD.fill_rect(posx, posy + 20, 5, 5, color)
    LCD.fill_rect(posx + 15, posy + 20, 5, 5, color)
    LCD.fill_rect(posx + 30, posy + 20, 5, 5, color)        
    
    LCD.fill_rect(posx + 10, posy + 25, 5, 5 , color)
    LCD.fill_rect(posx + 20, posy + 25, 5, 5, color)  

    LCD.fill_rect(posx + 10, posy + 30, 5, 5, color)
    LCD.fill_rect(posx + 20, posy + 30, 5, 5, color)  

    LCD.fill_rect(posx + 10 , posy + 35, 5, 5, color)
    LCD.fill_rect(posx + 20 , posy + 35, 5, 5, color)     


def displayWall(posx, posy, color):
    LCD.fill_rect(posx, posy, 5, 5, color)


def loadRoom(roomNumber):
    global virtualGraphicRoom
    virtualGraphicRoom = ""
    LCD.fill(colour(40,40,40))
    LCD.show()

    #print(data)
    
    i = 0
    x = 0
    y = 0
    
    filename = "room" + str(roomNumber) + ".txt"
    f = open(filename, "r")
    lines = f.readlines()

    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char == '\n':
                #print(' ')
                continue
            else:
                #print(i , ' ', char, x, ' ', y)
                if char == '1':
                    displayWall(5 * x, 5 * y, colour(0,255,0))
                virtualGraphicRoom += char    
        
    f.close()
    

def loadWorld(worldNumber):
    global virtualGraphicWorld
    virtualGraphicWorld = ""


    i = 0
    x = 0
    y = 0
    filename = "world" + str(worldNumber) + ".txt"
    f = open(filename, "r")
    lines = f.readlines()

    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char == '\n':
                continue
            else:
                #print(i , ' ', char, x, ' ', y)
                    
                virtualGraphicWorld += char    
                    

def getValueRoomFromGraphicPosition(gx, gy):
    vx = gx / 5
    vy = gy / 5
    
    i = (vy * 48) + vx 
    #print(gx, " " , gy, " / " , " ", vx, " " , vy, " : " ,i)
    return virtualGraphicRoom[int(i)] 


def checkCollisionLeft(posx, posy):
    for i in range(0, 40, 5):
        if getValueRoomFromGraphicPosition(posx - 5, posy + i) == "1":
            return 1
    return 0

def checkCollisionRight(posx, posy):
    print("checkCollisionRight")
    for i in range(0, 40, 5):
        if getValueRoomFromGraphicPosition(posx + 35, posy + i) == "1":
            print('collision right')
            return 1
    return 0

def checkCollisionUp(posx, posy):
    for i in range(0, 35, 5):
        if getValueRoomFromGraphicPosition(posx + i, posy - 5) == "1":
            return 1
    return 0        

def checkCollisionDown(posx, posy):
    print("checkCollisionDown")
    for i in range(0, 35, 5):
        if getValueRoomFromGraphicPosition(posx + i, posy + 40) == "1":
            print('collision down')
            return 1
    return 0   


# =========== Main ============
pwm = PWM(Pin(BL)) # Screen Brightness
pwm.freq(1000)
pwm.duty_u16(32768) # max 65535 - mid value

LCD = modlcd.LCD_1inch3()
# Background colour - dark grey
LCD.fill(colour(40,40,40))
LCD.show()

# Define pins for buttons and Joystick
keyA = Pin(15,Pin.IN,Pin.PULL_UP) # Normally 1 but 0 if pressed
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
keyX = Pin(19,Pin.IN,Pin.PULL_UP)
keyY= Pin(21,Pin.IN,Pin.PULL_UP)

up = Pin(2,Pin.IN,Pin.PULL_UP)
down = Pin(18,Pin.IN,Pin.PULL_UP)
left = Pin(16,Pin.IN,Pin.PULL_UP)
right = Pin(20,Pin.IN,Pin.PULL_UP)
ctrl = Pin(3,Pin.IN,Pin.PULL_UP)

# Draw background, frame, title and instructions
LCD.rect(0,0,240,240,LCD.red) # Red edge
# White Corners
LCD.pixel(1,1,LCD.white)     # LT
LCD.pixel(0,239,LCD.white)   # LB
LCD.pixel(239,0,LCD.white)   # RT
LCD.pixel(239,239,LCD.white) # RB
LCD.text('Raspico Roguelike', 20, 10, colour(0,0,255))
LCD.show()

def game():
    posx = 100
    posy = 100

    room = [0] * 10 * 10


    virtualGraphicRoom = ""
    virtualGraphicWorld = ""

    loadWorld(1)

    roomx = 4
    roomy = 2

    loadRoom(roomy * 10 + roomx)

    #displayRoom(room)
    print("room24")

    displayPlayer(posx, posy, LCD.white)


    currentPlayerWorldX = 4;
    currentPlayerWorldY = 2;


    running = True # Loop control
    # =========== Main loop ===============
    while(running):
        if keyA.value() == 0:
            print("A")
        
        if(keyB.value() == 0):
            print("B")
                       
        if(keyX.value() == 0):
            print("X")
            
        if(keyY.value() == 0):
            print("Y")
        
        # Move UP
        if(up.value() == 0):
            print("UP", " ", posx, "/", posy)
            
            if posy == 0:
                print("Go to another room up")
                            
                roomy = roomy - 1            
                loadRoom(roomy * 10 + roomx)
                print("Room:" + str(roomy * 10 + roomx))
                posy = 200
                
                
                displayPlayer(posx, posy, LCD.white)
                
            elif checkCollisionUp(posx, posy) == 0:
                hidePlayer(posx, posy, colour(40,40,40))
                posy = posy - 5
                displayPlayer(posx, posy, LCD.white)
                
        # Move DOWN        
        if(down.value() == 0):
            print("DOWN", " ", posx, "/", posy)
            
            if posy + 40 == 240:
                print("Go to another room down")
                
                roomy = roomy + 1
                loadRoom(roomy * 10 + roomx)
                print("Room:" + str(roomy * 10 + roomx))
                posy = 0
                
                
                displayPlayer(posx, posy, LCD.white)
                
                
            elif checkCollisionDown(posx, posy) == 0:
                hidePlayer(posx, posy, colour(40,40,40))
                posy = posy + 5
                displayPlayer(posx, posy, LCD.white)
            
            
        # Move LEFT    
        if(left.value() == 0):
            print("LEFT", " ", posx, "/", posy)
            
            print(getValueRoomFromGraphicPosition(posx - 5, posy))
            
            if posx == 0:
                print("Go to another room left")
                
                roomx = roomx - 1
                loadRoom(roomy * 10 + roomx)
                print("Room:" + str(roomy * 10 + roomx))
                posx = 205
                
                
                displayPlayer(posx, posy, LCD.white)
            elif checkCollisionLeft(posx, posy) == 0:
                hidePlayer(posx, posy, colour(40,40,40))
                posx = posx - 5
                displayPlayer(posx, posy, LCD.white) 
            
        # Move RIGHT
        if(right.value() == 0):
            print("RIGHT", " ", posx, "/", posy)
            
            if posx + 35 == 240:
                print("Go to another room right")
                
                roomx = roomx + 1
                loadRoom(roomy * 10 + roomx)
                print("Room:" + str(roomy * 10 + roomx))
                posx = 0
                
                
                displayPlayer(posx, posy, LCD.white) 
            elif checkCollisionRight(posx, posy) == 0:
                hidePlayer(posx, posy, colour(40,40,40))
                posx = posx + 5
                displayPlayer(posx, posy, LCD.white) 
            

        # CONTROL
        if(ctrl.value() == 0):
            print("CTRL")
                       
        LCD.show()
        if (keyA.value() == 0) and (keyY.value() == 0): # Halt looping?
            running = False
            
        utime.sleep(.15) # Debounce delay - reduce multiple button reads


game()

# Finish
LCD.fill(0)
for r in range(10):
    ring(120,120,60+r,colour(255,255,0))
LCD.text("Halted", 95, 115, colour(255,0,0))
LCD.show()
# Tidy up
utime.sleep(3)
LCD.fill(0)
LCD.show()

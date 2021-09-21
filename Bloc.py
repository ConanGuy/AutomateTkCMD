import pygame
from collections import deque
from Options import Options
import math

class Bloc:
    
    DEFAULT_ID = None
    DEFAULT_WIDTH = 0
    DEFAULT_HEIGHT = 0
    DEFAULT_COLOR = 'white'
    DEFAULT_BORDER = 'black'
    DEFAULT_BORDERSIZE = 1
    DEFAULT_BASPOS = 'tl' # (t,m,b) and (l,c,r)
    DEFAULT_BASPOSN = 0
    DEFAULT_PARPOS = 'tl' # (t,m,b) and (l,c,r)
    DEFAULT_PARPOSN = 0
    DEFAULT_PARENDPOS = None
    DEFAULT_TRANSLATE = 0

    def __init__(self, master, parent, **kwargs):
        self.master = master
        self.parent = parent
        if self.parent:
            self.parent.children.append(self)
        self.children = deque()

        ###
        self.id = kwargs.get('id', self.DEFAULT_ID)

        ###
        width = kwargs.get('width', None)
        self.width = self.DEFAULT_WIDTH
        if width:
            if '%' in width:
                self.width = parent.width * eval(width[:-1]) / 100
            else:
                self.width = eval(width)

        height = kwargs.get('height', None)
        self.height = self.DEFAULT_HEIGHT
        if height:
            if '%' in height:
                self.height = parent.height * eval(height[:-1]) / 100
            else:
                self.height = eval(height) 

        ###
        color = kwargs.get('color', self.DEFAULT_COLOR)
        self.color = pygame.color.THECOLORS[color]
        border = kwargs.get('border', self.DEFAULT_BORDER)
        self.border = pygame.color.THECOLORS[border] if border else None
        self.bordersize = kwargs.get('bordersize', self.DEFAULT_BORDERSIZE)

        ###
        self.x = 0
        self.y = 0

        ###
        self.baspos = kwargs.get('baspos', self.DEFAULT_BASPOS)
        self.basposx = kwargs.get('basposx', self.DEFAULT_BASPOSN)
        if self.basposx:
            if '%' in self.basposx:
                self.basposx = self.width * eval(self.barposx[:-1]) / 100
            else:
                self.basposx = eval(self.basposx)
        self.basposy = kwargs.get('basposy', self.DEFAULT_BASPOSN)
        if self.basposy:
            if '%' in self.basposy:
                self.basposy = self.height * eval(self.barposy[:-1]) / 100
            else:
                self.basposy = eval(self.basposy)

        ###
        self.parpos = kwargs.get('parpos', self.DEFAULT_PARPOS)
        self.parposx = kwargs.get('parposx', self.DEFAULT_PARPOSN)
        if self.parposx:
            if '%' in self.parposx:
                self.parposx = parent.width * eval(self.parposx[:-1]) / 100
            else:
                self.parposx = eval(self.parposx)
        self.parposy = kwargs.get('parposy', self.DEFAULT_PARPOSN)
        if self.parposy:
            if '%' in self.parposy:
                self.parposy = parent.height * eval(self.parposy[:-1]) / 100
            else:
                self.parposy = eval(self.parposy)

        self.parendpos = kwargs.get('parendpos', self.DEFAULT_PARENDPOS)
        translate = kwargs.get("translate", self.DEFAULT_TRANSLATE)
        self.translate = eval(str(translate))

        self.calculateCoords()
            
    #################################################################

    def calculateCoords(self):
        if not self.parent:
            return 

        self.x = self.parent.x + self.parposx - self.basposx
        self.y = self.parent.y + self.parposy - self.basposy

        if self.parendpos:
            if(self.parpos[0] == self.parendpos[0]):
                self.x += self.parent.width * self.translate
            if(self.parpos[1] == self.parendpos[1]):
                self.y += self.parent.height * self.translate

        # x calculation
        if 'r' in self.parpos:
            self.x += self.parent.width
        elif 'c' in self.parpos:
            self.x += self.parent.width/2

        if 'r' in self.baspos:
            self.x -= self.width
        elif 'c' in self.baspos:
            self.x -= self.width/2

        # y calculation
        if 'b' in self.parpos:
            self.y += self.parent.height
        elif 'm' in self.parpos:
            self.y += self.parent.height/2

        if 'b' in self.baspos:
            self.y -= self.height
        elif 'm' in self.baspos:
            self.y -= self.height/2
            
    #################################################################
            
    def draw(self):
        if self.border:
            pygame.draw.rect(self.master, self.border, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.master, self.color, (self.x+self.bordersize, self.y+self.bordersize, self.width-(2*+self.bordersize), self.height-(2*+self.bordersize)))
        
        if Options.showNames and self.id:
            font = pygame.font.Font(None, 18) 
            text = font.render(self.id, True, (255,255,255), (75,75,75,200)) 
            textRect = text.get_rect()  
            textRect.center = ((2*self.x+self.width) // 2, (2*self.y + self.height) // 2) 
            self.master.blit(text, textRect) 

    #################################################################

    def move(self, dist, axis):
        if axis == 0:
            self.x += dist
        if axis == 1:
            self.y -= dist

        for c in self.children:
            c.move(dist,axis)

    #################################################################

    def rotate(self, angle, center):
        angle = (angle) * (math.pi/180)

        nps = []
        for point in self.points:
            rotatedX = math.cos(angle) * (point.x - center.x) - math.sin(angle) * (point.y-center.y) + center.x
            rotatedY = math.sin(angle) * (point.x - center.x) + math.cos(angle) * (point.y - center.y) + center.y
            nps.append(Point(rotatedX,rotatedY))

        self.points = nps
        self.vectors = self.init_vectors()
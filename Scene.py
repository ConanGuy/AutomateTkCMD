import pygame
from Bloc import Bloc
import os
from collections import deque
import tkinter as tk
from tkinter import ttk
from Options import Options
import re

#####################################################################
#####################################################################
#####################################################################
#
# CLASSE Scene
#
#####################################################################
#####################################################################
#####################################################################
class Scene():

    def __init__(self, w=620, h=460, title="window"):
        
        self.width = w
        self.height = h
        self.win = pygame.display.set_mode((self.width, self.height)) 
        
        self.title = "Run scene"
        pygame.display.set_caption(self.title)

        self.initScene()
        self.run()

    def initScene(self, scene="scene2.txt"):
    
        self.blocList = deque()
        self.blocParent = None
        self.actions = deque()

        self.readScene(scene)
        self.correctCoords()
        self.blocSelected = self.blocList[0]

    #################################################################

    def run(self):
        
        win = tk.Tk()
        w=620
        h=296
        win.geometry(f"{w}x{h}")
        
        def disable_exit():
            pass

        win.protocol("WM_DELETE_WINDOW", disable_exit)
        win.grid_propagate(False)
        win.resizable(False, False)

        self.cmd = CMD(self, win, width=w, height=h)
        self.cmd.pack(expand='YES', fill='both')
        self.cmd.parser("help")
        
        clock = pygame.time.Clock() # to change update frequency

        while True:
            clock.tick(20) # update frequency
            try:
                self.cmd.update()
            except:
                pass

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit(0)

            if len(self.actions):
                self.executeAction(self.actions[0])

            self.win.fill((255,255,255))
            self.rec_draw(self.blocParent)
            
            pygame.display.update()
            
    #################################################################

    def rec_draw(self, cur):
        cur.draw()

        for c in cur.children:
            self.rec_draw(c)

    #################################################################

    def readScene(self, filename):
        filename = Options.path+"/scenes/"+filename
        file = open(filename, 'r')
        lines = file.readlines()
        file.close()

        for i in range(len(lines)):
            lines[i] = lines[i].replace("\n","")
            lines[i] = lines[i].replace("\t","")

        parent = None
        curBloc = None
        for l in lines:
            if l == '[':
                parent = curBloc

            elif l == ']':
                parent = parent.parent

            if len(l) > 1:
                s = ', '.join(l.split(" "))
                curBloc = eval(f"Bloc(self.win, parent, {s})")
                if not self.blocParent:
                    self.blocParent = curBloc
                self.blocList.append(curBloc)

    #################################################################

    def correctCoords(self):
        miny = 0
        minx = 0
        for b in self.blocList:
            miny = miny if b.y > miny else b.y
            minx = minx if b.x > minx else b.x

        miny -= 10
        minx -= 10

        for b in self.blocList:
            b.y -= miny
            b.x -= minx
            
    #################################################################

    def findBlocById(self, id):
        for b in self.blocList:
            if b.id:
                if b.id == id:
                    return b
        return None
            
    #################################################################

    def executeAction(self, action):
        i = -1
        for a in action:
            i += 1

            if a[0] == 'shownames':
                Options.showNames = not Options.showNames
                if Options.showNames:
                    self.cmd.insertText("Names shown") 
                else: 
                    self.cmd.insertText("Names hiden")
                action.pop(i)

            elif a[0] == 'names':
                self.cmd.insertText('List of names:')
                for b in self.blocList:
                    if b.id:
                        self.cmd.insertText(' - '+b.id)
                action.pop(i)

            elif a[0] == 'move':
                b = self.findBlocById(a[1])

                if not b:
                    self.cmd.insertText("No bloc found")
                    action.pop(i)
                    continue

                add = 1 if a[2] > 0 else -1

                axis = -1
                parpos = b.parpos
                endpos = b.parendpos

                if not endpos:
                    self.cmd.insertText("This bloc cannot move")
                    action.pop(i)
                    return

                if parpos[0] == endpos[0]:
                    axis = 0
                elif parpos[1] == endpos[1]:
                    axis = 1

                b.move(add, axis)
                a[2] -= add

                if a[2] == 0:
                    action.pop(i)
            
            elif a[0] == 'sleep':
                pygame.time.delay(a[1])
                action.pop(i)
            
            elif a[0] == 'script':
                filename = Options.path+"/scripts/"+a[1]
                file = open(filename, 'r')
                s = file.read()
                file.close()

                s.replace('\r', "")
                s.replace('\n', "")
                self.cmd.parser(s, 0)
                action.pop(i)
            
            elif a[0] == 'load':
                self.initScene(a[1])
            
            elif a[0] == 'help':            
                if a[1] == '*':
                    self.cmd.insertText('List of commands:')
                    for c in self.cmd.commands:
                        self.cmd.insertText(' - '+c)
                else:
                    filename = Options.path+"/doc/"+a[1]+".help"
                    file = open(filename, 'r')
                    self.cmd.insertText(file.read()+'\n')
                    file.close()
                action.pop(i)

        if action == []:
            self.actions.popleft()

#####################################################################
#####################################################################
#####################################################################
#
# CLASSE CMD
#
#####################################################################
#####################################################################
#####################################################################

class History:

    def __init__(self, history=deque(), i=-1):
        self.hist = history
        self.index = i
            
    #################################################################

    def read(self, dir):
        if not len(self.hist):
            return ''

        if dir == -1:
            
            self.index += dir
            if self.index < 0:
                return ''
        
        if dir == 1:
            if self.index >= len(self.hist)-1:
                return self.hist[self.index]
            
            self.index += dir

        return self.hist[self.index]


class CMD(tk.Canvas):
    
    def __init__(self, scene, widget, **kwargs):

        tk.Canvas.__init__(self, widget, **kwargs)
        
        self.scene = scene
        self.master = widget

        self.commands = self.initCommandList()
        self.history = History()

        self.command_text = tk.Text(self, height=17, width=75, bg='black', fg='white')
        self.command_text.config(state=tk.DISABLED)

        self.scrollb = ttk.Scrollbar(self, command=self.command_text.yview)
        self.command_text['yscrollcommand'] = self.scrollb.set

        beg_entry = tk.Text(self, height=1, width=5, bg='black', fg='white')
        beg_entry.insert(tk.END, 'cmd>')
        beg_entry.config(state=tk.DISABLED)

        self.command_entry = tk.Entry(self, bg='black', fg='white', insertbackground='white')
        self.command_entry.focus_set()
        self.command_entry.xview_moveto(1)

        self.command_text.grid(row=0, column=0, sticky='w')
        self.scrollb.grid(row=0, column=21, sticky='nsew', rowspan = 6)
        beg_entry.grid(row=5, sticky='snw')
        self.command_entry.grid(row=5, column=0,sticky='snwe', padx=(40,0))

        self.command_entry.bind('<Return>', self.send)
        self.command_entry.bind('<Up>', lambda event, x=1: self.readHist(x))
        self.command_entry.bind('<Down>', lambda event, x=-1: self.readHist(x))

        self.insertText('"help [nothing|command]" to get help')
            
    #################################################################

    def readHist(self, n):
        self.command_entry.delete(0, tk.END)
        self.command_entry.insert(0, self.history.read(n))
            
    #################################################################

    def insertText(self, text):
        self.command_text.config(state=tk.NORMAL)
        self.command_text.insert(tk.END, text+"\n")
        self.command_text.see(tk.END)
        self.command_text.config(state=tk.DISABLED)
            
    #################################################################

    def send(self, event):
        cmd = self.command_entry.get()
        self.insertText(">>> "+cmd)
        self.command_entry.delete(0, 'end')

        self.parser(cmd)

        self.history.index = -1
            
    #################################################################

    def initCommandList(self):
        commands = [
            "help",
            "move", # move <id> <distance>
            "shownames", # shownames    
            "names", # names
            "sleep", # sleep <ms>
            "script", # script <filename>
            "load" # load <filename>
        ]        
        return commands

    #################################################################

    def parser(self, command, hist=1):

        def is_dig(s):
            try:
                int(s)
                is_dig = True
            except ValueError:
                is_dig = False
            return is_dig

        if hist:
            if not len(self.history.hist):
                self.history.hist.appendleft(command)
            elif self.history.hist[0] != command:
                self.history.hist.appendleft(command)

        cmds = command.split(';')

        for cmd in cmds:
            cs = cmd.split('|')

            a = []
            for c in cs:
                s = c.split()
                l = len(s)

                if not len(s):
                    continue

                ####################
                # shownames        #
                if s[0] == 'shownames':
                    if l != 1:
                        self.insertText("Too many arguments")
                        break
                    a.append(['shownames'])

                ####################
                # names        #
                if s[0] == 'names':
                    if l != 1:
                        self.insertText("Too many arguments")
                        break
                    a.append(['names'])

                ####################
                # move             #
                elif s[0] == 'move':
                    if l == 1:
                        self.insertText("Missing arguments")
                        break
                    elif l <= 3:
                        
                        b,d = (self.scene.blocSelected.id, s[1]) if l == 2 else (s[1], s[2])
                        
                        if not is_dig(d):
                            self.insertText("Missing distance")
                            break

                        if d == '0':
                            self.insertText("Distance cannot be 0")
                            break

                        if b[0] == '@':
                            b = b[1:]
                            self.scene.blocSelected = self.scene.findBlocById(b)

                        a.append(['move', b, eval(d)])
                    
                    else:
                        self.insertText("Too many arguments")
                        break

                ####################
                # sleep            #
                if s[0] == 'sleep':
                    if l < 2:
                        self.insertText("Missing arguments")
                        break
                    if l > 2:
                        self.insertText("Too many arguments")
                        break

                    if not is_dig(s[1]):
                        self.insertText("Missing duration")
                        break                    

                    a.append(['sleep',eval(s[1])])

                ####################
                # script           #
                if s[0] == 'script':
                    if l < 2:
                        self.insertText("Missing arguments")
                        break
                    if l > 2:
                        self.insertText("Too many arguments")
                        break

                    if not s[1][-3:] == '.sc':
                        s[1] += '.sc'

                    if not s[1] in os.listdir(Options.path+"/scripts"):
                        self.insertText(f"File {s[1]} not found")
                        break

                    a.append(['script',s[1]])

                ####################
                # load            #
                if s[0] == 'load':
                    if l < 2:
                        self.insertText("Missing arguments")
                        break
                    if l > 2:
                        self.insertText("Too many arguments")
                        break

                    if not s[1][-4:] == '.txt':
                        s[1]+= '.txt'

                    if not s[1] in os.listdir(Options.path+"/scenes"):
                        self.insertText(f"File {s[1]} not found")
                        break

                    a.append(['load',s[1]])

                ####################
                # help             #
                elif s[0] == 'help' or s[0] == '?':
                    if l == 1:
                        a.append(['help', "*"])

                    elif l == 2:
                        if not s[1] in self.commands:
                            self.insertText(f'Command "{s[1]}" not found')
                            break       

                        a.append(['help', s[1]])

                    else:
                        self.insertText("Too many arguments")
                        break

            self.scene.actions.append(a)
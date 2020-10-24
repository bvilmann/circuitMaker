# -*- coding: utf-8 -*-
"""
Created on Mon May 11 07:33:14 2020

@author:    Benjamin Vilmann
            Stud. BEng., Electrical Energy Technology
            @ Technical University of Denmark (DTU)
            mail: bvilmann@hotmail.com
"""

import subprocess
import sys
import os
import pandas as pd
from numpy import array as arr
import numpy as np


"""
# ======================= HELPER FUNCTIONS =======================
"""

def addColor(rgb,item):
    return 'rgbdraw({},{},{},{})'.format(rgb[0],rgb[1],rgb[2],item)


"""
# ======================= COMPONENT CLASS =======================
"""
class component():

    def __init__(self,ID,comp,t,name,label,value,d,scale,here,starts,ends):
        dx = circuitMaker().dx
        dy = circuitMaker().dy

        self.comp = comp
        self.type = t
        self.name = name
        self.label = label
        self.value = value
        self.scale = scale

"""
# ======================= LINKED LISTS & NODE CLASS =======================
"""
class Node:
    def __init__(self, val=None):
        self.val = val
        self.nextval = None
        
class SLinkedList:
    def __init__(self):
        self.headval = None

    def __iter__(self):
        node = self.headval
        while node:
            yield node
            node = node.nextval

    def __getitem__(self,index):
        node = self.headval
        for i in range(index):
            node = node.nextval
        return node.val
   
    def __setitem__(self,index,obj,value):
        self.node[index].val.obj = value

    def getNode(self,find):
        node = self.headval
        while node is not None:
            if node.val.name == find or node.val.label == find:
                return node.val
            else:
                node = node.nextval

    def getID(self,find):
        node = self.headval
        cnt=0
        while node is not None:
            #print(node.val.comp,find)
            if node.val.comp == find:
                cnt +=1
                node = node.nextval

            else:
                node = node.nextval

        return cnt

    def getPos(self,find,pos):
        node = self.headval
        while node is not None:            
            if node.val.name == find or node.val.label == find:
                #if node.val.label != '': print('getPos: ',node.val.label, node.val.end,find,pos)
                if pos == 'up':
                    return node.val.up

                elif pos=='down':
                    return node.val.down

                elif pos=='mid':
                    return node.val.mid

                elif pos=='left':
                    return node.val.left

                elif pos=='right':
                    return node.val.right

                elif pos=='start':
                    return node.val.start

                elif pos=='end':
                    return node.val.end                
            else:
                node = node.nextval

        sys.exit('Could not find given name.')
        
    # Function to add newnode
    def AtEnd(self, newdata):
        NewNode = Node(newdata)
        if self.headval is None:
            self.headval = NewNode
            return
        laste = self.headval
        while(laste.nextval):
            laste = laste.nextval
        #if NewNode.val.label != '': print('node: ',NewNode.val.end)
        laste.nextval=NewNode
        
    def listLen(self,):
        val = self.headval
        cnt = 0
        while val is not None:
            cnt += 1
            val = val.nextval
        return cnt

    def replace_node(self, index, data):
        self.locate(index)
        self.current_node.data = data    
        
"""
# ======================= CIRCUITMAKER CLASS =======================
"""
class circuitMaker:
    __version__ = 0.002

    def __init__(self,dx = 20,dy = 20,O = (0,0),scale=25.4,fname = 'ex0.m4cm',dot=False):
        self.fname = fname
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.dest = os.path.dirname(os.path.abspath(__file__)) + r'\\' + fname 
        self.init = ['.PS','include(pstricks.m4)','scale = {}'.format(scale),'cct_init','dx = {}'.format(dx),'dy = {}'.format(dy),'O: {}'.format(O)]
        self.globalScale = scale
        self.dot = dot
        self.dx = dx
        self.dy = dy
        self.x = 0
        self.y = 0
        self.here = 0
        self.here = arr(O)
        self.map = []           # 0 = up, 1 = down, 2= left, 3= right
        self.nav = [0,0,0,0]    # up, down, left, right        
        self.components = []
        self.comps = SLinkedList()
        self.nodes = ['dot','ground']
        self.oneTerminal = ['generator','load','shunt_reactor','grid']
        self.twoTerminal = ['trf2','reactance','grid','reactor']
        self.lines = ['resistor','ebox','inductor','capacitor','fuse','lswitch','line','gap','lamp','pvcell','thermocouple','heater','reed','ttmotor','diode']
        self.directions = ['up','down','mid','right','left']
        self.semiconductors = ['bi_tr','igbt','mosfet','ujt','j_fet']

    def getRGB(self,color):
        if type(color) == type(list()):
            if len(color) == 3:
                return color
            else:
                sys.exit('To define a color you must either provide a name for the color or a list of 3 numbers in range from 0 to 1.')
        elif type(color) == type(''):
            if color.lower() == 'black':     
                return [0,0,0]
            elif color.lower() == 'red':        return [1,0,0]
            elif color.lower() == 'green':      return [0,1,0]
            elif color.lower() == 'blue':       return [0,0,1]
            elif color.lower() == 'cyan':       return [0,1,1]
            elif color.lower() == 'magenta':    return [1,0,1]
            elif color.lower() == 'yellow':     return [1,1,0]
            elif color.lower() == 'grey':       return [0.5,0.5,0.5]


    def text(self,text,at,t='',circle=False,color='black'):
        starts = at.split('.')
        if len(starts) == 1:
            starts.append('up')
        a = arr(self.comps.getPos(starts[0],starts[1]))
        if starts[1] == 'up':
            just1 = ' above '
        elif starts[1] == 'down':
            just1 = ' below '
        elif starts[1] == 'right':
            just1 = ' rjust '            
        elif starts[1] == 'left':
           just1 = ' ljust '

        if len(starts) > 2:
            if starts[2] == 'up':
                just2 = ' above '
            elif starts[2] == 'down':
                just2 = ' below '
            elif starts[2] == 'right':
                just2 = ' rjust '
            elif starts[2] == 'left':
                just2 = ' ljust '
        else:
            just2 = ''
        
        a = arr(self.comps.getPos(starts[0],starts[1]))
        a = str(tuple(a))
    
        rgb = self.getRGB(color)
        item = 'rgbdraw(%f,%f,%f,"$%s$" at %s %s %s);' % (rgb[0],rgb[1],rgb[2],text,a,just1,just2)
        self.components.append(item)

        # Circle features does not work yet.
        if circle == True:
            item = 'circle rad %i*dimen_/10 at %s' % (len(text),a)       
            self.components.append(item)

        
    def Print(self):
        for line in self.circuit:
            print(line)
        
    def draw(self,caption=None,lang='',x='',y=''):
        if x != '': self.x = x
        if y != '': self.y = y
        
        if caption == None:
            cap = ''
        else:
            cap = '\caption{' + caption +'}'
        self.circuit = []
        self.latex = [r'\documentclass[dvips]{article}',
                 #'\special{papersize=%smm,%smm}' % (self.x, self.y),
                 r'\usepackage{pstricks}',r'\usepackage[utf8]{inputenc}',
                 r'\usepackage{times}',
                 #r'\usepackage[a4paper, total={%smm, %smm}]{geometry}'% (self.x, self.y),
                 r'\pagestyle{empty}',
                 r'\begin{document}',
                 r'\begin{figure}[hbt]',
                 r'\begin{center}',
                 r'\include{ex0}',
                 cap,
                 r'\end{center}',
                 r'\end{figure}',
                 r'\end{document}']
        with open(self.path + r'\Example_0.tex', 'w') as file:
            for line in self.latex:
                file.write(line+'\n')         
        
        comps = self.init + self.components + ['.PE']
        with open(self.dest, 'w') as file:
            for line in comps:
                self.circuit.append(line)
                file.write(line+'\n')         

    def pdf(self,fname):
        #path = 'set m4path'
        #path = 'cd ' + str(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.dirname(os.path.abspath(__file__)).replace('\\\\','\\')
        args = ['cd ' + path,
                #'{} ex0.m4cm > ex0.pic'.format(self.path + r'\m4.exe'),
                #'{} -p ex0.pic > ex0.tex'.format(self.path + r'\dpic.exe'),
                'm4.exe ex0.m4cm > ex0.pic',
                'dpic.exe -p ex0.pic > ex0.tex',
                'latex -quiet {}.tex'.format(fname),
                'dvips -q {}.dvi'.format(fname),
                'ps2pdf {}.ps'.format(fname),
                ]
        for arg in args:
            print(arg)
            proc = subprocess.run(arg,stdout=subprocess.PIPE, shell=True)

    def jpg(self,resolution=600,fname = 'ex0.m4cm'):
        path = os.path.dirname(os.path.abspath(__file__)).replace('\\\\','\\')
        args = ['cd '+path,
                'm4cm.py -j -q ex0.m4cm'.format(resolution)
                #'m4cm.py -j -r{} -q -a _lol ex0.m4cm'.format(resolution)
                #'m4cm.py -j -a _lol ex0.m4cm'.format(resolution)
                ]
        with open('test.txt', 'wb') as f:  # replace 'w' with 'wb' for Python 3
            for arg in args:
                process = subprocess.Popen(arg, stdout=subprocess.PIPE, shell=True)
                for c in iter(lambda: process.stdout.readline(), b''):  # replace '' with b'' for Python 3
                    sys.stdout.write(c)
                    f.write(c)




    def add(self,comp,d='',start='',at='',end='',x1='',x2='',y1='',y2='',t='',name = '',label = '',label_pos = 'center',color = [0,0,0],breaker=None,scale=1,sign=None,value=None,crossover=False,variable=False,transformer_conf='',diode=False,draw_from='',ports=1,dot=None):       
        # ================= Variables =================
        direction = d
        starts = start.split('.')
        ats = at.upper().split('.')
        ends = end.upper().split('.')

        for l in [starts,ats,ends]:
            for iterator in range(len(l)):
                if iterator==0:
                    l[iterator] = l[iterator].upper()
                else:
                    if l[iterator] in self.directions:
                        l[iterator] = l[iterator].lower()

        start = starts[0]
        at = ats[0]
        end = ends[0]
        pos = ''
        a = b = move = arr([0,0])
        rgb = self.getRGB(color)

        # ================= Qualifying input =================
        #if (start != '' and len(starts) > 0) or (end != '' and len(ends) >0) and (end != 'O' or start != 'O'):
        #    sys.exit('Relative position to the desired component label must be provided if not start or end point is "O". Options are "up","down","mid","left","right","start","end".')


        # ================= String manipulation =================
        
        """# Type                            
        if t != '' and type(str('')) == type(t):
            t = ','+t
        """
        if comp in self.oneTerminal:
            if type(breaker) == type(str()):
                b1Key = breaker.split('.')[0]
                b1Val = breaker.split('.')[1]
            elif breaker == None:
                b1Key = ''
                b1Val = ''
            else:
                sys.exit('Wrong breaker syntax.')
        else:
            # Case: String
            if type(breaker) == type(str()):
                if '1' in breaker:
                    b1Key = breaker.split('.')[0]
                    b1Val = breaker.split('.')[1]
                    b2Key = ''
                    b2Val = ''
                    if len(breaker.split('.')) == 3:
                        sign1 = breaker.split('.')[2]
                elif '2' in breaker:
                    b1Key = ''
                    b1Val = ''
                    b2Key = breaker.split('.')[0]
                    b2Val = breaker.split('.')[1]                    
                    if len(breaker.split('.')) == 3:
                        sign2 = breaker.split('.')[2]
                    
            # Case: List with 2 elements
            elif type(breaker) == type(list()) and len(breaker)==2:
                b1Key = breaker[0].split('.')[0]
                b1Val = breaker[0].split('.')[1]
                b2Key = breaker[1].split('.')[0]
                b2Val = breaker[1].split('.')[1]
                for i in range(2):
                    if len(breaker[i].split('.')) == 3:
                        if '1' in breaker[i].split('.')[0]:
                            sign1 = breaker[i].split('.')[2]
                        elif '2' in breaker[i].split('.')[0]:
                            sign2 = breaker[i].split('.')[2]

            # Case: List with 1 elements
            elif type(breaker) == type(list()) and len(breaker)==1:
                if '1' in breaker[0]:
                    b1Key = breaker[0].split('.')[0]
                    b1Val = breaker[0].split('.')[1]
                    b2Key = ''
                    b2Val = ''

                elif '2' in breaker[0]:
                    b1Key = ''
                    b1Val = ''
                    b2Key = breaker[0].split('.')[0]
                    b2Val = breaker[0].split('.')[1]                    
                if len(breaker[0].split('.')) == 3:
                    if '1' in breaker[0].split('.')[0]:
                        sign1 = breaker[0].split('.')[2]
                        sign2 = ''
                    elif '2' in breaker[0].split('.')[0]:
                        sign1 = ''
                        sign2 = breaker[0].split('.')[2]

            elif breaker == None:
                b1Key = ''
                b1Val = ''
                b2Key = ''
                b2Val = ''
            else:
                raise ValueError('Wrong breaker syntax.')

        # LABEL
        if label != '' or sign != None or breaker!='':
            if sign == 'motor' or sign == 'm' or sign == 'load' or sign == 'l':
                sign1='+';sign2='-'
            elif sign == 'generator' or sign == 'g':
                sign1='-';sign2='+'

            if label_pos == 'center':
                if 'sign1' in locals() or 'sign2' in locals():
                    lab = 'llabel(,\hbox{%s},);rlabel(\hbox{%s},,\hbox{%s})' % (label,sign1,sign2)
                elif comp in self.oneTerminal:
                    lab = 'clabel(,,\hbox{%s})' % label
                elif comp in self.twoTerminal:
                    lab = 'llabel(,\hbox{%s},);' % (label)
                #lab = 'llabel({},{},{});'.format(sign1,label,sign2)
                #lab = 'rgbdraw({},{},{},llabel({},{},{}));'.format(rgb[0],rgb[1],rgb[2],sign1,label,sign2)
                else:
                    lab = ''
    
            if comp == 'busbar':
                lab = 'clabel(,,\hbox{%s})' % label                
    
        else:
            lab = ''

        if dot == True:
            dot = ';dot();'
        elif not self.dot:
            dot = '';
        else:
            dot = '';
            
        # ================= Positioning =================
        # DIRECTION ONLY
        if d != '':
            if d == 'up' or d=='u':
                move = arr([0,scale*self.dy])
                self.map = 0;
                self.nav[0] += 1*scale

            elif d=='down' or d=='d':
                move = arr([0,-scale*self.dy])
                self.map = 1;
                self.nav[1] += 1*scale
            elif d == 'left' or d=='l':
                move = arr([-scale*self.dx,0])
                self.map = 2;
                self.nav[2] += 1*scale

            elif d=='right' or d=='r':
                move = arr([scale*self.dx,0])
                self.map = 3;
                self.nav[3] += 1*scale

        # ================= Move cases =================
        # DIRECTION ONLY
        if d != '' and start == '' and end == '':
            if comp == 'busbar':                
                if d == 'vert' or d=='v':
                    d= 'up_ {}'.format(scale*self.dy*(ports/2)) 
                elif d== 'hori' or d=='h':
                    d= 'right_ {}'.format(scale*self.dx*(ports/2)) 
                else:
                    raise ValueError('Busbar requires a direction as orientation, e.g: "vert","v","hori", or "h"')
                
            else:
                self.here = arr(self.here) + arr(move)            
                if d == 'up' or d=='u':
                    d= d+'_ {}'.format(scale*self.dy)
                elif d=='down' or d=='d':
                    d= d+'_ {}'.format(scale*self.dy)
                elif d == 'left' or d=='l':
                    d= d+'_ {}'.format(scale*self.dx)
                elif d=='right' or d=='r':
                    d= d+'_ {}'.format(scale*self.dx) 

        # END
        elif start == '' and  d == '' and end != '':
            if end == 'O':
                b = arr((0,0))
                self.here = arr(tuple((0,0)))
            else:
                if ends[1] in self.directions: 
                    self.here = arr(self.comps.getPos(ends[0],ends[1]))
                    b = str(tuple(arr(self.comps.getPos(ends[0],ends[1]))))
                else: 
                    b = '{}.{}'.format(ends[0],ends[1])                    
            d = ' to ' + b                

        # START -> END
        elif start != '' and end != '':
            if start == 'O':
                a = str(tuple(arr((0,0))))
            else:
                if starts[1] in self.directions: 
                    a = str(tuple(arr(self.comps.getPos(starts[0],starts[1]))))
                else:
                    a = '{}.{}'.format(starts[0],starts[1])                    
            if end == 'O':
                b = str(tuple(arr((0,0))))
                self.here = arr(tuple((0,0)))
            else:
                if ends[1] in self.directions: 
                    self.here = arr(self.comps.getPos(ends[0],ends[1]))
                    b = str(tuple(arr(self.comps.getPos(ends[0],ends[1]))))            
                else:
                    b = '{}.{}'.format(ends[0],ends[1])                                        
            d = ' from ' + a + ' to ' + b
        # START WITH DIRECTION
        elif start != '' and end == '' and d != '':
            if comp == 'busbar':                
                if d == 'vert' or d=='v':
                    d= 'up'
                elif d== 'hori' or d=='h':
                    d= 'right'
                else:
                    raise ValueError('Busbar requires a direction as orientation, e.g: "vert","v","hori", or "h"')
            if start == 'O':
                a = arr((0,0))
                self.here = move
            else:
                if starts[1] in self.directions: 
                    self.here = arr(self.comps.getPos(starts[0],starts[1])) + move
                    a = str(tuple(arr(self.comps.getPos(starts[0],starts[1]))))
                else:
                    a = '{}.{}'.format(starts[0],starts[1])                    
            if comp == 'busbar':                
                d = d+'_ {} from ({},{})'.format((self.dx*ports)/2,a,a) 
            else: 
                d = d+'_ {} from ({},{})'.format(self.dx*scale,a,a) 
                

        # AT
        elif at != '':
            d = 'at {}.{}'.format(ats[0],ats[1])
            # Introduce busbar option?
            

        # Getting dimensions of circuit
        if max(self.x,self.here[0]) > self.x: self.x=self.here[0]        
        if max(self.y,self.here[1]) > self.y: self.y=self.here[1]    

        # ================= Appending component =================
        # ----------------- Linked list -----------------
        self.ID = ID = '{}{}'.format(comp,self.comps.getID(comp))        
        #print(label,a,type(a))
        C = component(ID,comp,t,name,label,value,direction,scale,self.here,a,b)
        #if comp in self.lines: print('C: ',C.label,C.start,C.end)
        self.comps.AtEnd(C)
        # ----------------- Printing list -----------------
        # String list for printing to m4cm doc
        if comp == 'line':
            if crossover == True:
                item = 'rgbdraw({},{},{},crossover({}{}));{}'.format(rgb[0],rgb[1],rgb[2],d,t,lab)
            else:
                item = '{}: {} {};{}'.format(ID.upper(),comp,d,t,lab)
                item = '{}: sldline({},{},{},{},{}) ;{}'.format(ID.upper(),d,b1Key,b1Val,b2Key,b2Val,lab)

        elif comp == 'generator':            
            item = '{}: {}({},{},{},{});{}{}'.format(ID.upper(),comp,d,t,b1Key,b1Val,lab,dot)

        elif comp == 'shunt_reactor':
            item = '{}: {}({},{},{},{});{}{}'.format(ID.upper(),comp,d,t,b1Key,b1Val,lab,dot)

        elif comp == 'trf2':
            item = '{}: {}({},{},{},{},{},{});{}{}'.format(ID.upper(),comp,d,t,b1Key,b1Val,b2Key,b2Val,lab,dot)

        elif comp == 'reactor':
            item = '{}: {}({},{},{},{},{});{}{}'.format(ID.upper(),comp,d,b1Key,b1Val,b2Key,b2Val,lab,dot)

        elif comp == 'grid':
            item = '{}: {}({},{},{});{}{}'.format(ID.upper(),comp,d,b1Key,b1Val,lab,dot)

        elif comp == 'busbar':
            lines = ports-1
            c = lines/2
            sp = np.floor(lines/2)
            if ports%2 == 0:                   
                n = ports - 2
            else:
                n = ports - 1
            offset = self.dx*((draw_from-1)*(ports*sp))/(lines*n) - self.dx*(ports*c)/(lines*2)
            if start == '':
                # Algorithm for mirroring values in range: for i in range(1,n+1): print(n,' ',i,' ',abs(i - (n+1)))
                draw_from = abs(draw_from - (ports+1))                
                offset = 'with .c at rvec_(0,{})'.format(-offset)
            else:
                offset = 'with .c at rvec_(0,{})'.format(offset)
                
            item = '{}: {}({},{},{}) {};{}'.format(ID.upper(),comp,d,ports,draw_from,offset,lab)

        else:            
            item = '{}: {}({},{});{}{}'.format(ID.upper(),comp,d,t,lab,dot)

        self.components.append(item)

    def move(self):
        self.components.append('move')
        
cm = circuitMaker()

cm.add('generator',d='left',t='SG',label='WT')
cm.add('trf2',d='right',breaker=['B1.Open.B001','B2.Closed.B002'],label='YNd')
cm.add('line',d='right')
cm.add('busbar',d='v',ports=3,draw_from=2,label='1')
cm.add('line',d='right',scale=2.5,start='BUSBAR0.P1',breaker=['B1.Open.B101','B2.Open.B102'],label='Line 1')
cm.add('line',d='right',scale=2.5,start='BUSBAR0.P3',breaker=['B1.Open.B201','B2.Closed.B202'],label='Line 2')
cm.add('busbar',d='v',start='LINE0.end',ports=3,draw_from=3,label='2')
cm.add('reactor',d='right',start='BUSBAR1.P2')
cm.add('grid',d='right',label='Grid')

cm.draw(caption='This is a caption')
cm.pdf('Example_0')
#cm.jpg('Example_0')

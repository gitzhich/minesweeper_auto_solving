"""module for Class Object"""

import random

_EASY = (9, 9, 10)
_NORMAL = (16, 16, 40)
_HARD = (30, 16, 99)

class MyBox:
    def __init__(self):
        self.info = {'flag': False, 'block': False, 'mine': False, 'around': 0}

class MyCells:
    
    num_table = {'0': '０', '1': '１', '2': '２', '3': '３', '4': '４', '5': '５', '6': '６', '7': '７', '8': '８', '9': '９'}
    """Initialization"""
    def __init__(self):
        self.width = 0
        self.height = 0
        self.mines = 0
        self.setting = False
        self.map = []
        self.explosion = False
        self.clear = False
    
    def outofMap(self, _x, _y):
        return _x < 0 or _x >= self.width or _y < 0 or _y >= self.height
    
    def makeMap(self):
        for y in range(self.height):
            for x in range(self.width):
                self.map[y][x] = MyBox()
                self.map[y][x].info['block'] = True
    
    def resetMap(self, _x, _y, _m):
        self.width = _x
        self.height = _y
        self.mines = _m
        self.setting = False
        self.map = [[0] * _x for n in range(_y)]
        self.makeMap()
        self.explosion = False
        self.clear = False
    
    def setMines(self, _x, _y):
        n = 0
        while n < self.mines:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            flag = False
            if self.map[y][x].info['mine'] or (x == _x and y == _y):
                flag = True
            for x2, y2 in self.checkAround(x, y):
                if _x == x2 and _y == y2:
                    flag = True
            if flag: continue
            self.map[y][x].info['mine'] = True
            n += 1
        self.countMines()
    
    def checkAround(self, _x, _y):
        for souY in range(-1,2):
            for souX in range(-1,2):
                if souY == 0 and souX == 0:
                    continue
                x2 = _x + souX
                y2 = _y + souY
                if self.outofMap(x2, y2):
                    continue
                yield x2, y2
    
    def countMines(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.map[y][x].info['mine']:
                    self.map[y][x].info['around'] = 10
                    continue
                n = 0
                for x2, y2 in self.checkAround(x, y):
                    if self.map[y2][x2].info['mine']:
                        n += 1
                self.map[y][x].info['around'] = n
    
    def openBlock(self, _x, _y):
        if (not self.map[_y][_x].info['flag']) and (self.map[_y][_x].info['block']):
            self.map[_y][_x].info['block'] = False
            if self.map[_y][_x].info['mine']:
                self.explosion = True
                print('\a')
                return
            for x2, y2 in self.checkAround(_x, _y):
                if self.map[y2][x2].info['around'] == 0:
                    #aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                    if (not self.map[y2][x2].info['flag']) and (self.map[y2][x2].info['block']):
                        self.openBlock(x2, y2)
            if self.map[_y][_x].info['around'] == 0:
                for x2, y2 in self.checkAround(_x, _y):
                    #aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                    if (not self.map[y2][x2].info['flag']) and (self.map[y2][x2].info['block']):
                        self.openBlock(x2, y2)
    
    def setFlag(self, _x, _y):
        if self.map[_y][_x].info['block']:
            self.map[_y][_x].info['flag'] = not self.map[_y][_x].info['flag']
    
    def checkClear(self):
        self.clear = True
        for y in range(self.height):
            for x in range(self.width):
                if (not self.map[y][x].info['mine']) and (self.map[y][x].info['block']):
                    self.clear = False
        if self.clear:
            print('\a')
    
    def doCommand(self, line):
        try:
            line = line.replace(' ', '')
            coms = line.split(',')
            if (len(coms) < 2) or (len(coms) > 3):
                raise ValueError('Incorrect command.')
            if not (coms[0].isdecimal() and coms[1].isdecimal()):
                raise ValueError('Please enter a number.')
        except ValueError as e:
            print('Error!')
            print(e)
            return
        if len(coms) == 2:
            [x, y] = coms
            command = 'open'
        else:
            [x, y, command] = coms
        x = int(x) - 1
        y = int(y) - 1
        if self.outofMap(x, y):
            print('Error!')
            print('x:[1 ~ %d], y:[1 ~ %d]' % (self.width, self.height))
            return
        if command == 'f':
            self.setFlag(x, y)
        else:
            if not self.setting:
                self.setMines(x, y)    # 最初にあけるブロックの周囲には爆弾は無い
                self.setting = True
            if (not self.map[y][x].info['flag']) and (self.map[y][x].info['block']):
                #aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
                self.openBlock(x, y)
        self.checkClear()
    
    def insertLine(self):
        line = '　　'
        for n in range(self.width): line += 'ー'
        print(line)
    
    def giveInfo(self):
        info_map = [[0] * self.width for n in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                if self.map[y][x].info['flag']:
                    info_map[y][x] = 'f'
                elif self.map[y][x].info['block']:
                    info_map[y][x] = 'b'
                elif self.map[y][x].info['mine']:
                    info_map[y][x] = 'm'
                elif self.map[y][x].info['around'] > 0:
                    info_map[y][x] = str(self.map[y][x].info['around'])
                else:
                    info_map[y][x] = '0'
        return info_map
    
    def writeFile(self, info_map, fname):
        with open(fname + '.txt', 'w') as f:
            for y in range(self.height):
                line = ''
                for x in range(self.width):
                    line += info_map[y][x]
                f.write(line + '\n')
    
    def showMap(self, gameoverflag):
        line = '　　'
        for x in range(self.width):
            line += MyCells.num_table[str((x+1) % 10)]
        print(line)
        self.insertLine()
        for y in range(self.height):
            line = MyCells.num_table[str((y+1) % 10)] + '｜'
            for x in range(self.width):
                if self.map[y][x].info['flag']:
                    line += 'Ｆ'
                elif self.map[y][x].info['block'] and (not (gameoverflag and self.map[y][x].info['mine'])):
                    line += '■'
                elif self.map[y][x].info['mine']:
                    line += '※'
                elif self.map[y][x].info['around'] > 0:
                    num = self.map[y][x].info['around']
                    line += MyCells.num_table[str(num)]
                else:
                    line += '・'
            print(line)
        self.insertLine()
    
    def getSize(self):
        while True:
            print('Easy: 1, Normal: 2, Hard: 3, Custom: 4')
            mode = input(':')
            if (mode == '1'):
                return list(_EASY)
            elif (mode == '2'):
                return list(_NORMAL)
            elif (mode == '3'):
                return list(_HARD)
            elif (mode == '4'):
                print('WIDTH:',end='')
                x = int(input())
                print('HEIGHT:', end='')
                y = int(input())
                print('How many mines?:', end='')
                m = int(input())
                return x, y, m
    
    def playGame(self):
        [x, y, m] = self.getSize()
        self.resetMap(x, y, m)
        while True:
            self.showMap(False)
            print('(x, y[, f])')
            print(':', end='')
            line = input()
            if (line == 'reset'):
                [x, y, m] = self.getSize()
                self.resetMap(x, y, m)
                continue
            if (line == 'end'): break
            self.doCommand(line)
            if self.explosion:
                self.showMap(True)
                print('Game Over')
                break
            elif self.clear:
                self.showMap(False)
                print('Game Clear')
                break

if __name__ == "__main__":
    a = MyCells()
    a.playGame()

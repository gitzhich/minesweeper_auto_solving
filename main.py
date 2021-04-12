# Mine Sweeper Project
"""Main module"""

from time import sleep
import subprocess
import mod_MyClass

class MySolveBox:
    def __init__(self):
        self.info = ''
        self.flags = 0
        self.complete = False
        self.around = set() # 空集合

class MySolve:
    
    # 初期化
    def __init__(self):
        self.width = 0
        self.height = 0
        self.mines = 0
        self.setFlag = 0
        self.blocks = 0
        self.map = []
        self.numbers = []
        self.commands = []
        self.dic = {}
        self.allBlocks = set()
    
    # 変数の設定
    def resetMap(self, _x, _y, _m):
        self.width = _x
        self.height = _y
        self.mines = _m
        self.map = [[0] * _x for n in range(_y)]
        self.makeMap()
    
    # map作成
    def makeMap(self):
        for y in range(self.height):
            for x in range(self.width):
                self.map[y][x] = MySolveBox()
    
    # 全探索のイテレータ
    def searchALL(self):
        for y in range(self.height):
            for x in range(self.width):
                yield x, y
    
    def outofMap(self, _x, _y):
        return _x < 0 or _x >= self.width or _y < 0 or _y >= self.height
    
    # 周囲1マスの探索をするイテレータ
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
    
    # map情報を読み込む
    def getInfo(self, info_map):
        if self.height != len(info_map):
            raise IndexError('Size Error : height (' + str(len(info_map)) + ')')
        for w in info_map:
            if self.width != len(w):
                raise IndexError('Size Error : width (' + str(len(w)) + ')')
        for y in range(self.height):
            for x in range(self.width):
                self.map[y][x].info = info_map[y][x]
    
    # debug用出力関数
    def debug(self):
        for y in range(self.height):
            line = []
            for x in range(self.width):
                line.append((self.map[y][x].flags))
            print(line)
    
    # 座標から通し番号への変換
    def toIndex(self, _x, _y):
        return self.width * _y + _x
    
    # 通し番号から座標への変換
    def toRef(self, _n):
        return _n % self.width, _n // self.width
    
    # 未完成の数字セルについて計算，コマンドを作成１
    def makeCommand1(self):
        for (cursorX, cursorY) in self.numbers:
            # 1つの数字セルにおいて計算
            val1 = int(self.map[cursorY][cursorX].info) - self.map[cursorY][cursorX].flags
            if len(self.map[cursorY][cursorX].around) == val1:
                for n in self.map[cursorY][cursorX].around:
                    (x2, y2) = self.toRef(n)
                    self.setFlag += 1
                    self.commands.append(str(x2 + 1) + ', ' + str(y2 + 1) + ', f')
                return True
            if val1 == 0:
                for n in self.map[cursorY][cursorX].around:
                    (x2, y2) = self.toRef(n)
                    self.commands.append(str(x2 + 1) + ', ' + str(y2 + 1))
                return True
        return False
    
    # 未完成の数字セルについて計算，コマンドを作成２
    def makeCommand2(self):
        for (cursorX, cursorY) in self.numbers:
            val1 = int(self.map[cursorY][cursorX].info) - self.map[cursorY][cursorX].flags
            # 2つの数字セルにおいて計算
            for (x, y) in self.numbers:
                if x == cursorX and y == cursorY: continue
                val2 = int(self.map[y][x].info) - self.map[y][x].flags
                if (self.map[cursorY][cursorX].around | self.map[y][x].around) == self.map[cursorY][cursorX].around:
                    blo = self.map[cursorY][cursorX].around - self.map[y][x].around
                    bomb = val1 - val2
                    if len(blo) == 0:
                        continue
                    if len(blo) == bomb:
                        for n in list(blo):
                            (x2, y2) = self.toRef(n)
                            self.setFlag += 1
                            self.commands.append(str(x2 + 1) + ', ' + str(y2 + 1) + ', f')
                        return True
                    if bomb == 0:
                        for n in list(blo):
                            (x2, y2) = self.toRef(n)
                            self.commands.append(str(x2 + 1) + ', ' + str(y2 + 1))
                        return True
                if len(self.map[cursorY][cursorX].around | self.map[y][x].around) != 0 and val1 > val2:
                    blo = self.map[cursorY][cursorX].around - self.map[y][x].around
                    bomb = val1 - val2
                    if len(blo) == bomb:
                        for n in list(blo):
                            (x2, y2) = self.toRef(n)
                            self.setFlag += 1
                            self.commands.append(str(x2 + 1) + ', ' + str(y2 + 1) + ', f')
                        return True
        return False
    
    # 未完成の数字セルについて計算，コマンドを作成３
    def makeCommand3(self):
        line = self.myFunc(self.dic, (self.allBlocks, self.mines - self.setFlag))
        return line
    
    # 再帰関数
    def myFunc(self, lists, parent):
        # debug用
        '''
        print('-------------------')
        for buf in lists:
            L = list(buf[0])
            L1 = [self.toRef(n) for n in L]
            print([[x+1 for x in a] for a in L1], str(buf[1]))
        L = list(parent[0])
        L1 = [self.toRef(n) for n in L]
        print([[x+1 for x in a] for a in L1], str(parent[1]))
        print('-------------------')
        '''
        if len(lists) == 0:
            return False
        child = lists[0]
        # del lists[0]
        lists = lists[1:]
        if (parent[0] | child[0]) == parent[0]:
            blo = parent[0] - child[0]
            bomb = parent[1] - child[1]
            if len(blo) == 0:
                return False
            if len(blo) == bomb:
                for n in list(blo):
                    (x2, y2) = self.toRef(n)
                    self.setFlag += 1
                    self.commands.append(str(x2 + 1) + ', ' + str(y2 + 1) + ', f')
                return True
            if bomb == 0:
                for n in list(blo):
                    (x2, y2) = self.toRef(n)
                    self.commands.append(str(x2 + 1) + ', ' + str(y2 + 1))
                return True
            res = self.myFunc(lists, (parent[0] - child[0], parent[1] - child[1]))
            if res:
                return res
        return self.myFunc(lists, parent)
    
    # 計算機（完成したコマンドを返す）
    def solver(self):
        self.numbers = []
        # self.debug()
        # 開いたセルにおいて周囲のブロック情報を保存
        self.blocks = 0
        self.allBlocks = set()
        for x, y in self.searchALL():
            if self.map[y][x].info == 'b':
                self.blocks += 1
                self.allBlocks.add(self.toIndex(x, y))
            if (self.map[y][x].info != 'b' and self.map[y][x].info != 'f') and int(self.map[y][x].info) > 0:
                self.map[y][x].around = set()
                if self.map[y][x].complete:
                    continue
                self.map[y][x].flags = 0
                for x2, y2 in self.checkAround(x, y):
                    if self.map[y2][x2].info == 'b':
                        self.map[y][x].around.add(self.toIndex(x2, y2))
                    if self.map[y2][x2].info == 'f':
                        self.map[y][x].flags += 1
                if len(self.map[y][x].around) == 0 and int(self.map[y][x].info) == self.map[y][x].flags:
                    self.map[y][x].complete = True
                    # print(x+1, y+1, ':complete')
                    continue
                self.numbers.append((x, y))
        # 残ったブロックの情報をまとめる
        self.dic = []
        for (cursorX, cursorY) in self.numbers:
            set1 = self.map[cursorY][cursorX].around
            val1 = int(self.map[cursorY][cursorX].info) - self.map[cursorY][cursorX].flags
            flag = True
            for (buf_set, buf_val) in self.dic:
                if len(set1 ^ buf_set) == 0 and val1 == buf_val:
                    flag = False
                    break
            if flag:
                self.dic.append((set1, val1))
        # 次に出力するコマンドが無いとき
        if len(self.commands) == 0:
            flag = False
            # 全ての爆弾にフラグを立てたとき
            if not flag and self.mines == self.setFlag:
                for n in list(self.allBlocks):
                    (x2, y2) = self.toRef(n)
                    self.commands.append(str(x2 + 1) + ', ' + str(y2 + 1))
                flag = True
            # 未完成の数字セルが無いとき
            if not flag and len(self.numbers) == 0:
                x = self.width // 2
                y = self.height // 2
                if self.map[y][x].info == 'b':
                    self.commands.append(str(x + 1) + ', ' + str(y + 1))
                flag = True
            # 未完成の数字セルでの処理
            if not flag:
                flag = self.makeCommand1()
                if not flag:
                    flag = self.makeCommand2()
                    if not flag:
                        self.makeCommand3()
        # 次に出力するコマンドがあるとき
        if len(self.commands) != 0:
            line = self.commands[0]
            self.commands = self.commands[1:]
            return line
        return False
    
    # 情報を表示
    def showRemains(self, mode):
        line = ''
        for n in range(20): line += '-'
        print('')
        print('Setted flags:', self.setFlag)
        print('Remaining:', self.mines - self.setFlag)
        print(line)
        if mode == 1:
            print('Blocks:', self.blocks)
            self.analyze()
    
    # テキストファイルから情報を読み込む
    def readFile(self, fname):
        info_map = []
        with open(fname + '.txt', 'r') as f:
            fileinfo = f.read()
            lines = fileinfo.split('\n')
            for n in lines[0:-1]:
                info_map.append(list(n))
        return info_map
    
    # 全列挙でシミュレーション
    def analyze(self):
        
        # print(self.dic)
        if len(self.dic) == 0:
            self.dic.append((self.allBlocks, self.mines - self.setFlag))
        d = {}
        a = 0
        for sett in self.dic:
            for x in sett[0]:
                if str(x) not in d:
                    d[str(x)] = a
                    a += 1
        num = len(d)
        N = 2 ** num
        print(num)
        if num > 20:
            return False
        # 残りの全ブロックが全列挙するブロックであれば
        if num == self.blocks:
            self.dic.append((self.allBlocks, self.mines - self.setFlag))
        
        allcount = 0
        count = [0 for i in range(num)]
        for n in range(N):
            box = [0 for i in range(num)]
            for x in range(num):
                box[x] = (n & (2**x)) // (2**x)
            #print(box[::-1], 'count:', count[::-1], end = '')
            # 条件
            X = len(self.dic)
            con = [False for x in range(X)]
            for x in range(X):
                val = 0
                for a in self.dic[x][0]:
                    val += box[d[str(a)]]
                con[x] = (val == self.dic[x][1])
            flag = True
            for x in range(X):
                flag &= con[x]
            if flag:
                allcount += 1
                #print(' @', end = '')
                count = [count[i] + box[i] for i in range(num)]
            #print('')
        for k, v in d.items():
            a = count[v] /  allcount * 100
            print(tuple([i+1 for i in self.toRef(int(k))]), ':', '[' + str(a) + '%]')
        print('')
    
if __name__ == "__main__":
    
    x = 16
    y = 16
    m = 40
    showmode = 0
    
    myGame = mod_MyClass.MyCells()
    # myGame.playGame()
    comGame = MySolve()
    
    #[x, y, m] = myGame.getSize()
    myGame.resetMap(x, y, m)
    comGame.resetMap(x, y, m)
    if showmode >= 0:
        subprocess.call("clear")
        print('')
    while True:
        # 表示
        if showmode >= 0:
            myGame.showMap()
            sleep(showmode)
        # 情報取得
        info_map = myGame.giveInfo()
        # myGame.writeFile(info_map, 'box\\' + 'sample')
        # info_map2 = comGame.readFile('box\\' + 'sample')
        comGame.getInfo(info_map)
        line = comGame.solver()
        if showmode >= 0:
            subprocess.call("clear")
            print(line)
        if line == False:
            myGame.showMap()
            print('Can\'t Open!')
            comGame.showRemains(1)
            print('(x, y[, f])')
            print(':', end='')
            line = input()
        myGame.doCommand(line)
        if myGame.explosion:
            myGame.showMap()
            comGame.showRemains(0)
            print('Game Over')
            break
        elif myGame.clear:
            # myGame.writeFile(myGame.giveInfo(), 'box\\' + 'map_clear')
            myGame.showMap()
            comGame.showRemains(0)
            print('Game Clear')
            break

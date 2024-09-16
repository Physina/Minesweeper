from pandas import DataFrame # , read_excel
from functools import reduce
from random import sample  # For choosing random Cells on the Board to hold cells. I think this is less workload than random.sample() as it fumbles more integers (in C) while doing less sequence & function calls...
from WhenXTension import confirmor, display_txt, autoLog, current_dt


#########################################################################################


## For Logging Purposes:
LOG_FILEPATH = f"MINESWEEPER_LOG_{current_dt(incl_yyyy=True, incl_microsecs=False)}.txt".replace(":", ";")
DebugMode:bool = confirmor("Initialise in DebugView? :D (Mostly affects Log Entries until the game starts.)")
DebugInfo = "\nInitializing in Debug Mode! :)" if DebugMode == True else ""
LOG = open(LOG_FILEPATH, mode="a")
print("Log Filename:", LOG.name, f"({LOG_FILEPATH})")
autoLog(f"Minesweeper Startup at datetime {current_dt(incl_yyyy=True, incl_microsecs=True)}...", DebugInfo, FileStream=LOG, TimestampPrecision=False, LogTag="INFO", end="\n---------------------------------------------------------------------------------\n\n"); del DebugInfo


#############################################################################################


DISPLAY_SYMBOLS = { # Lists -> Legacy Support! :D
    "Covered": ['#'],
    "Uncov_formal": ['O'],  # -> an artefact of me attempting to implement savegame functionality. Maybe one day...
    "Empty": ['.'],
    "Bomb": ['B'],
    "Flag": ['F!']
}
"""To not accidentally knock over symbols while coding:\n
* "Covered": ['#']
* "Uncov_formal": ['O']
* "Empty": ['.']
* "Bomb": ['B']
* "Flag": ['F!']\n
(No guarantee them's the ones, though!!)
"""


def search_Neighbours(coordinate:tuple[int,int]):
    """NOTE (because this is so far-removed from any applications):\n
    This function is the police! ;D It searches the neighbouring cells on the board...\n
    DON'T YOU DARE FORGET IT! ;*
    * coordinate: FORMAT: (x,y) !!!"""
    x,y = coordinate
    matrix = [
            (x-1,y+1), (x,y+1), (x+1,y+1),
            (x-1,y)  ,          (x+1,y)  ,
            (x-1,y-1), (x,y-1), (x+1,y-1)]
    for point in matrix: yield point; continue


##########################################################################################


class Cell:
    def __init__(self, Coordinate:tuple[int,int], Bomb:bool=False, Neighbours_Bombs:int=0, Flagged:bool=False, Uncovered:bool=False, Face:str='#'):
        """* Coordinate: Format: (x,y)
        * Bomb: If the cell contains a chance to game-over yourself or not
        Neighbour_Bombs: The n(Bombs) the cell sees. (It is entirely oblivious to its own state, of course!)
        * Flagged: If the cell has been flagged and thus locked as 'Uncovered = False' or not
        * Uncovered: Whether the cell is displaying its contents, meaning either a Bomb, its neighbour's bomb count, or just being MT
        *Face: The string representation of the cell's current state, i.e. if it is uncovered or has a bomb..."""
        self.Coordinate = Coordinate
        self.Bomb = Bomb
        self.Neighbours_Bombs = Neighbours_Bombs
        self.Flagged = Flagged
        self.Uncovered = Uncovered
        self.Face = Face
        return


    def update(self) -> str|int:
        """Logic that updates each Cell's display element ('self.Face') according to it's internal boolean states (i.e. outputting 'B' if self.Uncovered == True and self.Bomb == True).\n
        Notably **does not set/recognise GAMEOVER**! That's the main_gameloop's job. :)\n
        Returns self.Face."""
        if self.Flagged == True:
            self.Face = DISPLAY_SYMBOLS["Flag"][0]
        elif self.Uncovered == False:
            self.Face = DISPLAY_SYMBOLS["Covered"][0]
        else:
            if self.Bomb == True:
                print("BOMB")
                self.Face == DISPLAY_SYMBOLS["Bomb"][0]
                return self.Face
            else:
                if self.Neighbours_Bombs in [0, '0']:
                    print("is MT")
                    self.Face = DISPLAY_SYMBOLS["Empty"][0]
                elif self.Neighbours_Bombs not in [0, '0']:  # NOTE: and self.Bomb != True and self.Uncovered == True ! ^^
                    print("SEES COUNTS:", self.Neighbours_Bombs)
                    self.Face = self.Neighbours_Bombs
                else: autoLog(f"Can't update cell @ {self.Coordinate} apparently...", FileStream=LOG, TimestampPrecision=False, LogTag="WARNING")
        return self.Face

############################################################

class Board:
    DIFFICULTIES = {
    "Easy": 0.20,
    "Medium": 0.285,
    "Hard": 0.365,
    "Professional": 0.50,
    "Clairvoyant": 0.66,
    "Impossible": 0.75
    }
    "Default mine count factors that are multiplied with number of total Board Cells to get MineCount! :D"
    
    def create_cells(self) -> dict[tuple[int,int], Cell]:    # for LOADING later (maybe): Saved_Bs:DataFrame|list[tuple[int,int]]=None, Saved_Fs:DataFrame=None, Saved_UNCs:DataFrame|list[tuple[int,int]]=None)
        """Creates Board-specific dict of cell tiles, as well as (upon creating a new Board!) assigning bombs to randomly selected cells and counting neighbouring bombs for indication.\n
        Alternatively, can be provided datafiles that Board.save() creates. This will override the functionalities meant to set up new cells while utilising the same infrastructure...\n
        """
        from time import sleep
        Celldict:dict[tuple[int,int],Cell] = {}
        autoLog("Creating Cells...", FileStream=LOG, LogTag="INFO")
        ## CREATE CELLS AND ASSIGN BOMBS:
        x,y = self.Dimensions
        BombDistr = sample(range(1, self.Cell_Total+1), self.Bomb_Total)
        if DebugMode == True: autoLog(f"With x={x}, y={y} and {self.Bomb_Total} Bombs, sample yielded this distribution:\n{BombDistr}\n...Victory Check is #Flagged == Board.Bombs, which would evaluate to {True if len(BombDistr) == self.Bomb_Total else False} if all Bombs were flagged here...", FileStream=LOG, LogTag="DEBUG", TimestampPrecision=False, flush=DebugMode)
        for x in range(1, x+1):
            if DebugMode == True: sleep(.75)
            for y in range(1, y+1):
                hasbomb = True if len(list(Celldict.keys()))+1 in BombDistr else False
                Celldict.update({(x,y): Cell((x,y),hasbomb) })
                continue
            continue
        autoLog("Idea for a future gamemode: Don't count TOTAL number of bombs, but decrement centre.Neighbours_Bombs by 1 each time no bomb is found on a neighbour! >;D -- 08.09.2024", FileStream=LOG, TimestampPrecision=False, LogTag="INFO / IDEA")
        ## COUNTS BOMBS FOR EACH CELL:
        for centre in list(Celldict.values()):
            x,y = centre.Coordinate
            for point in search_Neighbours(coordinate=(x,y)):
                try: Celldict[point]
                except KeyError as err: autoLog("search_Neighbours() triggered OOB event: Board.Dimensions =", self.Dimensions, "-//-> (x,y):", err, FileStream=LOG, LogTag="WARNING", msgtoConsole=None, end="\n", flush=True); continue
                neighbour = Celldict[point]
                if neighbour.Bomb == True:
                    centre.Neighbours_Bombs += 1
                else: continue
            continue
        return Celldict
    
    def custom_dimens_n_diff(self) -> list[tuple[int,int],float]:
        display_txt(["Firstly, Board Dimensions:", "You will be asked for two inputs..."])
        try:
            x = int(input('One for x, aka the "left-to-right direction": '))
            y = int(input('-- and one for y, aka up and down: '))
        except TypeError as err: raise TypeError(autoLog(f"{type(err)} {err} Failed to convert inputs for Board Dimension entry!", FileStream=LOG, TimestampPrecision=False, LogTag="ERROR", flush=True))
        Dimensions:tuple[int,int] = tuple((x,y))
        display_txt(["Next, the difficulty:", "This is determined via the percentage of all cells which is supposed to hold bombs.", "To make this accessible to children:", "Imagine that your boardy had exactly 100 cells...", "How many of those cells do you want me to select and hide bombs under?"])
        Diff = input(" >> Bombs per 100 Cells:\n << ")
        try: Diff = float(Diff)
        except TypeError as err: raise TypeError(autoLog(f"{type(err)} {err} // Ruh-roh, Scoob! The difficulty prompt entered cannot be converted into float and thus evaluated!", FileStream=LOG, TimestampPrecision=False, LogTag="ERROR", flush=True))
        if (0.00 < Diff < 1.00): pass
        else: Diff /= 100
        return [Dimensions, Diff]



    def __init__(self, Dimensions:tuple[int,int]=(5,5), Difficulty:float=DIFFICULTIES['Medium'], Cells:dict[tuple[int,int], Cell]=..., DebugCustomBypass:bool=False, Game_Over:None|str=None, Bombs_flagged:int=0): #, Name:str=current_dt()):
        display_txt([f"Would you like to set custom board lengths and difficulty?", "(Defaults are:", f"Dimensions[x,y] = {Dimensions}", f"Difficulty = 'Medium'={self.DIFFICULTIES["Medium"]*100}% Bombs)\n"])
        if DebugCustomBypass == True: pass
        elif confirmor(" >> Set customs?\n << ") != True: pass
        else: Dimensions, Difficulty = self.custom_dimens_n_diff()
        self.Dimensions = Dimensions
        self.Difficulty = Difficulty
        self.Cell_Total = reduce(lambda x,y: x*y, self.Dimensions); autoLog(self.Dimensions, '"reduces" to:', self.Cell_Total, FileStream=LOG, TimestampPrecision=False, LogTag="DEBUG NOTE", msgtoConsole=None); from math import prod; autoLog(f"math.prod(self.Dimensions) = {prod(self.Dimensions)} ==> MORE DIMENSIONS per Board??!??!?!?!?!", FileStream=LOG, TimestampPrecision=False, LogTag="INFO / IDEA"); del prod
        self.Bomb_Total = int(self.Cell_Total*self.Difficulty)
        self.Cells:dict[tuple[int,int], Cell] = self.create_cells() if Cells == ... or Cells == None else Cells
        x,y = Dimensions
        self.Display = DataFrame(data=[['#' for _ in range(1,x+1)] for _ in range(1,y+1)], index=range(1,y+1), columns=range(1,x+1))
        self.Bombs_flagged = Bombs_flagged
        ...
        return
    


    def verifyDisplay(self):
        """Populate / verify Display:\n
        (Also checks if BombsTotal == BombsFlagged n such...)"""
        for coord in list(self.Cells.keys()):
            x,y = coord
            count = 0
            for N_Coord in search_Neighbours((x,y)):
                try:
                    if self.Cells[N_Coord].Bomb == True: count += 1
                except Exception: pass
            if self.Cells[coord].Neighbours_Bombs != count: autoLog(f"Found faulty Bombcount at {(x,y)} ({self.Cells[coord].Neighbours_Bombs} => {count}). Updating that...", FileStream=LOG, LogTag="ERROR")
            if self.Display.at[y, x] != self.Cells[coord].Face:
                autoLog(f"Found Display discrepancy at {(x,y)}: Cell.Face={self.Cells[coord].Face} , Display.at[coord]={self.Display.at[y, x]} ; ==> The display value was re-rendered to be: {self.Cells[coord].update()}...\n(For completeness -- Cell in question:)", self.Cells[coord].__dict__, "\nLocals:", locals(), FileStream=LOG, LogTag="ERROR", msgtoConsole=f"Display Error -- See Log entry (Filename: {LOG.name}) for more!", TimestampPrecision=True, end="\n", flush=DebugMode)
                self.Display.at[y, x] = self.Cells[coord].Face
            continue
        # if self.Bomb_Total <
        return None

    ##################################################################################################

## Command Lookup Table (instead of a gigantic convoluted nested if-else-tree...):
CmdLookup:dict[tuple[bool,bool,bool],list[str]] = {
    (False, False, False): ["UNCOV", "FLAG", "CHANGE"],
    (False, False, True): ["UNCOV", "FLAG", "VIEW", "CHANGE"],
    (False, True, False): ["UNFLAG", "CHANGE"],
    (False, True, True): ["UNFLAG", "VIEW", "CHANGE"],
    (True, False, False): ["Sorry, you can't re-bury cells! Too dangerous! :D\n(The cell is already uncovered.)", None],
    (True, False, True): ["VIEW", "CHANGE"],
    (True, True, False): [ValueError("Found a cell set BOTH to uncovered AND flagged simultaneously! :o"), None],
    (True, True, True): [ValueError("Found a cell set BOTH to uncovered AND flagged simultaneously! :o"), None]
}
"""CmdLookup: Format: Cell.Uncovered, Cell.Flagged, DebugMode"""



def main_gameloop(Bored:Board=None, DebugMode:bool=False) -> bool:
    """
    **The Main Gameloop**\n
    (Might change in future versions:) Generating and governing interactions with the Board.\n
    (Board behaviour is simpler than I would like, for now...)\n
    Returns boolean depending on whether or not a new game will be initiated.\n
    ---------------------------------------------------------------------------
    **PARAMS / BEHAVIOUR:**
    * Board: Can safely be ignored. All worries one might have are handled by the Board constructor! :) Except...
    * DebugMode: False by default. It changes various things, from performance requirements on hot summer days to **disabling availability of custom Board dimensions & difficulty (^^)** (for DEBUG speed...)."""
    ## Determine DebugMode and get Board:
    if DebugMode == True:
        # Bored = Board(Cells=..., DebugCustomBypass=True)    # == "DEbUGBOARD"
        autoLog("Running current Board in DebugMode -- Just fyi! ;D", FileStream=LOG, LogTag="DEBUG", msgtoConsole=None, TimestampPrecision=True, end="\n", flush=True)
    if type(Bored) == Board: Bored = Bored
    else:
        autoLog("Board parsed into main_gameloop was not of type(Board)...", FileStream=LOG, LogTag="WARNING", msgtoConsole=None)
        Bored = Board()

    ## MAIN LOOP:
    Bored.verifyDisplay()
    VICTORY = False
    BOOM = False
    while BOOM != True:
        if DebugMode == True: pass
        else: Bored.verifyDisplay()
        autoLog(Bored.Display, FileStream=LOG, TimestampPrecision=False, LogTag="BOARD VIEW", sep="", flush=DebugMode)
        ## Input Registry:
        x = ""; y = ""
        while type(x) != int and type(y) != int:
            x = input(" >> Give integer index of a column ('x'):\n << ")
            y = input(" >> Give integer index of a row ('y'):\n << ")
            try:
                y = int(y)
                x = int(x); break
            except ValueError as err: autoLog(type(err), err, f"Conversion of input ordinates x={x} & y={y} failed... Try again!", flush=DebugMode); continue
        if confirmor(f"{x, y} -- You happy with these coordinates?") == False:
            autoLog("Alright, cancelling coordinate entry. Please try again. ^^", FileStream=LOG, TimestampPrecision=False, LogTag="INFO", flush=DebugMode)
            continue
        else:
            ## BOARD COMMAND HANDLING:
            curCell = Bored.Cells[(x,y)]
            display_txt(["Here is a list of Board Commands available to you:"])
            commanded = False
            while commanded != True:
                COMMANDS = """ **** COMMAND OVERVIEW: ****
                (Note that these are case-insensitive as your input is converted to uppercase upon entry.)
                UNCOV -- To uncover that Cell, seeing its contents and possibly triggering a mine
                FLAG -- To mark that cell as likely containing a bomb (Stops you from accidentally opening it! ;D)
                UNFLAG -- Of course, you can also remove flags on cells, unlocking them again. :)
                CHANGE -- Lastly, you can also *ALWAYS* change the cell in question, picking a new one.
                VIEW -- (Only available in Debug Mode:) Prints out system variables and states for sifting through if any bugs occur...\n\n"""
                possibleCMDs = CmdLookup[(curCell.Uncovered, curCell.Flagged, DebugMode)]
                autoLog(f"For the selected cell {(x,y)}, these commands are available:", possibleCMDs, FileStream=LOG, LogTag="INFO", end="\n", flush=DebugMode)
                if None in possibleCMDs:
                    autoLog("No valid commands. Please pick another cell.", FileStream=LOG, LogTag="WARNING", flush=DebugMode)
                    if type(Exception) in possibleCMDs:
                        autoLog(possibleCMDs, f"Coordinate: {(x,y)}", f"Display Status: {Bored.Display}", f"Locals: {locals()}", 'f"\n\n(Globals:) {globals()}"', FileStream=LOG, LogTag="ERROR", sep="\n", flush=DebugMode)
                        Bored.Display.at[y,x] = curCell.update()
                        break
                    else: break
                display_txt([f" >> Which would you like to execute on that Cell at {(x,y)}?"])
                cmd = input(" << ").upper()
                autoLog(" << ", cmd, FileStream=LOG, LogTag="BOARD CMD", msgtoConsole=None, flush=DebugMode)
                if cmd not in possibleCMDs:
                    autoLog("Sorry, command not possible currently. Please try another:", FileStream=LOG, LogTag="WARNING", flush=DebugMode)
                    continue
                elif cmd == "CHANGE": autoLog("Changing cell selection...", FileStream=LOG, LogTag="INFO", flush=DebugMode); break
                elif cmd == "VIEW": autoLog("Printing out system state...\nLocals:", locals(), '"\n\nGlobals:", globals()', FileStream=LOG, LogTag="DEBUG", flush=DebugMode)
                elif cmd == "UNFLAG":
                    curCell.Flagged = False
                    Bored.Display.at[y,x] = curCell.update()
                    if curCell.Bomb == True: Bored.Bombs_flagged -= 1
                    pass
                elif cmd == "FLAG":
                    curCell.Flagged = True
                    Bored.Display.at[y,x] = curCell.update()
                    if curCell.Bomb == True: Bored.Bombs_flagged += 1
                    pass
                elif cmd == "UNCOV":
                    curCell.Uncovered = True
                    Bored.Display.at[y,x] = curCell.update(); print(curCell.__dict__)
                        # /* Cell-Filter so far:
                        # [X] Uncovered; [X] Flagged
                        # [ ] Bomb?; [ ] MT?; [ ] Neighbour_Count?
                        # */
                    ## Checks if game is over by uncovering a Bomb:
                    if Bored.Cells[(x,y)].Face in DISPLAY_SYMBOLS["Bomb"] or curCell.Bomb == True:
                        autoLog(Bored.Display, FileStream=LOG, LogTag="GAME OVER", flush=DebugMode)
                        autoLog("The Face of that Cell updated to Bomb. I'm sorry kid, but those were your last words! >:)", FileStream=LOG, TimestampPrecision=False, LogTag="GAME OVER", flush=DebugMode)
                        if (Bored.Cells[(x,y)].Bomb == True and Bored.Cells[(x,y)].Uncovered == True): print("\n\nBOOM!!\n\n"); BOOM = True # I want to integrate this line into the check above later on, but for now, the separation is to monitor the behaviour! :)
                        else: raise ValueError(autoLog(f"[!! FATAL GAME-OVER BUG !!]\n...Checking if currentCell.Bomb == True ({Bored.Cells[(x,y)].Bomb}) and \ncurrentCell.Uncovered == True ({Bored.Cells[(x,y)].Uncovered})\n==> found that Cell.update() must have updated the Cell faultily...?!\nI doubt this is ever gonna happen tbh... but apparently it did?! :o\n\nTHIS GAME IS NOT YET OVER!! >:(", Filestream=LOG, TimestampPrecision=False, LogTag="ERROR", flush=DebugMode))
                        # ^^ [X] Bomb! :)
                    else:
                        ## GUARANTEED: Uncovers a safe cell!
                        Proofcount = 0
                        for nen in search_Neighbours(coordinate=(x,y)):
                            try:
                                if Bored.Cells[nen].Bomb == True: Proofcount += 1
                            except KeyError: pass
                        if Proofcount != curCell.Neighbours_Bombs:
                            oldfeef = Bored.Display.at[y, x]
                            Bored.Display.at[y, x] = curCell.update()
                            autoLog(f"Corrected Bombcount of {curCell.Coordinate} from {curCell.Neighbours_Bombs} (displayed {curCell.Face}) to {Proofcount} (== {oldfeef}).", FileStream=LOG, LogTag="WARNING")
                        # Should check neighbours for safety, then uncover + update() those aswell (if safe):
                        ZeroUncovBuffer = []
                        Passed = []
                        ZeroUncovBuffer.append((x,y))
                        while ZeroUncovBuffer != []:
                            for neighbour_coord in search_Neighbours(coordinate=ZeroUncovBuffer[0]):
                                if neighbour_coord in Passed: continue
                                try: Neighbour = Bored.Cells[neighbour_coord]
                                except KeyError as err: Passed.append((x,y)); autoLog("ZeroUncovCheck triggered OOB event: .....", type(err), err, "-- Coordinate has been appended to 'Passed' list!", FileStream=LOG, LogTag="WARNING", msgtoConsole=None, end="\n", flush=True); continue
                                if Neighbour.Uncovered == True or Bored.Cells[neighbour_coord].Flagged == True: continue
                                elif Neighbour.Bomb != True and Neighbour.Neighbours_Bombs >= 0:    # NOTE: Checking for Neighbours_Bombs is irrelevant, but I'll include it none-the-less!
                                    Neighbour.Uncovered = True
                                    x,y = neighbour_coord
                                    Bored.Display.at[y,x] = Neighbour.update()
                                    if Neighbour.Neighbours_Bombs == 0: ZeroUncovBuffer.append(neighbour_coord)
                                    else:
                                        try: Passed.append(ZeroUncovBuffer.pop(0))
                                        except IndexError: pass
                                else: pass
                                continue
                            try: fish = ZeroUncovBuffer.pop(0)
                            except IndexError: fish = (x,y)
                            if DebugMode == True: autoLog(f"Finished checking neighbours of Cell {fish}. Continuing...", FileStream=LOG, LogTag="DEBUG", flush=DebugMode)
                            if fish not in Passed: Passed.append(fish)
                            continue
                        pass
                else: pass
                if Bored.Bomb_Total <= Bored.Bombs_flagged:
                    autoLog(Bored.Display, FileStream=LOG, TimestampPrecision=False, LogTag="BOARD VIEW", flush=DebugMode)
                    autoLog("--------------------------------------------------------\n\tYo...\tYOU JUST WON!!! ^-^\n--------------------------------------------------------", FileStream=LOG, TimestampPrecision=False, LogTag="GAME OVER", flush=DebugMode)
                    VICTORY = True; BOOM = True
                    commanded = True
                else: commanded = True
        LOG.flush()
        continue
    if VICTORY == True: print("Nicely done! ^-^")
    else: print("...May your remains indicate Danger to others, so as to not repeat this tragedy...!")
    autoLog("A game has ended. Would you like another? :D", FileStream=LOG, LogTag="RESTART?")
    choice = confirmor(); autoLog(choice, FileStream=LOG, LogTag="NEW GAME?", flush=DebugMode)
    return choice

LOG.close()

#################################################################################################





if __name__ == "__main__":

    with open(LOG_FILEPATH, mode="a") as LOG:
        running = True
        while running:
            running = main_gameloop(DebugMode=confirmor("Would you like to play this Board in DebugMode?\n(Mostly affects Logging, but tends to make interaction with the game quite crowded.)"))
    LOG.close()

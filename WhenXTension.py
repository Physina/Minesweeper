import time
import datetime as dt
# import sys
from typing import TextIO

class UserDismay(Exception):
    """This is a kind of Debug Tool...\n
    To be used (usually in conjunction with 'confirmor()') if User is unhappy with the result of a process:\n
    if confirmor("You happy?) == False:\n
    \traise UserDismay("User is unhappy...! :/")\n
    Then you can either handle the exception (make the User happy! :3) OR exit code execution to modify your code."""
    pass

def display_txt(texts:list[str], yield_mode:bool=False, pass_query:bool=False):
    """Displays all text segments from input list in order, waiting (len(segment)*2)*{0.33} seconds in-between\n
    * yield_mode: Wether or not this function should behave as a generator, simply **passing on** the individual texts or not.
    * pass_query: *If* texts-argument is a list, return the last string after printing for use in... oh, idk... THE GODFATHER FUNCTION: gtx.confirmor! :D
    """
    if texts is []: raise ValueError("display_txt failed bc an empty list was passed... WHERE B DA TEXT??")
    else: print(f"DEBUG: {texts} appears not empty. Continuing!")
    while texts != []:
        try:
            text:str = str(texts[0])
            t = len(text)*8/100
            print("DEBUG:", t)
            if yield_mode == True:
                yield text; print(f"[[DEBUG: display_sleep_start, sleeping {t}secs...]]"); time.sleep(t); print("[[DEBUG: display_sleep_end]]")
            else:
                if pass_query == True and len(texts) == 1:
                    time.sleep(t)
                    return text
                else:
                    print(text)
                    time.sleep(t)
            del texts[0]
        except TypeError as te: raise TypeError(f"Exception when attempting to convert {texts[0]} of {texts} to str: {te}")
    return None



def stdz_input(instruction:str|list[str]):
    """Applies custom formatting (see below) to input function, for io-optics' sake! :D\n
    -> takes one singular string, passes it as 'prompt' argument to input(), and returns the input given by user.\n
    (Essentially just a "make-fancy" wrapper around input().)
    ( Naturally, this is compatible with display_txt(yield_mode=True), since it returns one string to be used in this function here! )\n
    Format printed:\n
      >> {instruction}\n
      << {...input by user...}"""
    if type(instruction) == str:
        print("\n >>", instruction)
        return input(" << ")
    elif type(instruction) == list:
        print("############\nDEBUG: Is input list deminishing...?\nLength =", len(instruction), "\n############")
        if len(instruction) not in [1, 0]:
            print(display_txt(instruction[0], yield_mode=True))
        elif len(instruction) == 1:
            print(" >> ", instruction[0])
        else:
            assert instruction == []
            return input(f" << ")
    else: raise TypeError("'instructions' argument of stdz_input is neither str nor list[str].")



def confirmor(text:str|list[str]="Do you wish to continue?", log_inverse:bool=False, add_True_opt:list[str]=[], add_False_opt:list[str]=[], retries:int=3) -> bool:
    """**USE CASES:**\n
    This is a general purpose confirmor function. Any user input (i.e. decisions, settings, etc.!), accidental or otherwise, can require confirmation this way.\n
    ...In console only, I should accentuate. :/
    * Prompt format: "[text] (y/n):"
    * Retries possible, but defaults to 3
    * (also compatible with display_txt)
    ---------------------------------------------
    **PARAMS / BEHAVIOUR:**\n
    *NOTE THAT INPUT is parsed through str.lower() before evaluation. Thus, it is INSENSITIVE TO CASE ON LETTERS!*
    * text: Any text to be parsed as hold-up question to the user. If list is parsed, last element of list is used to ask for confirmation.
    * log_inverse: Illustrated best by default text: function would output True if choice was "Yes". Reverse outputs the logical not-operation.
    * add_True_opt: Pass lists here for custom availability of options to be chosen, i.e. anticipated typos, quirky responses, or easter eggs! ;)
    * add_False_opt: Same custom flexibility as add_True_opt here. :)
    * retries: confirmor is embedded in a for loop to allow for misspells to happen without undesires behaviour. The "retries" argument specifies the iteration limit, as I am unwilling to specify a default output. I think that would be hurrendous! >:o
    """
    for attempts in range(retries):
        if type(text) == str:
            inp = input(f"{text} (y/n): \n << ").lower().replace("!", "")
        elif type(text) == list[str]:
            # TODO: (MAYBEEE?!) IMPLEMENT LATER!!!
            # --23.07.2024
            """for text in texts:
                print("############\nDEBUG: Is input list deminishing...?\nLength =", len(instruction), "\n############")
                if len(texts) not in [2, 1]:
                    print(display_txt(texts, yield_mode=True))
                elif len(texts) == 2:
                    print(" <<", texts[1])
                else:
                    inp:str = input("\n >>", instruction[0])
                    return inp"""
            pass

        True_Options = ["yes", "ye", "y", "absolutely", "definetly", "totally", "totally!", "fuck this!", "yes, fuck this!", "yes please!", "yes please", "yes, please", "yes please!"]
        False_Options = ["no", "n", "please no!", "not done yet", "i'm not done yet", "i'm not done yet!"]
        [True_Options.append(x.lower()) for x in add_True_opt]
        [False_Options.append(x.lower()) for x in add_False_opt]

        if inp in True_Options:
            out = True
            if log_inverse == True:
                out = False
            break
        elif inp in False_Options:
            out = False
            if log_inverse == True:
                out = True
            break
        print("Error, try again!")
    if attempts == retries-1:
        display_txt(texts=["Well shit! You made it past the decision limit... Happy Glühstrumpf! ._.", "The confirmor will pass your response instead of a boolean now instead! :)"])
        time.sleep(2.0)
    return out




def autoLog(*values:object, FileStream:TextIO|None=None, LogTag:str='INFO', msgtoConsole:str|None="#printLog", TimestampPrecision:bool=True, sep:str|None=" ", end:str|None="\n\n", flush:bool=False) -> None|str:
    """**USE CASES:**\n
    Wrapper around print(), printing both to terminal AND Log File simultaneously! ;D\n
    (See also: print() )\n
    Requires an open TextIO filestream to print to. **Will ONLY print to terminal sys.stdout otherwise!**\n
    A Timestamp is included along with the LogTag (-> see below), which truncates year information. Please make sure to pre-print them to the Logs Header accordingly!\n
    Can also parse on Error messages (see 'LogTag' parameter).\n
    ----------------------------------------------------------------------------------
    **PARAMS / BEHAVIOUR:**\n
    * values: Just like print(), non-kwrdargs to be printed are parsed before the boilerplate! :D
    * FileStream: The output of open(). Binary files are strictly not allowed, and note that the 'x' and 'w' writing modes lead to FileAlreadyExists failure and overwriting an existing file entirely! Hence, I recommend 'a' or 'a+.
    * LogTag: Just a category for Log Entries, but LogTag = 'ERROR' will lead to return of all values as a string, in case autoLog is called from inside an error raise! Other than that, LogTag can really be ANY Godless string you want. Here's some examples: 'INFO', 'WARNING', 'ERROR', 'NOTE', 'FOO', etc...
    * msgtoConsole: By default, the Log entry is also written to sys.stdout after writing to file (parsing 'äprintLog' ^^). Alternatively, if msgtoConsole is parsed, that will be printed to the console instead. Parse None-Type to mute Console printout for the entry altogether.
    * TimestampPrecision: Determines whether microseconds are included in the timestamp.
    """
    # The following if-statement is left-over from when 'toConsole' was still a bool...:
    # if FileStream == None and toConsole == False: raise ValueError("autoLog was unable to find any valid output space!\nFileStream =", FileStream, "and toConsole =", toConsole)
    Timestamp = current_dt(incl_microsecs=TimestampPrecision)
    if FileStream != None: print(f"[{Timestamp}] [{LogTag}]:\n", *values, sep=sep, end=end, file=FileStream, flush=flush)
    if msgtoConsole == None: pass
    elif msgtoConsole == "#printLog": print(f"[{Timestamp}] [{LogTag}]:\n", *values, sep=sep, end=end, file=None, flush=flush)
    else: print(f"[{Timestamp}] [{LogTag}]:\n", *msgtoConsole, sep=sep, end=end, file=None, flush=flush)
    return None if LogTag != 'ERROR' else Exception(str(values))



def current_dt(incl_yyyy:bool=False, incl_microsecs:bool=False) -> str:
    """Uses dt.datetime.now() to create a datetime string.\n
    Returns formatted string: f"{nows.year}{month}{day}-{nows.hour}:{nows.minute}:{nows.second}:{microsecs}"\n
    (That is the longest possible format. Year and microsecond information can be excluded, see parameters.)\n
    **Please be aware that this string can not be used in windows filenames as is because of the colons ':'!** Modify substrings accordingly, i.e. using str.replace()\n
    ---------------------------------------------------------
    **PARAMS / BEHAVIOUR:**
    * incl_yyyy: Year information is truncated by default, for brevity's sake.
    * incl_microsecs: By default, the time is only parsed on down to the second. incl_microsecs includes microseconds (1ppm of a second), formatted as [...]:ss:mcs.usc."""
    nows = dt.datetime.now()
    if nows.month <= 9: month = "0" + str(nows.month)
    else: month = nows.month
    if nows.day <= 9: day = "0" + str(nows.day)
    else: day = nows.day
    if incl_microsecs == True: microsecs = round(nows.microsecond/1000, ndigits=3)
    # if nows.hour < 7: incl_mmdd = True
    if incl_yyyy == False and incl_microsecs == False: return f"{month}{day}-{nows.hour}:{nows.minute}:{nows.second}"
    elif incl_yyyy == False and incl_microsecs == True: return f"{month}{day}-{nows.hour}:{nows.minute}:{nows.second}:{microsecs}"
    elif incl_yyyy == True and incl_microsecs == False: return f"{nows.year}{month}{day}-{nows.hour}:{nows.minute}:{nows.second}"
    else: return f"{nows.year}{month}{day}-{nows.hour}:{nows.minute}:{nows.second}:{microsecs}"





"""IDEA 22.06.24:
Diagnostics:
(i.e. for catching errors and getting information about those errors at runtime already via console! ;D)

to be printed:
* variable type vs. expected type
* ...

def exception_handler():
## EXAMPLES:
    #####
    i = input("Try floats, tuples, etc...!\n")
    try:
        i = tuple(i)
    except Exception as e: print(e)
    #####
    if type(Dimensions) != tuple:
            try:
                Dimensions = tuple(Dimensions)
            except Exception as e:
                print("Yo, sometingg wong with Board Dimensions: ", e)
        else: pass

"""





def type_corrector(obj, desired_type:type):
    """FOR REFERENCE:
    while True:
        i = input("Try floats, tuples, etc...!\n")
        try:
            t = tuple(i)
            print(type(t), ": ", t)
        except Exception as e: print(e)
        try:
            l = list(i)
            print(type(l), ": ", l)
        except Exception as e: print(e)
        try:
            fl = float(i)
            print(type(fl), ": ", fl)
        except Exception as e: print(e)
    """
    if type(obj) != desired_type:
        try:
            obj = desired_type(obj)
        except Exception as e:
            print("Calling type_corrector was unable to solve the issue: ", e)
            # IDEALLY OFC MORE COMES AFTER THIS BASED ON THE EXCEPTION TYPE!!
            # ...that's ironic! I determine behaviour of a type correction function based on the type of an Exception! ;D

    else: print("Calling type_corrector was a waste of time ??")
    return obj






if __name__ == "__main__":
    pass
    # autoLog(["miep", "mooop!", 4,5], filepath="Log.txt")
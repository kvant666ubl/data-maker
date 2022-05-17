import click as console

silence_mode = False


def logCE(message):
    """ Console log of critical error messages """
    if (silence_mode != True):
        console.secho(" " + "[X] " + message,bg='red')
    pass


def logE(message):
    """ Console log of error messages """
    if (silence_mode != True):
        console.secho(" " + "[x] " + message, fg='red')
    pass


def logW(message):
    """ Console log of warning messages """
    if (silence_mode != True):
        console.secho(" " + "[-] " + message, fg='yellow')
    pass


def logI(message, bold : bool =False):
    """ Console log of information messages """
    if (silence_mode != True):
        if (bold == True):
            console.secho(" " + "[+] " + message, bg='blue')
        else:
            console.secho(" " + "[+] " + message, fg='blue')
    pass


def logS(message):
    """ Console log of success messages """
    if (silence_mode != True):
        console.secho(" " + "[+] " + message, fg='green')
    pass


def logD(message):
    """ Console log of debug messages """
    if (silence_mode != True):
        console.secho(" " + "[D] " + message, bg='white', fg='black')


def logSym(message, bold : bool =False):
    """ Console log of any symbol messages """
    if (silence_mode != True):
        console.secho(" " + message, fg='blue')
    pass
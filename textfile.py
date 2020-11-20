import sys


def cardNameToTextfile(cardname, filename='MagicCardList.txt'):
    file = open(filename, "a")
    file.write("%s\r\n" % cardname)
    file.close()

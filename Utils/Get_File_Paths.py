from os import path, makedirs
import os

def GetFileList(dirName, endings=[".jpg", ".jpeg", ".png", ".mp4"]):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Make sure all file endings start with a '.'

    for i, ending in enumerate(endings):
        if ending[0] != ".":
            endings[i] = "." + ending
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + GetFileList(fullPath, endings)
        else:
            for ending in endings:
                if entry.endswith(ending):
                    allFiles.append(fullPath)
    return allFiles


def ChangeToOtherMachine(filelist, repo="TrainYourOwnYOLO", remote_machine=""):

    filelist = [x.replace("\\", "/") for x in filelist]
    if repo[-1] == "/":
        repo = repo[:-1]
    if remote_machine:
        prefix = remote_machine.replace("\\", "/")
    else:
        prefix = ((os.path.dirname(os.path.abspath(__file__)).split(repo))[0]).replace(
            "\\", "/"
        )
    new_list = []

    for file in filelist:
        suffix = (file.split(repo))[1]
        if suffix[0] == "/":
            suffix = suffix[1:]
        new_list.append(os.path.join(prefix, repo + "/", suffix).replace("\\", "/"))
    return new_list

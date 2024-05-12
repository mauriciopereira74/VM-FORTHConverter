from parser import analyser
import sys
from parser import usage

def main(filename,outFilename=None):
    if not outFilename:
        outFilename = filename.split(".")[0]
    outFilename += ".vm"
    fullLine = ""
    flag = False
    with open(filename,"r") as file:
        for line in file:
            if flag:
                fullLine += line
                if ";" in line:
                    usage()
                    analyser.parse(fullLine)
                    fullLine = ""
            if ":" in line and ";" not in line:
                flag = True
                fullLine += line
            else:
                usage()
                analyser.parse(line)
        with open(outFilename,"w") as outFile:
            outFile.write(analyser.operations)

if __name__  == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 4:
        if sys.argv[2] == "-o":
            main(sys.argv[1],sys.argv[3])

from os import listdir
from os.path import isfile, join

# WARNING: DO NOT USE!!!! VERY SPECIFIC USE CASE
if __name__ == "__main__":
    
    input("are you sure???")
    csv_files = [file for file in listdir("./") if isfile(file) and ".csv" in file]
    # parse csv files and output with each word in a seperate line
    for file in csv_files:
        with open(file, "r+") as f:
            line = f.readline()
            line = line.replace(", ", "\n")
            f.truncate(0)
            f.write(line)
    print("done")
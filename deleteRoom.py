import os

for f in os.listdir("."):
    if "room" in f and ".txt" in f:
        print(f)
        os.remove(f)
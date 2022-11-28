import os

for f in os.listdir("./room"):
    if "room" in f and ".txt" in f:
        print(f)
        os.remove(f)
        
for j in range(0, 10):
    for i in range(0, 10):
        
        roomNamefile = "./room/room" + str((j * 10) + i) + ".txt"
        with open(roomNamefile, 'w') as file:
            pass

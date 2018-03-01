import os
import random
import string

characters = string.digits + string.letters
for i in range(100): # generate 100 files
    #select a random file name lenght
    size = random.randint(7,10) # a random file size
    a = ""
    for i in range(size):
        a += random.choice(characters)
    a += '.txt'
    a = './Files/' + a
#     print a
    command = 'touch '+a
    print command
    os.system(command)
    

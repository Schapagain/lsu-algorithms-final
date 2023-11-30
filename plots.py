from FMIndex import FMIndex
from time import time
from random import randint,choice
from math import floor, log2
import os
from matplotlib import pyplot as plt
import numpy as np

META_CHAR = '$'
text = ""
BLOCK_SIZE = None

sample_data_path = '../sample-data/dna.50MB'
if (os.path.isfile(sample_data_path)):
    with open(sample_data_path) as f:
        i = 0
        for line in f.readlines()[:3]:
            i+=1
            line = line.strip()
            print('read line:',i,'length:',len(line))
            text += line
text += META_CHAR
sorted_chars = sorted(list(set(text+META_CHAR)))
character_set = ''.join(sorted_chars)

t1 = time()
index = FMIndex(text,character_set=character_set,debug=True, block_size=BLOCK_SIZE)
t2 = time()
print(f'Index has been built on the text in {(t2-t1):.3f} seconds')

def plotByBlockSize():
    ms = []
    ts = []
    n = len(text)
    block_sizes =range(1,1000,100)
    num_repeats = 1
    for i,b in enumerate(block_sizes):
        b = int(b)
        currIndex = FMIndex(text,character_set=character_set,debug=True, block_size=b)
        time_elapsed = 0
        for _ in range(num_repeats):
            shift = randint(b,n-b)
            deviation = randint(1,max(b//2,1))
            probePos = shift + choice([-1,1]) * deviation
            charIdx = randint(2,len(character_set)-1) # Exclude the META_CHAR from tests
            t1 = time()
            currIndex._waveletTree.getRank(charIdx,probePos)
            t2 = time()
            time_elapsed+= (t2-t1)
        ms.append(b)
        ts.append(float("{:.4f}".format(time_elapsed*1000/num_repeats)))
        print(f'Block #{i} / {len(block_sizes)} blocks')
    
    fig,(ax1) = plt.subplots()
    fig.suptitle('Query Time Vs Block Size (λ)')

    ax1.scatter(ms,ts,marker='x')
    ax1.set_ylabel('Query Time (ms)')
    ax1.set_xlabel('Block Size (λ)')

    z = np.polyfit(ms,ts,1)
    p = np.poly1d(z)
    ax1.plot(ms,p(ms),'r-')
    plt.show()


def plotBlockVsNoBlock():
    num_repeats = 10
    shift = 0
    skip = 50
    ts = []
    ms = []
    for i in range(0,min(100,len(text)+1)):
        time_elapsed = 0
        for trail_num in range(num_repeats):
            charIdx = randint(2,len(character_set)-1) # Exclude the META_CHAR from tests
            textIdx = shift+i*skip
            t1 = time()
            index._waveletTree.getRank(charIdx,textIdx)
            t2 = time()
            time_elapsed+= (t2-t1)
        ms.append(textIdx)
        ts.append(float("{:.4f}".format(time_elapsed*1000/num_repeats)))
        print(f'Index: {textIdx} for char: {charIdx}, time: {(time_elapsed*1000/num_repeats):.3f}')
    
    blockedIndex = FMIndex(text,character_set=character_set,debug=True, block_size=500)

    t2s = []
    m2s = []
    for i in range(0,min(100,len(text)+1)):
        time_elapsed = 0
        for trail_num in range(num_repeats):
            charIdx = randint(2,len(character_set)-1) # Exclude the META_CHAR from tests
            textIdx = shift+i*skip
            t1 = time()
            blockedIndex._waveletTree.getRank(charIdx,textIdx)
            t2 = time()
            time_elapsed+= (t2-t1)
        m2s.append(textIdx)
        t2s.append(float("{:.4f}".format(time_elapsed*1000/num_repeats)))
        print(f'Index: {textIdx} for char: {charIdx}, time: {(time_elapsed*1000/num_repeats):.3f}')

    fig,(ax1,ax2) = plt.subplots(2,1)
    fig.suptitle('Difference in query time for blocked and non-blocked bit-arrays')

    ax1.scatter(ms,ts,marker='x')
    ax1.set_ylabel('Query Time (ms)')

    z = np.polyfit(ms,ts,1)
    p = np.poly1d(z)
    ax1.plot(ms,p(ms),'r-')

    ax2.scatter(m2s,t2s)
    ax2.set_ylabel('Query Time (ms)')
    ax2.set_xlabel('Query Index (λ=500)')

    for i in range(10):
        z = np.polyfit(m2s[10*i:(i+1)*10],t2s[10*i:(i+1)*10],1)
        p = np.poly1d(z)
        ax2.plot(m2s[10*i:(i+1)*10],p(m2s[10*i:(i+1)*10]),'r-')
   
    plt.show()

def main():
    plotByBlockSize()

if __name__ == '__main__': main()
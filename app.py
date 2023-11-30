from flask import Flask, render_template, request
from FMIndex import FMIndex
from time import time
import json
from random import randint,choice
from math import floor, log2
import os


META_CHAR = '$'
text = ""
BLOCK_SIZE = 100

sample_data_path = '../sample-data/dna.50MB'
if (os.path.isfile(sample_data_path)):
    with open(sample_data_path) as f:
        i = 0
        for line in f.readlines()[:4]:
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

app = Flask(__name__)

@app.route("/",methods=['GET','POST'])
def main():
    if request.method == 'GET':
        return render_template('index.html',character_set=' | '.join(sorted_chars))
    else:
        pattern = request.form.get('q')
        t1 = time()
        print('searching for...',pattern)
        count = index.findMatchCount(pattern)
        t2 = time()
        return render_template('index.html',count=count, query=pattern, t_span=t2-t1,character_set=' | '.join(sorted_chars))

@app.route("/rank/",methods=['GET'])
def rank():
    try:
        charIdx = int(request.args.get('char_idx'))
        idx = int(request.args.get('idx'))
    except:
        return f"<p> Error: char_index and idx must be provided as query params </p>"
    t1 = time()
    charRank = index._waveletTree.getRank(charIdx,idx)
    t2 = time()
    return f"<p>Rank: {index._waveletTree.getRank(charIdx,idx)}. Computed in {(t2-t1):.3f} seconds</p>"

@app.route("/trends",methods=['GET'])
def trends():
    '''
    Build a plot indicating how the WaveletTree getRank() method performs
    as a function of character size (Σ) and length of length of the indexed text (n)
    '''
    data = {
        "text_length": len(text),
        "block_size": BLOCK_SIZE,
        "y_label": "Run Time (s)",
        "x_label": "Pattern Length",
        "title": "",
        "plot_data":{
            "ms": [],
            "ts": []
        }
    }
    # Only vary the position of the rank query, not the text
    if request.args.get('single_text') in ['True','true']:
        data['title'] =  "Query Time vs Query Index on DNA Dataset"
        new_block_size = request.args.get('block_size')
        if new_block_size is not None:
            try:
                newIndex = FMIndex(text,character_set=character_set,debug=True, block_size=int(new_block_size))
                data['block_size'] = new_block_size
            except:
                print('Invalid block_size provided')

        num_repeats = 5
        shift = 10000
        skip = 1
        for i in range(0,min(1000,len(text)+1)):
            time_elapsed = 0
            for trail_num in range(num_repeats):
                charIdx = randint(2,len(character_set)-1) # Exclude the META_CHAR from tests
                textIdx = (shift+i)*skip
                t1 = time()
                if new_block_size is None:
                    index._waveletTree.getRank(charIdx,textIdx)
                else:
                    newIndex._waveletTree.getRank(charIdx,textIdx)
                t2 = time()
                time_elapsed+= (t2-t1)
            data['plot_data']['ms'].append(textIdx)
            data['plot_data']['ts'].append("{:.7f}".format(time_elapsed/num_repeats))
            print(f'Index: {i} for char: {charIdx}')

    # Vary block size and do random rank queries
    else:
        data['x_label'] = "Block Size"
        data['y_label'] =  "Query Time (s)"
        n = len(text)
        data['title'] =  f"Query Time vs Block Size on DNA Dataset (n={n})"
        block_sizes = [log2(n),log2(n)**2,log2(n)**3]
        num_repeats = 2
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
            data['plot_data']['ms'].append(b)
            data['plot_data']['ts'].append("{:.7f}time".format(time_elapsed/num_repeats))
            print(f'Block #{i} / {len(block_sizes)} blocks')


    return render_template('trends.html',jsonData=json.dumps(data))
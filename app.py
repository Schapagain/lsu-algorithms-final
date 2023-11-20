from flask import Flask, render_template, request
from FMIndex import FMIndex
from time import time
import json
from random import randint
from math import floor
import os

META_CHAR = '$'
text = ""

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
index = FMIndex(text,character_set=character_set,debug=True, block_size=1)
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
        "plot_data":{
            "ms": [],
            "ts": []
        }
    }
    
    # Only vary the position of the rank query, not the text
    if request.args.get('single_text') in ['True','true']:
        shift = 0
        skip = 10
        for i in range(0,300):
            charIdx = randint(2,len(character_set)) # Exclude the META_CHAR from tests
            t1 = time()
            index._waveletTree.getRank(1,(shift+i)*skip)
            t2 = time()
            time_elapsed = (t2-t1)
            data['plot_data']['ms'].append(i)
            data['plot_data']['ts'].append(time_elapsed)
            print(f'Index: {i}')

    return render_template('trends.html',jsonData=json.dumps(data))
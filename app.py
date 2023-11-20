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
        for line in f.readlines()[:4]:
            i+=1
            line = line.strip()
            print('read line:',i,'length:',len(line))
            text += line

text += META_CHAR
sorted_chars = sorted(list(set(text+META_CHAR)))
character_set = ''.join(sorted_chars)

t1 = time()
index = FMIndex(text,character_set=character_set,debug=True)
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

@app.route("/trends",methods=['GET'])
def trends():
    data = {
        "text_length": len(text),
        "plot_data":{
            "ms": [],
            "ts": []
        }
    }

    num_repeats = 1 # Repeat queries for the same m and take average for consistency
    pattern_lengths =  [200,400,600,800,1000,1200]
    characters_in_pattern = character_set[1:] # Exclude the META_CHAR from the pattern
    for i,m in enumerate(pattern_lengths):
        total_time = 0
        for j in range(num_repeats):
            shift = randint(0,len(text)-m-1)
            pattern = text[shift:shift+m]
            t1 = time()
            index.findMatchCount(pattern)
            t2 = time()
            time_elapsed = (t2-t1)
            print(f'Trail {j+1} for m={m} finished in {time_elapsed} seconds.')
            total_time += time_elapsed

        data['plot_data']['ms'].append(m)
        data['plot_data']['ts'].append(total_time/num_repeats)

    return render_template('trends.html',jsonData=json.dumps(data))
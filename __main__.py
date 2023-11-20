from FMIndex import FMIndex

text = "acacaac$"
index = FMIndex(text,character_set="$abcd")
print('Index has been built on the text')
print(index.findMatchCount('aca'))
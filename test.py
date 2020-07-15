import os,sys,re
import wordapi
kata=re.compile('[\u30a1-\u30f6]')
result=kata.search('aワ')
if result:
    print(result.group())
else:
    print('No matching!')
katas=wordapi.getAllKata()
print(len(katas))
# for i in katas:
#     print(i)
# print(type(result))
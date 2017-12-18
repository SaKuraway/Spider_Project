#-*-coding:utf-8-*-
index = 0
a = [1,2,3]
b = [1,2,3]
c = [1,2,3]
d = zip(a,b,c)
for i,j,k in d:
    print(index,i,j,k)
    index += 1
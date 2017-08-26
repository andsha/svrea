n,m = map(int, input().split())
arr = list(map(int, input().split()))
A = set(map(int, input().split()))
B = set(map(int, input().split()))

s = 0

for i in arr:
    if i in A:
        s+=1
    elif i in B:
        s -= 1

print(s)
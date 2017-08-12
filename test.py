string= 'BANANA'
v = 'AEIOU'
stu = {}
kev = {}
for idx in range(len(string)):
        for idy in range(idx + 1, len(string) + 1):
                sub = string[idx:idy]
            if sub[0] in v:
                if sub in kev:
                    kev[sub] += 1
                else:
                    kev[sub] = 1
            else:
                if sub in stu:
                    stu[sub] += 1
                else:
                    stu[sub] = 1
kevscore = 0
for word in kev:
        kevscore += kev[word]

stuscore = 0
for word in stu:
        stuscore += stu[word]

print('Kevin %' % kevscore if kevscore > stuscore else 'Stuart %s' % stuscore)

aefa

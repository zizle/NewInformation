# _*_ coding:utf-8 _*_
b_list = []
a_list = [x for x in range(1, 10)]
for i in a_list:
    if i % 2 == 0:
        b_list.append({})
    else:
        b_list.append(i)

print(b_list)
for item in b_list:
    if item:
        print('1')
    else:
        print('2')
# toim1=10
# toim2=20
# toim3=30
# rete=toim1+toim2+toim3
# sad=toim1*toim2*toim3
# timer=toim1+\
#     rete+\
#     sad
#
# print(timer.__str__()+r"dasdasd\n")
# print(toim1)
# print(toim2)
# print(toim3)
# print(toim1,end="")
# print(toim2,end="")
# import sys
# print(sys.path)
# print(type(toim1))
# print(isinstance(toim1, int))
# print(17%3)
# print(17//3)
# print(17/3)
# print(17**3)
# def reverse_string(s):
#     return s[::-1]
# print(reverse_string("hello"))
# def reverse_string(input_string):
#     input_string=input_string.split(" ")
#     input_string.reverse()
#     print(input_string)
#     return " ".join(input_string)
#
#
# print(reverse_string("hello world how are you"))
# dict2=([('Runoob', 1), ('Google', 2), ('Taobao', 3)])
# print(type(dict2))
# print(dict2)
# dict1={x: x**2 for x in (2, 4, 6)}
# print(type(dict1))
# print(dict1)
# dict22={"Runoob":1, "Google":2, "Taobao":3}
# print(dict22)
# list1=[1,2,3,4,5]
# list2=[6,7,8,9,10]
# list3=list1+list2+list1
# print(list3)
# sorted_list=sorted(list3)
# print(sorted_list)
#
# if (data:=1)>10:
#     print("data is greater than 10")
# else:
#     print("data is less than or equal to 10")
# # while (line := input("输入内容: ")) != "exit":
# #     print(f"你输入了：{line}")
# a = (x for x in range(1, 10))
# print(next(a))
# print(a)
# tuple(a)
# print(a[0])
# list(a)
# print(a)
# # !/usr/bin/python3

# import sys  # 引入 sys 模块
#
# list = [1, 2, 3, 4]
# it = iter(list)  # 创建迭代器对象
#
# while True:
#     try:
#         print(next(it))
#         # if next(it) == 3:
#         #     break
#     except StopIteration:
#         print("StopIteration")
#         sys.exit()
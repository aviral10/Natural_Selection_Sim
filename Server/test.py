# import random
# class test:
#     def __init__(self, x,y):
#         self.x = x
#         self.y = y
#     def __repr__(self):
#         return f"{self.__dict__}"
# arr = [test(i,i*10) for i in range(5)]
# choice = random.choice(arr)
# print(choice)
# choice.x = 10000
# print(arr)
# print(int("11111111111111111111111111111111", 2), (1<<32) - 1)
arr = [1,2,3,4,5]
brr = [5,6,7,8,9,10,11]
brr = brr[:len(arr)]
print(brr)
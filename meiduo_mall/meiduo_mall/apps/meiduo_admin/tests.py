from django.test import TestCase


# Create your tests here.
# def adder(x):
#     def wrapper(y):
#         return x + y
#
#     return wrapper
#
#
# adder5 = adder(5)
# print(adder5(adder5(6)))

class D:
    data = {'a': 1}

    def __init__(self):
        self.dict1 = {'a': 1}

    def data1(self):
        return self.dict1


d = D()
d.data['b'] = 2
print(d.data)

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

class dengcha:
    def __init__(self, a1, an, d):
        self.a1 = a1
        self.an = an
        self.d = d

    def he(self):
        i = self.a1
        sum1 = i
        while i < self.an:
            temp = i + 2
            sum1 = sum1 + temp
            i = temp
        return sum1


dc = dengcha(20, 70, 2)
print(dc.he())
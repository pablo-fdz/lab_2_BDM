# coding=utf-8
from model1 import Model1
from model2 import Model2
from model3 import Model3
import datetime
import sys
from pymongo import MongoClient

# Show options for the user when the program starts
def show_options(new):
    print("Choose the option you want to execute:")
    print("\t 0 - Exit")
    print("\t 1 - Model 1")
    print("\t 2 - Model 2")
    print("\t 3 - Model 3")

new = True
show_options(new)
op = int(input())

while op != 0:
    if op == 1:
        n = int(input("Insert the number of documents to create:"))
        m = Model1()
        m.data_generator(n)
    elif op == 2:
        n = int(input("Insert the number of documents to create:"))
        m = Model2()
        m.data_generator(n)
    elif op == 3:
        n = int(input("Insert the number of documents to create:"))
        m = Model3()
        m.data_generator(n)
    else:
        print ("Exitting ...")
        sys.exit()

    show_options(new)
    op = int(input())
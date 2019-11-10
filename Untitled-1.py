#Problem 1

class Library:

    def __init__(self):
        self.books = []

    def __str__(self):
        return str(self.books)

    def add_book(self, book):
        self.books.append(book)

    def borrow_book(self, book):
        ind = self.available(book)
        if ind >= 0:
            self.books.pop(ind)
            return True
        else:
            return False
            
    def available(self, book):
        for i in range(len(self.books)):
            if self.books[i] == book:
                return i
        return -1
'''
lib = Library()
lib.add_book("A Game of Thrones")
lib.add_book("Moneyball")
lib.add_book("Moby Dick")
print(lib.available("Moneyball"))
#__________________________
lib.borrow_book("Moby Dick")
#__________________________
print(lib)
#_____________________________________________________
print(lib.borrow_book("Becoming"))
#___________________________
'''
# Problem 2
class Odometer():

    def __init__(self):
        self.mileage = 0

    def __str__(self):
        return str(self.mileage)

    def __repr__(self):
        return str(self)

    def get_mileage(self):
        return self.mileage

    def add_mileage(self, miles):
        self.mileage += miles

    def reset_mileage(self):
        self.mileage = 0
'''
od1 = Odometer()
print(od1)
print(od1.get_mileage())
od1.add_mileage(60)
print(od1.get_mileage())
od1.reset_mileage()
print(od1.get_mileage())
'''
#Problem 3
import random

class HeapOfBeans():

    def __init__(self):
        self.beans = 16

    def is_over(self):
        return not self.beans > 0

    def player_1_turn(self):
        removed = random.randint(1,3)
        self.beans -= removed
        if self.beans < 0:
            self.beans = 0
        print("player 1 removed", removed, "beans,", self.beans, "remaining")

    def player_2_turn(self):
        if self.beans % 2 == 0:
            removed = 1
        else:
            removed = 2
        self.beans -= removed
        if self.beans < 0:
            self.beans = 0
        print("player 2 removed", removed, "beans,", self.beans, "remaining")

def main():
    game = HeapOfBeans()

    while not game.is_over():
        game.player_1_turn()
        if not game.is_over():
            game.player_2_turn()
            if game.is_over():
                print("player 2 lost")
        else:
            print("player 1 lost")
    
#main()

#Problem 4
class Student ():

    def __init__(self, name, NYU_id, net_id):
        self.name = name
        self.NYU_id = NYU_id
        self.net_id = net_id
        self.grades_list = []

    def add_grade(self, catalog_name, grade):
        self.grades_list.append((catalog_name, grade))

    def average(self):
        grades_sum = 0
        grades_count = 0
        for course, grade in self.grades_list:
            if grade != "":
                grades_sum += int(grade)
                grades_count += 1
        return round(grades_sum / grades_count)
        
    def get_email(self):
        return self.net_id + "@nyu.edu"

    def __str__(self):
        return self.name + " " + self.NYU_id + " " + self.net_id + " " + str(self.grades_list)

def load_students(students_data_filename):

    student_lst = []

    file_obj = open(students_data_filename, "r")

    courses = file_obj.readline().strip().split(",")[3:] #first just readline, then take courses from it

    for line in file_obj:
        line_lst = line.strip().split(",")
        idnum = line_lst[0]
        name = line_lst[1]
        netid = line_lst[2]
        current_student = Student(name, idnum, netid)
        #current_student.grades_list = []
        grades = line_lst[3:]
        for i in range(len(grades)):
            current_student.grades_list.append((courses[i],grades[i]))
        student_lst.append(current_student)

    return student_lst, courses

def generate_performance_report(students_lst):
    average_lst = []
    for student in students_lst:
        avg = student.average()
        average_lst.append((student.NYU_id, avg))

    return average_lst

def generate_course_mailing_list(students_lst, catalog_name):
    mailing_lst = []
    
    for student in students_lst:
        grades = student.grades_list
        for course, grade in grades:
            if course == catalog_name and grade != "":
                mailing_lst.append(student.get_email())

    return mailing_lst
            
def main():
    
    student_list, courses = load_students("grades.csv")

    for item in student_list[:5]:
        print(item)

##    print(student_list[0])
##
##    print(student_list[0].get_email())
##
##    student_list[0].add_grade("CS-UY 2124", "85")
##
##    print(student_list[0])

    perf_rep = generate_performance_report(student_list)
    print(perf_rep[:5])

    mailing_lst = generate_course_mailing_list(student_list, "CS-UY 1134")
    print(mailing_lst[:5])
 
'''
    mailing_lst_dict = {}
    for course in courses:
        mailing_lst_dict[course] = generate_course_mailing_list(student_list, course)

    for course in mailing_lst_dict:
        print(course)
        for email in mailing_lst_dict[course]:
            print(email)
        print()
'''
#main()




        
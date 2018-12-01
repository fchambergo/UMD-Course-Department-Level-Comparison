from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QComboBox, QPushButton, QMessageBox
from PyQt5.QtCore import QSize, QRect, Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap
import requests
import sys
import matplotlib.pyplot as plt
import numpy as np


class ApplicationWindow(QMainWindow):
    def __init__(self):
        """
        This constructor creates a graphical user interface with loaded departments from the UMD Web API
        """

        #request UMD Web API information on departments
        r = requests.get('https://api.umd.io/v0/courses/departments')

        status = r.status_code
        if status != 200:
            print("error: server returned code {}".format(status))

        #read information from API into a variable
        data = r.json()  # list of dictionaries

        self.dept = {} #initialize dictionary to keep departments separate. dept_id(key), department name (value)

        #Fill in dictionary
        for id in data:
            self.dept[id['dept_id']] = id['department']

        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(640, 400))
        self.setWindowTitle("UMD Web API - Course Level Department Comparison")

        # Create layouts for insertion of widgets
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        gridLayout = QGridLayout(self)
        centralWidget.setLayout(gridLayout)

        # Create combobox for list of departments
        self.comboBox1 = QComboBox()
        self.comboBox1.move(200,100)
        self.comboBox1.setGeometry(QRect(10, 10, 100, 31))
        self.comboBox1.setObjectName(("comboBox1"))
        for key, value in self.dept.items():
            self.comboBox1.addItem(key + ' - ' + value)
        gridLayout.addWidget(self.comboBox1, 1, 1)

        # Create another combobox for list of departments
        self.comboBox2 = QComboBox()
        self.comboBox2.move(1200, 100)
        #self.comboBox2.setGeometry(QRect(40, 40, 100, 31))
        self.comboBox2.setObjectName(("comboBox2"))
        for key, value in self.dept.items():
            self.comboBox2.addItem(key + ' - ' + value)
        gridLayout.addWidget(self.comboBox2, 1, 2)

        # Create a button for giving the comparison bar graph
        self.button = QPushButton("Give Graph", self)
        self.button.move(200, 300)
        self.button.clicked.connect(self.run_graph)

        # Create a button for listing the classes of a department
        self.button2 = QPushButton("List Classes", self)
        self.button2.move(400, 300)
        self.button2.clicked.connect(self.run_msg)

        # Description for the top of program with a custom image
        self.label = QLabel(self)
        pixmap = QPixmap('C:/Users/frank/Desktop/School/Classes/INST326/326 project stuff/umd courses project.png')
        pixmap2 = pixmap.scaled(700,700, Qt.KeepAspectRatio)
        self.label.setPixmap(pixmap2)
        self.label.resize(1000,200)

    def run_msg(self):
        """
        This function creates objects from the user-selected departments and runs the generate message function
        to create a list classes for both departments
        """
        choice1 = str(self.comboBox1.currentText())[0:4]
        choice2 = str(self.comboBox2.currentText())[0:4]
        dept1 = CoursesOfDepartment(choice1)
        dept2 = CoursesOfDepartment(choice2)

        self.generate_message(dept1, dept2)

    def run_graph(self):
        """
        his function creates objects from the user-selected departments and runs the generate graph function
        to create a bar graph comparing both departments
        """
        choice1 = str(self.comboBox1.currentText())[0:4]
        choice2 = str(self.comboBox2.currentText())[0:4]
        dept1 = CoursesOfDepartment(choice1)
        dept2 = CoursesOfDepartment(choice2)

        self.generate_graph(dept1, dept2)

    def generate_graph(self, department1, department2):
        """
        This message generates a bar graph comparing the number of 100, 200, 300, and 400 levels classes
        for the two user-selected departments
        :param department1: first department choice of user
        :param department2: second department choice of user
        """

        n_groups = 4
        d1 = (department1.separate_level().values())
        d2 = (department2.separate_level().values())

        # create plot
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 0.35
        opacity = 0.8

        rects1 = plt.bar(index, d1, bar_width,
                         alpha=opacity,
                         color='b',
                         label=department1.get_department())

        rects2 = plt.bar(index + bar_width, d2, bar_width,
                         alpha=opacity,
                         color='g',
                         label=department2.get_department())

        #create labeling
        plt.xlabel('Levels')
        plt.ylabel('Number of Classes')
        plt.title('# of Classes: ' + department1.get_department() + " v " + department2.get_department())
        plt.xticks(index + bar_width, ('100', '200', '300', '400'))
        plt.legend()

        plt.tight_layout()
        plt.show()

    def generate_message(self, c1, c2):
        """
        This function creates the format of the classes within the user-selected departments and puts the text
        as a pop up message.
        :param c1: user selected department choice one
        :param c2: user selected department choice two
        """

        #Initialize strings
        msg = ""
        msg2 = ""

        #Create text/list of courses within departments
        for key, value in c1.courses_list.items():
            if int(key[4]) < 5:
                before = key + " - " + value + "\n"
                msg = msg + before

        for k, v in c2.courses_list.items():
            if int(k[4]) < 5:
                b = k + " - " + v + "\n"
                msg2 = msg2 + b

        #Generate pop up messages
        QMessageBox.information(self, c1.get_department() + " - " + c2.get_department(), self.comboBox1.currentText()[7:] + "\n\n" + msg, QMessageBox.Ok, QMessageBox.Ok)
        QMessageBox.information(self, c1.get_department() + " - " + c2.get_department(), self.comboBox2.currentText()[7:] + "\n\n" + msg2, QMessageBox.Ok, QMessageBox.Ok)

class CoursesOfDepartment():
    """
    This class grabs the information of courses of a department
    """

    def __init__(self, dept):
        """
        This class grabs the information on courses of a department from the UMD Web API
        :param dept: the passed department from the user
        """
        self.courses_list = {}
        self.dept = dept
        resp = requests.get('https://api.umd.io/v0/courses?dept_id=' + dept)
        status = resp.status_code
        if status != 200:
            print("error: server returned code {}".format(status))

        #transfer information from umd web api to another dictionary for methods
        self.dept_info = resp.json()  # list of dictionaries

        #fill dictionary with course name/course id information. Course id = key, course name = value
        for course in self.dept_info:
            self.courses_list[course["course_id"]] = course["name"]


    def get_department(self):
        """
        This function returns the name of the department in its abbreviated form. i.e: INST (for Information Science)
        :return: the abbreviated form of department
        """
        return self.dept

    def separate_level(self):
        """
        This function creates a dictionary of the number of classes for level 100, 200, 300, and 400 classes.
        The keys of the dictionary are the levels and values are the number of courses of that level that are present
        :return: the dictionary of number of undergrad courses
        """

        #intialize level dictionary with values set to 0
        level_dict = {100: 0, 200: 0, 300: 0, 400: 0}

        #figure which classes belong to which level and then increment their count by 1
        for key, value in self.courses_list.items():
            if int(key[4]) == 1:
                level_dict[100] += 1
            elif int(key[4]) == 2:
                level_dict[200] += 1
            elif int(key[4]) == 3:
                level_dict[300] += 1
            elif int(key[4]) == 4:
                level_dict[400] += 1
        return level_dict

    def get_courses_list(self):
        """
        This function returns the dictionary of course information. course-id(key):course-name(value)
        i.e: INST314: Statistics for Information Science
        :return: the dictionary of courses information: course id and course name
        """
        return self.courses_list


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = ApplicationWindow()
    mainWin.show()
    sys.exit(app.exec_())
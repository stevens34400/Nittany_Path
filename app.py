from flask import Flask, render_template, request
from unicodedata import normalize
import unicodedata
import sqlite3 as sql
import pandas as pd
import os
import hashlib
import re

from pandas import DataFrame

app = Flask(__name__)

host = 'http://127.0.0.1:5000/'

#Used to hash passwords
users={}

#Global variable for user input email
user_input_email = "test"

@app.route('/')
def index():
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    ###CREATE AND FILL IN Posts_Comment_csv
    cursor.execute('CREATE TABLE IF NOT EXISTS post_comment_csv(Courses TEXT, Drop_Deadline TEXT, Post_1 TEXT, Post_1_By TEXT, Comment_1 TEXT, Comment_1_By TEXT, Post_No INTEGER, Comment_No INTEGER, UNIQUE(Courses,Post_No))')
    post_comment_csv = pd.read_csv('dataset/Posts_Comments.csv')
    df = pd.DataFrame(post_comment_csv)
    df.columns = df.columns.str.replace(' ', '_')
    df.to_sql('post_comment_csv', connection, if_exists='replace', index=False)

    ###CREATE AND FILL IN Students_TA_csv
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS students_ta_csv(Full_Name TEXT, Student_Email TEXT PRIMARY KEY, Age INTEGER, Zip INTEGER , Phone TEXT, Gender TEXT, City TEXT, State TEXT, Password TEXT, Street TEXT, Major TEXT, Courses_1 TEXT, Course_1_Name TEXT, Course_1_Details TEXT, Course_1_Section TEXT, Course_1_Section_Limit TEXT, '
        'Course_1_HW_No INTEGER, Course_1_HW_Details TEXT, Course_1_HW_Grade INTEGER, Course_1_Exam_No INTEGER , Course_1_Exam_Details TEXT, Course_1_EXAM_Grade INTEGER, Courses_2 TEXT, Course_2_Name TEXT, Course_2_Details TEXT, Course_2_Section TEXT, Course_2_Section_Limit TEXT, Course_2_HW_No INTEGER, Course_2_HW_Details TEXT, '
        'Course_2_HW_Grade INTEGER, Course_2_Exam_No INTEGER , Course_2_Exam_Details TEXT, Course_2_EXAM_Grade INTEGER, Courses_3 TEXT, Course_3_Name TEXT, Course_3_Details TEXT, Course_3_Section TEXT, Course_3_Section_Limit TEXT, Course_3_HW_No INTEGER, Course_3_HW_Details TEXT, Course_3_HW_Grade INTEGER, Course_3_Exam_No INTEGER , '
        'Course_3_Exam_Details TEXT, Course_3_EXAM_Grade INTEGER, Teaching_Team_ID INTEGER)')
    students_ta_csv = pd.read_csv('dataset/Students_TA.csv')

    df = pd.DataFrame(students_ta_csv)
    df.columns = df.columns.str.replace(' ', '_')
    df.to_sql('students_ta_csv', connection, if_exists='replace', index=False)

    #Hash the passwords?
    """
    cursor.execute('''SELECT Student_Email
                        FROM students_ta_csv
    ''')

    student_email = cursor.fetchall()
    #index = 0;
    for email in student_email:
        print(email)
        salt = os.urandom(32)
        cursor.execute('''SELECT Password
                            FROM    students_ta_csv
                            WHERE   Student_email = ?''', email)
        password = (cursor.fetchall())
        hash_key = hashlib.pbkdf2_hmac('sha256',str(password[0]).encode('utf-8'),salt,100000)
        print(hash_key)
        users[email]={
            'student ': email,
            'salt': salt,
            'key': hash_key
        }

        cursor.execute('''UPDATE Students_ta_csv
                            SET Password = ''
                            WHERE Student_Email =?''', email)
    """

    ###CREATE AND FILL IN Professor_csv
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS professor_csv(Name TEXT, Professor_Email TEXT PRIMARY KEY, Password TEXT, Age INTEGER, Gender TEXT, Department TEXT, Office TEXT, Department_Name TEXT, Title TEXT, Teaching_TEAM_ID INTEGER, Teaching TEXT)')
    professor_csv = pd.read_csv('dataset/Professors.csv')
    df = pd.DataFrame(professor_csv)
    df.columns = df.columns.str.replace(' ', '_')
    df.to_sql('professor_csv', connection, if_exists='replace', index=False)

    ###CREATE AND FILL IN STUDENTS TABLE
    cursor.execute('CREATE TABLE IF NOT EXISTS Students(Student_Email TEXT PRIMARY KEY, Password TEXT, Full_Name TEXT, Age INTEGER, Gender CHARACTER(1), Major TEXT, Street TEXT, Zip INTEGER)')
    cursor.execute('''INSERT OR IGNORE INTO Students(Student_Email, Password, Full_Name, Age, Gender, Major, Street, Zip)
                        SELECT  Student_Email, Password, Full_Name, Age, Gender, Major, Street, Zip
                        FROM    students_ta_csv
                        ''')

    ###CREATE AND FILL IN ZIPCODES TABLE
    cursor.execute('CREATE TABLE IF NOT EXISTS Zipcodes(Zip INTEGER PRIMARY KEY, City TEXT, State TEXT)')
    cursor.execute('''INSERT OR IGNORE INTO Zipcodes(Zip, City, State)
                        SELECT  Zip, City, State
                        FROM    students_ta_csv
    ''')

    ###CREATE AND FILL IN PROFESSORS TABLE
    cursor.execute('''CREATE TABLE IF NOT EXISTS Professors(Professor_Email TEXT PRIMARY KEY,Password TEXT,Name TEXT,
                        Age INTEGER, Gender TEXT, Office_Address TEXT, Department TEXT, Title TEXT, Course TEXT)''')
    cursor.execute('''INSERT OR IGNORE INTO Professors(Professor_Email, Password, Name, Age, Gender, Office_Address, Department, Title, Course)
                        SELECT  Professor_Email, Password, Name, Age, Gender, Office_Address, Department, Title, Teaching AS Course
                        FROM    professor_csv
    ''')

    ###CREATE AND FILL IN DEPARTMENTS TABLE
    cursor.execute('CREATE TABLE IF NOT EXISTS Departments(Department TEXT PRIMARY KEY, Department_Name TEXT, Title TEXT, UNIQUE(Department, Department_Name))')
    cursor.execute('''INSERT OR IGNORE INTO Departments(Department, Department_Name, Title)
                        SELECT  Department, Department_Name, Title
                        FROM    professor_csv
    ''')

    ###CREATE AND FILL IN COURSES TABLE
    #Course123 to merge courses1, courses2 and courses3
    cursor.execute('CREATE TABLE IF NOT EXISTS Course123(Courses_1 TEXT, Courses_2 TEXT, Courses_3 TEXT, Course_1_Name TEXT, Course_2_Name TEXT, Course_3_Name TEXT, Course_1_Details TEXT, Course_2 Details TEXT, Course_3 Details TEXT)')
    course123 = pd.read_csv('dataset/Students_TA.csv',
                            usecols=['Courses 1', 'Courses 2', 'Courses 3', 'Course 1 Name', 'Course 2 Name',
                                     'Course 3 Name', 'Course 1 Details', 'Course 2 Details', 'Course 3 Details'])
    df = pd.DataFrame(course123)
    df.columns = df.columns.str.replace(' ', '_')
    df.to_sql('Course123', connection, if_exists='replace', index=False)

    #Make new table Course_ID to manipulate course123 to have all courses under one table
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS Course_ID(Courses TEXT, Course_Name TEXT, Course_Details TEXT, UNIQUE(Courses))')
    cursor.execute('''INSERT OR IGNORE INTO Course_ID(Courses, Course_Name, Course_Details)
                      SELECT Courses_1, Course_1_Name, Course_1_Details 
                      FROM  Course123
                      WHERE Courses_1 IS NOT NULL AND Course_1_Name IS NOT NULL AND Course_1_Details IS NOT NULL 
                      UNION 
                      SELECT Courses_2, Course_2_Name, Course_2_Details 
                      FROM  Course123
                      WHERE Courses_2 IS NOT NULL AND Course_2_Name IS NOT NULL AND Course_2_Details IS NOT NULL 
                      UNION
                      SELECT Courses_3, Course_3_Name, Course_3_Details
                      FROM  Course123
                      WHERE Courses_3 IS NOT NULL AND Course_3_Name IS NOT NULL AND Course_3_Details IS NOT NULL 
                   ''')

    # Add in other courses professors teach but no student is taking
    cursor.execute('''INSERT OR IGNORE INTO Course_ID(Courses,Course_Name,Course_Details)
                        SELECT  Teaching AS Courses, NULL, NULL
                        FROM    professor_csv
                        WHERE   Teaching IS NOT NULL 
                        UNION 
                        SELECT  Courses, Course_Name,Course_Details
                        FROM    Course_ID
                        WHERE   Courses IS NOT NULL AND Course_Name IS NOT NULL AND Course_Details IS NOT NULL                 
    ''')

    #Add in drop deadline from post_comment_csv
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS Course(Courses TEXT PRIMARY KEY, Course_Name TEXT, Course_Details TEXT, Drop_Deadline TEXT, UNIQUE(Courses,Course_Name))')
    cursor.execute('''INSERT OR IGNORE INTO Course(Courses, Course_Name, Course_Details, Drop_Deadline)
                      SELECT c1.Courses, c1.Course_Name, c1.Course_Details, p1.Drop_Deadline
                      FROM  Course_ID c1, post_comment_csv p1
                      WHERE c1.Courses = p1.Courses
                    ''')

    ###CREATE AND FILL IN SECTIONS TABLE
    cursor.execute('CREATE TABLE IF NOT EXISTS Sections(Courses TEXT, Course_Section TEXT, Course_Section_Limit TEXT,Teaching_Team_ID INTEGER, PRIMARY KEY (Courses,Course_Section))')
    #Insert Course, course section and course section limit all from students_ta_csv table
    cursor.execute('''INSERT OR IGNORE INTO Sections(Courses, Course_Section, Course_Section_Limit)
                      SELECT Courses_1, Course_1_Section, Course_1_Section_Limit 
                      FROM  students_ta_csv
                      WHERE Courses_1 IS NOT NULL AND Course_1_Section IS NOT NULL AND Course_1_Section_Limit IS NOT NULL 
                      UNION 
                      SELECT Courses_2, Course_2_Section, Course_2_Section_Limit 
                      FROM  students_ta_csv
                      WHERE Courses_2 IS NOT NULL AND Course_2_Section IS NOT NULL AND Course_2_Section_Limit IS NOT NULL 
                      UNION
                      SELECT Courses_3, Course_3_Section, Course_3_Section_Limit
                      FROM  students_ta_csv
                      WHERE Courses_3 IS NOT NULL AND Course_3_Section IS NOT NULL AND Course_3_Section_Limit IS NOT NULL 
                   ''')

    #Add in Teaching_Team_ID from professors_csv
    cursor.execute('''UPDATE Sections
                      SET   Teaching_Team_ID = (SELECT Teaching_Team_ID FROM professor_csv 
                                                WHERE professor_csv.Teaching = Sections.Courses)
    ''')

    ###CREATE AND FILL IN ENROLLS TABLE
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS Enrolls(Student_Email TEXT, Courses TEXT, Course_Section INTEGER, PRIMARY KEY(Student_Email,Courses,Course_Section))')

    #From students_ta_csv -> Email
    #From Sections -> Courses and Course_Section due to having only one column for all courses
    cursor.execute('''INSERT OR IGNORE INTO Enrolls(Student_Email, Courses, Course_Section)
                      SELECT st1.Student_Email, s1.Courses, s1.Course_Section 
                      FROM  students_ta_csv st1, Sections s1
                      WHERE (s1.Courses = st1.Courses_1 AND s1.Course_Section = st1.Course_1_Section) OR (s1.Courses = st1.Courses_2 AND s1.Course_Section=st1.Course_2_Section)
                            OR (s1.Courses = st1.Courses_3 AND s1.Course_Section = st1.Course_3_Section)  
                      ORDER BY st1.Student_Email
                    ''')

    ###CREATE AND FILL IN PROF_TEACHING_TEAMS TABLE
    cursor.execute('CREATE TABLE IF NOT EXISTS Prof_teaching_teams(Professor_Email TEXT PRIMARY KEY, Teaching_Team_ID INTEGER)')
    cursor.execute('''INSERT OR IGNORE INTO Prof_teaching_teams(Professor_Email, Teaching_Team_ID)
                        SELECT  Professor_Email, Teaching_Team_ID
                        FROM    professor_csv
    ''')

    ###CREATE AND FILL IN TA_TEACHING_TEAMS
    cursor.execute('CREATE TABLE IF NOT EXISTS TA_teaching_teams(Student_Email TEXT PRIMARY KEY, Teaching_Team_ID INTEGER)')
    cursor.execute('''INSERT OR IGNORE INTO TA_teaching_teams(Student_Email, Teaching_Team_ID)
                        SELECT  Student_Email, Teaching_Team_ID
                        FROM    students_ta_csv
    ''')

    cursor.execute('''DELETE FROM TA_teaching_teams WHERE Teaching_Team_ID IS NULL OR trim(Teaching_Team_ID)='' ''')

    ###CREATE AND FILL IN HOMEWORKS
    #From Sections table
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS Homework(Courses TEXT, Course_Section INTEGER, Course_HW_No INTEGER, Course_HW_Details TEXT,PRIMARY KEY(Courses, Course_Section), UNIQUE(Courses,Course_Section, Course_HW_No))')
    cursor.execute('''INSERT OR IGNORE INTO Homework(Courses, Course_Section)
                        SELECT Courses, Course_Section
                        FROM Sections
    ''')
    cursor.execute('''UPDATE Homework
                      SET   Course_HW_No = (SELECT Course_1_HW_No FROM students_ta_csv 
                                                WHERE students_ta_csv.Courses_1 = Homework.Courses AND students_ta_csv.Course_1_Section = Homework.Course_Section)
                      , Course_HW_Details = (SELECT Course_1_HW_Details FROM students_ta_csv 
                                                WHERE students_ta_csv.Courses_1 = Homework.Courses AND students_ta_csv.Course_1_Section = Homework.Course_Section)   
    ''')

    ###CREATE AND FILL IN HOMEWORK_GRADES
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS Homework_Grades(Student_Email TEXT, Courses TEXT, Course_Section INTEGER, Course_HW_No INTEGER, Course_HW_Grade INTEGER,PRIMARY KEY(Student_Email, Courses, Course_Section) ,UNIQUE(Student_Email,Courses,Course_Section,Course_HW_No))')
    cursor.execute('''INSERT OR IGNORE INTO Homework_Grades(Student_Email, Courses, Course_Section,Course_HW_No)
                        SELECT st1.Student_Email, h1.Courses, h1.Course_Section, h1.Course_HW_No
                        FROM    Homework h1, students_ta_csv st1
                        WHERE   (st1.Courses_1=h1.Courses AND st1.Course_1_Section=h1.Course_Section) OR (st1.Courses_2=h1.Courses AND st1.Course_2_Section=h1.Course_Section) OR (st1.Courses_3=h1.Courses AND st1.Course_3_Section=h1.Course_Section)
    ''')

    # Fill in grade for hw course 1
    cursor.execute('''UPDATE OR IGNORE Homework_Grades
                        SET Course_HW_Grade=(SELECT Course_1_HW_Grade FROM students_ta_csv
                                                WHERE students_ta_csv.Courses_1 = Homework_Grades.Courses AND students_ta_csv.Course_1_Section=Homework_Grades.Course_Section AND students_ta_csv.Student_Email = Homework_Grades.Student_Email)                   
    ''')

    # Fill in grade for hw course_2
    cursor.execute('''UPDATE OR IGNORE Homework_Grades
                        SET Course_HW_Grade=coalesce(Course_HW_Grade,(SELECT Course_2_HW_Grade FROM students_ta_csv
                                                WHERE students_ta_csv.Courses_2 = Homework_Grades.Courses AND students_ta_csv.Course_2_Section=Homework_Grades.Course_Section AND students_ta_csv.Student_Email = Homework_Grades.Student_Email) )                  
    ''')

    # Fill in grade for hw course_3
    cursor.execute('''UPDATE OR IGNORE Homework_Grades
                        SET Course_HW_Grade=coalesce(Course_HW_Grade,(SELECT Course_3_HW_Grade FROM students_ta_csv
                                                WHERE students_ta_csv.Courses_3 = Homework_Grades.Courses AND students_ta_csv.Course_3_Section=Homework_Grades.Course_Section AND students_ta_csv.Student_Email = Homework_Grades.Student_Email))                   
    ''')

    ###CREATE AND FILL IN EXAMS
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS Exams(Courses TEXT, Course_Section INTEGER, Course_Exam_No INTEGER, Course_Exam_Details TEXT, PRIMARY KEY(Courses, Course_Section), UNIQUE(Courses, Course_Section, Course_Exam_No))')
    cursor.execute('''INSERT OR IGNORE INTO Exams(Courses, Course_Section)
                        SELECT Courses, Course_Section
                        FROM Sections
    ''')
    cursor.execute('''UPDATE Exams
                      SET   Course_Exam_No = (SELECT Course_1_Exam_No FROM students_ta_csv 
                                                WHERE students_ta_csv.Courses_1 = Exams.Courses AND students_ta_csv.Course_1_Section = Exams.Course_Section)
                      , Course_Exam_Details = (SELECT Course_1_Exam_Details FROM students_ta_csv 
                                                WHERE students_ta_csv.Courses_1 = Exams.Courses AND students_ta_csv.Course_1_Section = Exams.Course_Section)   
    ''')

    # Delete classes with no exams
    cursor.execute('''DELETE FROM Exams
                        WHERE Course_Exam_No IS NULL OR trim(Course_Exam_No)=''
    ''')

    ###CREATE AND FILL IN EXAM_GRADES
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS Exam_Grades(Student_Email TEXT, Courses TEXT, Course_Section INTEGER, Course_Exam_No INTEGER, Course_Exam_Grade INTEGER,PRIMARY KEY(Student_Email, Courses, Course_Section) ,UNIQUE(Student_Email,Courses,Course_Section,Course_Exam_No))')
    cursor.execute('''INSERT OR IGNORE INTO Exam_Grades(Student_Email, Courses, Course_Section,Course_Exam_No)
                        SELECT st1.Student_Email, e1.Courses, e1.Course_Section, e1.Course_Exam_No
                        FROM    Exams e1, students_ta_csv st1
                        WHERE   (st1.Courses_1=e1.Courses AND st1.Course_1_Section=e1.Course_Section) OR (st1.Courses_2=e1.Courses AND st1.Course_2_Section=e1.Course_Section) OR (st1.Courses_3=e1.Courses AND st1.Course_3_Section=e1.Course_Section)
    ''')

    # Fill in grade for exam course 1
    cursor.execute('''UPDATE Exam_Grades
                        SET Course_Exam_Grade=(SELECT Course_1_Exam_Grade FROM students_ta_csv
                                                WHERE students_ta_csv.Courses_1 = Exam_Grades.Courses AND students_ta_csv.Course_1_Section=Exam_Grades.Course_Section AND students_ta_csv.Student_Email = Exam_Grades.Student_Email)                   
    ''')

    # Fill in grade for exam course_2
    cursor.execute('''UPDATE Exam_Grades
                        SET Course_Exam_Grade=coalesce(Course_Exam_Grade,(SELECT Course_2_Exam_Grade FROM students_ta_csv
                                                WHERE students_ta_csv.Courses_2 = Exam_Grades.Courses AND students_ta_csv.Course_2_Section=Exam_Grades.Course_Section AND students_ta_csv.Student_Email = Exam_Grades.Student_Email) )                  
    ''')

    # Fill in grade for exam course_3
    cursor.execute('''UPDATE Exam_Grades
                        SET Course_Exam_Grade=coalesce(Course_Exam_Grade,(SELECT Course_3_Exam_Grade FROM students_ta_csv
                                                WHERE students_ta_csv.Courses_3 = Exam_Grades.Courses AND students_ta_csv.Course_3_Section=Exam_Grades.Course_Section AND students_ta_csv.Student_Email = Exam_Grades.Student_Email))                   
    ''')

    ###CREATE AND FILL IN POSTS
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS Posts(Courses TEXT, Post_No INTEGER, Student_Email TEXT, Post_Info TEXT, PRIMARY KEY(Courses,Post_No))')
    cursor.execute('''INSERT OR IGNORE INTO Posts(Courses, Post_No, Student_Email, Post_Info)
                        SELECT  Courses, Post_No, Post_1_By AS Student_Email, Post_1 AS Post_Info  
                        FROM    post_comment_csv
    ''')

    #Make sure to delete empty entries
    cursor.execute('''DELETE FROM Posts
                        WHERE   (Post_No IS NULL OR trim(Post_No)='') AND (Post_Info IS NULL OR trim(Post_Info)='')
    ''')

    ###CREATE AND FILL IN COMMENTS
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS Comments(Courses TEXT, Post_No INTEGER, Comment_No INTEGER, Student_Email TEXT, Comment_Info TEXT, PRIMARY KEY(Courses, Post_No, Comment_No))')
    cursor.execute('''INSERT OR IGNORE INTO Comments(Courses, Post_No, Comment_No, Student_Email, Comment_Info)
                        SELECT  p1.Courses, p1.Post_No, pcsv1.Comment_No, pcsv1.Comment_1_By AS Student_Email, pcsv1.Comment_1 AS Comment_Info
                        FROM    Posts p1, post_comment_csv pcsv1
                        WHERE   p1.Courses=pcsv1.Courses AND p1.Post_No=pcsv1.Post_No

    ''')

    print(cursor.fetchall())
    connection.commit()



    return render_template('index.html')

@app.route('/login', methods=['POST','GET'])
def login():
    error = None
    if request.method == 'POST' :
        #make sure to utilize gloabla user_input_email so that further functionalities can consider this
        global user_input_email
        user_input_email = (request.form['Email'])
        user_input_password = request.form['Password']

        user_input_student_checked = check_user_input_student(user_input_email, user_input_password)
        user_input_prof_checked = check_user_input_prof(user_input_email,user_input_password)

        if user_input_student_checked:
            return (render_template('Home_Student.html'))
        if (user_input_prof_checked):
            return (render_template('Home_Prof.html'))
        else:
            return(render_template('login_page_fail.html'))

        """
        #Check hash table (method-2)
        salt = users[user_input_email]['salt']  #get salt
        key = users[user_input_email]['key'] #get previous key
        print(key)

        new_key = hashlib.pbkdf2_hmac('sha256',user_input_password.encode('utf-8'),salt,100000)
        print(new_key)
        """


    return render_template('login_page.html')

###USER INFO FUNCTIONALITY
@app.route('/userinfo', methods=['POST','GET'])
def user_info():
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    #Get rid of unwanted characters after obtaining string from fetchall()
    remove_chars = ['(', ')', ',']

    print("Global variable email input:", user_input_email)

    ## Course description
    cursor.execute('''SELECT c1.Courses, c1.Course_Name, e1.Course_Section
                        FROM Enrolls e1, Course c1
                        WHERE (e1.Student_Email = ? AND e1.Courses = c1.Courses)
                        GROUP BY c1.Courses
                        ''', (user_input_email,))
    course_description = cursor.fetchall()

    ## Proff contact
    cursor.execute('''SELECT p1.Professor_Email, p1.Office_Address
                        FROM Enrolls e1, Sections s1, Prof_teaching_teams pf1, Professors p1
                        WHERE (e1.Student_Email = ?) AND e1.Courses = s1.Courses AND e1.Course_Section = s1.Course_Section AND 
                                s1.Teaching_Team_ID = pf1.Teaching_Team_ID AND pf1.Professor_Email = p1.Professor_Email
                        GROUP BY s1.Courses
                        ''',(user_input_email,))
    prof_contact = cursor.fetchall()


    ## Student info (everything from Students table)
    cursor.execute('''SELECT *
                        FROM Students
                        WHERE Students.Student_Email = ?''',(user_input_email,))
    student_info = cursor.fetchall()

    ## Hw grade
    cursor.execute('''SELECT e1.Courses, hw1.Course_HW_Grade
                        FROM Enrolls e1, Homework_Grades hw1
                        WHERE (e1.Student_Email = ? AND e1.Student_Email = hw1.Student_Email AND e1.Courses = hw1.Courses AND e1.Course_Section = hw1.Course_Section)
                        ''',(user_input_email,))
    hw_grades = cursor.fetchall()

    ## Exam grade
    cursor.execute('''SELECT e1.Courses, ex1.Course_Exam_Grade
                            FROM Enrolls e1, Exam_Grades ex1
                            WHERE (e1.Student_Email = ? AND e1.Student_Email = ex1.Student_Email AND e1.Courses = ex1.Courses AND e1.Course_Section = ex1.Course_Section)
                            ''', (user_input_email,))
    exam_grades = cursor.fetchall()

    #print("course description: ",course_description)
    #print("prof contact: ",prof_contact)
    #print("student info: ",student_info)
    #print("hw grade: ",hw_grades)
    #print("exam grade: ", exam_grades)
    df_exam_grades = pd.DataFrame(exam_grades)
    df_hw_grades = pd.DataFrame(hw_grades)
    df=pd.DataFrame(course_description)

    print(df)

    #only courses column from course_description
    #Note: all courses a student is taking
    df_description_course = df[0]

    #print("hw_grades")
    #print(df_hw_grades)
    #print("exam_grades")
    #print(df_exam_grades)
    #Split hw_grades into two lists
    df_hw_grades_course = df_hw_grades[0]
    df_hw_grades_score = df_hw_grades [1]
    #Split exam_grades into two lists
    df_exam_grades_course = df_exam_grades[0]
    df_exam_grades_score = df_exam_grades[1]

    ###Algorithm to make sure that specified course has a HW grade
    #List to append to final dataframe pushed to page
    hw_scores = []

    # indexes for iteration
    index1 = 0;  # exam
    index2 = 0;  # description
    match = 0
    #Compare every course taken by student to the courses that have homework (courses->hw_courses)
    for i in df_description_course:
        for x in df_hw_grades_course:
            if (df_hw_grades_course[index1] == df_description_course[index2]):
                match = index1+1
                break;
            #increment for description
            index1 = index1 + 1

        if match:
            match = match-1
            hw_scores.append(df_hw_grades_score[match])
        else:
            hw_scores.append('NULL')
        index1 = 0
        index2 = index2 + 1

    print(hw_scores)


    #Add in HW grade column into dataframe
    df['HW_Grade']=hw_scores

    ###Algorithm to make sure that specified course has a Exam grade
    #exam score list to attach on final dataframe
    exam_scores=[]

    # indexes for iteration
    index1 = 0;  # exam
    index2 = 0;  # description
    match = 0
    for i in df_description_course:
        for x in df_exam_grades_course:
            if (df_exam_grades_course[index1] == df_description_course[index2]):
                match = index1+1
                break;
            #increment for description
            index1 = index1 + 1

        if match:
            match = match-1
            exam_scores.append(df_exam_grades_score[match])
        else:
            exam_scores.append('N/A')
        index1 = 0
        match = 0
        index2 = index2 + 1

    df['Exam_Grade']=exam_scores

    df_prof_contact = pd.DataFrame(prof_contact)
    df['Professor_Email']=df_prof_contact[0]
    df['Office_Address']=df_prof_contact[1]
    #print(df)

    test=df.values.tolist()
    print(test)
    print(student_info)

    connection.commit()
    return render_template('user_info.html', course_description=test, student_info=student_info)

@app.route('/createpost', methods=['POST','GET'])
def create_post():
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    #user input email from global variable
    courses = get_courses(user_input_email)
    print(courses[0])
    print(courses[1])
    print(courses[2])

    #Posts and info from course 1
    cursor.execute('''SELECT *
                                FROM Posts p1
                                WHERE p1.Courses=?''', courses[0])
    course_1 = cursor.fetchall()
    df_course1_posts = pd.DataFrame(course_1)
    if (df_course1_posts.empty==False):
        df_course1_posts = df_course1_posts.drop(columns=0)
    df_course1_posts = df_course1_posts.values.tolist()
    # print(df_course1_posts)

    #Posts and info from course 2
    cursor.execute('''SELECT *
                                    FROM Posts p1
                                    WHERE p1.Courses=?''', courses[1])
    course_2_posts = cursor.fetchall()
    df_course2_posts = pd.DataFrame(course_2_posts)
    if (df_course2_posts.empty == False):
        df_course2_posts = df_course2_posts.drop(columns=0)
    df_course2_posts = df_course2_posts.values.tolist()
    # print(df_course2_posts)

    #Obtain comments from all posts of course 2
    df_course2_posts_comments = pd.DataFrame(course_2_posts)
    df_course2_posts_comments = df_course2_posts_comments.values.tolist()
    print(df_course2_posts_comments)
    index = 0
    comments_course2 = []
    # iteration through number of posts
    for i in df_course2_posts_comments:
        cursor.execute('''SELECT c1.Comment_No, c1.Comment_Info, c1.Student_Email
                            FROM Comments c1
                            WHERE c1.Courses = ? AND Post_No = ?''',(df_course2_posts_comments[0][0],df_course2_posts_comments[index][1]))
        index=index+1
        comments_course2.append(cursor.fetchall())
    print(comments_course2[1])
    #comments_course2 [post_no]-[comment_no]-[element]

    index = 0
    for i in comments_course2:
        index = index+1
    print(index)


    #Posts from course 3
    cursor.execute('''SELECT *
                                    FROM Posts p1
                                    WHERE p1.Courses=?''', courses[2])
    course_3 = cursor.fetchall()
    df_course3_posts = pd.DataFrame(course_3)
    if (df_course3_posts.empty == False):
        df_course3_posts = df_course3_posts.drop(columns=0)
    df_course3_posts = df_course3_posts.values.tolist()

    return render_template('create_posts.html', course1=courses[0][0], course2=courses[1][0], course3=courses[2][0],
                           course1_posts=df_course1_posts,course2_posts=df_course2_posts,course2_comments=comments_course2[0],course3_posts=df_course3_posts)

@app.route('/createassignment',methods=['POST','GET'])
def create_assignment():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    print(user_input_email)
    return render_template('create_assignment.html')

def check_user_input_student(user_input_email, user_input_password):
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('''SELECT Student_Email
                        FROM Students
                        WHERE (Student_Email = ? AND Password = ?)''', (user_input_email, user_input_password))
    result = cursor.fetchall()

    # If result has an email, return true based of Students table checkup
    if result:
        return True
    # Else, return false
    else:
        return False

def check_user_input_prof(user_input_email, user_input_password):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''SELECT Professor_Email
                        FROM Professors
                        WHERE Professor_Email = ? AND Password = ?''',(user_input_email,user_input_password))
    result = cursor.fetchall()
    connection.commit()

    # If valid result from Professors table checkup, return true
    if result:
        return True
    # If no value from both Students and Professors table check up, return false
    else:
        return False

def get_courses(email):
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('''SELECT c1.Courses
                            FROM Enrolls e1, Course c1
                            WHERE (e1.Student_Email = ? AND e1.Courses = c1.Courses)
                            GROUP BY c1.Courses
                            ''', (email,))
    course_description = cursor.fetchall()
    connection.commit()
    return(course_description)



if __name__ == '__main__':
    app.run()

from flask import Flask, render_template, request
from unicodedata import normalize
import unicodedata
import sqlite3 as sql
import pandas as pd
import datetime

from pandas import DataFrame

app = Flask(__name__)

host = 'http://127.0.0.1:5000/'

#Used to hash passwords
users={}

#Global variable for user input email
user_input_email = "test"
user_input_password = "test"

#Global variables used for creating posts functionality
selected_course=""
tag = 0
post_no = -1

#Global variable used for submitting scores
student_email="test"
assign =0
hw_no=0
exam_no=0

#Global vairable used for specifying TA
team_id = 0
ta_course =""

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
        'CREATE TABLE IF NOT EXISTS Homework(Courses TEXT, Course_Section INTEGER, Course_HW_No INTEGER, Course_HW_Details TEXT,PRIMARY KEY(Courses, Course_Section))')
    cursor.execute('''INSERT OR IGNORE INTO Homework(Courses, Course_Section)
                        SELECT Courses, Course_Section
                        FROM Sections
    ''')
    #Make sure that when you insert new entries to use coalesce, deals with new entries that aren't in initial csv file/table
    cursor.execute('''UPDATE Homework
                      SET   Course_HW_No = case when coalesce(Course_HW_No,'')='' then
                                            (SELECT Course_1_HW_No FROM students_ta_csv 
                                                WHERE students_ta_csv.Courses_1 = Homework.Courses AND students_ta_csv.Course_1_Section = Homework.Course_Section)
                                            else
                                                Course_HW_No
                                            end 
                      , Course_HW_Details = case when coalesce(Course_HW_Details,'')='' then
                                            (SELECT Course_1_HW_Details FROM students_ta_csv 
                                                WHERE students_ta_csv.Courses_1 = Homework.Courses AND students_ta_csv.Course_1_Section = Homework.Course_Section)
                                            else
                                                Course_HW_Details
                                            end
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
                        SET Course_HW_Grade= case when coalesce(Course_HW_Grade,'')='' then
                                            (SELECT Course_1_HW_Grade FROM students_ta_csv
                                                WHERE students_ta_csv.Courses_1 = Homework_Grades.Courses AND 
                                                students_ta_csv.Course_1_Section=Homework_Grades.Course_Section AND 
                                                students_ta_csv.Student_Email = Homework_Grades.Student_Email)
                                            else
                                                Course_HW_Grade
                                            end                   
    ''')

    # Fill in grade for hw course_2
    cursor.execute('''UPDATE OR IGNORE Homework_Grades
                        SET Course_HW_Grade=case when coalesce (Course_HW_Grade,'')='' then
                                            coalesce(Course_HW_Grade,(SELECT Course_2_HW_Grade FROM students_ta_csv
                                                WHERE students_ta_csv.Courses_2 = Homework_Grades.Courses AND 
                                                students_ta_csv.Course_2_Section=Homework_Grades.Course_Section AND 
                                                students_ta_csv.Student_Email = Homework_Grades.Student_Email) )
                                            else
                                                Course_HW_Grade
                                            end                  
    ''')

    # Fill in grade for hw course_3
    cursor.execute('''UPDATE OR IGNORE Homework_Grades
                        SET Course_HW_Grade=case when coalesce (Course_HW_Grade,'')='' then
                                            coalesce(Course_HW_Grade,(SELECT Course_3_HW_Grade FROM students_ta_csv
                                                WHERE students_ta_csv.Courses_3 = Homework_Grades.Courses AND 
                                                students_ta_csv.Course_3_Section=Homework_Grades.Course_Section AND 
                                                students_ta_csv.Student_Email = Homework_Grades.Student_Email))
                                            else
                                                Course_HW_Grade
                                            end                   
    ''')

    ###CREATE AND FILL IN EXAMS
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS Exams(Courses TEXT, Course_Section INTEGER, Course_Exam_No INTEGER, Course_Exam_Details TEXT, PRIMARY KEY(Courses, Course_Section))')
    cursor.execute('''INSERT OR IGNORE INTO Exams(Courses, Course_Section)
                        SELECT Courses, Course_Section
                        FROM Sections
    ''')
    cursor.execute('''UPDATE Exams
                      SET   Course_Exam_No = case when coalesce(Course_Exam_No,'')='' then
                                                (SELECT Course_1_Exam_No FROM students_ta_csv 
                                                WHERE students_ta_csv.Courses_1 = Exams.Courses AND students_ta_csv.Course_1_Section = Exams.Course_Section)
                                            else
                                                Course_Exam_No
                                            end 
                            , Course_Exam_Details = case when coalesce(Course_Exam_Details,'')=''then 
                                                        (SELECT Course_1_Exam_Details FROM students_ta_csv 
                                                        WHERE students_ta_csv.Courses_1 = Exams.Courses AND students_ta_csv.Course_1_Section = Exams.Course_Section)   
                                                    else
                                                        Course_Exam_Details
                                                    end 
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
    cursor.execute('''UPDATE OR IGNORE  Exam_Grades
                        SET Course_Exam_Grade=case when coalesce (Course_Exam_Grade,'')=''then
                                                (SELECT Course_1_Exam_Grade FROM students_ta_csv
                                                WHERE students_ta_csv.Courses_1 = Exam_Grades.Courses AND 
                                                students_ta_csv.Course_1_Section=Exam_Grades.Course_Section AND 
                                                students_ta_csv.Student_Email = Exam_Grades.Student_Email)
                                                else
                                                    Course_Exam_Grade
                                                end 
    ''')

    # Fill in grade for exam course_2
    cursor.execute('''UPDATE OR IGNORE Exam_Grades
                        SET Course_Exam_Grade=case when coalesce(Course_Exam_Grade,'')=''then
                                                coalesce(Course_Exam_Grade,(SELECT Course_2_Exam_Grade FROM students_ta_csv
                                                WHERE students_ta_csv.Courses_2 = Exam_Grades.Courses AND 
                                                students_ta_csv.Course_2_Section=Exam_Grades.Course_Section AND 
                                                students_ta_csv.Student_Email = Exam_Grades.Student_Email) )
                                                else
                                                    Course_Exam_Grade
                                                end                  
    ''')

    # Fill in grade for exam course_3
    cursor.execute('''UPDATE OR IGNORE Exam_Grades
                        SET Course_Exam_Grade=case when coalesce (Course_Exam_Grade,'')=''then
                                                coalesce(Course_Exam_Grade,(SELECT Course_3_Exam_Grade FROM students_ta_csv
                                                WHERE students_ta_csv.Courses_3 = Exam_Grades.Courses AND 
                                                students_ta_csv.Course_3_Section=Exam_Grades.Course_Section AND 
                                                students_ta_csv.Student_Email = Exam_Grades.Student_Email))        
                                                else
                                                    Course_Exam_Grade
                                                end           
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
    global team_id
    if request.method == 'POST' :
        #make sure to utilize gloabla user_input_email so that further functionalities can consider this
        global user_input_email
        global user_input_password
        global TA
        user_input_email = (request.form['Email'])
        user_input_password = request.form['Password']

        user_input_student_checked = check_user_input_student(user_input_email, user_input_password)
        user_input_prof_checked = check_user_input_prof(user_input_email,user_input_password)

        if user_input_student_checked:
            team_id = check_TA(user_input_email)
            if(team_id):
                print('TA')
                return (render_template('Home_Student.html'))
            else:
                return (render_template('Home_Student.html'))
        elif (user_input_prof_checked):
            team_id = 0
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

@app.route('/home',methods=['POST','GET'])
def home():
    global user_input_email
    global user_input_password
    if (check_user_input_prof(user_input_email,user_input_password)):
        return render_template('Home_Prof.html')
    elif (check_user_input_student(user_input_email,user_input_password)):
        return render_template('Home_Student.html')

###USER INFO FUNCTIONALITY
@app.route('/userinfo', methods=['POST','GET'])
def user_info():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    global user_input_password
    global team_id

    if request.method == "POST":
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        new_password2 = request.form['new_password2']
        valid = check_password(old_password)
        if valid:
            if (new_password == new_password2):
                cursor.execute('''UPDATE Students
                                    SET  Password = ?
                                    WHERE Student_Email = ? AND Password = ?''',
                               (new_password, user_input_email, old_password))
                user_input_password=new_password
                connection.commit()
            else:
                return render_template('change_password_fail.html')
        else:
            return render_template('change_password_fail.html')

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
    cursor.execute('''SELECT Student_Email, Full_Name, Age, Gender, Major, Street, Zip
                        FROM Students
                        WHERE Students.Student_Email = ?''',(user_input_email,))
    student_info = cursor.fetchall()

    df=pd.DataFrame(course_description)

    df_prof_contact = pd.DataFrame(prof_contact)
    df['Professor_Email']=df_prof_contact[0]
    df['Office_Address']=df_prof_contact[1]

    test=df.values.tolist()

    #If student is a TA
    if(team_id):
        #Obtain course student is TAing
        cursor.execute('''SELECT Courses
                            FROM Sections
                            WHERE Teaching_Team_ID = ?
                            GROUP BY Courses''',team_id[0])
        course_ta = cursor.fetchall()
        connection.commit()
        return render_template('user_info_TA.html', course_description=test, student_info=student_info,courses=course_ta[0])

    else:
        connection.commit()
        return render_template('user_info.html', course_description=test, student_info=student_info)

@app.route('/showgrades',methods=['POST','GET'])
def show_grades():
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    if request.method == "POST":
        course = request.form['course']
        #Obtain Homework Number and Homework Grades
        cursor.execute('''SELECT Course_HW_No, Course_HW_Grade
                            FROM Homework_Grades
                            WHERE Student_Email = ? AND Courses = ?''',(user_input_email,course))
        homework = cursor.fetchall()
        df_homework = pd.DataFrame(homework)
        df_homework = df_homework.values.tolist()

        #Obtain Exam Number and Exam Grades
        cursor.execute('''SELECT Course_Exam_No, Course_Exam_Grade
                                    FROM Exam_Grades
                                    WHERE Student_Email = ? AND Courses = ?''', (user_input_email, course))
        exam = cursor.fetchall()
        df_exam = pd.DataFrame(exam)
        df_exam = df_exam.values.tolist()


    return render_template('show_grades.html',homework=df_homework,exam=df_exam)

@app.route('/changepassword',methods=['POST','GET'])
def change_password():
    return render_template('change_password.html')

@app.route('/createpostcourse',methods=['POST','GET'])
def create_post_course():
    global tag
    global team_id
    global ta_course
    courses = get_courses(user_input_email)
    df_courses = pd.DataFrame(courses)
    print(df_courses)

    if(team_id):
        ta_course = TA_course(team_id)
        df_courses = df_courses.append(ta_course,ignore_index=True)

    df_courses = df_courses[0].values.tolist()
    tag = 0
    print(df_courses)
    return render_template('create_posts_course.html',courses=df_courses)

@app.route('/createpoststudent', methods=['POST','GET'])
def create_post_student():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    global selected_course
    global post_no
    global team_id

    #user input email from global variable
    courses = get_courses(user_input_email)
    if team_id:
        courses_TA = TA_course(team_id)



    if request.method == 'POST' :
        if (tag==0):
            print('test')
            selected_course=request.form['Course']
        #Create posts
        elif (tag==1):
            # post_content = post_info
            post_content = request.form['Post']
            # obtain max post no for the course
            cursor.execute('''SELECT max(p1.Post_No)
                                            FROM Posts p1
                                            WHERE p1.Courses = ?''', (selected_course,))
            max_post_no = cursor.fetchall()
            if (max_post_no[0][0]):
                max_post_no = max_post_no[0][0] + 1
            else:
                max_post_no = 1
            # enter new post
            enter_post(selected_course, max_post_no, user_input_email, post_content)
        else:
            comment_content = request.form['Comment']
            cursor.execute('''SELECT max(c1.Comment_No)
                                FROM Comments c1
                                WHERE c1.Courses = ? AND c1.Post_No = ?''', (selected_course,post_no))
            max_comment_no = cursor.fetchall()
            if (max_comment_no[0][0]):
                max_comment_no = max_comment_no[0][0] + 1
            else:
                max_comment_no = 1
            # enter new comment
            enter_comment(selected_course,post_no,max_comment_no,user_input_email,comment_content)




    ##User selects course 1
    if (selected_course==courses[0][0]):
        #Posts and info from course 1
        cursor.execute('''SELECT *
                                    FROM Posts p1
                                    WHERE p1.Courses=?''', courses[0])
        course_1_posts = cursor.fetchall()
        df_course_posts = pd.DataFrame(course_1_posts)
        #If there are posts delete the course column
        if (df_course_posts.empty==False):
            df_course_posts = df_course_posts.drop(columns=0)
        df_course_posts = df_course_posts.values.tolist()

        # All posts from course 2 including course attribute
        df_course_posts_course = pd.DataFrame(course_1_posts)
        df_course_posts_course = df_course_posts_course.values.tolist()

        index = 0
        comments_course = []
        # iteration through number of posts
        for i in df_course_posts_course:
            cursor.execute('''SELECT c1.Post_No, c1.Comment_No, c1.Comment_Info, c1.Student_Email
                                        FROM Comments c1
                                        WHERE c1.Courses = ? AND Post_No = ?''',
                           (df_course_posts_course[0][0], df_course_posts_course[index][1]))
            index = index + 1
            comments_course.append(cursor.fetchall())
        # comments_course2 [Post No]-[comment_no]-[element]

        # Iterate through post no
        df_course_comments = pd.DataFrame()
        for posts in comments_course:
            df_course_comments = df_course_comments.append(posts, ignore_index=True)
        df_course_comments = df_course_comments.values.tolist()

        df_post_no = pd.DataFrame(df_course_posts)
        df_post_no = df_post_no.drop(columns=[1, 2]).drop_duplicates()
        df_post_no = df_post_no.transpose()
        df_post_no = df_post_no.values.tolist()
        print(df_post_no)

        print('course1')
        return render_template('create_posts.html', course=selected_course, course_posts=df_course_posts, course_comments=df_course_comments,tvalues=df_post_no[0])

    ##User selects course 2
    if (selected_course==courses[1][0]):
        #Posts and info from course 2
        cursor.execute('''SELECT *
                                        FROM Posts p1
                                        WHERE p1.Courses=?''', courses[1])
        course_2_posts = cursor.fetchall()
        df_course_posts = pd.DataFrame(course_2_posts)
        # If there are posts delete the course column
        if (df_course_posts.empty == False):
            df_course_posts = df_course_posts.drop(columns=0)
        df_course_posts = df_course_posts.values.tolist()

        #All posts from course 2 including course attribute
        df_course_posts_course = pd.DataFrame(course_2_posts)
        df_course_posts_course = df_course_posts_course.values.tolist()

        index = 0
        comments_course2 = []
        # iteration through number of posts
        for i in df_course_posts_course:
            cursor.execute('''SELECT c1.Post_No, c1.Comment_No, c1.Comment_Info, c1.Student_Email
                                FROM Comments c1
                                WHERE c1.Courses = ? AND Post_No = ?''',(df_course_posts_course[0][0],df_course_posts_course[index][1]))
            index=index+1
            comments_course2.append(cursor.fetchall())
        # comments_course2 [Post No]-[comment_no]-[element]

        #Iterate through post no
        df_course_comments = pd.DataFrame()
        for posts in comments_course2:
            df_course_comments= df_course_comments.append(posts,ignore_index=True)
        df_course_comments = df_course_comments.values.tolist()

        df_post_no = pd.DataFrame(df_course_posts)
        df_post_no = df_post_no.drop(columns=[1,2]).drop_duplicates()
        df_post_no = df_post_no.transpose()
        df_post_no = df_post_no.values.tolist()
        print(df_post_no)

        return render_template('create_posts.html',course=selected_course,course_posts=df_course_posts,course_comments=df_course_comments,tvalues=df_post_no[0])

    ##User selects course 3
    if (selected_course==courses[2][0]):
        #Posts from course 3
        cursor.execute('''SELECT *
                                        FROM Posts p1
                                        WHERE p1.Courses=?''', courses[2])
        course_3_posts = cursor.fetchall()
        df_course_posts = pd.DataFrame(course_3_posts)
        # If there are posts delete the course column
        if (df_course_posts.empty == False):
            df_course_posts = df_course_posts.drop(columns=0)
        df_course_posts = df_course_posts.values.tolist()

        # All posts from course 3 including course attribute
        df_course_posts_course = pd.DataFrame(course_3_posts)
        df_course_posts_course = df_course_posts_course.values.tolist()

        index = 0
        comments_course = []
        # iteration through number of posts
        for i in df_course_posts_course:
            cursor.execute('''SELECT c1.Post_No, c1.Comment_No, c1.Comment_Info, c1.Student_Email
                                                FROM Comments c1
                                                WHERE c1.Courses = ? AND Post_No = ?''',
                           (df_course_posts_course[0][0], df_course_posts_course[index][1]))
            index = index + 1
            comments_course.append(cursor.fetchall())
        # comments_course2 [Post No]-[comment_no]-[element]

        # Iterate through post no
        df_course_comments = pd.DataFrame()
        for posts in comments_course:
            df_course_comments = df_course_comments.append(posts, ignore_index=True)
        df_course_comments = df_course_comments.values.tolist()

        df_post_no = pd.DataFrame(df_course_posts)
        df_post_no = df_post_no.drop(columns=[1, 2]).drop_duplicates()
        df_post_no = df_post_no.transpose()
        df_post_no = df_post_no.values.tolist()
        print(df_post_no)

        print('course3')

        return render_template('create_posts.html', course=selected_course, course_posts=df_course_posts,course_comments=df_course_comments,tvalues=df_post_no[0])

    for i in ta_course:
        if (selected_course==i[0]):
            # Posts from course TA
            cursor.execute('''SELECT *
                                                    FROM Posts p1
                                                    WHERE p1.Courses=?''', (i[0],))
            course_ta_posts = cursor.fetchall()
            df_course_posts = pd.DataFrame(course_ta_posts)
            # If there are posts delete the course column
            if (df_course_posts.empty == False):
                df_course_posts = df_course_posts.drop(columns=0)
            df_course_posts = df_course_posts.values.tolist()

            # All posts from course TA including course attribute
            df_course_posts_course = pd.DataFrame(course_ta_posts)
            df_course_posts_course = df_course_posts_course.values.tolist()

            index = 0
            comments_course = []
            # iteration through number of posts
            for i in df_course_posts_course:
                cursor.execute('''SELECT c1.Post_No, c1.Comment_No, c1.Comment_Info, c1.Student_Email
                                                            FROM Comments c1
                                                            WHERE c1.Courses = ? AND Post_No = ?''',
                               (df_course_posts_course[0][0], df_course_posts_course[index][1]))
                index = index + 1
                comments_course.append(cursor.fetchall())
            # comments_course2 [Post No]-[comment_no]-[element]

            # Iterate through post no
            df_course_comments = pd.DataFrame()
            for posts in comments_course:
                df_course_comments = df_course_comments.append(posts, ignore_index=True)
            df_course_comments = df_course_comments.values.tolist()

            df_post_no = pd.DataFrame(df_course_posts)
            df_post_no = df_post_no.drop(columns=[1, 2]).drop_duplicates()
            df_post_no = df_post_no.transpose()
            df_post_no = df_post_no.values.tolist()
            print(df_post_no)

            print('courseTA')

            return render_template('create_posts.html', course=selected_course, course_posts=df_course_posts,
                                   course_comments=df_course_comments, tvalues=df_post_no[0])


@app.route('/createpostprof',methods=['POST','GET'])
def create_post_prof():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''SELECT p1.Course
                            FROM Professors p1
                            WHERE p1.Professor_Email = ?''', (user_input_email,))
    # Obtain course he's teaching
    course_teaching = cursor.fetchall()
    global tag
    global post_no

    if request.method == 'POST' :
        if (tag==0):
            print('test')
            selected_course=request.form['Course']
        #Create posts
        elif (tag==1):
            # post_content = post_info
            post_content = request.form['Post']
            # obtain max post no for the course
            cursor.execute('''SELECT max(p1.Post_No)
                                            FROM Posts p1
                                            WHERE p1.Courses = ?''', course_teaching[0])
            max_post_no = cursor.fetchall()
            if (max_post_no[0][0]):
                max_post_no = max_post_no[0][0] + 1
            else:
                max_post_no = 1
            # enter new post
            enter_post(course_teaching[0][0], max_post_no, user_input_email, post_content)
        else:
            comment_content = request.form['Comment']
            cursor.execute('''SELECT max(c1.Comment_No)
                                FROM Comments c1
                                WHERE c1.Courses = ? AND c1.Post_No = ?''', (course_teaching[0][0],post_no))
            max_comment_no = cursor.fetchall()
            if (max_comment_no[0][0]):
                max_comment_no = max_comment_no[0][0] + 1
            else:
                max_comment_no = 1
            print(max_comment_no)
            # enter new comment
            enter_comment(course_teaching[0][0],post_no,max_comment_no,user_input_email,comment_content)

    #Obtain posts from class teaching
    cursor.execute('''SELECT *
                                            FROM Posts p1
                                            WHERE p1.Courses=?''', course_teaching[0])
    course_posts = cursor.fetchall()
    df_course_posts = pd.DataFrame(course_posts)
    # If there are posts delete the course column
    if (df_course_posts.empty == False):
        df_course_posts = df_course_posts.drop(columns=0)
    df_course_posts = df_course_posts.values.tolist()

    # All posts from course 3 including course attribute
    df_course_posts_course = pd.DataFrame(course_posts)
    df_course_posts_course = df_course_posts_course.values.tolist()

    index = 0
    comments_course = []
    # iteration through number of posts
    for i in df_course_posts_course:
        cursor.execute('''SELECT c1.Post_No, c1.Comment_No, c1.Comment_Info, c1.Student_Email
                                                    FROM Comments c1
                                                    WHERE c1.Courses = ? AND Post_No = ?''',
                       (df_course_posts_course[0][0], df_course_posts_course[index][1]))
        index = index + 1
        comments_course.append(cursor.fetchall())
    # comments_course2 [Post No]-[comment_no]-[element]

    # Iterate through post no
    df_course_comments = pd.DataFrame()
    for posts in comments_course:
        df_course_comments = df_course_comments.append(posts, ignore_index=True)
    df_course_comments = df_course_comments.values.tolist()

    df_post_no = pd.DataFrame(df_course_posts)
    df_post_no = df_post_no.drop(columns=[1, 2]).drop_duplicates()
    df_post_no = df_post_no.transpose()
    df_post_no = df_post_no.values.tolist()
    print(df_post_no)

    return render_template('create_posts_prof.html',course=course_teaching[0][0],course_posts=df_course_posts,course_comments=df_course_comments,tvalues=df_post_no[0])

@app.route('/createpostsubmit',methods=['POST','GET'])
def create_post_submit():
    global tag
    tag = 1
    print(user_input_email)
    if(check_user_input_student(user_input_email,user_input_password)):
        return render_template('create_posts_submit.html')
    elif(check_user_input_prof(user_input_email,user_input_password)):
        return render_template('create_posts_submit_prof.html')

@app.route('/createcommentsubmit',methods=['POST','GET'])
def create_comment_submit():
    global tag
    global post_no
    tag = 2
    if request.method == "POST":
        post_no = request.form['tvalue']

    if (check_user_input_student(user_input_email, user_input_password)):
        return render_template('create_comment_submit.html')
    elif (check_user_input_prof(user_input_email, user_input_password)):
        return render_template('create_comment_submit_prof.html')

#Link to show the assignments already in tables used
@app.route('/createassignment',methods=['POST','GET'])
def create():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''SELECT p1.Course
                        FROM Professors p1
                        WHERE p1.Professor_Email = ?''',(user_input_email,))
    #Obtain course he's teaching
    course_teaching = cursor.fetchall()

    # Show all assignments already in course
    cursor.execute('''SELECT e1.Course_Exam_No, e1.Course_Exam_Details
                        FROM Exams e1
                        WHERE e1.Courses = ?
                        GROUP BY e1.Course_Exam_No''',course_teaching[0])
    exams = cursor.fetchall()
    df_exams = pd.DataFrame(exams)
    #Also insert assignment tag
    df_exams.insert(0,"Assignment","Exam",True)

    cursor.execute('''SELECT h1.Course_HW_No, h1.Course_HW_Details
                        FROM Homework h1
                        WHERE h1.Courses = ?
                        GROUP BY h1.Course_HW_No''',course_teaching[0])
    homework = cursor.fetchall()
    df_homework = pd.DataFrame(homework)
    #Also insert assignment tag
    df_homework.insert(0,"Assignment","Homework",True)

    df_assign = df_exams.append(df_homework)
    df_assign = df_assign.values.tolist()

    connection.commit()
    return render_template('create_assignment.html',course1=course_teaching[0][0],assignment=df_assign)

#Link to creating a hw assignment
@app.route('/createhw',methods=['POST','GET'])
def createhw():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''SELECT p1.Course
                        FROM Professors p1
                        WHERE p1.Professor_Email = ?''',(user_input_email,))
    #Obtain course he's teaching
    course_teaching = cursor.fetchall()

    # Show all assignments already in course
    cursor.execute('''SELECT e1.Course_Exam_No, e1.Course_Exam_Details
                        FROM Exams e1
                        WHERE e1.Courses = ?
                        GROUP BY e1.Course_Exam_No''',course_teaching[0])
    exams = cursor.fetchall()
    df_exams = pd.DataFrame(exams)
    #Also insert assignment tag
    df_exams.insert(0,"Assignment","Exam",True)

    cursor.execute('''SELECT h1.Course_HW_No, h1.Course_HW_Details
                        FROM Homework h1
                        WHERE h1.Courses = ?
                        GROUP BY h1.Course_HW_No''',course_teaching[0])
    homework = cursor.fetchall()
    df_homework = pd.DataFrame(homework)
    #Also insert assignment tag
    df_homework.insert(0,"Assignment","Homework",True)

    df_assign = df_exams.append(df_homework)
    df_assign = df_assign.values.tolist()

    if request.method == 'POST':
        #Obtain user input for new hw assignment detail
        assign_detail = request.form['Assign_Detail']

        #Obtain max assignment number and set to next hw no
        cursor.execute('''SELECT MAX(Course_HW_No)
                            FROM Homework h1
                            WHERE h1.Courses = ?''', course_teaching[0])
        max_hw_no = cursor.fetchall()
        max_hw_no = max_hw_no[0][0]+1

        #function used to just insert new element into table
        enter_homework(course_teaching,max_hw_no,assign_detail)

        cursor.execute('''SELECT h1.Course_HW_No, h1.Course_HW_Details
                                FROM Homework h1
                                WHERE h1.Courses = ?
                                GROUP BY h1.Course_HW_No''', course_teaching[0])
        new_homework = cursor.fetchall()
        df_new_homework = pd.DataFrame(new_homework)
        # Also insert assignment tag
        df_new_homework.insert(0, "Assignment", "Homework", True)
        df_new_homework = df_new_homework.values.tolist()
        df_exams = df_exams.values.tolist()
        df_assign = df_exams+df_new_homework

    connection.commit()
    return render_template('create_hw.html',course1=course_teaching[0][0],assignment=df_assign)

#Link to create a new exam
@app.route('/createexam',methods=['POST','GET'])
def createexam():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''SELECT p1.Course
                        FROM Professors p1
                        WHERE p1.Professor_Email = ?''',(user_input_email,))
    #Obtain course he's teaching
    course_teaching = cursor.fetchall()

    # Show all assignments already in course
    cursor.execute('''SELECT e1.Course_Exam_No, e1.Course_Exam_Details
                        FROM Exams e1
                        WHERE e1.Courses = ?
                        GROUP BY e1.Course_Exam_No''',course_teaching[0])
    exams = cursor.fetchall()
    df_exams = pd.DataFrame(exams)
    #Also insert assignment tag
    df_exams.insert(0,"Assignment","Exam",True)

    cursor.execute('''SELECT h1.Course_HW_No, h1.Course_HW_Details
                        FROM Homework h1
                        WHERE h1.Courses = ?
                        GROUP BY h1.Course_HW_No''',course_teaching[0])
    homework = cursor.fetchall()
    df_homework = pd.DataFrame(homework)
    #Also insert assignment tag
    df_homework.insert(0,"Assignment","Homework",True)

    df_assign = df_exams.append(df_homework)
    df_assign = df_assign.values.tolist()

    if request.method == 'POST':
        #Obtain user input for new hw assignment
        assign_detail = request.form['Assign_Detail']

        # Obtain max assignment number and set to next exam no
        cursor.execute('''SELECT MAX(Course_Exam_No)
                                    FROM Exams e1
                                    WHERE e1.Courses = ?''', course_teaching[0])
        max_exam_no = cursor.fetchall()
        max_exam_no = max_exam_no[0][0] + 1

        #function used to just insert new element into table
        enter_exam(course_teaching,max_exam_no,assign_detail)

        cursor.execute('''SELECT e1.Course_Exam_No, e1.Course_Exam_Details
                                FROM Exams e1
                                WHERE e1.Courses = ?
                                GROUP BY e1.Course_Exam_No''', course_teaching[0])
        new_exam = cursor.fetchall()
        df_new_exam = pd.DataFrame(new_exam)
        # Also insert assignment tag
        df_new_exam.insert(0, "Assignment", "Exam", True)
        df_new_exam = df_new_exam.values.tolist()
        df_homework = df_homework.values.tolist()
        df_assign = df_new_exam+df_homework

    connection.commit()
    return render_template('create_exam.html',course1=course_teaching[0][0],assignment=df_assign)

@app.route('/submitscore',methods=['POST','GET'])
def submitscores():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    global tag
    global ta_course
    tag=0
    # Obtain class prof is teaching
    cursor.execute('''SELECT p1.Course
                                FROM Professors p1
                                WHERE p1.Professor_Email = ?''', (user_input_email,))
    # Obtain course he's teaching
    course_teaching = cursor.fetchall()
    print('teamid: ',team_id)
    if(team_id):
        print('ta')
        ta_course=TA_course(team_id)
        print(ta_course)
        return render_template('submit_scores.html',course=ta_course[0][0])

    return render_template('submit_scores.html',course=course_teaching[0][0])

@app.route('/submitscorehw',methods=['POST','GET'])
def submitscoreshw():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    global tag
    global student_email
    global hw_no
    global assign
    assign = 1 #1-Homework

    #Obtain class prof is teaching
    cursor.execute('''SELECT p1.Course
                            FROM Professors p1
                            WHERE p1.Professor_Email = ?''', (user_input_email,))
    # Obtain course he's teaching
    course_teaching = cursor.fetchall()

    if (team_id):
        course_teaching =ta_course

    #Obtain number of assignments for hw
    cursor.execute('''SELECT h1.Course_HW_No
                        FROM Homework h1
                        WHERE h1.Courses = ?
                        GROUP BY h1.Course_HW_No''',course_teaching[0])
    course_hw_no = cursor.fetchall()
    df_course_hw_no = pd.DataFrame(course_hw_no)
    df_course_hw_no = df_course_hw_no[0].values.tolist()

    #Obtain user selection for which hw to show
    if request.method == 'POST':
        print('tag: ',tag)
        #Tag=0, will obtain which assignment number to grade
        if (tag==0):
            print('test')
            hw_no = request.form['tvalue']
            cursor.execute('''SELECT hg1.Student_Email, hg1.Course_HW_Grade
                                FROM Homework_Grades hg1
                                WHERE hg1.Courses = ? AND hg1.Course_HW_No = ?''',(course_teaching[0][0],hw_no))
            student_hw_grade = cursor.fetchall()
            df_student_email = pd.DataFrame(student_hw_grade)
            df_student_email = df_student_email.drop(columns=1)
            df_student_email = df_student_email[0].values.tolist()

            return render_template('submit_scores_hw.html',emails=df_student_email,tvalues=df_course_hw_no,
                                   student_hw_grade=student_hw_grade,hw_no=hw_no,course=course_teaching[0][0])
        #Tag=1, will change the score for that student after going through assigngradeno
        else:
            grade = request.form['Grade']
            cursor.execute('''UPDATE Homework_Grades
                                SET Course_HW_Grade = ?
                                WHERE Student_Email = ? AND Courses=? AND Course_HW_No=?''',(grade,student_email,course_teaching[0][0],hw_no))

            cursor.execute('''SELECT hg1.Student_Email, hg1.Course_HW_Grade
                                           FROM Homework_Grades hg1
                                           WHERE hg1.Courses = ? AND hg1.Course_HW_No = ?''',
                           (course_teaching[0][0], hw_no))
            student_hw_grade = cursor.fetchall()
            df_student_email = pd.DataFrame(student_hw_grade)
            df_student_email = df_student_email.drop(columns=1)
            df_student_email = df_student_email[0].values.tolist()

            connection.commit()
            tag=0
            return render_template('submit_scores_hw.html', emails=df_student_email, tvalues=df_course_hw_no,
                                   student_hw_grade=student_hw_grade, hw_no=hw_no, course=course_teaching[0][0])

    connection.commit()
    return render_template('submit_scores_hw.html',tvalues=df_course_hw_no,course=course_teaching[0][0])

#Allow to change grade of specific student email
@app.route('/assigngradeno',methods=['POST','GET'])
def assign_grade_no():
    global tag
    global student_email
    global assign
    tag=1
    if request.method == "POST":
        student_email=request.form['email']

    if assign ==1:
        return render_template('submit_scores_hw_change.html')
    elif assign == 2:
        return render_template('submit_scores_exam_change.html')

@app.route('/submitscoreexam',methods=['POST','GET'])
def submitscoreexam():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    global tag
    global student_email
    global assign
    global exam_no
    assign = 2 #2-exams

    # Obtain class prof is teaching
    cursor.execute('''SELECT p1.Course
                                FROM Professors p1
                                WHERE p1.Professor_Email = ?''', (user_input_email,))
    # Obtain course he's teaching
    course_teaching = cursor.fetchall()

    if(team_id):
        course_teaching = ta_course

    # Obtain number of assignments for exam
    cursor.execute('''SELECT e1.Course_Exam_No
                            FROM Exams e1
                            WHERE e1.Courses = ?
                            GROUP BY e1.Course_Exam_No''', course_teaching[0])
    course_exam_no = cursor.fetchall()
    df_course_exam_no = pd.DataFrame(course_exam_no)
    df_course_exam_no = df_course_exam_no[0].values.tolist()

    # Obtain user selection for which exam to show
    if request.method == 'POST':
        if (tag==0):
            exam_no = request.form['tvalue']
            cursor.execute('''SELECT eg1.Student_Email, eg1.Course_Exam_Grade
                                    FROM Exam_Grades eg1
                                    WHERE eg1.Courses = ? AND eg1.Course_Exam_No = ?''', (course_teaching[0][0], exam_no))
            student_exam_grade = cursor.fetchall()
            df_student_email = pd.DataFrame(student_exam_grade)
            df_student_email = df_student_email.drop(columns=1)
            df_student_email = df_student_email[0].values.tolist()

            return render_template('submit_scores_exam.html', tvalues=df_course_exam_no, student_exam_grade=student_exam_grade,
                                   exam_no=exam_no,course=course_teaching[0][0],emails=df_student_email)
        else:
            grade = request.form['Grade']
            cursor.execute('''UPDATE Exam_Grades
                                            SET Course_Exam_Grade = ?
                                            WHERE Student_Email = ? AND Courses=? AND Course_Exam_No=?''',
                           (grade, student_email, course_teaching[0][0], exam_no))

            cursor.execute('''SELECT eg1.Student_Email, eg1.Course_Exam_Grade
                                                FROM Exam_Grades eg1
                                                WHERE eg1.Courses = ? AND eg1.Course_Exam_No = ?''',
                           (course_teaching[0][0], exam_no))
            student_exam_grade = cursor.fetchall()
            df_student_email = pd.DataFrame(student_exam_grade)
            df_student_email = df_student_email.drop(columns=1)
            df_student_email = df_student_email[0].values.tolist()
            tag = 0
            connection.commit()

            return render_template('submit_scores_exam.html', tvalues=df_course_exam_no,
                                   student_exam_grade=student_exam_grade,
                                   exam_no=exam_no, course=course_teaching[0][0], emails=df_student_email)

    connection.commit()
    return render_template('submit_scores_exam.html', tvalues=df_course_exam_no,course=course_teaching[0][0])

@app.route('/dropcourse',methods=['POST','GET'])
def drop_course():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    result = True

    if request.method == "POST":
        dropcourse=request.form['Course']
        cursor.execute('''SELECT Drop_Deadline
                            FROM Course
                            WHERE Courses=?''',(dropcourse,))
        latedropdate=cursor.fetchall()
        latedropdate = latedropdate[0][0]
        latedropdate_day = latedropdate[3]+latedropdate[4]
        latedropdate_month = latedropdate[0]+latedropdate[1]
        latedropdate_year = latedropdate[6]+latedropdate[7]+latedropdate[8]+latedropdate[9]

        current_date = datetime.datetime.today()
        print(current_date)

        if(current_date.year>int(latedropdate_year)):
            result = False
            print('year')
        if(current_date.month>int(latedropdate_month)):
            result = False
            print('month')
        if(current_date.day>int(latedropdate_day)):
            result = False
            print('day')

        if (result):
            #Delete user from Enrolls table
            cursor.execute('''DELETE FROM Enrolls
                                WHERE Student_Email = ? AND Courses = ?''',(user_input_email,dropcourse))

            #Delete comments
            cursor.execute('''DELETE FROM Comments
                                WHERE Student_Email = ? AND Courses = ?''',(user_input_email,dropcourse))

            #Obtain Post Numbers for posts created by user
            cursor.execute('''SELECT Post_No
                                FROM Posts
                                WHERE Student_Email = ? AND Courses = ?''',(user_input_email,dropcourse))
            postnumbers = cursor.fetchall()

            #Delete Posts from post numbers
            for i in postnumbers:
                cursor.execute('''DELETE FROM Posts
                                    WHERE Post_No = ?''',(i))

            #Delete Comments with the same post number listed
            for i in postnumbers:
                cursor.execute('''DELETE FROM Comments
                                    WHERE Post_No=?''',i)
            connection.commit()
        else:
            courses = get_courses(user_input_email)
            df_courses = pd.DataFrame(courses)
            df_courses = df_courses[0].values.tolist()

            return render_template('drop_course_fail.html',courses=df_courses)

    courses = get_courses(user_input_email)
    df_courses = pd.DataFrame(courses)
    df_courses = df_courses[0].values.tolist()

    return render_template('drop_course.html',courses=df_courses)

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

def enter_homework(course_teaching, assign_no, assign_detail):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO Homework(Courses,Course_HW_No,Course_HW_Details) VALUES (?,?,?);'''
                   , (course_teaching[0][0], assign_no, assign_detail))
    cursor.execute('''SELECT Count(Student_Email)
                        FROM Homework_Grades
                        WHERE Courses = ?''',(course_teaching[0][0],))
    number_students = cursor.fetchall()

    cursor.execute('''SELECT Student_Email
                        FROM Homework_Grades
                        WHERE Courses = ?''',(course_teaching[0][0],))
    students = cursor.fetchall()

    for i in range(0,number_students[0][0]):
        cursor.execute('''INSERT INTO Homework_Grades(Courses,Student_Email,Course_HW_No,Course_HW_Grade) 
                            VALUES (?,?,?,?);''',(course_teaching[0][0],students[i][0],assign_no,"N/A"))
    connection.commit()

def enter_exam(course_teaching, assign_no, assign_detail):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO Exams(Courses,Course_Exam_No,Course_Exam_Details) VALUES (?,?,?);'''
                   , (course_teaching[0][0], assign_no, assign_detail))
    cursor.execute('''SELECT Count(Student_Email)
                        FROM Exam_Grades
                        WHERE Courses = ?''', (course_teaching[0][0],))
    number_students = cursor.fetchall()

    cursor.execute('''SELECT Student_Email
                        FROM Exam_Grades
                        WHERE Courses = ?''', (course_teaching[0][0],))
    students = cursor.fetchall()

    for i in range(0, number_students[0][0]):
        cursor.execute('''INSERT INTO Exam_Grades(Courses,Student_Email,Course_Exam_No,Course_Exam_Grade) 
                            VALUES (?,?,?,?);''', (course_teaching[0][0], students[i][0], assign_no, "N/A"))

    connection.commit()

def enter_post(Courses, Post_No,Student_Email,Post_Info):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO Posts(Courses,Post_No,Student_Email,Post_Info) VALUES (?,?,?,?);
    ''',(Courses,Post_No,Student_Email,Post_Info))
    connection.commit()

def enter_comment(Courses, Post_No,Comment_No,Student_Email,Comment_Info):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO Comments(Courses,Post_No,Comment_No,Student_Email,Comment_Info) VALUES (?,?,?,?,?);
    ''',(Courses,Post_No,Comment_No,Student_Email,Comment_Info))
    connection.commit()

def check_password(password):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('''SELECT s1.Student_Email
                        FROM Students s1
                        WHERE s1.Password = ? AND s1.Student_Email=?''',(password,user_input_email))
    result = cursor.fetchall()
    if(result):
        return True
    else:
        return False

def check_TA(user_input_email):
    connection = sql.connect('database.db')
    cursor = connection.cursor()

    #Obtain Teaching team id if TA
    cursor.execute('''SELECT Teaching_Team_ID
                        FROM TA_teaching_teams
                        WHERE Student_Email = ?''',(user_input_email,))
    team_id = cursor.fetchall()
    return team_id

def TA_course(team_id):
    connection=sql.connect('database.db')
    cursor = connection.cursor()

    # Obtain course student is TAing
    cursor.execute('''SELECT Courses
                                FROM Sections
                                WHERE Teaching_Team_ID = ?
                                GROUP BY Courses''', team_id[0])
    return cursor.fetchall()

if __name__ == '__main__':
    app.run()

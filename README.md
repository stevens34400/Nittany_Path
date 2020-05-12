# Nittany Path (in progress)
This project was a submission for Penn State's Database Management Systems course (CMPSC 431W). Nittany path is designed and implemented to be a course management website for students and faculty. Stakeholders only include students, teaching assistants (TA), and professors. Functionalities include but are not limited to professors creating assignment, students checking courses they are taking, and TAs submitting scores for assignments. The back-end interface uses python as a programming language and the web framework, flask. Front-end template designs use HTML, CSS and JS. Note that dataset for Nittany State University was given through these [csv files](https://github.com/stevens34400/nittany_path/tree/master/dataset) also can be seen under the dataset folder in repository.

## ER Diagram

## Login Page
<p align="center">
  <img width="800" height="500" src="https://github.com/stevens34400/nittany_path/blob/master/images/login.gif">
</p>
Login page for user to enter email and password. Will verify whether user is part of Nittany State University.

## Student and TA Home Page

### Student Userinfo and Courses Page

### TA Userinfo and Courses Page

#### Click specific course Student
<p align="center">
  <img width="800" height="500" src="https://github.com/stevens34400/nittany_path/blob/master/images/clickcourse.gif">
</p>
Click specific course to retrieve and display all course assignments for logged in student.

### Create/View Posts and Comments page
<p align="center">
  <img width="800" height="500" src="https://github.com/stevens34400/nittany_path/blob/master/images/viewpostscomm.gif">
</p>
To view all posts and comments already created in a course.

### Create new post
<p align="center">
  <img width="800" height="500" src="https://github.com/stevens34400/nittany_path/blob/master/images/createpost.gif">
</p>
Creating new post for logged-in user and specified course. Note that each post includes a post number, stakeholder and post content.

### Create new comment
<p align="center">
  <img width="800" height="500" src="https://github.com/stevens34400/nittany_path/blob/master/images/createcomment.gif">
</p>
Creating a new comment for logged-in user and specified course. Note that each comment includes a comment number, stakeholder and comment content.

### Drop Courses Page
<p align="center">
  <img width="800" height="500" src="https://github.com/stevens34400/nittany_path/blob/master/images/dropcourse.gif">
</p>
Allows students to drop a course assuming that the current date has not passed the late drop deadline. Once student drops a course, all corresponding assignments, posts and comments by student will be dropped for that course. 

## Professor Home Page

### Create assignment
<p align="center">
  <img width="800" height="500" src="https://github.com/stevens34400/nittany_path/blob/master/images/createassign.gif">
</p>
Model only allows professors to create assignments for course he/she is teaching in. Assignments can come in the form of an exam or homework. Once new assignments are created, each student in that course will get a "N/A" grade as a default score for that assignment. Scores can be further adjusted by professor or TA shown below. Note that each assignment contains an assignment type, number and details. 

### Submit Scores Professor
<p align="center">
  <img width="800" height="500" src="https://github.com/stevens34400/nittany_path/blob/master/images/submitscoreprof.gif">
</p>
Model allows professor to submit scores for a specific assignment. Note that scores table includes a student email and their corresponding grade for that assignment.

### Submit Scores TA
<p align="center">
  <img width="800" height="500" src="https://github.com/stevens34400/nittany_path/blob/master/images/submitscoreta.gif">
</p>
Model also allows TAs for the course to submit scores of an assignment. In order to submit scores have to navigate to the 
"UserInfo and Courses" menu and click the hyperlinked class they are helping. Design of model was to treat TAs as students while allowing the extra feature of submitting scores. 

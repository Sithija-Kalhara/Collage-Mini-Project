-- ====================================================================
-- SQL QUERIES & JOINS REPORT
-- ====================================================================

-- 1. Fetch Student Names along with their Registered Course Names
SELECT s.Student_Name,
       c.Course_Name
FROM Students s 
INNER JOIN Courses c ON s.Course_ID = c.Course_ID;


-- 2. Fetch Student Names, Course Names, and Instructor Details
SELECT s.Student_Name,
       c.Course_Name,
       c.Instructor
FROM Students s 
INNER JOIN Courses c ON s.Course_ID = c.Course_ID;


-- 3. Count Total Students Registered per Course
SELECT c.Course_Name,
       COUNT(*) AS Total_Students
FROM Students s 
INNER JOIN Courses c ON s.Course_ID = c.Course_ID
GROUP BY c.Course_Name;


-- 4. Find Students who are Not Enrolled in any Course (Orphaned Students)
SELECT s.Student_Name
FROM Students s 
LEFT JOIN Courses c ON s.Course_ID = c.Course_ID 
WHERE c.Course_ID IS NULL;


-- 5. Fetch Student Names and their Tuition Fee Amount & Payment Status
SELECT s.Student_Name,
       f.Amount,
       f.Status
FROM Students s 
LEFT JOIN Fees f ON s.Student_ID = f.Student_ID;


-- 6. All Courses with Enrolled Student Names (Includes Courses with 0 Students)
SELECT s.Student_Name,
       c.Course_Name
FROM Students s 
RIGHT JOIN Courses c ON s.Course_ID = c.Course_ID;


-- 7. Find Courses that currently have No Students Registered
SELECT c.Course_Name
FROM Students s 
RIGHT JOIN Courses c ON s.Course_ID = c.Course_ID
WHERE s.Student_ID IS NULL; 

-- 8.Full Outer Join
SELECT s.Student_Name,
		c.Course_Name
FROM Students s 
FULL OUTER JOIN Courses c 
on s.Course_ID = c.Course_ID

-- 9.
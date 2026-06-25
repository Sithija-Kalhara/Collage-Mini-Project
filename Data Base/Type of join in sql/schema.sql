--Table Students
CREATE TABLE Students (
  Student_ID VARCHAR(10) PRIMARY KEY,
  Student_Name VARCHAR(50) NOT NULL,
  Course_ID VARCHAR(10),Courses	
  City VARCHAR(50)
  );
  
  -- Courses Table
  CREATE TABLE Courses (
  Course_ID VARCHAR(10) PRIMARY KEY,
  Course_Name VARCHAR(50) NOT NULL,
  Instructor VARCHAR(50)
);

-- Fees Table
CREATE TABLE Fees (
  Student_ID VARCHAR(10),
  Amount DECIMAL(10,2),
  Status VARCHAR(20),
  PRIMARY KEY (Student_ID),
  FOREIGN KEY(Student_ID) REFERENCES Students(Student_ID)
);

--Students Values
INSERT INTO Students VALUES
('5101','John', 'C01', 'Tokyo'),
('5102','Sara', 'C02', 'Osaka'),
('5103','David', 'C01', 'Nagoya'),
('5104','Emma', NULL, 'Kyoto');

--Courses Values
INSERT INTO Courses VALUES
('C01', 'SQL','Thanaka'),
('C02', 'Python','Suzuka'),
('C03', 'Java','Yamamoto');

--Fees Values
INSERT INTO Fees VALUES
('5101', 50000 ,'Paid'),
('5102', 60000 ,'Paid'), 
('5103', 50000 ,'Pending'); 

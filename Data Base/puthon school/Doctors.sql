CREATE TABLE Doctors
(
DoctorID INT PRIMARY KEY,
DoctorName VARCHAR(30),
Specialization VARCHAR(30),
DepartmentID INT
);

INSERT INTO Doctors VALUES
(201, 'Dr. Sharma', 'Cardiology', 1),
(202, 'Dr. Kumar', 'Neurology', 2),
(203, 'Dr. Priya', 'Orthopedics', 3),
(204, 'Dr. Ramesh', 'Dermatology', 2),
(205, 'Dr. Joseph', 'ENT', 4);
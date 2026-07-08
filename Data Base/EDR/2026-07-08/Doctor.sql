CREATE TABLE `Doctors` (
  `doctor_id` INT PRIMARY KEY,
  `doctor_name` VARCHAR(100),
  `specialization` VARCHAR(100),
  `phone` VARCHAR(20)
);

CREATE TABLE `Patients` (
  `Patient_id` INT PRIMARY KEY,
  `Patient_name` VARCHAR(100),
  `age` INT,
  `address` VARCHAR(200)
);

CREATE TABLE `Appointments` (
  `appointment_id` INT PRIMARY KEY,
  `doctor_id` INT,
  `Patient_id` INT,
  `appointment_date` DATE,
  `reason` VARCHAR(200)
);

ALTER TABLE `Appointments` ADD FOREIGN KEY (`doctor_id`) REFERENCES `Doctors` (`doctor_id`);

ALTER TABLE `Appointments` ADD FOREIGN KEY (`Patient_id`) REFERENCES `Patients` (`Patient_id`);

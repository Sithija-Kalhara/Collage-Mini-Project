-- Airline Bookings | SQL Practice Database
-- Portable schema/data for SQLite and MySQL 8+ (explicit IDs and foreign keys).
-- Contains fictional sample records for learning.

CREATE TABLE Passengers (
    PassengerID INTEGER PRIMARY KEY,
    PassengerName VARCHAR(80) NOT NULL,
    City VARCHAR(60) NOT NULL,
    Age INTEGER NOT NULL
);

CREATE TABLE Destinations (
    DestinationID INTEGER PRIMARY KEY,
    DestinationName VARCHAR(100) NOT NULL
);

CREATE TABLE Flights (
    FlightID INTEGER PRIMARY KEY,
    FlightCode VARCHAR(100) NOT NULL,
    DestinationID INTEGER NOT NULL,
    BaseFare DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (DestinationID) REFERENCES Destinations(DestinationID)
);

CREATE TABLE FlightBookings (
    BookingID INTEGER PRIMARY KEY,
    PassengerID INTEGER NOT NULL,
    FlightID INTEGER NOT NULL,
    BookingDate DATE NOT NULL,
    FarePaid DECIMAL(12,2) NOT NULL,
    Status VARCHAR(20) NOT NULL,
    FOREIGN KEY (PassengerID) REFERENCES Passengers(PassengerID),
    FOREIGN KEY (FlightID) REFERENCES Flights(FlightID)
);

CREATE TABLE Baggage (
    BaggageID INTEGER PRIMARY KEY,
    BookingID INTEGER NOT NULL,
    WeightKg DECIMAL(12,2) NOT NULL,
    BaggageType VARCHAR(120) NOT NULL,
    FOREIGN KEY (BookingID) REFERENCES FlightBookings(BookingID)
);

INSERT INTO Passengers (PassengerID, PassengerName, City, Age) VALUES
  (1, 'Nora Patel', 'Delhi', 24),
  (2, 'Yash Sharma', 'Mumbai', 32),
  (3, 'Sofia Rao', 'Pune', 27),
  (4, 'Aditya Jain', 'Chennai', 41),
  (5, 'Priya Kapoor', 'Hyderabad', 36),
  (6, 'Zain Ali', 'Jaipur', 29),
  (7, 'Mira Nair', 'Kolkata', 45),
  (8, 'Evan Roy', 'Bengaluru', 22);

INSERT INTO Destinations (DestinationID, DestinationName) VALUES
  (1, 'Delhi'),
  (2, 'Mumbai'),
  (3, 'Bengaluru'),
  (4, 'Kolkata');

INSERT INTO Flights (FlightID, FlightCode, DestinationID, BaseFare) VALUES
  (1, 'SK101 Delhi AM', 1, 6800),
  (2, 'SK102 Delhi PM', 1, 7300),
  (3, 'SK201 Mumbai AM', 2, 5200),
  (4, 'SK202 Mumbai PM', 2, 5500),
  (5, 'SK301 Bengaluru AM', 3, 8900),
  (6, 'SK302 Bengaluru PM', 3, 9400),
  (7, 'SK401 Kolkata AM', 4, 6100);

INSERT INTO FlightBookings (BookingID, PassengerID, FlightID, BookingDate, FarePaid, Status) VALUES
  (1, 1, 1, '2025-01-08', 7820.0, 'Completed'),
  (2, 2, 2, '2025-01-11', 9654.25, 'Completed'),
  (3, 3, 3, '2025-01-15', 6578.0, 'Pending'),
  (4, 1, 2, '2025-02-02', 8227.1, 'Completed'),
  (5, 4, 4, '2025-02-07', 5060.0, 'Cancelled'),
  (6, 5, 5, '2025-02-16', 12282.0, 'Completed'),
  (7, 2, 1, '2025-03-02', 8211.0, 'Completed'),
  (8, 6, 6, '2025-03-05', 10269.5, 'Pending'),
  (9, 3, 2, '2025-03-10', 11333.25, 'Completed'),
  (10, 4, 3, '2025-03-14', 5083.0, 'Completed'),
  (11, 5, 4, '2025-04-01', 6325.0, 'Completed'),
  (12, 1, 5, '2025-04-12', 13817.25, 'Pending'),
  (13, 2, 6, '2025-04-19', 11891.0, 'Completed'),
  (14, 6, 3, '2025-05-05', 7475.0, 'Completed'),
  (15, 3, 1, '2025-05-16', 4692.0, 'Cancelled'),
  (16, 4, 6, '2025-05-27', 10810.0, 'Completed'),
  (17, 1, 4, '2025-06-03', 8855.0, 'Completed'),
  (18, 5, 2, '2025-06-11', 7555.5, 'Pending');

INSERT INTO Baggage (BaggageID, BookingID, WeightKg, BaggageType) VALUES
  (1, 1, 7, 'Cabin'),
  (2, 2, 15, 'Checked'),
  (3, 3, 10, 'Checked'),
  (4, 4, 20, 'Checked'),
  (5, 5, 5, 'Cabin'),
  (6, 7, 8, 'Cabin'),
  (7, 9, 12, 'Checked'),
  (8, 11, 25, 'Oversize'),
  (9, 13, 9, 'Checked'),
  (10, 17, 14, 'Checked');


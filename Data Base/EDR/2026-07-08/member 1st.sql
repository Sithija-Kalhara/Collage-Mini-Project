CREATE TABLE `Members` (
  `member_id` INT PRIMARY KEY,
  `member_name` VARCHAR(100),
  `phone` VARCHAR(20),
  `email` VARCHAR(100)
);

CREATE TABLE `Books` (
  `book_id` INT PRIMARY KEY,
  `book_title` VARCHAR(100),
  `author` VARCHAR(100),
  `category` VARCHAR(50)
);

CREATE TABLE `Borrowings` (
  `borrow_id` INT PRIMARY KEY,
  `member_id` INT,
  `book_id` INT,
  `borrow_data` DATE,
  `return_data` DATE
);

ALTER TABLE `Borrowings` ADD FOREIGN KEY (`member_id`) REFERENCES `Members` (`member_id`);

ALTER TABLE `Borrowings` ADD FOREIGN KEY (`book_id`) REFERENCES `Books` (`book_id`);

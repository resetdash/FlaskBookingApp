-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jan 14, 2019 at 06:42 AM
-- Server version: 5.7.19
-- PHP Version: 7.1.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `booking`
--
CREATE DATABASE IF NOT EXISTS `booking_db` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `booking_db`;

-- --------------------------------------------------------

--
-- Table structure for table `booking_table`
--

DROP TABLE IF EXISTS `booking_table`;
CREATE TABLE IF NOT EXISTS `booking_table` (
  `booking_id` INT(11) NOT NULL AUTO_INCREMENT,
  `patient_id` INT(11) NOT NULL,
  `doctor_id` INT(11) NOT NULL,
  `consultation_date` DATETIME NOT NULL,
  `consultation_details` varchar(255) NOT NULL DEFAULT 'Consultation yet to happen',
  `payment_status` VARCHAR(20) NOT NULL DEFAULT 'UNPAID',
  `modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`booking_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `booking_table`
--

INSERT INTO `booking_table` (`booking_id`, `patient_id`, `doctor_id`, `consultation_date`, `consultation_details`, `payment_status`,`modified`) VALUES
(1 , 801, 501, '2021-03-21 10:00:00','got cough and fever, need to rest', 'UNPAID','2021-04-03 13:00:00'),
(2 , 802, 502, '2021-03-21 10:30:00','severe headache and stuff','PAID','2021-04-03 13:00:00'),
(3 , 801, 501, '2021-03-21 11:00:00','stomachace from food poisoning','PAID','2021-04-03 13:00:00'),
(4 , 802, 501, '2021-03-21 15:00:00','Consultation yet to happen', 'UNPAID','2021-04-03 13:00:00'),
(5 , 801, 501, '2021-03-21 14:00:00','Consultation yet to happen', 'UNPAID','2021-04-03 13:00:00');


-- --------------------------------------------------------

--
-- Table structure for table `drug_details_table`
--

DROP TABLE IF EXISTS `drug_details_table`;
CREATE TABLE IF NOT EXISTS `drug_details_table` (
  `details_id` int(11) NOT NULL AUTO_INCREMENT,
  `booking_id` int(11) NOT NULL,
  `item_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  PRIMARY KEY (`details_id`),
  KEY `FK_booking_id` (`booking_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;


INSERT INTO `drug_details_table` (`details_id`, `booking_id`, `item_id`, `quantity`) VALUES
(1, 1, 1, 4),
(2, 1, 2, 3);

-- Constraints for table `drug_details_table`
ALTER TABLE `drug_details_table`
  ADD CONSTRAINT `FK_booking_id` FOREIGN KEY (`booking_id`) REFERENCES `booking_table` (`booking_id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

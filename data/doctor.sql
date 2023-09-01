-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Mar 19, 2021 at 10:30 AM
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
-- Database: `Doctor`
--
  
CREATE DATABASE IF NOT EXISTS `doctor_db` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `doctor_db`;

-- --------------------------------------------------------

--
-- Table structure for table `doctor`
--

DROP TABLE IF EXISTS `doctor_table`;
CREATE TABLE IF NOT EXISTS `doctor_table` (
    `doctor_id` INT(11) NOT NULL,
    `doctor_name` varchar(64) NOT NULL,
    `date_time` datetime NOT NULL,
    `availability` boolean NOT NULL,
    CONSTRAINT PK_doctor PRIMARY KEY (doctor_id,date_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `doctor`
--

INSERT INTO `doctor_table` (`doctor_id`, `doctor_name`, `date_time`, `availability`) VALUES
('501','Shao Man','2021-03-21 09:00:00','0'),
('501','Shao Man','2021-03-21 09:30:00','0'),
('501','Shao Man','2021-03-21 10:00:00','1'),
('501','Shao Man','2021-03-21 10:30:00','1'),
('501','Shao Man','2021-03-21 11:00:00','1'),
('501','Shao Man','2021-03-21 11:30:00','1'),
('501','Shao Man','2021-03-21 12:00:00','0'),
('502','Jarod Hong','2021-03-21 09:00:00','0'),
('502','Jarod Hong','2021-03-21 09:30:00','1'),
('502','Jarod Hong','2021-03-21 10:00:00','1'),
('502','Jarod Hong','2021-03-21 10:30:00','0'),
('502','Jarod Hong','2021-03-21 11:00:00','1'),
('502','Jarod Hong','2021-03-21 11:30:00','0'),
('502','Jarod Hong','2021-03-21 12:00:00','0');

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
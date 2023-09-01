CREATE DATABASE IF NOT EXISTS `inventory`;
USE `inventory`;

--
-- Database: `inventory`
--

-- --------------------------------------------------------

--
-- Table structure for table `inventory`
--

DROP TABLE IF EXISTS `inventory`;
CREATE TABLE `inventory` (
  `ItemID` int NOT NULL AUTO_INCREMENT,
  `ItemName` varchar(50) NOT NULL,
  `ItemDescription` varchar(150) NOT NULL,
  `CostPrice` double NOT NULL,
  `RetailPrice` double NOT NULL,
  `Quantity` int,
  PRIMARY KEY (`ItemID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `inventory`
--

INSERT INTO `inventory` (`ItemID`, `ItemName`, `ItemDescription`, `CostPrice`, `RetailPrice`, `Quantity`) VALUES
('1', 'Consultation', 'Consult', '15.0', '15.0', '9999'),
('2', 'Checkup', 'Checkup', '25.0', '25.0', '9999'),
('3', 'Ibuprofen', 'Painkiller for a range of aches and pains, including back pain, period pain, toothache', '5.0', '2.0', '99'),
('4', 'Hydrocodone', 'Treating acute or chronic moderate to moderately severe pain', '7.0', '5.0', '99'),
('5', 'Lisinopril', 'Treating high blood pressure, congestive heart failure', '15.0', '12.0', '99'),
('6', 'Azithromycin', 'Antibiotic used for treating ear, throat, and sinus infections as well as pneumonia, bronchitis', '6.0', '3.0', '99');
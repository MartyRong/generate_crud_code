CREATE  database school default character set utf8mb4 collate utf8mb4_bin;

CREATE TABLE `student` (
  `id` bigint(20) AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_bin NOT NULL,
  `gender` varchar(32) COLLATE utf8mb4_bin NOT NULL,
  `age` int(11) NOT NULL DEFAULT '0',
  `grade` tinyint(4) NOT NULL DEFAULT '0',
  `order_number` bigint(20) NOT NULL DEFAULT '0',
  `description` text DEFAULT '',
  `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
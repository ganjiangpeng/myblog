-- MySQL dump 10.13  Distrib 5.5.17, for Win64 (x86)
--
-- Host: localhost    Database: blog
-- ------------------------------------------------------
-- Server version	5.5.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `posts`
--

DROP TABLE IF EXISTS `posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `posts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `body` text,
  `timestamp` datetime DEFAULT NULL,
  `author_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts`
--

LOCK TABLES `posts` WRITE;
/*!40000 ALTER TABLE `posts` DISABLE KEYS */;
INSERT INTO `posts` VALUES (1,'hello this is my first post!','2017-09-30 08:10:49',1),(2,'Hello World!!','2017-09-30 08:50:01',15);
/*!40000 ALTER TABLE `posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `default` tinyint(1) DEFAULT '0',
  `permissions` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Administrator',0,255),(2,'Moderator',0,7),(3,'User',1,3);
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) DEFAULT NULL,
  `password_hash` varchar(128) NOT NULL,
  `name` varchar(64) DEFAULT NULL,
  `email` varchar(64) NOT NULL,
  `about_me` text,
  `role_id` int(11) DEFAULT NULL,
  `confirmed` tinyint(1) DEFAULT '0',
  `location` varchar(64) DEFAULT NULL,
  `create_at` datetime DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  `avatar_hash` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'gan','pbkdf2:sha1:1000$VfpGaO0G$aa3e4fd4a91cbe6232bafd43d08fa655b3d2d359','山石玉-甘江鹏','ganjiangpeng@3shiyu.com','我在深圳福田上班！',2,1,'深圳福田','2017-09-28 06:57:19','2017-09-30 08:43:24','495b046cb750bf6049fd5210bf1da5f0'),(2,'jiang','pbkdf2:sha1:1000$VfpGaO0G$aa3e4fd4a91cbe6232bafd43d08fa655b3d2d359',NULL,'jiang@test.com',NULL,1,0,NULL,'2017-09-28 06:57:19','2017-09-28 06:57:19',NULL),(3,'peng','pbkdf2:sha1:1000$VfpGaO0G$aa3e4fd4a91cbe6232bafd43d08fa655b3d2d359',NULL,'peng@test.com',NULL,3,0,NULL,'2017-09-28 06:57:19','2017-09-28 06:57:19',NULL),(5,'xu','pbkdf2:sha1:1000$VfpGaO0G$aa3e4fd4a91cbe6232bafd43d08fa655b3d2d359',NULL,'xu@test.com',NULL,3,0,NULL,'2017-09-28 06:57:19','2017-09-28 06:57:19',NULL),(8,'summer','pbkdf2:sha1:1000$VfpGaO0G$aa3e4fd4a91cbe6232bafd43d08fa655b3d2d359',NULL,'summer@test.com',NULL,3,0,NULL,'2017-09-28 06:57:19','2017-09-28 06:57:19',NULL),(14,'ganjiangpeng','pbkdf2:sha1:1000$7zLnq4D2$0f0a5e51070fe0bf2345817bdb6a6efc69c45afb','甘江鹏','82132532@qq.com','my name is gan ,i come from guizhou ! test avatar ',1,1,'贵州盘县','2017-09-28 06:57:19','2017-09-30 07:04:41',''),(15,'king','pbkdf2:sha1:1000$RaZzORUD$38aaac72c845d91cd4209515ed0106279f324e15',NULL,'gan@kingguo.top',NULL,3,1,NULL,'2017-09-30 01:15:45','2017-09-30 09:05:21','');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-09-30 18:31:54

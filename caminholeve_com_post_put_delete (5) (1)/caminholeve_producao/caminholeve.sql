-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: localhost    Database: caminho_leve_mc
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `administrador`
--

DROP TABLE IF EXISTS `administrador`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `administrador` (
  `email` varchar(100) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `senha` varchar(255) NOT NULL,
  `criado_em` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `administrador`
--

LOCK TABLES `administrador` WRITE;
/*!40000 ALTER TABLE `administrador` DISABLE KEYS */;
/*!40000 ALTER TABLE `administrador` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `artigos`
--

DROP TABLE IF EXISTS `artigos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `artigos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `titulo` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  `origem` varchar(255) DEFAULT NULL,
  `autor` varchar(255) DEFAULT NULL,
  `ano_artigo` varchar(45) DEFAULT NULL,
  `tipo` varchar(45) DEFAULT NULL,
  `criado_por` varchar(200) DEFAULT NULL,
  `criado_em` datetime DEFAULT CURRENT_TIMESTAMP,
  `aprovado_por` varchar(255) DEFAULT NULL,
  `revisado` char(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `criado_por` (`criado_por`),
  KEY `artigos_ibfk_2_idx` (`aprovado_por`),
  CONSTRAINT `artigos_ibfk_1` FOREIGN KEY (`criado_por`) REFERENCES `usuarios` (`email`),
  CONSTRAINT `artigos_ibfk_2` FOREIGN KEY (`aprovado_por`) REFERENCES `usuarios` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `artigos`
--

LOCK TABLES `artigos` WRITE;
/*!40000 ALTER TABLE `artigos` DISABLE KEYS */;
INSERT INTO `artigos` VALUES (1,'Titutlo1','http:zz/','UUUUU','autorrrrr',NULL,NULL,'teste@teste.com','2026-12-06 00:00:00',NULL,'0'),(3,'AAAAAAAA','sadasd','asdasd','asdasd',NULL,NULL,'teste@teste.com','2025-12-02 00:00:00',NULL,'0');
/*!40000 ALTER TABLE `artigos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forum`
--

DROP TABLE IF EXISTS `forum`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `forum` (
  `id` int NOT NULL AUTO_INCREMENT,
  `autor_id` varchar(200) NOT NULL,
  `texto` text NOT NULL,
  `criado_em` datetime DEFAULT CURRENT_TIMESTAMP,
  `likes` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `autor_id` (`autor_id`),
  CONSTRAINT `forum_ibfk_1` FOREIGN KEY (`autor_id`) REFERENCES `usuarios` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum`
--

LOCK TABLES `forum` WRITE;
/*!40000 ALTER TABLE `forum` DISABLE KEYS */;
INSERT INTO `forum` VALUES (2,'rafaelmuniz.ti@gmail.com123','teste','2026-06-19 19:07:42',0),(3,'rafaelmuniz.ti@gmail.com123','aaaa','2026-06-19 19:07:55',1),(4,'teste@tet.com','sdf sdf sdf sdf sd fsd fds fds fsdf','2026-08-12 15:51:34',0);
/*!40000 ALTER TABLE `forum` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forum_curtidas`
--

DROP TABLE IF EXISTS `forum_curtidas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `forum_curtidas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `forum_id` int NOT NULL,
  `usuario_email` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `forum_id` (`forum_id`,`usuario_email`),
  KEY `usuario_email` (`usuario_email`),
  CONSTRAINT `forum_curtidas_ibfk_1` FOREIGN KEY (`forum_id`) REFERENCES `forum` (`id`) ON DELETE CASCADE,
  CONSTRAINT `forum_curtidas_ibfk_2` FOREIGN KEY (`usuario_email`) REFERENCES `usuarios` (`email`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_curtidas`
--

LOCK TABLES `forum_curtidas` WRITE;
/*!40000 ALTER TABLE `forum_curtidas` DISABLE KEYS */;
INSERT INTO `forum_curtidas` VALUES (2,3,'rafaelmuniz.ti@gmail.com123');
/*!40000 ALTER TABLE `forum_curtidas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forum_resposta_curtidas`
--

DROP TABLE IF EXISTS `forum_resposta_curtidas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `forum_resposta_curtidas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `resposta_id` int NOT NULL,
  `usuario_email` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `resposta_id` (`resposta_id`,`usuario_email`),
  KEY `usuario_email` (`usuario_email`),
  CONSTRAINT `forum_resposta_curtidas_ibfk_1` FOREIGN KEY (`resposta_id`) REFERENCES `forum_respostas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `forum_resposta_curtidas_ibfk_2` FOREIGN KEY (`usuario_email`) REFERENCES `usuarios` (`email`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_resposta_curtidas`
--

LOCK TABLES `forum_resposta_curtidas` WRITE;
/*!40000 ALTER TABLE `forum_resposta_curtidas` DISABLE KEYS */;
INSERT INTO `forum_resposta_curtidas` VALUES (2,3,'rafaelmuniz.ti@gmail.com123');
/*!40000 ALTER TABLE `forum_resposta_curtidas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forum_resposta_denuncia`
--

DROP TABLE IF EXISTS `forum_resposta_denuncia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `forum_resposta_denuncia` (
  `id` int NOT NULL AUTO_INCREMENT,
  `resposta_id` int DEFAULT NULL,
  `usuario_email` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `denunciar_idx` (`usuario_email`),
  CONSTRAINT `denunciar` FOREIGN KEY (`usuario_email`) REFERENCES `usuarios` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_resposta_denuncia`
--

LOCK TABLES `forum_resposta_denuncia` WRITE;
/*!40000 ALTER TABLE `forum_resposta_denuncia` DISABLE KEYS */;
INSERT INTO `forum_resposta_denuncia` VALUES (3,3,'rafaelmuniz.ti@gmail.com123'),(4,3,'teste@tet.com'),(5,4,'teste@tet.com');
/*!40000 ALTER TABLE `forum_resposta_denuncia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forum_respostas`
--

DROP TABLE IF EXISTS `forum_respostas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `forum_respostas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `forum_id` int NOT NULL,
  `autor_email` varchar(200) NOT NULL,
  `texto` text NOT NULL,
  `criado_em` datetime DEFAULT CURRENT_TIMESTAMP,
  `likes` int DEFAULT '0',
  `ativo` char(1) DEFAULT 'S',
  PRIMARY KEY (`id`),
  KEY `forum_id` (`forum_id`),
  KEY `autor_email` (`autor_email`),
  CONSTRAINT `forum_respostas_ibfk_1` FOREIGN KEY (`forum_id`) REFERENCES `forum` (`id`) ON DELETE CASCADE,
  CONSTRAINT `forum_respostas_ibfk_2` FOREIGN KEY (`autor_email`) REFERENCES `usuarios` (`email`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_respostas`
--

LOCK TABLES `forum_respostas` WRITE;
/*!40000 ALTER TABLE `forum_respostas` DISABLE KEYS */;
INSERT INTO `forum_respostas` VALUES (2,2,'rafaelmuniz.ti@gmail.com123','asdasdsad','2026-06-19 19:07:48',0,'S'),(3,3,'rafaelmuniz.ti@gmail.com123','teste','2026-06-19 19:16:10',1,'N'),(4,3,'rafaelmuniz.ti@gmail.com123','Rafael','2026-06-19 19:16:17',0,'S'),(5,3,'teste@tet.com','aaaaaaaaaaaaaa','2026-08-12 15:51:46',0,'S');
/*!40000 ALTER TABLE `forum_respostas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `relato_curtidas`
--

DROP TABLE IF EXISTS `relato_curtidas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `relato_curtidas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `relato_id` int NOT NULL,
  `usuario_email` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `relato_id` (`relato_id`,`usuario_email`),
  KEY `usuario_email` (`usuario_email`),
  CONSTRAINT `relato_curtidas_ibfk_1` FOREIGN KEY (`relato_id`) REFERENCES `relatos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `relato_curtidas_ibfk_2` FOREIGN KEY (`usuario_email`) REFERENCES `usuarios` (`email`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `relato_curtidas`
--

LOCK TABLES `relato_curtidas` WRITE;
/*!40000 ALTER TABLE `relato_curtidas` DISABLE KEYS */;
/*!40000 ALTER TABLE `relato_curtidas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `relatos`
--

DROP TABLE IF EXISTS `relatos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `relatos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `autor_email` varchar(200) NOT NULL,
  `texto` text NOT NULL,
  `criado_em` datetime DEFAULT CURRENT_TIMESTAMP,
  `likes` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `autor_email` (`autor_email`),
  CONSTRAINT `relatos_ibfk_1` FOREIGN KEY (`autor_email`) REFERENCES `usuarios` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `relatos`
--

LOCK TABLES `relatos` WRITE;
/*!40000 ALTER TABLE `relatos` DISABLE KEYS */;
/*!40000 ALTER TABLE `relatos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `email` varchar(200) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `cidade` varchar(100) DEFAULT NULL,
  `estado` varchar(50) DEFAULT NULL,
  `nascimento` date DEFAULT NULL,
  `tipo` enum('Portador','Outros') NOT NULL,
  `senha` varchar(255) NOT NULL,
  `criado_em` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES ('rafaelmuniz.ti@gmail.com','RAFAEL MUNIZ','Jundiaí','SP','2026-06-12','Portador','123123','2026-06-12 16:49:24'),('rafaelmuniz.ti@gmail.com1','Rafael Muniz','Jundiaí','SP','2000-01-01','Portador','scrypt:32768:8:1$eRFbgQ9pvQS0g8o3$eb211348dadf0cc84078545b751d90a85da5782e600efcfc089686abd09ed90276962976d4a59747a57a375cf2332ff7971dcfeb010604d6a6ba429e6df38211','2026-06-19 18:44:16'),('rafaelmuniz.ti@gmail.com123','Rafael Muniz','Jundiaí','SP','2026-06-13','Portador','scrypt:32768:8:1$GrJljzgObk7c3Ehd$d2eaa17413127e535d2537b4de76801444f72ad1237fa995c6d29711a29b696c5b9033cc15d424e75505488e424637a289a36f6d03c772aa4aac2250a500bfa6','2026-06-13 13:25:07'),('teste@teste.com','Teste','Cidade','Estado','2000-01-01','Portador','$2y$10$XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX','2026-06-03 15:44:49'),('teste@tet.com','teste','1111','SP','2000-11-11','Portador','scrypt:32768:8:1$ZMSfOJI9yLgM5Z0k$d516aaa2c5bca9e25ec4d041f3a06bde23d267020ef7f18a98691bf9ec6fb0add80d9e638dd202bad0c18fb19ad3544e4a5d43884d389c35288a1d3990f20131','2026-08-12 15:51:04'),('teste1@caminholeve.com','Usuário Teste 1','Cidade 1','SP','1990-01-01','Portador','123','2026-06-19 19:07:12'),('teste2@caminholeve.com','Usuário Teste 2','Cidade 2','RJ','1995-05-05','Outros','123','2026-06-19 19:07:12');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-08 19:12:59

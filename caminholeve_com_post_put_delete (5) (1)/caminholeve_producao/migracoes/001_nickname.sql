-- 001_nickname.sql — adiciona o apelido público (nickname) dos usuários.
-- O nickname é o nome exibido no site (fórum, respostas, relatos, saudação).
-- O nome completo continua guardado, mas só aparece no perfil e no painel ADM.
-- UNIQUE: dois usuários não podem ter o mesmo apelido. Com a collation utf8mb4_0900_ai_ci
-- a comparação ignora maiúsculas e acentos ("Ana" = "ana" = "Aná").
-- Contas antigas ficam com NULL e o site mostra o nome até a pessoa definir um apelido no perfil.
ALTER TABLE usuarios
    ADD COLUMN nickname VARCHAR(30) NULL AFTER nome,
    ADD UNIQUE KEY uk_usuarios_nickname (nickname);

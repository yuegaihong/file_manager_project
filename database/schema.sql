CREATE DATABASE IF NOT EXISTS file_manager;
USE file_manager;

-- 用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(6) NOT NULL UNIQUE,
    password VARCHAR(12) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);

-- 文件表，使用LONGBLOB存储文件数据
CREATE TABLE files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_data LONGBLOB NOT NULL,  -- 使用LONGBLOB存储二进制文件数据
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建管理员账户
INSERT INTO users (username, password, is_admin) VALUES ('yue', '031031', TRUE);

CREATE DATABASE agent_saas;

USE agent_saas;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- Agents table
CREATE TABLE agents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100),
    token VARCHAR(255) NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'inactive',
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Commands table
CREATE TABLE commands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    command TEXT NOT NULL,
    status ENUM('queued', 'running', 'completed', 'failed') DEFAULT 'queued',
    output TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
);

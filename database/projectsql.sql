-- INPUT SQL TABLE HERE --
-- REMBMBER TO PULL CHANGES BEFORE MAKING CHANGES HERE, THEN COMMIT & PUSH AFTER CHANGES --
DROP DATABASE finance_db;

CREATE DATABASE finance_db;
USE finance_db;

CREATE TABLE stocks (
    stock_id INT PRIMARY KEY AUTO_INCREMENT,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    company_name VARCHAR(100) NOT NULL,
    sector VARCHAR(50)
);
CREATE TABLE portfolio (
    portfolio_id INT PRIMARY KEY AUTO_INCREMENT,
    stock_id INT NOT NULL,
    quantity DECIMAL(12, 2) NOT NULL,
    avg_price DECIMAL(10, 2) NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
);
INSERT INTO stocks (symbol, company_name, sector) VALUES
('AAPL', 'Apple Inc.', 'Technology'),
('GOOGL', 'Alphabet Inc.', 'Technology'),
('AMZN', 'Amazon.com, Inc.', 'Consumer Discretionary'),
('TSLA', 'Tesla, Inc.', 'Automotive'),
('MSFT', 'Microsoft Corporation', 'Technology'),
('JPM', 'JPMorgan Chase & Co.', 'Financial'),
('NFLX', 'Netflix, Inc.', 'Communication Services'),
('NVDA', 'NVIDIA Corporation', 'Technology'),
('PFE', 'Pfizer Inc.', 'Healthcare');
INSERT INTO portfolio (stock_id, quantity, avg_price, last_updated) VALUES
(1, 50.00, 145.20, '2025-07-15 10:23:00'),
(2, 10.00, 2800.00, '2025-07-14 09:10:00'),
(3, 5.00, 3450.50, '2025-07-16 14:30:00'),
(4, 12.00, 720.00, '2025-07-12 08:00:00'),
(5, 20.00, 299.99, '2025-07-13 11:45:00'),
(6, 100.00, 165.00, '2025-07-10 16:12:00'),
(7, 7.00, 590.25, '2025-07-09 10:00:00'),
(8, 15.00, 850.00, '2025-07-11 17:50:00'),
(9, 80.00, 39.90, '2025-07-08 13:37:00'),


-- FORMAT FOR CREATING STORED PROCEEDURE --
USE stocks_sproc
DELIMITER //
CREATE PROCEDURE stocks_sproc
(	symbol VARCHAR(20),
	company_name VARCHAR(100),
    sector VARCHAR(50))
BEGIN
	INSERT INTO stocks
    (symbol, company_name, sector)
    VALUES
    (symbol, company_name, sector);
END//
DELIMITER ;

		-- HOW TO USE THE STORED PROCEEDURE TO ENTER DATA --
CALL stocks_sproc('KO', 'The Coca-Cola Company', 'Consumer Staples');

-- VIEWING THE TABLE
SELECT * FROM stocks;





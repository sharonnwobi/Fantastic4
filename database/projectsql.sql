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
ALTER TABLE stocks AUTO_INCREMENT=1000;

CREATE TABLE transactions (
    -- portfolio_id INT PRIMARY KEY AUTO_INCREMENT,-- is a portfolio_id needed if we are only having unique stock id?
    -- upon entry, logic dhould check if user holds a stock in porfolio, if yes, then a row modification is made based on stock_id
    -- IF NO, then a new row is entered: use SYMBOL from user input to find mathcung stock_id on stocks table, then insert into portolo with relevant quantities.
    -- Note: if adding new row, only two fields are needed in logic, call stored proceedure
    
    stock_id INT, -- cannot be primary key 
    price DOUBLE NOT NULL,
    quantity DECIMAL(12, 2) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) 
   
);

CREATE TABLE portfolio_history(
-- history_id INT PRIMARY KEY AUTO_INCREMENT,
symbol VARCHAR(50),
avg_price DOUBLE,
timestamp_hist DATETIME
FOREIGN KEY (symbol) REFERENCES stocks(symbol) ON DELETE CASCADE
 -- Create trigger to auto remove history based on portfolio: link histtory to portfolio
)



-- STORED PROCEEDURE for stocks --
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
DELIMITER;


-- STORED PROCEEDURE for transactions --
USE transactions_sproc
DELIMITER //
CREATE PROCEDURE transactions_sproc
	(
	stock_id INT,
    price DOUBLE,
	quantity DECIMAL(12, 2))
BEGIN
	INSERT INTO transactions
    (stock_id, price, quantity)
    VALUES
    (stock_id, price, quantity);
END//
DELIMITER ;
-- TO ENTER DATA WRITE QUERY:   CALL portfolio_stocks(1001, 50);


-- STORED PROCEEDURE for historytable --
USE history_sproc
DELIMITER //
CREATE PROCEDURE history_sproc
	(
	symbol VARCHAR(250),
	avg_price DOUBLE)
BEGIN
	INSERT INTO portfolio_history
    (symbol, avg_price)
    VALUES
    (symbol, avg_price);
END//
DELIMITER ;
-- TO ENTER DATA WRITE: CALL history_sproc(APPL, 20.49)





		-- POPULATING STOCKS AND PORTFOLIO TABLES, history needs live data.

CALL stocks_sproc('AAPL', 'Apple Inc.', 'Technology');
CALL stocks_sproc('GOOGL', 'Alphabet Inc.', 'Technology');
CALL stocks_sproc('AMZN', 'Amazon.com, Inc.', 'Consumer Discretionary');
CALL stocks_sproc('TSLA', 'Tesla, Inc.', 'Automotive');
CALL stocks_sproc('MSFT', 'Microsoft Corporation', 'Technology');
CALL stocks_sproc('JPM', 'JPMorgan Chase & Co.', 'Financial');
CALL stocks_sproc('NFLX', 'Netflix, Inc.', 'Communication Services');
CALL stocks_sproc('NVDA', 'NVIDIA Corporation', 'Technology');
CALL stocks_sproc('PFE', 'Pfizer Inc.', 'Healthcare');
CALL stocks_sproc('KO', 'The Coca-Cola Company', 'Consumer Staples');

CALL transactions_sproc(1001, 14.00, 4 );
CALL transactions_sproc(1001, -15.50, -2);
CALL transactions_sproc(1003, 205.00, 3);
CALL transactions_sproc(1005, 50.77, 1);
CALL transactions_sproc(1003, 189.00, -1 );

SELECT * FROM transactions;
SELECT s.symbol, SUM(t.price) AS total_price, SUM(t.quantity) AS total_quantity FROM transactions t JOIN stocks s ON  s.stock_id = t.stock_id GROUP BY s.symbol;









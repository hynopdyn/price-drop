-- db/init.sql
CREATE TABLE prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(512) NOT NULL,
    title VARCHAR(512),
    image_url VARCHAR(512),
    current_price DECIMAL(10,2),
    previous_price DECIMAL(10,2),
    lowest_price DECIMAL(10,2)
);
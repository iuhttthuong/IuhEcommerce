-- Create shops table
CREATE TABLE shops (
    seller_id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    mail VARCHAR(100) UNIQUE,
    address TEXT,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);

-- Add indexes for performance
CREATE INDEX idx_shops_username ON shops(username);
CREATE INDEX idx_shops_mail ON shops(mail);

-- Add comment
COMMENT ON TABLE shops IS 'Stores information about shops/sellers accounts';

-- First, let's get the hashed password using pgcrypto extension
DROP EXTENSION IF EXISTS pgcrypto CASCADE;
CREATE EXTENSION pgcrypto;

-- Xóa bảng shops nếu đã tồn tại
DROP TABLE IF EXISTS shops;

-- Tạo lại bảng shops, shop_id là INT, không phải SERIAL, không liên kết FK với sellers
CREATE TABLE shops (
    shop_id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255),
    email VARCHAR(100) UNIQUE,
    shop_name VARCHAR(100),
    description TEXT,
    logo_url VARCHAR(255),
    address TEXT,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    rating DECIMAL(3,2),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Thêm dữ liệu từ bảng sellers vào shops, shop_id = seller_id
INSERT INTO shops (
    shop_id,
    username, 
    password, 
    email, 
    shop_name, 
    description, 
    logo_url, 
    address, 
    phone, 
    is_active, 
    rating
)
SELECT 
    s.seller_id as shop_id,
    'shop_' || s.seller_id::text as username,
    crypt('shop' || s.seller_id::text, gen_salt('bf', 12)) as password,
    'shop' || s.seller_id::text || '@iuhecomerce.com' as email,
    COALESCE(s.seller_name, 'Shop ' || s.seller_id::text) as shop_name,
    'Welcome to Shop ' || s.seller_id::text as description,
    'https://rubee.com.vn/wp-content/uploads/2021/05/Logo-IUH.jpg' as logo_url,
    '123 Shop Street, City ' || s.seller_id::text as address,
    CASE 
        WHEN length(s.seller_id::text) <= 4 THEN '090000' || lpad(s.seller_id::text, 4, '0')
        ELSE '090000' || right(s.seller_id::text, 4)
    END as phone,
    true as is_active,
    0.00 as rating
FROM sellers s;

-- Add new columns if they don't exist
DO $$ 
BEGIN
    -- Add shop_id if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'shop_id') THEN
        ALTER TABLE shops ADD COLUMN shop_id SERIAL PRIMARY KEY;
    END IF;

    -- Add other columns if they don't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'username') THEN
        ALTER TABLE shops ADD COLUMN username VARCHAR(50) UNIQUE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'password') THEN
        ALTER TABLE shops ADD COLUMN password VARCHAR(255);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'email') THEN
        ALTER TABLE shops ADD COLUMN email VARCHAR(100) UNIQUE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'shop_name') THEN
        ALTER TABLE shops ADD COLUMN shop_name VARCHAR(100);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'description') THEN
        ALTER TABLE shops ADD COLUMN description TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'logo_url') THEN
        ALTER TABLE shops ADD COLUMN logo_url VARCHAR(255);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'address') THEN
        ALTER TABLE shops ADD COLUMN address TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'phone') THEN
        ALTER TABLE shops ADD COLUMN phone VARCHAR(20);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'is_active') THEN
        ALTER TABLE shops ADD COLUMN is_active BOOLEAN DEFAULT true;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'rating') THEN
        ALTER TABLE shops ADD COLUMN rating DECIMAL(3,2);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'last_login') THEN
        ALTER TABLE shops ADD COLUMN last_login TIMESTAMP;
    END IF;
END $$;

-- Update existing records with generated values
UPDATE shops 
SET 
    username = COALESCE(username, 'shop_' || shop_id::text),
    password = COALESCE(password, crypt('shop' || shop_id::text, gen_salt('bf', 12))),
    email = COALESCE(email, 'shop' || shop_id::text || '@iuhecomerce.com'),
    shop_name = COALESCE(shop_name, 'Shop ' || shop_id::text),
    description = COALESCE(description, 'Welcome to Shop ' || shop_id::text),
    logo_url = COALESCE(logo_url, 'https://rubee.com.vn/wp-content/uploads/2021/05/Logo-IUH.jpg'),
    address = COALESCE(address, '123 Shop Street, City ' || shop_id::text),
    phone = COALESCE(phone, 
        CASE 
            WHEN length(shop_id::text) <= 4 THEN '090000' || lpad(shop_id::text, 4, '0')
            ELSE '090000' || right(shop_id::text, 4)
        END
    ),
    is_active = COALESCE(is_active, true),
    rating = COALESCE(rating, 0.00)
WHERE username IS NULL 
   OR password IS NULL 
   OR email IS NULL 
   OR shop_name IS NULL 
   OR description IS NULL 
   OR logo_url IS NULL 
   OR address IS NULL 
   OR phone IS NULL 
   OR is_active IS NULL 
   OR rating IS NULL;

-- Insert new shops if they don't exist
INSERT INTO shops (
    username, 
    password, 
    email, 
    shop_name, 
    description, 
    logo_url, 
    address, 
    phone, 
    is_active, 
    rating
)
SELECT 
    'shop_' || s.seller_id::text as username,
    crypt('shop' || s.seller_id::text, gen_salt('bf', 12)) as password,
    'shop' || s.seller_id::text || '@iuhecomerce.com' as email,
    COALESCE(s.seller_name, 'Shop ' || s.seller_id::text) as shop_name,
    'Welcome to Shop ' || s.seller_id::text as description,
    'https://rubee.com.vn/wp-content/uploads/2021/05/Logo-IUH.jpg' as logo_url,
    '123 Shop Street, City ' || s.seller_id::text as address,
    CASE 
        WHEN length(s.seller_id::text) <= 4 THEN '090000' || lpad(s.seller_id::text, 4, '0')
        ELSE '090000' || right(s.seller_id::text, 4)
    END as phone,
    true as is_active,
    0.00 as rating
FROM sellers s
LEFT JOIN shops sh ON s.seller_id = sh.shop_id
WHERE sh.shop_id IS NULL;

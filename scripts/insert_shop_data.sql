-- First, let's get the hashed password using pgcrypto extension
DROP EXTENSION IF EXISTS pgcrypto CASCADE;
CREATE EXTENSION pgcrypto;

-- Add new columns if they don't exist
DO $$ 
BEGIN
    -- Add shop_id if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'shop_id') THEN
        ALTER TABLE shops ADD COLUMN shop_id SERIAL PRIMARY KEY;
    END IF;

    -- Add other columns if they don't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'username') THEN
        ALTER TABLE shops ADD COLUMN username VARCHAR(255) UNIQUE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'password') THEN
        ALTER TABLE shops ADD COLUMN password VARCHAR(255);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'name') THEN
        ALTER TABLE shops ADD COLUMN name VARCHAR(255);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'mail') THEN
        ALTER TABLE shops ADD COLUMN mail VARCHAR(255);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'shops' AND column_name = 'phone') THEN
        ALTER TABLE shops ADD COLUMN phone VARCHAR(20);
    END IF;
END $$;

-- Update existing records with generated values
UPDATE shops 
SET 
    username = COALESCE(username, 'shop_' || seller_id::text),
    password = COALESCE(password, crypt(seller_id::text, gen_salt('bf'))),
    name = COALESCE(name, 'Shop ' || seller_id::text),
    mail = COALESCE(mail, 'shop' || seller_id::text || '@iuhecomerce.com'),
    phone = COALESCE(phone, 
        CASE 
            WHEN length(seller_id::text) <= 4 THEN '090000' || lpad(seller_id::text, 4, '0')
            ELSE '090000' || right(seller_id::text, 4)
        END
    )
WHERE username IS NULL OR password IS NULL OR name IS NULL OR mail IS NULL OR phone IS NULL;

-- Thêm các seller chưa có trong shops
INSERT INTO shops (seller_id, username, password, name, mail, phone)
SELECT 
    s.seller_id,
    'shop_' || s.seller_id::text as username,
    crypt(s.seller_id::text, gen_salt('bf')) as password,
    COALESCE(s.seller_name, 'Shop ' || s.seller_id::text) as name,
    'shop' || s.seller_id::text || '@iuhecomerce.com' as mail,
    CASE 
        WHEN length(s.seller_id::text) <= 4 THEN '090000' || lpad(s.seller_id::text, 4, '0')
        ELSE '090000' || right(s.seller_id::text, 4)
    END as phone
FROM sellers s
LEFT JOIN shops sh ON s.seller_id = sh.seller_id
WHERE sh.seller_id IS NULL;

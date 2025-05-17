-- First, let's get the hashed password using pgcrypto extension
DROP EXTENSION IF EXISTS pgcrypto CASCADE;
CREATE EXTENSION pgcrypto;

-- Clear existing data to avoid conflicts
TRUNCATE TABLE shops CASCADE;

-- Insert data for each seller with encrypted passwords
INSERT INTO shops (seller_id, username, password, name, mail, phone)
SELECT 
    s.seller_id,
    s.seller_id::text as username,
    crypt(s.seller_id::text, gen_salt('bf')) as password,
    COALESCE(s.seller_name, 'Shop ' || s.seller_id::text) as name,
    'shop' || s.seller_id::text || '@iuhecomerce.com' as mail,
    CASE 
        WHEN length(s.seller_id::text) <= 4 THEN '090000' || lpad(s.seller_id::text, 4, '0')
        ELSE '090000' || right(s.seller_id::text, 4)
    END as phone
FROM 
    sellers s
ON CONFLICT (seller_id) 
DO UPDATE SET 
    username = EXCLUDED.username,
    password = EXCLUDED.password,
    name = EXCLUDED.name,
    mail = EXCLUDED.mail,
    phone = EXCLUDED.phone;

CREATE TABLE [IF NOT EXISTS] sms_item (
   id serial PRIMARY KEY,
   sms_text VARCHAR ( 50 ) NOT NULL,
   sms_id INT UNIQUE NOT NULL,
   user_email VARCHAR( 50 ) NOT NULL,
   recipient_phone_number VARCHAR( 50 ) NOT NULL,
   sender_phone_number VARCHAR( 50 ) NOT NULL,
   sms_date DATE NOT NULL DEFAULT CURRENT_DATE
);
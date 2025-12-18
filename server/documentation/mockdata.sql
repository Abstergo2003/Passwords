-- 1. Create a Main User
INSERT INTO Users (id, email, passwordHash, tfaCode)
VALUES 
('user-01', 'radoslaw@example.com', 'hashed_secret_123', '987654');

-- 2. Create Passwords (Google & GitHub)
INSERT INTO Password (id, email, login, password, domain, tfa, favourite)
VALUES 
('pass-01', 'radoslaw@gmail.com', 'rad_korszla', 'secure_pass_1', 'google.com', 'secret_key_1', TRUE),
('pass-02', 'dev@github.com', 'Abstergo2003', 'secure_pass_2', 'github.com', 'secret_key_2', FALSE);

-- Link Passwords to User
INSERT INTO Password_User (Users_id, Password_id)
VALUES 
('user-01', 'pass-01'),
('user-01', 'pass-02');

-- 3. Create Notes
INSERT INTO Notes (id, name, content, favourite)
VALUES 
('note-01', 'Project Ideas', '1. Gravel biking app\n2. AI Personal Assistant', TRUE),
('note-02', 'Shopping List', 'Milk, Bread, RTX 4090', FALSE);

-- Link Notes to User
INSERT INTO User_Notes (Users_id, Notes_id)
VALUES 
('user-01', 'note-01'),
('user-01', 'note-02');

-- 4. Create Identity
INSERT INTO "Identity" (id, name, surname, IDnumber, country, state, city, street, number, favourite)
VALUES 
('id-01', 'Radosław', 'Korszla', 'WA12345', 'Poland', 'Masovian', 'Warsaw', 'Politechnika St', '10', TRUE);

-- Link Identity to User
INSERT INTO User_Identity (Users_id, Identity_id)
VALUES 
('user-01', 'id-01');

-- 5. Create Credit Card
INSERT INTO CreditCard (id, bankName, number, brand, cvv, owner, expDate, favourite)
VALUES 
('card-01', 'mBank', '1234-5678-9012-3456', 'Visa', '123', 'RADOSLAW KORSZLA', '12/28', TRUE);

-- Link Credit Card to User
INSERT INTO User_CreditCard (Users_id, CreditCard_id)
VALUES 
('user-01', 'card-01');

-- 6. Create License (using JSONB)
INSERT INTO License (id, name, diverse, favourite)
VALUES 
('lic-01', 'Driving License', '{"category": "B", "restrictions": "None", "issued_by": "Warsaw City Hall"}', TRUE);

-- Link License to User
INSERT INTO User_License (Users_id, License_id)
VALUES 
('user-01', 'lic-01');

-- 7. Create Attachments
INSERT INTO Attachment (id, name, content)
VALUES 
('att-01', 'scheme_draft.png', 'base64_encoded_string_representation_of_image'),
('att-02', 'contract.pdf', 'base64_encoded_string_representation_of_pdf');

-- Link Attachment 01 to the 'Project Ideas' Note
INSERT INTO Attachment_Notes (Notes_id, Attachment_id)
VALUES 
('note-01', 'att-01');

-- Link Attachment 02 to the Identity
INSERT INTO Identity_Attachment (Identity_id, Attachment_id)
VALUES 
('id-01', 'att-02');
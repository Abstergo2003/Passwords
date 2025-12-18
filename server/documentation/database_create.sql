-- Created by Redgate Data Modeler (https://datamodeler.redgate-platform.com)
-- Last modification date: 2025-12-18 10:44:31.542

-- tables
-- Table: Attachment
CREATE TABLE Attachment (
    id varchar(50)  NOT NULL,
    name varchar(50)  NOT NULL,
    content text  NOT NULL,
    CONSTRAINT Attachment_pk PRIMARY KEY (id)
);

-- Table: Attachment_Notes
CREATE TABLE Attachment_Notes (
    Attachment_id varchar(50)  NOT NULL,
    Notes_id varchar(50)  NOT NULL
);

-- Table: Attachment_Password
CREATE TABLE Attachment_Password (
    Password_id varchar(50)  NOT NULL,
    Attachment_id varchar(50)  NOT NULL
);

-- Table: CreditCard
CREATE TABLE CreditCard (
    id varchar(50)  NOT NULL,
    bankName text  NOT NULL,
    number text  NOT NULL,
    brand text  NOT NULL,
    cvv text  NOT NULL,
    owner text  NOT NULL,
    expDate text  NOT NULL,
    favourite boolean  NOT NULL,
    CONSTRAINT CreditCard_pk PRIMARY KEY (id)
);

-- Table: CreditCard_Attachment
CREATE TABLE CreditCard_Attachment (
    Attachment_id varchar(50)  NOT NULL,
    CreditCard_id varchar(50)  NOT NULL
);

-- Table: Identity
CREATE TABLE "Identity" (
    id varchar(50)  NOT NULL,
    name text  NOT NULL,
    surname text  NOT NULL,
    country text  NOT NULL,
    state text  NOT NULL,
    city text  NOT NULL,
    street text  NOT NULL,
    number text  NOT NULL,
    favourite boolean  NOT NULL,
    CONSTRAINT Identity_pk PRIMARY KEY (id)
);

-- Table: Identity_Attachment
CREATE TABLE Identity_Attachment (
    Identity_id varchar(50)  NOT NULL,
    Attachment_id varchar(50)  NOT NULL
);

-- Table: License
CREATE TABLE License (
    id varchar(50)  NOT NULL,
    name text  NOT NULL,
    diverse text  NOT NULL,
    favourite boolean  NOT NULL,
    CONSTRAINT License_pk PRIMARY KEY (id)
);

-- Table: License_Attachment
CREATE TABLE License_Attachment (
    License_id varchar(50)  NOT NULL,
    Attachment_id varchar(50)  NOT NULL
);

-- Table: Notes
CREATE TABLE Notes (
    id varchar(50)  NOT NULL,
    name text  NOT NULL,
    content text  NOT NULL,
    favourite boolean  NOT NULL,
    CONSTRAINT Notes_pk PRIMARY KEY (id)
);

-- Table: Password
CREATE TABLE Password (
    id varchar(50)  NOT NULL,
    email text  NOT NULL,
    login text  NOT NULL,
    password text  NOT NULL,
    domain text  NOT NULL,
    tfa text  NOT NULL,
    favourite boolean  NOT NULL,
    CONSTRAINT Password_pk PRIMARY KEY (id)
);

-- Table: Password_User
CREATE TABLE Password_User (
    Users_id varchar(37)  NOT NULL,
    Password_id varchar(50)  NOT NULL
);

-- Table: User_CreditCard
CREATE TABLE User_CreditCard (
    CreditCard_id varchar(50)  NOT NULL,
    Users_id varchar(37)  NOT NULL
);

-- Table: User_Identity
CREATE TABLE User_Identity (
    Identity_id varchar(50)  NOT NULL,
    Users_id varchar(37)  NOT NULL
);

-- Table: User_License
CREATE TABLE User_License (
    License_id varchar(50)  NOT NULL,
    Users_id varchar(37)  NOT NULL
);

-- Table: User_Notes
CREATE TABLE User_Notes (
    Notes_id varchar(50)  NOT NULL,
    Users_id varchar(37)  NOT NULL
);

-- Table: Users
CREATE TABLE Users (
    id varchar(37)  NOT NULL,
    email text  NOT NULL,
    passwordHash text  NOT NULL,
    tfaCode text  NOT NULL,
    salt text  NOT NULL,
    CONSTRAINT Users_pk PRIMARY KEY (id)
);

-- foreign keys
-- Reference: Attachment_Cipher_Attachment (table: Attachment_Password)
ALTER TABLE Attachment_Password ADD CONSTRAINT Attachment_Cipher_Attachment
    FOREIGN KEY (Attachment_id)
    REFERENCES Attachment (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Attachment_Cipher_Password (table: Attachment_Password)
ALTER TABLE Attachment_Password ADD CONSTRAINT Attachment_Cipher_Password
    FOREIGN KEY (Password_id)
    REFERENCES Password (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Attachment_Notes_Attachment (table: Attachment_Notes)
ALTER TABLE Attachment_Notes ADD CONSTRAINT Attachment_Notes_Attachment
    FOREIGN KEY (Attachment_id)
    REFERENCES Attachment (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Attachment_Notes_Notes (table: Attachment_Notes)
ALTER TABLE Attachment_Notes ADD CONSTRAINT Attachment_Notes_Notes
    FOREIGN KEY (Notes_id)
    REFERENCES Notes (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: CreditCard_Attachment_Attachment (table: CreditCard_Attachment)
ALTER TABLE CreditCard_Attachment ADD CONSTRAINT CreditCard_Attachment_Attachment
    FOREIGN KEY (Attachment_id)
    REFERENCES Attachment (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: CreditCard_Attachment_CreditCard (table: CreditCard_Attachment)
ALTER TABLE CreditCard_Attachment ADD CONSTRAINT CreditCard_Attachment_CreditCard
    FOREIGN KEY (CreditCard_id)
    REFERENCES CreditCard (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Identity_Attachment_Attachment (table: Identity_Attachment)
ALTER TABLE Identity_Attachment ADD CONSTRAINT Identity_Attachment_Attachment
    FOREIGN KEY (Attachment_id)
    REFERENCES Attachment (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Identity_Attachment_Identity (table: Identity_Attachment)
ALTER TABLE Identity_Attachment ADD CONSTRAINT Identity_Attachment_Identity
    FOREIGN KEY (Identity_id)
    REFERENCES "Identity" (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: License_Attachment_Attachment (table: License_Attachment)
ALTER TABLE License_Attachment ADD CONSTRAINT License_Attachment_Attachment
    FOREIGN KEY (Attachment_id)
    REFERENCES Attachment (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: License_Attachment_License (table: License_Attachment)
ALTER TABLE License_Attachment ADD CONSTRAINT License_Attachment_License
    FOREIGN KEY (License_id)
    REFERENCES License (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Password_User_Password (table: Password_User)
ALTER TABLE Password_User ADD CONSTRAINT Password_User_Password
    FOREIGN KEY (Password_id)
    REFERENCES Password (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: Password_User_Users (table: Password_User)
ALTER TABLE Password_User ADD CONSTRAINT Password_User_Users
    FOREIGN KEY (Users_id)
    REFERENCES Users (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: User_CreditCard_CreditCard (table: User_CreditCard)
ALTER TABLE User_CreditCard ADD CONSTRAINT User_CreditCard_CreditCard
    FOREIGN KEY (CreditCard_id)
    REFERENCES CreditCard (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: User_CreditCard_Users (table: User_CreditCard)
ALTER TABLE User_CreditCard ADD CONSTRAINT User_CreditCard_Users
    FOREIGN KEY (Users_id)
    REFERENCES Users (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: User_Identity_Identity (table: User_Identity)
ALTER TABLE User_Identity ADD CONSTRAINT User_Identity_Identity
    FOREIGN KEY (Identity_id)
    REFERENCES "Identity" (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: User_Identity_Users (table: User_Identity)
ALTER TABLE User_Identity ADD CONSTRAINT User_Identity_Users
    FOREIGN KEY (Users_id)
    REFERENCES Users (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: User_License_License (table: User_License)
ALTER TABLE User_License ADD CONSTRAINT User_License_License
    FOREIGN KEY (License_id)
    REFERENCES License (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: User_License_Users (table: User_License)
ALTER TABLE User_License ADD CONSTRAINT User_License_Users
    FOREIGN KEY (Users_id)
    REFERENCES Users (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: User_Notes_Notes (table: User_Notes)
ALTER TABLE User_Notes ADD CONSTRAINT User_Notes_Notes
    FOREIGN KEY (Notes_id)
    REFERENCES Notes (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- Reference: User_Notes_Users (table: User_Notes)
ALTER TABLE User_Notes ADD CONSTRAINT User_Notes_Users
    FOREIGN KEY (Users_id)
    REFERENCES Users (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

-- End of file.


-- scripts/init_db.sql
BEGIN;
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email VARCHAR(256) NOT NULL UNIQUE,
  hashed_password VARCHAR(512) NOT NULL,
  role VARCHAR(50) DEFAULT 'client',
  is_active BOOLEAN DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS clients (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER UNIQUE,
  company_name VARCHAR(256),
  contact_name VARCHAR(256),
  contact_phone VARCHAR(100),
  contact_email VARCHAR(256),
  status VARCHAR(50) DEFAULT 'pending',
  kyc_uploaded BOOLEAN DEFAULT 0,
  payment_verified BOOLEAN DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS files (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename TEXT NOT NULL,
  path TEXT NOT NULL,
  file_type VARCHAR(100),
  uploader_id INTEGER,
  uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(uploader_id) REFERENCES users(id)
);
COMMIT;


-- append to scripts/init_db.sql
CREATE TABLE IF NOT EXISTS refresh_tokens (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  token TEXT NOT NULL UNIQUE,
  user_id INTEGER NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  expires_at DATETIME NOT NULL,
  revoked BOOLEAN DEFAULT 0,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

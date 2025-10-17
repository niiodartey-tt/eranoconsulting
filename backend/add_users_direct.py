import psycopg2
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], default="argon2")

# Database connection
conn = psycopg2.connect(
    dbname="eranos_db",
    user="postgres",
    password="password",
    host="localhost"
)
cur = conn.cursor()

# Test users
users = [
    ("admin@eranoconsulting.com", "Admin123!", "Admin User", "admin"),
    ("consultant@eranoconsulting.com", "Consultant123!", "Sarah Johnson", "staff"),
    ("accountant@eranoconsulting.com", "Staff123!", "Michael Chen", "staff"),
    ("taxadvisor@eranoconsulting.com", "Staff123!", "Emily Davis", "staff"),
    ("client1@example.com", "Client123!", "John Doe", "client"),
    ("client2@example.com", "Client123!", "Jane Smith", "client"),
]

print("Creating test users...\n")

for email, password, name, role in users:
    # Check if exists
    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cur.fetchone():
        print(f"✓ User already exists: {email}")
        continue
    
    # Hash password
    hashed = pwd_context.hash(password)
    
    # Insert user
    cur.execute("""
        INSERT INTO users (email, hashed_password, full_name, role, is_active, is_verified, failed_login_attempts, created_at, updated_at)
        VALUES (%s, %s, %s, %s, true, true, 0, NOW(), NOW())
    """, (email, hashed, name, role))
    
    print(f"✓ Created: {email} ({role}) - {name}")

conn.commit()
cur.close()
conn.close()

print("\n" + "="*60)
print("✅ Test users created successfully!")
print("="*60)
print("\n🔑 LOGIN CREDENTIALS:\n")

for email, password, name, role in users:
    print(f"{name} ({role.upper()})")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print("-" * 60)

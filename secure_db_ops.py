import psycopg2
import hashlib
import os
import base64
from cryptography.fernet import Fernet # pip install cryptography

# ==========================================
# [보안 로직: 암호화 및 해싱 모듈]
# ==========================================
class SecurityVault:
    def __init__(self):
        # 데모용 키 생성 (실무에서는 환경변수나 KMS에서 관리 필수)
        # 매 실행마다 키가 바뀌므로 데모용으로만 사용
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def hash_password(self, password):
        """단방향 암호화: 비밀번호 저장용 (Salt + SHA256)"""
        salt = os.urandom(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return salt.hex() + ":" + pwd_hash.hex()

    def encrypt_data(self, data):
        """양방향 암호화: 주민번호, 계좌번호 등 저장용 (AES)"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt_data(self, token):
        """복호화: 데이터 조회용"""
        return self.cipher.decrypt(token.encode()).decode()

# ==========================================
# [DB 매니저: SQL Injection 방지 적용]
# ==========================================
def run_db_operations():
    # GitHub Actions Service Container 연결 정보
    conn = psycopg2.connect(
        host="localhost",
        database="testdb",
        user="postgres",
        password="password"
    )
    cur = conn.cursor()
    vault = SecurityVault()

    print("🔒 [Step 1] 보안 테이블 생성 (DDL)")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS secure_users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            password_hash VARCHAR(200) NOT NULL, -- 해시된 비번
            ssn_encrypted VARCHAR(200) NOT NULL, -- 암호화된 주민번호
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            log_id SERIAL PRIMARY KEY,
            action VARCHAR(100),
            ip_addr VARCHAR(20),
            access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    print("🛡️ [Step 2] 데이터 안전 삽입 (Secure Insert)")
    # SQL Injection 방지를 위해 %s 바인딩 변수 사용 (PreparedStatement)
    user_id = "admin_01"
    raw_pw = "my_secret_p@ssword"
    raw_ssn = "900101-1234567"

    hashed_pw = vault.hash_password(raw_pw)
    encrypted_ssn = vault.encrypt_data(raw_ssn)

    query = "INSERT INTO secure_users (username, password_hash, ssn_encrypted) VALUES (%s, %s, %s)"
    cur.execute(query, (user_id, hashed_pw, encrypted_ssn))
    
    # 감사 로그(Audit Log) 기록
    cur.execute("INSERT INTO access_logs (action, ip_addr) VALUES (%s, %s)", ("USER_REGISTRATION", "127.0.0.1"))

    print("🔍 [Step 3] 데이터 조회 및 복호화 (Query & Decrypt)")
    cur.execute("SELECT username, ssn_encrypted FROM secure_users WHERE username = %s", (user_id,))
    row = cur.fetchone()
    
    if row:
        decrypted_ssn = vault.decrypt_data(row[1])
        print(f"   -> 사용자: {row[0]}")
        print(f"   -> DB저장값(암호문): {row[1][:20]}...")
        print(f"   -> 복호화값(평문): {decrypted_ssn}")

    conn.commit()
    cur.close()
    conn.close()
    print("✅ 모든 보안 DB 작업 완료.")

if __name__ == "__main__":
    run_db_operations()

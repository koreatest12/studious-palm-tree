import os
import random
import datetime
import re

# ==========================================
# [정보보안기사 방대한 지식 베이스 (업그레이드됨)]
# ==========================================
KNOWLEDGE_BASE = {
    "시스템 보안": [
        {"topic": "리눅스 로그 파일 (utmp, wtmp, btmp)", "content": "utmp(현재 사용자), wtmp(로그인/아웃 이력, last), btmp(실패 이력, lastb). 로그 삭제 공격에 대비해 별도 서버 전송 필요."},
        {"topic": "SetUID/SetGID/StickyBit", "content": "SetUID(4000): 실행 시 소유자 권한. StickyBit(1000): 공용 디렉토리(/tmp)에서 삭제 제한."},
        {"topic": "버퍼 오버플로우 (Stack/Heap)", "content": "메모리 경계를 넘는 입력으로 RET 변조. 대응: ASLR, Stack Guard, NX-Bit."},
        {"topic": "레이스 컨디션 (Race Condition)", "content": "실행 순서/타이밍을 조작하여 권한 상승. 심볼릭 링크를 이용한 공격이 대표적. 대응: 임시파일 생성 시 랜덤 이름 사용."},
        {"topic": "윈도우 인증 구조 (LSA, SAM)", "content": "LSA: 보안 서브시스템 호출. SAM: 사용자/그룹 계정 정보 DB (해시 저장). NTLM/Kerberos 사용."},
        {"topic": "파일 시스템 (Inode, Superblock)", "content": "Superblock: 파일시스템 전체 정보. Inode: 파일 메타데이터(소유자, 권한, 크기, 위치). 파일명은 디렉토리 엔트리에 저장됨."}
    ],
    "네트워크 보안": [
        {"topic": "OSI 7계층과 보안 프로토콜", "content": "2계층(L2TP), 3계층(IPSec), 4계층(SSL/TLS), 7계층(S-HTTP, SSH)."},
        {"topic": "DoS/DDoS 공격 유형", "content": "Syn Flooding(Backlog Queue 고갈), Smurfing(ICMP 증폭), Slowloris(HTTP 헤더 지연)."},
        {"topic": "IPSec (AH vs ESP)", "content": "AH: 무결성+인증(암호화X). ESP: 기밀성+무결성+인증. 전송 모드(Payload만) vs 터널 모드(전체 패킷)."},
        {"topic": "방화벽 vs IDS vs IPS", "content": "방화벽: 접근 제어. IDS: 탐지(오탐/미탐 관리). IPS: 탐지 및 능동 차단."},
        {"topic": "VPN 기술 (SSL vs IPSec)", "content": "IPSec VPN: Site-to-Site 연결에 적합, 전용 SW 필요. SSL VPN: 웹 브라우저 이용, Client-to-Site 적합."},
        {"topic": "ARP Spoofing", "content": "공격자가 자신의 MAC을 게이트웨이 IP에 매핑하여 패킷 스니핑. 대응: 정적(Static) ARP 설정."}
    ],
    "어플리케이션 보안": [
        {"topic": "SQL Injection", "content": "입력값 검증 미흡으로 쿼리 조작. Union-based, Error-based, Blind SQLi. 대응: Prepared Statement."},
        {"topic": "XSS (Cross Site Scripting)", "content": "악성 스크립트 실행. Reflected(링크 클릭), Stored(게시글 저장). 대응: HTML Entity 치환, HttpOnly 쿠키."},
        {"topic": "CSRF (Cross Site Request Forgery)", "content": "사용자 권한으로 원치 않는 요청 실행. 대응: Referer 검증, CSRF Token 사용."},
        {"topic": "파일 업로드 취약점", "content": "Webshell 업로드로 서버 장악. 대응: 확장자 화이트리스트, 실행 권한 제거, 저장 경로 변경."},
        {"topic": "SSRF (Server Side Request Forgery)", "content": "서버가 내부망의 다른 시스템으로 요청을 보내도록 유도. 클라우드 메타데이터 탈취 등에 악용."},
        {"topic": "전자상거래 보안 (SET vs SSL)", "content": "SET: 이중 서명(Dual Signature)으로 상점에게 카드정보 숨김. 복잡해서 사장됨. 현재는 SSL/TLS+PG사 결제창 사용."}
    ],
    "정보보안 일반": [
        {"topic": "대칭키 vs 공개키 암호화", "content": "대칭키: 빠름, 키 배송 문제(AES, ARIA). 공개키: 느림, 키 배송 해결, 전자서명 가능(RSA, ECC)."},
        {"topic": "해시 함수와 무결성", "content": "단방향성, 충돌 회피성. SHA-256, HMAC(키+해시). 패스워드 저장(Salt 추가) 및 파일 위변조 검증에 사용."},
        {"topic": "접근 통제 모델 (DAC, MAC, RBAC)", "content": "DAC: 신원 기반(유연). MAC: 등급 기반(군사). RBAC: 역할 기반(기업)."},
        {"topic": "전자서명 (Digital Signature)", "content": "송신자 개인키 암호화 -> 수신자 공개키 복호화. 부인방지, 무결성, 인증 제공."},
        {"topic": "접근 통제 보안 원칙", "content": "Need-to-Know(알 필요성), Least Privilege(최소 권한), 직무 분리(Separation of Duty)."},
        {"topic": "키 분배 프로토콜 (Diffie-Hellman)", "content": "대칭키를 공유하지 않고도 공통의 비밀키를 생성하는 알고리즘. 중간자 공격(MITM)에 취약."}
    ],
    "정보보안 관리 및 법규": [
        {"topic": "ISMS-P 인증", "content": "관리체계(16개), 보호대책(64개), 개인정보(22개). 총 102개 인증 기준. 의무대상: 매출 100억/이용자 100만 등."},
        {"topic": "개인정보의 종류", "content": "일반정보, 고유식별정보(주민, 여권, 운전, 외국인), 민감정보(사상, 의료, 범죄). 별도 동의 필수."},
        {"topic": "개인정보 파기", "content": "목적 달성 시 지체 없이(5일 이내) 파기. 복구 불가능한 방법(소각, 디가우징, 덮어쓰기)."},
        {"topic": "재해 복구 시스템 (RTO/RPO)", "content": "RTO(목표 복구 시간), RPO(목표 복구 시점). Mirror(실시간, RTO=0) > Hot > Warm > Cold Site."},
        {"topic": "CC (Common Criteria)", "content": "정보보호 제품 평가 기준. PP(보호프로파일), ST(보안목표명세서), EAL(평가보증등급 1~7)."},
        {"topic": "PIA (개인정보 영향평가)", "content": "공공기관이 5만명(고유식별)/50만명(연계결과) 이상의 파일 구축 시 수행. 위험요인 사전 분석."}
    ]
}

def update_readme(today, category, topic):
    """README.md 파일을 읽어서 최신 학습 내용을 업데이트하는 함수"""
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        print("README.md not found. Skipping update.")
        return

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 오늘의 학습 주제 업데이트 (정규표현식 사용)
    # ... 사이를 교체
    daily_pattern = re.compile(r"()(.*?)()", re.DOTALL)
    new_daily_section = f"""\\1
## 🔥 오늘의 학습 주제
* **날짜**: {today}
* **과목**: {category}
* **주제**: {topic}
\\3"""
    content = daily_pattern.sub(new_daily_section, content)

    # 2. 학습 로그 테이블에 한 줄 추가
    # 바로 뒤에 새 행 추가
    log_pattern = re.compile(r"()(\s*\|.*\|)", re.DOTALL)
    # 기존 테이블 헤더가 있다고 가정하고, 그 아래에 추가하는 방식 대신 심플하게 LOG_START 아래에 추가
    # 테이블 구조: | 날짜 | 과목 | 주제 |
    new_log_entry = f"\n| {today} | {category} | {topic} |"
    
    # LOG_START 태그 바로 다음에 새 로그 삽입
    content = content.replace("", "" + new_log_entry)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("README.md updated successfully.")

def generate_daily_study():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 1. 랜덤 주제 선정
    category = random.choice(list(KNOWLEDGE_BASE.keys()))
    subject_data = random.choice(KNOWLEDGE_BASE[category])
    
    # 2. 마크다운 포스트 생성
    markdown_content = f"""---
title: "[정보보안기사] 오늘의 학습: {subject_data['topic']}"
date: {today}
categories: ["정보보안기사", "{category}"]
tags: ["Security", "Study", "{category}", "Certification"]
---

## 📅 날짜: {today}
## 📚 과목: {category}

---

### 💡 오늘의 핵심 주제: {subject_data['topic']}

#### 📝 핵심 요약
{subject_data['content']}

---

### 🚀 학습 팁
* **{subject_data['topic']}** 관련 기출문제를 반드시 풀어보세요.
* 위 요약 내용은 암기용 핵심 키워드입니다.

_Generated by Auto-Study Bot_
"""
    
    file_name = f"_posts/{today}-security-study.md"
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print(f"Generated Post: {file_name}")

    # 3. README 업데이트 호출
    update_readme(today, category, subject_data['topic'])

if __name__ == "__main__":
    generate_daily_study()

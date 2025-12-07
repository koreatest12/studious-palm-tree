import os
import random
import datetime

# ==========================================
# [정보보안기사 핵심 지식 베이스 (대량 데이터)]
# ==========================================
KNOWLEDGE_BASE = {
    "시스템 보안": [
        {
            "topic": "리눅스/유닉스 로그 파일",
            "content": """
- **utmp**: 현재 시스템에 로그인한 사용자 정보 (who 명령어로 확인)
- **wtmp**: 사용자의 로그인/로그아웃, 시스템 부팅/종료 이력 (last 명령어로 확인)
- **btmp**: 로그인 실패 기록 (lastb 명령어로 확인)
- **syslog**: 시스템 전반적인 메시지 기록 (/var/log/syslog 또는 /var/log/messages)
- **xferlog**: FTP 파일 전송 로그
            """
        },
        {
            "topic": "권한 관리 (chmod & chown)",
            "content": """
- **SetUID (4000)**: 실행 시 파일 소유자의 권한으로 실행 (보안 취약점 주의)
- **SetGID (2000)**: 실행 시 파일 그룹의 권한으로 실행
- **Sticky Bit (1000)**: /tmp 디렉토리 등에서 사용, 누구나 생성 가능하나 삭제는 소유자만 가능
- 예시: `chmod 4755 file` -> 소유자(rwx)+SetUID, 그룹(rx), 기타(rx)
            """
        },
        {
            "topic": "버퍼 오버플로우 (Buffer Overflow)",
            "content": """
- **개념**: 할당된 메모리 버퍼의 크기를 초과하여 데이터를 입력함으로써 프로세스 흐름을 조작.
- **스택(Stack) 버퍼 오버플로우**: 리턴 주소(RET)를 덮어씌워 공격자가 원하는 코드를 실행.
- **힙(Heap) 버퍼 오버플로우**: 힙 영역의 데이터나 함수 포인터를 조작.
- **대응**: ASLR(주소 무작위화), Stack Guard(Canary), Non-Executable Stack (NX bit).
            """
        }
    ],
    "네트워크 보안": [
        {
            "topic": "OSI 7 Layer & 보안 프로토콜",
            "content": """
1. **물리**: 탭핑, 도청 위협
2. **데이터링크**: MAC 스푸핑, ARP 스푸핑 / 대응: 정적 ARP, Port Security
3. **네트워크**: IP 스푸핑, 스니핑 / 보안: IPSec (AH: 무결성/인증, ESP: 기밀성 추가)
4. **전송**: TCP Syn Flooding / 보안: SSL/TLS
7. **응용**: HTTP Flooding / 보안: PGP, S/MIME, HTTPS
            """
        },
        {
            "topic": "DoS/DDoS 공격 유형",
            "content": """
- **Syn Flooding**: 3-way Handshake 취약점 이용, Syn만 대량 전송하여 Backlog Queue 고갈. (대응: Syncookie)
- **Smurfing**: ICMP Echo Request를 브로드캐스트 주소로 보내 피해자에게 응답 폭주 유도.
- **Land Attack**: 출발지 IP와 목적지 IP를 동일하게 설정하여 루프 발생 유도.
- **Slowloris**: HTTP 헤더를 비정상적으로 느리게 보내 연결 자원 고갈.
            """
        },
        {
            "topic": "방화벽(Firewall) 유형",
            "content": """
- **패킷 필터링**: IP, Port 기반 차단 (Layer 3-4). 속도 빠름, 로깅 빈약.
- **어플리케이션 게이트웨이**: Proxy 사용. Layer 7 검사 가능. 보안성 높으나 느림.
- **상태 기반 감시(Stateful Inspection)**: 세션 테이블을 유지하여 패킷의 문맥 파악.
- **DPI(Deep Packet Inspection)**: 패킷의 데이터 부분(Payload)까지 검사.
            """
        }
    ],
    "어플리케이션 보안": [
        {
            "topic": "OWASP Top 10 주요 취약점",
            "content": """
- **Injection (SQL, OS)**: 신뢰할 수 없는 데이터가 명령어나 쿼리의 일부로 보내질 때 발생.
- **Broken Authentication**: 인증 및 세션 관리 실패 (세션 하이재킹 등).
- **XSS (Cross Site Scripting)**: 웹 페이지에 악성 스크립트 삽입. (Reflected, Stored, DOM).
- **Insecure Deserialization**: 직렬화된 객체를 역직렬화할 때 악성 코드 실행.
            """
        },
        {
            "topic": "SQL Injection 상세",
            "content": """
- **Error-Based**: DB 에러 메시지를 통해 정보 획득.
- **Union-Based**: UNION 연산자를 이용해 다른 테이블 정보 조회.
- **Blind SQLi**: 참/거짓 반응(Boolean)이나 시간 지연(Time-based)을 통해 데이터 추론.
- **대응**: Prepared Statement 사용, 입력값 검증, 특수문자 치환.
            """
        },
        {
            "topic": "웹 보안 헤더",
            "content": """
- **HSTS**: HTTPS 접속 강제.
- **X-Frame-Options**: Clickjacking 방지 (iframe 제한).
- **X-XSS-Protection**: 브라우저의 내장 XSS 필터 활성화.
- **CSP (Content Security Policy)**: 허용된 소스에서만 스크립트 실행 허용.
            """
        }
    ],
    "정보보안 일반": [
        {
            "topic": "암호학 개요 (대칭키 vs 공개키)",
            "content": """
- **대칭키(Symmetric)**: 암호화키 = 복호화키. 속도 빠름. 키 배송 문제 발생. (AES, DES, SEED, ARIA)
- **공개키(Public Key)**: 암호화키 != 복호화키. 속도 느림. 키 배송 해결, 전자서명 가능. (RSA, ECC, ElGamal)
- **해시 함수**: 단방향 암호화. 무결성 검증. (SHA-256, MD5)
            """
        },
        {
            "topic": "접근 통제 모델 (Access Control)",
            "content": """
- **DAC (임의적 접근 통제)**: 소유자가 권한 결정 (Identity 기반). 유연하나 트로이 목마에 취약.
- **MAC (강제적 접근 통제)**: 보안 등급(Label)과 허가 등급(Clearance) 비교. 군사/기밀용 (BLP 모델).
- **RBAC (역할 기반 접근 통제)**: 사용자의 역할(Role)에 따라 권한 부여. 인사 이동 시 관리 용이.
            """
        },
        {
            "topic": "전자서명과 PKI",
            "content": """
- **기능**: 인증(Authentication), 무결성(Integrity), 부인방지(Non-repudiation).
- **절차**: 송신자의 개인키로 해시값을 암호화 -> 수신자는 송신자의 공개키로 복호화.
- **PKI 구성요소**: CA(인증기관), RA(등록기관), CRL(인증서 폐기 목록), Repository.
            """
        }
    ],
    "정보보안 관리 및 법규": [
        {
            "topic": "ISMS-P 인증 기준",
            "content": """
- **관리체계 수립 및 운영 (16개)**: 정책 수립, 경영진 참여, 위험 관리 등.
- **보호대책 요구사항 (64개)**: 인적 보안, 외부자 보안, 물리 보안, 암호화 등.
- **개인정보 처리 단계별 요구사항 (22개)**: 수집, 보유/이용, 제공, 파기 등.
- **의무 대상자**: ISP(정보통신망 서비스 제공자), 매출액 100억/일일 이용자 100만 이상 등.
            """
        },
        {
            "topic": "개인정보보호법 주요 내용",
            "content": """
- **개인정보**: 살아있는 개인을 식별할 수 있는 정보 (가명정보 포함).
- **고유식별정보**: 주민번호, 여권번호, 운전면허번호, 외국인등록번호. (별도 동의 또는 법령 근거 필요)
- **민감정보**: 사상, 신념, 건강, 범죄 경력 등.
- **안전성 확보 조치**: 내부관리계획, 접근통제, 암호화, 접속기록 보관(최소 1년/2년), 보안프로그램.
            """
        },
        {
            "topic": "재해 복구 시스템 (DRS) 유형",
            "content": """
- **Mirror Site**: 즉시 복구 (RTO=0), 실시간 동기화, 비용 최고.
- **Hot Site**: 수 시간 내 복구, 데이터 최신 상태 유지, 대기 상태 시스템.
- **Warm Site**: 수 일~수 주 내 복구, 주요 장비만 보유.
- **Cold Site**: 수 주~수 달 소요, 공간/전원만 확보, 비용 최저.
            """
        }
    ]
}

def generate_daily_study():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 1. 랜덤 주제 선정
    category = random.choice(list(KNOWLEDGE_BASE.keys()))
    subject_data = random.choice(KNOWLEDGE_BASE[category])
    
    # 2. 마크다운 파일 내용 생성
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
* 위 내용은 **정보보안기사 필기/실기** 시험에 자주 출제되는 핵심 키워드입니다.
* 관련된 용어를 추가로 검색하여 심화 학습을 진행하세요.
* 매일 생성되는 이 문서를 통해 꾸준히 복습하는 것이 합격의 지름길입니다!

_This document was automatically generated by GitHub Actions._
"""
    
    # 3. 파일 저장 (posts 디렉토리가 있다고 가정)
    file_name = f"_posts/{today}-security-study.md"
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print(f"Successfully generated: {file_name}")

if __name__ == "__main__":
    generate_daily_study()

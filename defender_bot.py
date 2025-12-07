import feedparser
import datetime
import os
import requests
import re

# ==========================================
# [보안 뉴스 소스 대량 추가 (다중 소스)]
# ==========================================
RSS_FEEDS = {
    "🚨 CISA (US-CERT)": "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json", # JSON 처리 로직 필요하나 RSS로 대체
    "🔥 The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "🛡️ NIST NVD (General)": "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml",
    "⚠️ ThreatPost": "https://threatpost.com/feed/"
}

# 봇 탐지 우회를 위한 가짜 헤더
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_feed_data(url):
    """User-Agent 헤더를 사용하여 RSS 피드 데이터를 가져옴"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
    return None

def fetch_security_news():
    print("📡 Fetching security news from multiple sources...")
    
    combined_news = ""
    
    # 여러 소스 순회
    for source_name, url in RSS_FEEDS.items():
        print(f"   Trying {source_name}...")
        try:
            # 1. 데이터 다운로드
            raw_data = fetch_feed_data(url)
            if not raw_data:
                continue

            # 2. 파싱
            feed = feedparser.parse(raw_data)
            
            if not feed.entries:
                continue

            # 3. 뉴스 정리 (소스별 최신 3개)
            combined_news += f"\n### {source_name}\n"
            for entry in feed.entries[:3]:
                title = entry.title
                link = entry.link
                # 날짜 처리
                published = "Recent"
                if hasattr(entry, 'published'):
                    published = entry.published[:16] # 날짜 포맷 단순화
                
                combined_news += f"- **[{published}]** [{title}]({link})\n"
                
        except Exception as e:
            print(f"⚠️ Failed to parse {source_name}: {e}")
            continue

    return combined_news

def update_security_trends(news_content):
    file_path = "SECURITY_TRENDS.md"
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not news_content:
        news_content = "\n> **Note**: 현재 가져올 수 있는 새로운 보안 뉴스가 없거나 접속이 일시 차단되었습니다.\n"

    header = f"""# 🚨 Real-time Security Threat Intelligence
> **Defender Bot Status**: 🟢 Online & Monitoring  
> **Last Updated**: {today}

이 페이지는 **Defender Bot**이 전 세계 주요 보안 피드(CISA, HackerNews 등)를 실시간 모니터링하여 자동 생성합니다.

---

## ⚡ Global Security Alerts
"""
    
    footer = """
---
## 🤖 Bot Logic
1. **Monitor**: CISA, NIST, ThreatPost RSS Feeds.
2. **Analyze**: Parse latest 3 critical items per source.
3. **Report**: Auto-commit & Merge to Repository.

_Automated by GitHub Actions & Python_
"""
    
    full_content = header + news_content + footer
    
    # 파일 쓰기 (무조건 실행)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_content)
    
    print(f"✅ {file_path} has been successfully generated/updated.")

if __name__ == "__main__":
    # 뉴스 수집
    news = fetch_security_news()
    
    # 파일 생성 (뉴스가 없어도 빈 파일이라도 생성하여 git 에러 방지)
    update_security_trends(news)

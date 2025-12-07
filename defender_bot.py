import feedparser # RSS 피드 파싱 라이브러리 (설치 필요)
import datetime
import os
import re

# 보안 뉴스 피드 (CISA, ThreatPost 등)
RSS_URL = "https://www.cisa.gov/uscert/ncas/current-activity/xml"

def fetch_security_news():
    print(f"📡 Fetching security news from {RSS_URL}...")
    feed = feedparser.parse(RSS_URL)
    
    news_items = []
    # 최신 5개 뉴스만 가져오기
    for entry in feed.entries[:5]:
        title = entry.title
        link = entry.link
        published = entry.published
        # 날짜 포맷 정리
        try:
            dt = datetime.datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %z")
            published = dt.strftime("%Y-%m-%d")
        except:
            pass
            
        news_items.append(f"- **[{published}]** [{title}]({link})")
    
    return "\n".join(news_items)

def update_security_trends(news_content):
    file_path = "SECURITY_TRENDS.md"
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    header = f"""# 🚨 Real-time Security Threat Intelligence
> **Defender Bot Status**: 🟢 Active  
> **Last Updated**: {today}

이 페이지는 디펜더 봇이 전 세계 보안 위협 정보를 실시간으로 수집하여 업데이트합니다.

---

## ⚡ 최신 보안 이슈 (CISA Alert)
"""
    
    footer = """
---
*Automated by Defender Bot 🤖*
"""
    
    full_content = header + news_content + footer
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_content)
    
    print("✅ SECURITY_TRENDS.md has been updated.")

def update_readme_status():
    """README에 봇의 마지막 활동 시간을 기록"""
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        return

    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # README에 뱃지나 상태가 있다면 업데이트 (없으면 생략)
    # 예시: 봇 상태 문구를 찾아서 교체
    if "Defender Bot Last Check:" in content:
        content = re.sub(r"Defender Bot Last Check: .*", f"Defender Bot Last Check: {today}", content)
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    news = fetch_security_news()
    if news:
        update_security_trends(news)
        update_readme_status()
    else:
        print("⚠️ No news fetched.")

import requests
import yaml
import os
import time
import random
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup

# ==========================================
# 1. 基础工具与配置
# ==========================================

def load_config():
    """加载项目根目录下的 config.yaml"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

def get_common_headers():
    """统一的请求头，模拟真实浏览器"""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Referer": "https://www.google.com/"
    }

def apply_rate_limit(min_sec=1.0, max_sec=3.0):
    """请求速率控制，防止封 IP"""
    time.sleep(random.uniform(min_sec, max_sec))

# ==========================================
# 2. API 数据源 (Football-Data.org & The Odds API)
# ==========================================

def fetch_football_data_api(endpoint, config):
    """封装 Football-Data.org API 调用"""
    api_key = config.get('api', {}).get('football_data', {}).get('key')
    if not api_key or "YOUR" in api_key:
        return {"error": "Football-Data API Key 未配置"}
    
    url = f"https://api.football-data.org/v4/{endpoint}"
    headers = {"X-Auth-Token": api_key}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def fetch_the_odds_api(config, home_team, away_team):
    """封装 The Odds API 赔率抓取"""
    api_key = config.get('api', {}).get('the_odds_api', {}).get('key')
    if not api_key or "YOUR" in api_key:
        return None
        
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/"
    params = {
        "apiKey": api_key,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        all_odds = response.json()
        
        # 模糊匹配对阵
        for match in all_odds:
            if (home_team.lower() in match['home_team'].lower() or match['home_team'].lower() in home_team.lower()) and \
               (away_team.lower() in match['away_team'].lower() or match['away_team'].lower() in away_team.lower()):
                return match.get('bookmakers', [])
        return None
    except:
        return None

# ==========================================
# 3. 网页抓取数据源 (Okooo, 500.com, OddsShark)
# ==========================================

def scrape_okooo(home_team, away_team):
    """澳客网抓取实现"""
    try:
        apply_rate_limit()
        url = "http://www.okooo.com/jingcai/"
        resp = requests.get(url, headers=get_common_headers(), timeout=15)
        if resp.status_code != 200: return None
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        for row in soup.select("tr.TrMatch"):
            text = row.get_text()
            if home_team.lower() in text.lower() or away_team.lower() in text.lower():
                odds = row.select("td.p_odds")
                if len(odds) >= 3:
                    return {
                        "source": "Okooo (澳客网)",
                        "odds": {"win": odds[0].text.strip(), "draw": odds[1].text.strip(), "loss": odds[2].text.strip()},
                        "url": url
                    }
        return None
    except: return None

def scrape_500com(home_team, away_team):
    """500.com 抓取实现"""
    try:
        apply_rate_limit()
        url = "https://live.500.com/2h1.shtml"
        resp = requests.get(url, headers=get_common_headers(), timeout=15)
        if resp.status_code != 200: return None
        
        content = resp.content.decode('gbk', 'ignore')
        soup = BeautifulSoup(content, 'html.parser')
        for row in soup.select("#table_match tr"):
            text = row.get_text()
            if home_team in text or away_team in text:
                nums = re.findall(r'\d+\.\d+', text)
                if len(nums) >= 3:
                    return {
                        "source": "500.com",
                        "odds": {"win": nums[0], "draw": nums[1], "loss": nums[2]},
                        "url": url
                    }
        return None
    except: return None

def scrape_oddsshark(home_team, away_team):
    """OddsShark 抓取实现"""
    try:
        apply_rate_limit()
        url = "https://www.oddsshark.com/soccer"
        resp = requests.get(url, headers=get_common_headers(), timeout=15)
        if resp.status_code != 200: return None
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        for match in soup.select(".match-row"):
            text = match.get_text().lower()
            if home_team.lower() in text or away_team.lower() in text:
                odds_vals = match.select(".odds-value")
                if len(odds_vals) >= 2:
                    return {
                        "source": "OddsShark",
                        "odds": {"home": odds_vals[0].text.strip(), "away": odds_vals[1].text.strip()},
                        "url": url
                    }
        return None
    except: return None

# ==========================================
# 4. 高层编排逻辑 (Orchestrators)
# ==========================================

def web_search_odds(home_team, away_team):
    """联网搜索赔率的统一入口 (Orchestrator)"""
    print(f"[*] 正在尝试联网抓取 {home_team} vs {away_team} 的实时赔率...")
    
    scrapers = [scrape_okooo, scrape_500com, scrape_oddsshark]
    for scraper in scrapers:
        result = scraper(home_team, away_team)
        if result:
            print(f"[+] 成功从 {result['source']} 获取数据")
            return result
            
    return {
        "status": "failed",
        "message": "未能自动抓取到有效赔率",
        "candidate_urls": ["http://www.okooo.com/jingcai/", "https://live.500.com/", "https://www.oddsshark.com/soccer"]
    }

def get_match_detail_data(match_id, config=None):
    """供其他脚本（如 analyzer.py）调用的详情获取函数，返回 dict"""
    if config is None:
        config = load_config()
        
    data = {"match_id": match_id}
    h2h_raw = fetch_football_data_api(f"matches/{match_id}/head2head", config)
    
    if "error" not in h2h_raw:
        agg = h2h_raw.get('aggregates', {})
        home_team = agg.get('homeTeam', {}).get('name', '')
        away_team = agg.get('awayTeam', {}).get('name', '')
        
        data.update({
            "home_team": home_team, "away_team": away_team,
            "h2h_aggregates": {
                "matches": agg.get('numberOfMatches'), "goals": agg.get('totalGoals'),
                "home_wins": agg.get('homeTeam', {}).get('wins'), "away_wins": agg.get('awayTeam', {}).get('wins'),
                "draws": agg.get('homeTeam', {}).get('draws')
            }
        })
        
        odds = fetch_the_odds_api(config, home_team, away_team)
        if not odds:
            odds = web_search_odds(home_team, away_team)
        data["realtime_odds"] = odds
        return data
    else:
        return {"match_id": match_id, "error": h2h_raw["error"]}

def fetch_data(match_id=None, odds_only=False):
    """主数据获取入口 (CLI Orchestrator)"""
    config = load_config()
    
    # 1. 列表模式
    if not match_id:
        raw_matches = fetch_football_data_api("matches", config)
        if "error" in raw_matches:
            print(json.dumps(raw_matches, ensure_ascii=False, indent=2))
            return
            
        matches = [{"id": m['id'], "league": m['competition']['name'], 
                    "home_team": m['homeTeam']['name'], "away_team": m['awayTeam']['name'],
                    "utcDate": m['utcDate'], "status": m['status']} 
                   for m in raw_matches.get('matches', [])]
        print(json.dumps({"date": datetime.now().strftime("%Y-%m-%d"), "matches": matches}, ensure_ascii=False, indent=2))
        return

    # 2. 详情模式
    data = get_match_detail_data(match_id, config)
    print(json.dumps(data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--match", help="指定 Match ID 获取详情，不传则列出今日赛事")
    parser.add_argument("--odds-only", action="store_true", help="仅获取赔率数据")
    args = parser.parse_args()
    
    fetch_data(match_id=args.match, odds_only=args.odds_only)

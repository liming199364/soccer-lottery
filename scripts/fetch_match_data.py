import requests
import yaml
import os
from datetime import datetime

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

def fetch_odds_from_the_odds_api(config, sport="soccer_epl"):
    """从 The Odds API 获取赔率数据"""
    api_key = config.get('the_odds_api_key', '')
    if not api_key:
        return {"matches": []}
    
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
    params = {
        "apiKey": api_key,
        "regions": "eu",
        "markets": "h2h,spreads",
        "oddsFormat": "decimal"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return parse_odds_api_response(response.json())
        else:
            return {"matches": []}
    except Exception as e:
        return {"matches": []}

def parse_odds_api_response(data):
    """解析 The Odds API 响应"""
    matches = []
    
    for event in data:
        home_team = event.get("home_team", "")
        away_team = event.get("away_team", "")
        commence_time = event.get("commence_time", "")
        
        if commence_time:
            dt = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
            match_date = dt.strftime("%m-%d")
            # 转换为北京时间 (UTC+8)
            match_time = (dt + datetime.timedelta(hours=8)).strftime("%H:%M")
        else:
            match_date = ""
            match_time = ""
        
        bookmakers_data = []
        for bookmaker in event.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market.get("key") == "h2h":
                    h2h_odds = {}
                    for outcome in market.get("outcomes", []):
                        name = outcome.get("name", "")
                        price = outcome.get("price", 0)
                        if name == home_team:
                            h2h_odds["home_odds"] = price
                        elif name == away_team:
                            h2h_odds["away_odds"] = price
                        else:
                            h2h_odds["draw_odds"] = price
                    
                    bookmakers_data.append({
                        **h2h_odds,
                        "handicap": None,
                        "home_handicap_odds": 0,
                        "away_handicap_odds": 0
                    })
                elif market.get("key") == "spreads":
                    for outcome in market.get("outcomes", []):
                        point = outcome.get("point", 0)
                        price = outcome.get("price", 0)
                        if point != 0:
                            if bookmakers_data:
                                bookmakers_data[-1]["handicap"] = point
                                if outcome.get("name") == home_team:
                                    bookmakers_data[-1]["home_handicap_odds"] = price
                                else:
                                    bookmakers_data[-1]["away_handicap_odds"] = price
        
        matches.append({
            "home_team": home_team,
            "away_team": away_team,
            "match_date": match_date,
            "match_time": match_time,
            "bookmakers": bookmakers_data,
            "league_name": get_league_name(sport),
            "league_code": sport
        })
    
    return {"matches": matches}

def get_league_name(sport_key):
    """根据 sport_key 获取联赛中文名"""
    league_map = {
        "soccer_epl": "英超",
        "soccer_la_liga": "西甲",
        "soccer_bundesliga": "德甲",
        "soccer_serie_a": "意甲",
        "soccer_ligue_1": "法甲",
        "soccer_eredivisie": "荷甲",
        "soccer_portugal_primeira_liga": "葡超",
        "soccer_russia_premier_league": "俄超",
        "soccer_scotland_premiership": "苏超",
        "soccer_belgium_pro_league": "比甲",
        "soccer_sweden_allsvenskan": "瑞超",
        "soccer_norwegian_eliteserien": "挪超",
        "soccer_champions_league": "欧冠",
        "soccer_europa_league": "欧联"
    }
    return league_map.get(sport_key, "未知")

def fetch_match_details(match_id, config):
    """获取比赛详情（用于 H2H 分析）"""
    # 模拟 H2H 数据
    return {
        "aggregates": {
            "homeTeam": {"name": "Team A", "wins": 10, "draws": 5},
            "awayTeam": {"name": "Team B", "wins": 8, "draws": 5},
            "numberOfMatches": 25
        }
    }

def fetch_backup_soccer_data():
    """从备用网页数据源获取足球比赛数据（包含国内足彩覆盖的所有联赛）"""
    from bs4 import BeautifulSoup
    
    backup_data = []
    
    # ===== 国内足彩覆盖的所有联赛 =====
    sources = [
        # 英超
        {"name": "Flashscore", "url": "https://www.flashscore.com/football/england/premier-league/", "league": "英超"},
        {"name": "Betexplorer", "url": "https://www.betexplorer.com/football/england/premier-league/", "league": "英超"},
        # 西甲
        {"name": "Flashscore", "url": "https://www.flashscore.com/football/spain/laliga/", "league": "西甲"},
        {"name": "Betexplorer", "url": "https://www.betexplorer.com/football/spain/la-liga/", "league": "西甲"},
        # 意甲
        {"name": "Flashscore", "url": "https://www.flashscore.com/football/italy/serie-a/", "league": "意甲"},
        {"name": "Betexplorer", "url": "https://www.betexplorer.com/football/italy/serie-a/", "league": "意甲"},
        # 德甲
        {"name": "Flashscore", "url": "https://www.flashscore.com/football/germany/bundesliga/", "league": "德甲"},
        {"name": "Betexplorer", "url": "https://www.betexplorer.com/football/germany/bundesliga/", "league": "德甲"},
        # 法甲
        {"name": "Flashscore", "url": "https://www.flashscore.com/football/france/ligue-1/", "league": "法甲"},
        {"name": "Betexplorer", "url": "https://www.betexplorer.com/football/france/ligue-1/", "league": "法甲"},
        # 荷甲
        {"name": "Flashscore", "url": "https://www.flashscore.com/football/netherlands/eredivisie/", "league": "荷甲"},
        {"name": "Betexplorer", "url": "https://www.betexplorer.com/football/netherlands/eredivisie/", "league": "荷甲"},
        # 葡超
        {"name": "Flashscore", "url": "https://www.flashscore.com/football/portugal/primeira-liga/", "league": "葡超"},
        {"name": "Betexplorer", "url": "https://www.betexplorer.com/football/portugal/primeira-liga/", "league": "葡超"},
        # 俄超
        {"name": "Flashscore", "url": "https://www.flashscore.com/football/russia/premier-league/", "league": "俄超"},
        {"name": "Betexplorer", "url": "https://www.betexplorer.com/football/russia/premier-league/", "league": "俄超"},
        # 苏超
        {"name": "Flashscore", "url": "https://www.flashscore.com/football/scotland/premiership/", "league": "苏超"},
        {"name": "Betexplorer", "url": "https://www.betexplorer.com/football/scotland/premiership/", "league": "苏超"},
        # 比甲
        {"name": "Flashscore", "url": "https://www.flashscore.com/football/belgium/pro-league/", "league": "比甲"},
        {"name": "Betexplorer", "url": "https://www.betexplorer.com/football/belgium/pro-league/", "league": "比甲"},
        # 瑞超
        {"name": "Flashscore", "url": "https://www.flashscore.com/football/sweden/allsvenskan/", "league": "瑞超"},
        {"name": "Betexplorer", "url": "https://www.betexplorer.com/football/sweden/allsvenskan/", "league": "瑞超"},
        # 挪超
        {"name": "Flashscore", "url": "https://www.flashscore.com/football/norway/eliteserien/", "league": "挪超"},
        {"name": "Betexplorer", "url": "https://www.betexplorer.com/football/norway/eliteserien/", "league": "挪超"},
        # 欧冠
        {"name": "Flashscore", "url": "https://www.flashscore.com/football/europe/champions-league/", "league": "欧冠"},
        {"name": "Betexplorer", "url": "https://www.betexplorer.com/football/europe/champions-league/", "league": "欧冠"},
        # 欧联
        {"name": "Flashscore", "url": "https://www.flashscore.com/football/europe/europa-league/", "league": "欧联"},
        {"name": "Betexplorer", "url": "https://www.betexplorer.com/football/europe/europa-league/", "league": "欧联"}
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    for source in sources:
        try:
            response = requests.get(source["url"], headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 尝试解析页面获取比赛数据
                matches = parse_flashscore_page(soup, source["league"])
                backup_data.extend(matches)
        except Exception as e:
            continue
    
    return backup_data

def parse_flashscore_page(soup, league):
    """解析 Flashscore 页面获取比赛数据"""
    matches = []
    
    # 尝试多种解析方式
    match_rows = soup.find_all('div', class_=['event__match', 'match-row'])
    
    for row in match_rows:
        try:
            home_team = row.find('div', class_=['event__participant--home', 'team-home'])
            away_team = row.find('div', class_=['event__participant--away', 'team-away'])
            match_time = row.find('div', class_=['event__time', 'match-time'])
            
            if home_team and away_team:
                matches.append({
                    "home_team": home_team.get_text(strip=True),
                    "away_team": away_team.get_text(strip=True),
                    "league_name": league,
                    "match_time": match_time.get_text(strip=True) if match_time else "",
                    "bookmakers": []
                })
        except:
            continue
    
    return matches

def get_all_leagues():
    """获取所有支持的联赛列表"""
    return [
        {"code": "soccer_epl", "name": "英超"},
        {"code": "soccer_la_liga", "name": "西甲"},
        {"code": "soccer_bundesliga", "name": "德甲"},
        {"code": "soccer_serie_a", "name": "意甲"},
        {"code": "soccer_ligue_1", "name": "法甲"},
        {"code": "soccer_eredivisie", "name": "荷甲"},
        {"code": "soccer_portugal_primeira_liga", "name": "葡超"},
        {"code": "soccer_russia_premier_league", "name": "俄超"},
        {"code": "soccer_scotland_premiership", "name": "苏超"},
        {"code": "soccer_belgium_pro_league", "name": "比甲"},
        {"code": "soccer_sweden_allsvenskan", "name": "瑞超"},
        {"code": "soccer_norwegian_eliteserien", "name": "挪超"},
        {"code": "soccer_champions_league", "name": "欧冠"},
        {"code": "soccer_europa_league", "name": "欧联"}
    ]

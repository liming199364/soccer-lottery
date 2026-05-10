import argparse
import json
import yaml
import os
import requests
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return None

def get_headers(config):
    headers = {}
    if config and 'api' in config and 'football_data' in config['api']:
        api_key = config['api']['football_data'].get('key')
        if api_key and api_key != "YOUR_API_KEY_HERE":
            headers['X-Auth-Token'] = api_key
    return headers

def get_the_odds_api_key(config):
    """获取 The Odds API 的 API Key"""
    if config and 'api' in config and 'the_odds_api' in config['api']:
        api_key = config['api']['the_odds_api'].get('key')
        if api_key and api_key != "YOUR_THE_ODDS_API_KEY_HERE":
            return api_key
    return None

def fetch_odds_from_the_odds_api(config, sport="soccer_epl", region="eu", markets="h2h,spreads"):
    """从 The Odds API 获取赔率数据"""
    api_key = get_the_odds_api_key(config)
    
    if not api_key:
        return {"error": "The Odds API Key not configured. Please check config.yaml."}
    
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
    
    params = {
        'apiKey': api_key,
        'regions': region,
        'markets': markets,
        'oddsFormat': 'decimal',
        'dateFormat': 'iso'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        sport_code_map = {
            "soccer_epl": "英超",
            "soccer_la_liga": "西甲",
            "soccer_bundesliga": "德甲",
            "soccer_serie_a": "意甲",
            "soccer_ligue_1": "法甲"
        }
        
        sport_code_mapper = {
            "soccer_epl": "PL",
            "soccer_la_liga": "PD",
            "soccer_bundesliga": "BL1",
            "soccer_serie_a": "SA",
            "soccer_ligue_1": "FL1"
        }
        
        matches = []
        for idx, match in enumerate(data):
            commence_time = match.get('commence_time', '')
            if commence_time:
                try:
                    utc_time = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
                    beijing_time = utc_time + timedelta(hours=8)
                    match_time = beijing_time.strftime("%H:%M")
                    match_date = beijing_time.strftime("%m-%d")
                except:
                    match_time = "未知"
                    match_date = "未知"
            else:
                match_time = "未知"
                match_date = "未知"
            
            sport_key = match.get('sport_key', '')
            league_code = sport_code_mapper.get(sport_key, sport_key.upper())
            league_name = sport_code_map.get(sport_key, sport_key)
            
            match_data = {
                "home_team": match.get('home_team'),
                "away_team": match.get('away_team'),
                "commence_time": commence_time,
                "match_time": match_time,
                "match_date": match_date,
                "sport_key": sport_key,
                "league_code": league_code,
                "league_name": league_name,
                "bookmakers": []
            }
            
            for bookmaker in match.get('bookmakers', []):
                bookmaker_odds = {
                    "bookmaker": bookmaker.get('title'),
                    "home_odds": 0,
                    "draw_odds": 0,
                    "away_odds": 0,
                    "handicap": None,
                    "home_handicap_odds": 0,
                    "away_handicap_odds": 0
                }
                
                for market in bookmaker.get('markets', []):
                    if market.get('key') == 'h2h':
                        outcomes = market.get('outcomes', [])
                        for outcome in outcomes:
                            if outcome.get('name') == match.get('home_team'):
                                bookmaker_odds["home_odds"] = outcome.get('price')
                            elif outcome.get('name') == match.get('away_team'):
                                bookmaker_odds["away_odds"] = outcome.get('price')
                            else:
                                bookmaker_odds["draw_odds"] = outcome.get('price')
                    
                    elif market.get('key') == 'spreads':
                        outcomes = market.get('outcomes', [])
                        for outcome in outcomes:
                            if outcome.get('name') == match.get('home_team'):
                                bookmaker_odds["handicap"] = outcome.get('point')
                                bookmaker_odds["home_handicap_odds"] = outcome.get('price')
                            elif outcome.get('name') == match.get('away_team'):
                                bookmaker_odds["away_handicap_odds"] = outcome.get('price')
                
                match_data["bookmakers"].append(bookmaker_odds)
            
            matches.append(match_data)
        
        return {
            "source": "The Odds API",
            "sport": sport,
            "region": region,
            "matches": matches,
            "remaining_requests": response.headers.get('X-Requests-Remaining')
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Data parsing failed: {str(e)}"}

def fetch_all_soccer_odds(config):
    """获取多个足球联赛的赔率"""
    sports = [
        "soccer_epl",           # 英超
        "soccer_efl_champ",     # 英冠
        "soccer_la_liga",       # 西甲
        "soccer_serie_a",       # 意甲
        "soccer_bundesliga",    # 德甲
        "soccer_ligue_1",       # 法甲
        "soccer_champions_league"  # 欧冠
    ]
    
    all_odds = []
    for sport in sports:
        result = fetch_odds_from_the_odds_api(config, sport=sport)
        if "matches" in result:
            all_odds.extend(result["matches"])
    
    return {"matches": all_odds}

def get_sport_key(league_name):
    """将联赛名称转换为 The Odds API 的 sport_key"""
    league_map = {
        "premier-league": "soccer_epl",
        "epl": "soccer_epl",
        "england": "soccer_epl",
        "la-liga": "soccer_la_liga",
        "laliga": "soccer_la_liga",
        "spain": "soccer_la_liga",
        "serie-a": "soccer_serie_a",
        "italy": "soccer_serie_a",
        "bundesliga": "soccer_bundesliga",
        "germany": "soccer_bundesliga",
        "ligue-1": "soccer_ligue_1",
        "france": "soccer_ligue_1",
        "champions-league": "soccer_champions_league",
        "ucl": "soccer_champions_league",
        "europa": "soccer_europa_league"
    }
    return league_map.get(league_name.lower(), "soccer_epl")

def fetch_today_matches(config):
    headers = get_headers(config)
    if not headers:
        return {"error": "API Key not configured. Please check config.yaml."}
        
    url = "https://api.football-data.org/v4/matches"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # 过滤出配置的联赛
        target_leagues = config.get('settings', {}).get('leagues', ["PL", "PD", "BL1", "SA", "FL1", "CL"])
        filtered_matches = []
        
        for match in data.get('matches', []):
            if match.get('competition', {}).get('code') in target_leagues:
                filtered_matches.append({
                    "id": match['id'],
                    "league": match['competition']['name'],
                    "home_team": match['homeTeam']['name'],
                    "away_team": match['awayTeam']['name'],
                    "utcDate": match['utcDate'],
                    "status": match['status']
                })
        return {"date": datetime.now().strftime("%Y-%m-%d"), "matches": filtered_matches}
    except Exception as e:
        return {"error": str(e)}

def fetch_match_details(match_id, config):
    headers = get_headers(config)
    if not headers:
        return {"error": "API Key not configured"}
        
    # 获取比赛详情和H2H
    url = f"https://api.football-data.org/v4/matches/{match_id}/head2head"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def fetch_oddsportal_odds(league="premier-league"):
    """从 OddsPortal 抓取赔率数据"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.oddsportal.com/'
    }
    
    # OddsPortal 足球赛事页面
    url = f"https://www.oddsportal.com/soccer/england/{league}/"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找比赛列表
        matches = []
        match_rows = soup.find_all('tr', class_=['deactivate', 'odd', 'even'])
        
        for row in match_rows:
            # 跳过表头
            if 'header' in row.get('class', []):
                continue
                
            match_data = {}
            
            # 获取比赛时间
            time_cell = row.find('td', class_='time')
            if time_cell:
                match_data['time'] = time_cell.get_text(strip=True)
            
            # 获取比赛队伍
            teams_cell = row.find('td', class_='name table-participant')
            if teams_cell:
                teams = teams_cell.get_text(strip=True).split(' - ')
                if len(teams) == 2:
                    match_data['home_team'] = teams[0]
                    match_data['away_team'] = teams[1]
            
            # 获取赔率数据
            odds_cells = row.find_all('td', class_=['odds-nowrp'])
            if len(odds_cells) >= 3:
                match_data['odds'] = {
                    'home': odds_cells[0].get_text(strip=True),
                    'draw': odds_cells[1].get_text(strip=True),
                    'away': odds_cells[2].get_text(strip=True)
                }
            
            if match_data.get('home_team') and match_data.get('away_team'):
                matches.append(match_data)
            
            # 添加请求间隔，避免被封
            time.sleep(1)
        
        return {"league": league, "matches": matches}
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Parsing error: {str(e)}"}

def search_oddsportal_match(home_team, away_team):
    """搜索特定比赛的赔率"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # 构建搜索URL
    search_url = f"https://www.oddsportal.com/search/{home_team.replace(' ', '-').lower()}-{away_team.replace(' ', '-').lower()}/"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找搜索结果中的比赛链接
        result_links = soup.find_all('a', href=True)
        for link in result_links:
            if '/soccer/' in link['href'] and ('result' not in link['href'] or 'preview' in link['href']):
                # 获取比赛详情
                match_url = f"https://www.oddsportal.com{link['href']}"
                match_response = requests.get(match_url, headers=headers, timeout=30)
                match_soup = BeautifulSoup(match_response.text, 'html.parser')
                
                # 提取赔率数据
                odds_data = extract_odds_from_page(match_soup)
                return odds_data
        
        return {"error": "Match not found on OddsPortal"}
        
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}

def extract_odds_from_page(soup):
    """从比赛页面提取赔率数据"""
    odds_data = {}
    
    # 获取比赛信息
    title = soup.find('h1')
    if title:
        odds_data['match_title'] = title.get_text(strip=True)
    
    # 提取欧洲赔率
    eu_odds = soup.find('table', class_='table-main detail-odds sortable')
    if eu_odds:
        rows = eu_odds.find_all('tr')
        bookmakers = []
        for row in rows[1:]:  # 跳过表头
            cols = row.find_all('td')
            if len(cols) >= 5:
                bookmaker = {
                    'name': cols[0].get_text(strip=True),
                    'home': cols[1].get_text(strip=True),
                    'draw': cols[2].get_text(strip=True),
                    'away': cols[3].get_text(strip=True)
                }
                bookmakers.append(bookmaker)
        odds_data['european_odds'] = bookmakers
    
    # 提取亚洲盘口（如果有）
    asian_section = soup.find('div', {'id': 'odds-data-table'})
    if asian_section:
        asian_odds = []
        # 尝试查找亚洲盘口表格
        for table in asian_section.find_all('table', class_='table-main'):
            # 检查是否是亚洲盘
            caption = table.find('caption')
            if caption and 'Asian' in caption.get_text():
                rows = table.find_all('tr')
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= 5:
                        asian_odds.append({
                            'bookmaker': cols[0].get_text(strip=True),
                            'handicap': cols[1].get_text(strip=True),
                            'home_odds': cols[2].get_text(strip=True),
                            'away_odds': cols[4].get_text(strip=True)
                        })
        if asian_odds:
            odds_data['asian_odds'] = asian_odds
    
    return odds_data

def fetch_data(match_id=None, odds_only=False, injuries_only=False, league=None):
    config = load_config()
    
    # 如果没有提供 match_id 且需要赔率数据，使用 The Odds API
    if not match_id and odds_only:
        # 默认抓取英超赔率
        sport_key = get_sport_key(league) if league else "soccer_epl"
        result = fetch_odds_from_the_odds_api(config, sport=sport_key)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    
    # 如果没有提供 match_id，则获取今日热门赛事
    if not match_id:
        result = fetch_today_matches(config)
        # 同时尝试从 The Odds API 获取赔率
        try:
            odds_result = fetch_odds_from_the_odds_api(config, sport="soccer_epl")
            if "matches" in odds_result:
                result["odds"] = odds_result["matches"]
                result["odds_source"] = "The Odds API"
                result["remaining_requests"] = odds_result.get("remaining_requests")
        except Exception as e:
            pass
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 如果提供了 match_id，获取特定比赛的详细信息
    data = {"match_id": match_id}
    
    # 从 football-data.org 获取真实数据 (H2H和近期战绩)
    h2h_data = fetch_match_details(match_id, config)
    
    if odds_only:
        # 使用 The Odds API 获取赔率数据
        data["odds_source"] = "The Odds API"
        data["odds"] = fetch_odds_from_the_odds_api(config, sport="soccer_epl")
        
    elif injuries_only:
        data["injuries"] = {"error": "Injuries data requires RapidAPI integration. Not fully implemented in basic tier."}
    else:
        # 组装基础信息和H2H
        if "error" not in h2h_data:
            match_info = h2h_data.get('aggregates', {})
            data["h2h_aggregates"] = {
                "numberOfMatches": match_info.get('numberOfMatches'),
                "totalGoals": match_info.get('totalGoals'),
                "homeTeamWins": match_info.get('homeTeam', {}).get('wins'),
                "awayTeamWins": match_info.get('awayTeam', {}).get('wins'),
                "draws": match_info.get('homeTeam', {}).get('draws')
            }
            
            # 提取最近的交锋记录
            recent_matches = []
            for m in h2h_data.get('matches', [])[:5]:
                recent_matches.append({
                    "date": m.get('utcDate'),
                    "home": m.get('homeTeam', {}).get('name'),
                    "away": m.get('awayTeam', {}).get('name'),
                    "score": f"{m.get('score', {}).get('fullTime', {}).get('home', '?')}-{m.get('score', {}).get('fullTime', {}).get('away', '?')}"
                })
            data["recent_h2h"] = recent_matches
        else:
            data["h2h_error"] = h2h_data["error"]
            
        # 尝试从 OddsPortal 获取赔率
        data["odds_source"] = "OddsPortal"
        data["odds"] = {"status": "Fetching from OddsPortal..."}
        
    print(json.dumps(data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match", required=False, help="Match ID")
    parser.add_argument("--odds-only", action="store_true", help="Fetch only odds data")
    parser.add_argument("--injuries-only", action="store_true", help="Fetch only injuries data")
    parser.add_argument("--league", required=False, help="League name for odds (e.g., premier-league, la-liga, bundesliga)")
    args = parser.parse_args()
    
    fetch_data(args.match, args.odds_only, args.injuries_only, args.league)

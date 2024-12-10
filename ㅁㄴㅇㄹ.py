import random
import requests
import pprint
import time
import csv
import os

# API Key and Base URL configuration
API_KEY = "Api 키를 입력하세요"
BASE_URL = "https://open-api.bser.io/v1"
HEADERS = {"x-api-key": API_KEY}

# 글로벌 데이터
global_combination_data = {}
processed_game_ids = set()  # 이미 처리된 게임 ID 추적용

# Character mapping
CHARACTER_MAP = {
    1: "재키", 2: "아야", 3: "피오라", 4: "매그너스", 5: "자히르", 6: "나딘", 7: "현우", 8: "하트", 
    9: "아이솔", 10: "리다이린", 11: "유키", 12: "혜진", 13: "쇼우", 14: "키아라", 15: "시셀라", 
    16: "실비아", 17: "아드리아나", 18: "쇼이치", 19: "엠마", 20: "레녹스", 21: "로지", 22: "루크", 
    23: "캐시", 24: "아델라", 25: "버니스", 26: "바바라", 27: "알렉스", 28: "수아", 29: "레온", 
    30: "일레븐", 31: "리오", 32: "윌리엄", 33: "니키", 34: "나타폰", 35: "얀", 36: "이바", 
    37: "다니엘", 38: "제니", 39: "카밀로", 40: "클로에", 41: "요한", 42: "비앙카", 43: "셀린", 
    44: "에키온", 45: "마이", 46: "에이든", 47: "라우라", 48: "띠아", 49: "펠릭스", 50: "엘레나", 
    51: "프리야", 52: "아디나", 53: "마커스", 54: "칼라", 55: "에스텔", 56: "피올로", 57: "마르티나", 
    58: "헤이즈", 59: "아이작", 60: "타지아", 61: "이렘", 62: "테오도르", 63: "이안", 64: "바냐", 
    65: "데비와 마를렌", 66: "아르다", 67: "아비게일", 68: "알론소", 69: "레니", 70: "츠바메", 
    71: "케네스", 72: "카티야", 73: "샬럿", 74: "다르코", 75: "르노어", 76: "가넷", 77: "유민"
}

def get_users_in_tier():
    url = f"{BASE_URL}/rank/top/27/3"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return [user["userNum"] for user in data["topRanks"]]

def get_recent_matches(user_num, max_matches=200):
    url = f"{BASE_URL}/user/games/{user_num}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    matches = data["userGames"]

    while len(matches) < max_matches and "next" in data:
        next_url = f"{url}?next={data['next']}"
        response = requests.get(next_url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        matches.extend(data["userGames"])

    return matches[:max_matches]

def get_game_detail(gameid):
    global processed_game_ids

    if gameid in processed_game_ids:
        print(f"게임 {gameid}은 이미 처리되었습니다. 건너뜁니다.")
        return None

    url = f"{BASE_URL}/games/{gameid}"
    delay = 1
    while True:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 429:
            print(f"429 Too Many Requests. {delay}초 대기 중...")
            time.sleep(delay)
            delay = min(delay * 2, 10)
            continue
        response.raise_for_status()
        processed_game_ids.add(gameid)
        return response.json()

def calculate_team_scores(match_record):
    rank_points = {1: 10, 2: 7, 3: 5, 4: 2, 5: 1, 6: 0, 7: 0, 8: 0}
    combination_data = {}
    team_data = {}

    for player in match_record["userGames"]:
        team_id = player["teamNumber"]
        character_name = CHARACTER_MAP[player["characterNum"]]
        rank = player["gameRank"]
        kills = player["teamKill"]

        if team_id not in team_data:
            team_data[team_id] = {"rank": rank, "kills": kills, "characters": []}
        team_data[team_id]["characters"].append(character_name)

    for team in team_data.values():
        if len(team["characters"]) != 3:
            continue

        characters = tuple(sorted(team["characters"]))
        rank = team["rank"]
        kills = team["kills"]
        score = rank_points.get(rank, 0) + kills * 2

        if characters not in combination_data:
            combination_data[characters] = {"average_score": 0, "count": 0, "total_score": 0}
        combination_data[characters]["total_score"] += score
        combination_data[characters]["count"] += 1
        combination_data[characters]["average_score"] = combination_data[characters]["total_score"] / combination_data[characters]["count"]

    return combination_data

def update_global_combination_data(new_data):
    global global_combination_data

    for characters, scores in new_data.items():
        if characters not in global_combination_data:
            global_combination_data[characters] = {"average_score": 0, "count": 0, "total_score": 0}
        global_combination_data[characters]["total_score"] += scores["total_score"]
        global_combination_data[characters]["count"] += scores["count"]
        global_combination_data[characters]["average_score"] = global_combination_data[characters]["total_score"] / global_combination_data[characters]["count"]
def get_user_num(nickName: str):
    """
    닉네임으로 유저 번호 가져오기.
    """
    url = f"{BASE_URL}/user/nickname?query={nickName}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["user"]["userNum"]
def save_to_csv_on_desktop_with_averages(filename):
    global global_combination_data

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    full_path = os.path.join(desktop_path, filename)

    with open(full_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Combination", "Average Score"])
        for characters, data in global_combination_data.items():
            writer.writerow([", ".join(characters), data["average_score"]])

    print(f"데이터가 바탕화면에 {filename} 파일로 저장되었습니다.")

def main():
    global global_combination_data
    global processed_game_ids

    first_nickName = input("첫 번째 유저 닉네임을 입력하세요: ")
    first_user_num = get_user_num(first_nickName)

    if not first_user_num:
        print("첫 번째 유저 정보를 가져올 수 없습니다.")
        return

    first_matches = get_recent_matches(first_user_num, max_matches=30)
    if not first_matches:
        print("첫 번째 유저의 전적을 가져올 수 없습니다.")
        return

    for match in first_matches:
        if match["gameId"] in processed_game_ids:
            print(f"게임 {match['gameId']}은 이미 처리되었습니다. 건너뜁니다.")
            continue

        game_data = get_game_detail(match["gameId"])
        if game_data:
            team_scores = calculate_team_scores(game_data)
            update_global_combination_data(team_scores)
            break

    max_iterations = 30000
    iterations_completed = 0
    users_in_tier = get_users_in_tier()

    while iterations_completed < max_iterations:
        try:
            random_user = random.choice(users_in_tier)
            matches = get_recent_matches(random_user, max_matches=30)

            if not matches:
                print(f"유저 {random_user}의 전적이 없습니다. 다음 유저를 선택합니다.")
                continue

            for match in matches:
                if match["gameId"] in processed_game_ids:
                    print(f"게임 {match['gameId']}은 이미 처리되었습니다. 건너뜁니다.")
                    continue

                game_data = get_game_detail(match["gameId"])
                if game_data:
                    team_scores = calculate_team_scores(game_data)
                    update_global_combination_data(team_scores)
                    iterations_completed += 1
                    break

            print(f"유저 {random_user}의 전적 처리 완료. 현재 처리된 이터레이션: {iterations_completed}")

        except Exception as e:
            print(f"오류 발생: {e}")
            break

        time.sleep(0.25)

    print("글로벌 조합 점수 데이터:")
    pprint.pprint(global_combination_data)
    save_to_csv_on_desktop_with_averages("global_combination_data_with_averages.csv")

if __name__ == "__main__":
    main()

import pandas as pd
import json
from sklearn.metrics.pairwise import cosine_similarity
from firebase_admin import credentials, initialize_app, db

# 데이터 로드
data_path = r"C:\Users\chaem\OneDrive\Desktop\텀프로젝트\global_combination_data_with_averages.csv"  # CSV 파일 경로
df = pd.read_csv(data_path)

# 데이터 전처리 함수
def parse_combination(combination_str):
    try:
        return json.loads(combination_str.replace("'", '"'))
    except json.JSONDecodeError:
        return [char.strip() for char in combination_str.split(',')]

# 데이터 전처리
df['Combination'] = df['Combination'].apply(parse_combination)

# 추천 함수
def recommend_combinations(fixed_character, df, top_n=5):
    filtered_combinations = df[df['Combination'].apply(lambda x: fixed_character in x)]
    scores = filtered_combinations.groupby(filtered_combinations['Combination'].apply(tuple))['Average Score'].mean()
    sorted_scores = scores.sort_values(ascending=False)
    return sorted_scores.head(top_n)

# 캐릭터 선택 및 추천 실행
fixed_character = input("고정할 캐릭터를 입력하세요 (예: 재키): ")
recommended_combinations = recommend_combinations(fixed_character, df, top_n=5)

print(f"{fixed_character}와 함께 추천하는 상위 {len(recommended_combinations)}개 조합:")
print(recommended_combinations)

# Firebase 초기화
cred = credentials.Certificate(r"C:\Users\chaem\OneDrive\Desktop\텀프로젝트\config\firebase-adminsdk.json")
initialize_app(cred, {
    'databaseURL': 'https://er-squadscore-default-rtdb.firebaseio.com/'
})

# Firebase 업로드 함수
def upload_to_firebase(data, character):
    ref = db.reference(f'recommendations/{character}')
    
    # JSON 형식으로 업로드하기 위해 값을 문자열로 변환
    data_dict = {str(k): str(v) for k, v in data.items()}
    ref.set(data_dict)
    print(f"{character}에 대한 추천 데이터가 Firebase에 업로드되었습니다.")

upload_to_firebase(recommended_combinations, fixed_character)   
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# 1. 인구감소지역 (89개)
decline_areas = [
    ("부산광역시", "동구"), ("부산광역시", "서구"), ("부산광역시", "영도구"),
    ("대구광역시", "남구"), ("대구광역시", "서구"), ("대구광역시", "군위군"), ("경상북도", "군위군"),
    ("인천광역시", "강화군"), ("인천광역시", "옹진군"),
    ("경기도", "가평군"), ("경기도", "연천군"),
    ("강원특별자치도", "고성군"), ("강원특별자치도", "삼척시"), ("강원특별자치도", "양구군"), ("강원특별자치도", "양양군"), ("강원특별자치도", "영월군"), ("강원특별자치도", "정선군"), ("강원특별자치도", "철원군"), ("강원특별자치도", "태백시"), ("강원특별자치도", "평창군"), ("강원특별자치도", "홍천군"), ("강원특별자치도", "화천군"), ("강원특별자치도", "횡성군"),
    ("강원도", "고성군"), ("강원도", "삼척시"), ("강원도", "양구군"), ("강원도", "양양군"), ("강원도", "영월군"), ("강원도", "정선군"), ("강원도", "철원군"), ("강원도", "태백시"), ("강원도", "평창군"), ("강원도", "홍천군"), ("강원도", "화천군"), ("강원도", "횡성군"),
    ("충청북도", "괴산군"), ("충청북도", "단양군"), ("충청북도", "보은군"), ("충청북도", "영동군"), ("충청북도", "옥천군"), ("충청북도", "제천시"),
    ("충청남도", "공주시"), ("충청남도", "금산군"), ("충청남도", "논산시"), ("충청남도", "보령시"), ("충청남도", "부여군"), ("충청남도", "서천군"), ("충청남도", "예산군"), ("충청남도", "청양군"), ("충청남도", "태안군"),
    ("전북특별자치도", "고창군"), ("전북특별자치도", "김제시"), ("전북특별자치도", "남원시"), ("전북특별자치도", "무주군"), ("전북특별자치도", "부안군"), ("전북특별자치도", "순창군"), ("전북특별자치도", "임실군"), ("전북특별자치도", "장수군"), ("전북특별자치도", "정읍시"), ("전북특별자치도", "진안군"),
    ("전라북도", "고창군"), ("전라북도", "김제시"), ("전라북도", "남원시"), ("전라북도", "무주군"), ("전라북도", "부안군"), ("전라북도", "순창군"), ("전라북도", "임실군"), ("전라북도", "장수군"), ("전라북도", "정읍시"), ("전라북도", "진안군"),
    ("전라남도", "강진군"), ("전라남도", "고흥군"), ("전라남도", "곡성군"), ("전라남도", "구례군"), ("전라남도", "담양군"), ("전라남도", "보성군"), ("전라남도", "신안군"), ("전라남도", "영광군"), ("전라남도", "영암군"), ("전라남도", "완도군"), ("전라남도", "장성군"), ("전라남도", "장흥군"), ("전라남도", "진도군"), ("전라남도", "함평군"), ("전라남도", "해남군"), ("전라남도", "화순군"),
    ("경상북도", "고령군"), ("경상북도", "문경시"), ("경상북도", "봉화군"), ("경상북도", "상주시"), ("경상북도", "성주군"), ("경상북도", "안동시"), ("경상북도", "영덕군"), ("경상북도", "영양군"), ("경상북도", "영주시"), ("경상북도", "영천시"), ("경상북도", "울릉군"), ("경상북도", "울진군"), ("경상북도", "의성군"), ("경상북도", "청도군"), ("경상북도", "청송군"),
    ("경상남도", "거창군"), ("경상남도", "고성군"), ("경상남도", "남해군"), ("경상남도", "밀양시"), ("경상남도", "산청군"), ("경상남도", "의령군"), ("경상남도", "창녕군"), ("경상남도", "하동군"), ("경상남도", "함안군"), ("경상남도", "함양군"), ("경상남도", "합천군")
]
decline_set = set(decline_areas)

# 2. 문화관광축제 (명칭 정규화 매칭을 위해 여백 제거용)
festival_list = [
    "관악강감찬축제", "광안리어방축제", "동래읍성역사축제", "부산국제록페스티벌", "대구약령시한방문화축제", "대구치맥페스티벌", "부평풍물대축제",
    "소래포구축제", "인천펜타포트음악축제", "광주김치축제", "대전효문화뿌리축제", "울산옹기축제", "태화강마두희축제", "세종한글축제", "세종축제", "부천국제만화축제",
    "수원화성문화제", "시흥갯골축제", "안성맞춤남사당바우덕이축제", "여주오곡나루축제", "연천구석기축제", "화성뱃놀이축제", "강릉커피축제", "정선아리랑제",
    "철원한탄강얼음트레킹축제", "평창송어축제", "괴산고추축제", "음성품바축제", "논산딸기축제", "서산해미읍성축제", "한산모시문화제", "순창장류축제",
    "임실N치즈축제", "장수한우랑사과랑축제", "진안홍삼축제", "곡성세계장미축제", "목포항구축제", "보성다향대축제", "영암왕인문화축제", "정남진장흥물축제",
    "고령대가야축제", "청송사과축제", "포항국제불빛축제", "김해분청도자기축제", "밀양아리랑축제", "탐라문화제",
    "추억의충장축제", "춘천마임축제", "평창효석문화제", "화천산천어축제", "영동난계국악축제", "금산인삼축제", "보령머드축제", "천안흥타령축제",
    "김제지평선축제", "무주반딧불축제", "담양대나무축제", "진도신비의바닷길축제", "함평나비축제", "문경찻사발축제", "안동국제탈춤페스티벌",
    "영주풍기인삼축제", "산청한방약초축제", "진주유등축제", "통영한산대첩축제", "하동야생차문화축제"
]

def load_population_data():
    pop_files = {
        2023: '/Users/g-goubley/Desktop/2nd Project/202301_202312_주민등록인구및세대현황_월간.xlsx',
        2024: '/Users/g-goubley/Desktop/2nd Project/202401_202412_주민등록인구및세대현황_월간.xlsx',
        2025: '/Users/g-goubley/Desktop/2nd Project/202501_202512_주민등록인구및세대현황_월간.xlsx',
        2026: '/Users/g-goubley/Desktop/2nd Project/202601_202603_주민등록인구및세대현황_월간.xlsx'
    }
    
    pop_records = []
    
    for year, f in pop_files.items():
        try:
            df_pop = pd.read_excel(f, skiprows=2)
            for _, row in df_pop.iterrows():
                agency = str(row['행정기관']).strip()
                if not agency or agency == 'nan': continue
                
                parts = agency.split(' ')
                sido = parts[0]
                if '전국' in sido: continue
                
                if len(parts) >= 3 and not parts[1].startswith('('):
                    sigungu = parts[1]
                else:
                    sigungu = '-' # 광역 단위 혹은 기초 없음
                
                pop_val = str(row['총인구수']).replace(',', '').strip()
                try:
                    pop_val = int(pop_val)
                    pop_records.append({
                        '연도': year,
                        '광역시도': sido,
                        '기초지자체': sigungu,
                        '기초인구수': pop_val
                    })
                except:
                    pass
        except Exception as e:
            print(f"Error loading {year}: {e}")
            
    return pd.DataFrame(pop_records)

def main():
    print("Loading festival data...")
    # 첫번째 컬럼명이 메타데이터라 skiprows=1 처리됨
    original_df = pd.read_csv('/Users/g-goubley/Desktop/2nd Project/민섭님자료/지역축제_2023_2026_통합전처리완료.csv', skiprows=1)
    
    print("Loading population data...")
    df_pop = load_population_data()
    # 인구 데이터에 중복이 있을 수 있으니 GroupBy로 첫값 취하기
    df_pop = df_pop.groupby(['연도', '광역시도', '기초지자체'], as_index=False).first()
    
    print("Merging data...")
    df = original_df.copy()
    
    # 광역시도 전처리 (전북특별자치도 <-> 전라북도 등 통일, 혹은 인구데이터 쪽과 매핑)
    # csv 데이터는 주로 "부산광역시", "제주특별자치도" 등으로 적혀있음
    df['매핑_기초'] = df['기초지자체'].astype(str).str.replace(' ', '')
    df['매핑_기초'] = df['매핑_기초'].apply(lambda x: '-' if '(광역주관)' in x or 'nan' == x.lower() else x)
    
    def unify_sido(x):
        x = str(x)
        if x in ['강원도', '제주도']: return x.replace('도', '특별자치도')
        if x == '전라북도': return '전북특별자치도' 
        return x
        
    df['매핑_광역'] = df['광역시도'].apply(unify_sido)
    df_pop['매핑_광역'] = df_pop['광역시도'].apply(unify_sido)
    df_pop['매핑_기초'] = df_pop['기초지자체'].astype(str).str.replace(' ', '')
    
    df_pop_sub = df_pop[['연도', '매핑_광역', '매핑_기초', '기초인구수']]
    
    df_merged = pd.merge(df, df_pop_sub, on=['연도', '매핑_광역', '매핑_기초'], how='left')
    
    # 관계인구 지수
    df_merged['기초인구수'] = pd.to_numeric(df_merged['기초인구수'], errors='coerce')
    visit_col_name = '방문객합계\n(前년실적)'
    df_merged['방문객_val'] = pd.to_numeric(df_merged[visit_col_name].replace(',', '', regex=True), errors='coerce')
    df_merged['관계인구지수'] = df_merged['방문객_val'] / df_merged['기초인구수']
    
    # 인구감소지역 여부
    def check_decline(row):
        sido, sigungu = str(row['광역시도']), str(row['매핑_기초'])
        for dsido, dsigungu in decline_set:
            if (dsido in sido or sido in dsido) and (dsigungu == sigungu):
                return 1
        return 0
        
    df_merged['인구감소지역_여부'] = df_merged.apply(check_decline, axis=1)
    
    # 문화관광축제 여부
    def check_festival(name):
        n = str(name).replace(' ', '').replace('!', '').replace('?', '')
        for f in festival_list:
            if f in n or n in f:
                return 1
        return 0
        
    df_merged['문화관광축제_지정여부'] = df_merged['축제명'].apply(check_festival)
    
    # 중간 매핑 컬럼 제거
    df_merged.drop(columns=['매핑_기초', '매핑_광역', '방문객_val'], inplace=True, errors='ignore')
    
    output_path = '/Users/g-goubley/Desktop/2nd Project/민섭님자료/지역축제_2023_2026_최종분석용.csv'
    # 원본이 skiprows=1로 인해 헤더가 사라진 상태이므로, 빈 타이틀을 맨위에 붙여주기
    # 우선 DF 저장
    df_merged.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"Missing Population Info (Rows): {df_merged['기초인구수'].isna().sum()} / {len(df_merged)}")
    print(f"Successfully saved to {output_path}")

if __name__ == '__main__':
    main()

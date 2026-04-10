import pandas as pd
import os
import glob

# 설정
folder = '/Users/g-goubley/Desktop/2nd Project/'
output_folder = os.path.join(folder, '전처리_완료')
os.makedirs(output_folder, exist_ok=True)

excel_files = glob.glob(os.path.join(folder, '*.xlsx'))
csv_files = glob.glob(os.path.join(folder, '*.csv'))

# 지역명 매핑
region_mapping = {
    '광역지자체': '광역자치단체명',
    '광역지자체명': '광역자치단체명',
    '광역지자체 명': '광역자치단체명',
    '시도명': '광역자치단체명',
    '시도': '광역자치단체명',
    '광역시/도': '광역자치단체명',
    
    '기초지자체': '기초자치단체명',
    '기초지자체명': '기초자치단체명',
    '기초지자체 명': '기초자치단체명',
    '시군구명': '기초자치단체명',
    '시군구': '기초자치단체명',
    '시/군/구': '기초자치단체명',
}

# 1. 파일별 전처리 및 저장
processed_files = []
for file_path in excel_files + csv_files:
    name = os.path.basename(file_path)
    if '전처리_완료' in file_path or 'preprocess_data.py' in name:
        continue
        
    try:
        # 파일 읽기
        if name.endswith('.xlsx'):
            skip = 2 if '갭지수' in name else 0
            df = pd.read_excel(file_path, skiprows=skip)
            
            # 개행문자 포함된 컬럼명 정리
            df.columns = [str(c).replace('\n', '') for c in df.columns]
        else:
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='cp949')

        # 컬럼명 변경 (표준화)
        df.rename(columns=region_mapping, inplace=True)
        
        # 특정 문자열 정리 (예: '서울' -> '서울특별시' 등 필요시 확장 가능, 현재는 기초작업)
        for col in ['광역자치단체명', '기초자치단체명']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                
        # 특수문자 제거(숫자형 변환)
        # 예시: '예산(백만원)', 금액 비율 등에서 , 제거
        for col in df.columns:
            if df[col].dtype == 'object':
                # 숫자로 변환 가능하면서 콤마가 포함된 경우 처리 (단, 지역명 등은 제외)
                if col not in ['광역자치단체명', '기초자치단체명', '축제명', '최초개최연도', '축제유형', '개최기간', '개최장소', '개최방식', '카테고리중분류명', '대분류', '중분류', '대분류 지출액 비율', '중분류 지출액 비율', '소분류 카테고리', '관광지명', '관광지ID', '등급', '인구감소여부', '인구감소']:
                    try:
                        # 콤마 제거 후 변환 시도
                        temp = df[col].str.replace(',', '').astype(float)
                        df[col] = temp
                    except:
                        pass
        
        # 저장
        if name.endswith('.xlsx'):
            out_name = name.replace('.xlsx', '_전처리.csv')
        else:
            out_name = name.replace('.csv', '_전처리.csv')
            
        out_path = os.path.join(output_folder, out_name)
        df.to_csv(out_path, index=False, encoding='utf-8-sig')
        processed_files.append((name, out_path, df))
        print(f"[{name}] -> [{out_name}] 전처리 및 저장 완료.")
    except Exception as e:
        print(f"Error processing {name}: {e}")

# 2. 통합 가능한 데이터 (우선순위: 연도, 광역, 기초가 모두 있는 데이터들) MERGE 시도
merged_df = None
dfs_to_merge = []

merge_keys = ['연도', '광역자치단체명', '기초자치단체명']
for name, path, df in processed_files:
    # 갭지수 등 연도가 없는 데이터는 제외 (또는 따로 처리)
    if all(k in df.columns for k in merge_keys):
        # 중복 방지를 위해 컬럼명 변경 (키 제외)
        temp_df = df.copy()
        for c in temp_df.columns:
            if c not in merge_keys:
                temp_df.rename(columns={c: f"{name.replace('.csv', '').replace('.xlsx', '').replace('_통합', '')}_{c}"}, inplace=True)
        dfs_to_merge.append(temp_df)

if dfs_to_merge:
    merged_df = dfs_to_merge[0]
    for i in range(1, len(dfs_to_merge)):
        # on='연도', '광역...', '기초...'
        merged_df = pd.merge(merged_df, dfs_to_merge[i], on=merge_keys, how='outer')

    # 저장
    merged_path = os.path.join(output_folder, '00_수요지수_연도_지역별_총통합본.csv')
    merged_df.to_csv(merged_path, index=False, encoding='utf-8-sig')
    print(f"\n[통합데이터 생성 완료] -> {merged_path}")
else:
    print("\n[통합데이터 생성 불가] 연도/광역/기초자치단체명을 모두 포함한 파일이 부족합니다.")


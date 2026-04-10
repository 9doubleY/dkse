import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc

# 맷플롯립 한글 설정 (Mac OS)
plt.rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False
sns.set_palette('muted')

base_dir = '/Users/g-goubley/Desktop/2nd Project/전처리_완료'
plot_dir = '/Users/g-goubley/.gemini/antigravity/brain/c49e0210-9940-481c-bebb-7924167ce6c2/artifacts/EDA_plots'
os.makedirs(plot_dir, exist_ok=True)

# 1. 시군구 갭지수 로드 (주요 타겟 필터용)
gap_df = pd.read_csv(os.path.join(base_dir, '시군구_갭지수_3개년보정판_전처리.csv'))
gap_df = gap_df[gap_df['인구감소여부'] == '지정'].copy() # 인구감소 지정 지역만

# 숫자형 변환
def to_float(x):
    if isinstance(x, str):
        return pd.to_numeric(x.replace('%', '').replace(',', ''), errors='coerce')
    return float(x) if pd.notnull(x) else 0.0

gap_df['갭지수(0~100)'] = gap_df['갭지수(0~100)'].apply(to_float)
gap_df['수요종합'] = gap_df['수요종합'].apply(to_float)
gap_df['공급점수'] = gap_df['공급점수'].apply(to_float)

# 2. 지역축제 데이터 로드 (공급 인프라 평가용)
fest_df = pd.read_csv(os.path.join(base_dir, '지역축제_2024_2025_2026_통합_전처리.csv'))
fest_df['예산(백만원)'] = pd.to_numeric(fest_df['예산(백만원)'], errors='coerce').fillna(0)
fest_df['방문객수'] = pd.to_numeric(fest_df['방문객수'], errors='coerce').fillna(0)
# 기초지자체별 평균 예산 및 축제 건수
fest_agg = fest_df.groupby(['광역자치단체명', '기초자치단체명']).agg({'예산(백만원)': 'sum', '방문객수': 'sum', '축제명': 'count'}).reset_index()
fest_agg.rename(columns={'축제명': '축제건수'}, inplace=True)

# 3. 데이터 병합 (갭지수 + 축제집계)
df_merged = pd.merge(gap_df, fest_agg, how='left', on=['광역자치단체명', '기초자치단체명'])
df_merged['예산(백만원)'] = df_merged['예산(백만원)'].fillna(0)
df_merged['축제건수'] = df_merged['축제건수'].fillna(0)
df_merged['방문객수'] = df_merged['방문객수'].fillna(0)

# 후보군 추출 로직
# 조건 1: 갭지수 상위권 (잠재력 높음)
# 조건 2: 기존 축제 예산 하위권 (공백존재, 신규 기획 투입 시 효과 극대화)
df_merged['갭지수점수_Norm'] = df_merged['갭지수(0~100)'] / df_merged['갭지수(0~100)'].max()
max_budget = df_merged['예산(백만원)'].max()
if max_budget == 0: max_budget = 1
df_merged['예산부족점수_Norm'] = 1 - (df_merged['예산(백만원)'] / max_budget)
df_merged['최종매력도스코어'] = (df_merged['갭지수점수_Norm'] * 0.6) + (df_merged['예산부족점수_Norm'] * 0.4)

ranking = df_merged.sort_values(by='최종매력도스코어', ascending=False)
top_candidates = ranking.head(3)
final_one = top_candidates.iloc[0]

cand_names = [f"{row['광역자치단체명']} {row['기초자치단체명']}" for _, row in top_candidates.iterrows()]
final_name = cand_names[0]

# =============== 시각화 생성 (20+) ===============
plot_paths = []

def save_fig(name):
    path = os.path.join(plot_dir, name)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    plot_paths.append(path)

# P1_1: 인구감소지역 지정 vs 비지정 현황 (시군구수) - 전체 갭데이터 재로딩
full_gap = pd.read_csv(os.path.join(base_dir, '시군구_갭지수_3개년보정판_전처리.csv'))
plt.figure(figsize=(8,5))
sns.countplot(data=full_gap, x='인구감소여부', order=['지정', '관심', '-'])
plt.title('인구감소지역 지정 현황 분포')
save_fig('01_pop_decline_dist.png')

# P1_2: 전국 갭지수(평균) vs 인구감소여부
full_gap['갭지수(0~100)'] = full_gap['갭지수(0~100)'].apply(to_float)
plt.figure(figsize=(8,5))
sns.boxplot(data=full_gap, x='인구감소여부', y='갭지수(0~100)', order=['지정', '관심', '-'])
plt.title('인구감소여부에 따른 갭지수 분포 비교')
save_fig('02_gap_index_by_decline.png')

# P1_3: 수요 대비 공급점수 산점도 (인구감소지역 집중)
plt.figure(figsize=(8,6))
sns.scatterplot(data=df_merged, x='수요종합', y='공급점수', size='축제건수', sizes=(20, 200), legend=False, alpha=0.6)
plt.title('인구감소(지정) 지역의 수요종합 vs 공급점수')
plt.xlabel('수요종합 (수요 잠재력)')
plt.ylabel('공급점수 (관광 인프라)')
save_fig('03_demand_vs_supply_scatter.png')

# P1_4: 축제 예산 분포 (Histogram)
plt.figure(figsize=(8,5))
sns.histplot(df_merged['예산(백만원)'], bins=20, kde=True)
plt.title('인구감소지역 소재 축제 예산 총합 분포')
plt.xlabel('예산 (백만원)')
save_fig('04_budget_distribution.png')

# P1_5: 갭지수 상위 10개 지역
top10_gap = ranking.sort_values(by='갭지수(0~100)', ascending=False).head(10)
plt.figure(figsize=(10,6))
sns.barplot(data=top10_gap, x='갭지수(0~100)', y='기초자치단체명')
plt.title('인구감소지역 내 갭지수 상위 Top 10')
save_fig('05_top10_gap_regions.png')

# P1_6: 축제건수 별 평균 갭지수
df_merged['축제건수분류'] = pd.cut(df_merged['축제건수'], bins=[-1, 0, 2, 5, 10, 100], labels=['0건', '1~2건', '3~5건', '6~10건', '10건초과'])
plt.figure(figsize=(8,5))
sns.barplot(data=df_merged, x='축제건수분류', y='갭지수(0~100)')
plt.title('축제 개최 건수별 평균 갭지수')
save_fig('06_gap_by_fest_count.png')

# P1_7: 축제 예산 vs 방문객 수 산점도
plt.figure(figsize=(8,6))
sns.scatterplot(data=df_merged, x='예산(백만원)', y='방문객수', alpha=0.6)
plt.title('축제 예산 대비 방문객수 상관관계 (인구감소지역)')
plt.xscale('symlog')
plt.yscale('symlog')
save_fig('07_budget_vs_visitors.png')

# P1_8: 광역별 인구감소지역 수
plt.figure(figsize=(10,5))
sns.countplot(data=df_merged, y='광역자치단체명', order=df_merged['광역자치단체명'].value_counts().index)
plt.title('광역지자체별 인구감소(지정) 기초지자체 수')
save_fig('08_pop_decline_by_province.png')

# P1_9: 광역별 축제예산 총합
agg_prov = df_merged.groupby('광역자치단체명')['예산(백만원)'].sum().sort_values(ascending=False).reset_index()
plt.figure(figsize=(10,5))
sns.barplot(data=agg_prov, y='광역자치단체명', x='예산(백만원)')
plt.title('광역별 인구감소구역 내 축제예산 총합')
save_fig('09_budget_by_province.png')

# P2_10: Top 3 후보군 갭지수 비교
plt.figure(figsize=(6,4))
sns.barplot(data=top_candidates, x='기초자치단체명', y='갭지수(0~100)')
plt.title('Top 3 후보 지역 갭지수 비교')
save_fig('10_top3_gap.png')

# P2_11: Top 3 후보군 축제 예산 비교
plt.figure(figsize=(6,4))
sns.barplot(data=top_candidates, x='기초자치단체명', y='예산(백만원)')
plt.title('Top 3 후보 지역 기존 축제 종합 예산')
save_fig('11_top3_budget.png')

# P2_12: Top 3 후보군 5대 점수 (레이더 차트용 변환 Data) 
# 방문, 지출, 검색, 체류, 숙박
spider_cols = ['방문점수(25%)', '지출점수(20%)', '검색점수(15%)', '체류점수(10%)', '숙박점수(10%)']
categories = spider_cols
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]
plt.figure(figsize=(6,6))
ax = plt.subplot(111, polar=True)
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)
plt.xticks(angles[:-1], ['방문', '지출', '검색', '체류', '숙박'])

for _, row in top_candidates.iterrows():
    values = []
    for c in spider_cols:
        v = to_float(row[c])
        values.append(v)
    values += values[:1]
    ax.plot(angles, values, linewidth=1, linestyle='solid', label=row['기초자치단체명'])
    ax.fill(angles, values, alpha=0.1)
plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
plt.title('Top 3 후보 지역 수요 점수 레이더 차트')
save_fig('12_top3_radar.png')

# P2_13: 매력도스코어 비교
plt.figure(figsize=(6,3))
sns.barplot(data=top_candidates, x='기초자치단체명', y='최종매력도스코어')
plt.title('기획자 관점의 매력도 스코어 (Gap - Budget)')
save_fig('13_top3_attraction_score.png')

# 추가 지표 불러오기 (시계열)
trend_df = pd.read_csv(os.path.join(base_dir, '검색건수_추이_통합_전처리.csv'))
sub_trend = trend_df[trend_df['기초자치단체명'].isin(top_candidates['기초자치단체명'].tolist())] if '기초자치단체명' in trend_df.columns else pd.DataFrame()

# P2_14: 검색건수 추이 (더미 or 실제 데이터가 기초지자체까지 없으면 광역으로 대체)
# 지역별 검색건수_통합 확인
srch_df = pd.read_csv(os.path.join(base_dir, '지역별_검색건수_통합_전처리.csv'))
top_s = srch_df[srch_df['기초자치단체명'].isin(top_candidates['기초자치단체명'].tolist())]
if not top_s.empty:
    plt.figure(figsize=(8,5))
    sns.lineplot(data=top_s, x='연도', y='기초지자체 검색건수', hue='기초자치단체명', marker='o')
    plt.title('Top 3 지역 연도별 검색건수 비교')
    plt.xticks([2023, 2024, 2025, 2026])
    save_fig('14_top3_search_trend.png')

# P2_15: 지출액 비율 비교
exp_df = pd.read_csv(os.path.join(base_dir, '지역별_지출액_통합_전처리.csv'))
if not exp_df.empty and '기초지자체 지출액 비율(%)' in exp_df.columns:
    top_e = exp_df[exp_df['기초자치단체명'].isin(top_candidates['기초자치단체명'].tolist())]
    if not top_e.empty:
        plt.figure(figsize=(8,5))
        sns.barplot(data=top_e[top_e['연도']==top_e['연도'].max()], x='기초자치단체명', y='기초지자체 지출액 비율(%)')
        plt.title('Top 3 지역 최근연도 지출액 비율')
        save_fig('15_top3_expenditure.png')

# P3 (최종 지역 딥다이브)
# P3_16: 최종 지역의 기존 축제들
final_fest = fest_df[(fest_df['광역자치단체명'] == final_one['광역자치단체명']) & (fest_df['기초자치단체명'] == final_one['기초자치단체명'])]
if not final_fest.empty:
    plt.figure(figsize=(8,6))
    f_budget = final_fest.groupby('축제명')['예산(백만원)'].sum().reset_index()
    sns.barplot(data=f_budget, x='예산(백만원)', y='축제명')
    plt.title(f'최종 선정지역({final_name}) 보유 축제 예산')
    save_fig('16_final_fest_budget.png')

    # P3_17: 최종지역 축제 방문객 수
    plt.figure(figsize=(8,6))
    f_vis = final_fest.groupby('축제명')['방문객수'].sum().reset_index()
    sns.barplot(data=f_vis, x='방문객수', y='축제명')
    plt.title(f'최종 선정지역({final_name}) 보유 축제 방문객수')
    save_fig('17_final_fest_visitor.png')

    # P3_18: 최종지역 축제 유형 분포
    plt.figure(figsize=(6,6))
    f_type = final_fest['축제유형'].value_counts()
    plt.pie(f_type, labels=f_type.index, autopct='%1.1f%%', startangle=140)
    plt.title(f'최종 선정지역 축제 유형 비율')
    save_fig('18_final_fest_types.png')

# P3_19: 광역별 방문자 수 통계 (최종지역 소속 광역 vs 타 광역)
v_df = pd.read_csv(os.path.join(base_dir, '광역별_방문자_수_통합_전처리.csv'))
if not v_df.empty:
    plt.figure(figsize=(8,5))
    prov_agg = v_df.groupby('광역자치단체명')['광역지자체 방문자 수'].mean().sort_values(ascending=False).head(10)
    colors = ['red' if x == final_one['광역자치단체명'] else 'grey' for x in prov_agg.index]
    sns.barplot(x=prov_agg.values, y=prov_agg.index, palette=colors)
    plt.title('광역 단위별 방문자수 비교 (최종 타겟 소속지역 하이라이트)')
    save_fig('19_final_province_compare.png')

# P3_20: 최종 지역 갭지수 vs 타겟 전체 평균
labels = ['갭지수', '수요종합', '공급점수']
final_vals = [final_one['갭지수(0~100)'], final_one['수요종합'], final_one['공급점수']]
mean_vals = [df_merged['갭지수(0~100)'].mean(), df_merged['수요종합'].mean(), df_merged['공급점수'].mean()]
x = np.arange(len(labels))
width = 0.35
plt.figure(figsize=(8,5))
plt.bar(x - width/2, final_vals, width, label=final_name)
plt.bar(x + width/2, mean_vals, width, label='인구감소지역 평균')
plt.xticks(x, labels)
plt.legend()
plt.title('최종선정지역 지표 vs 평균 비교')
save_fig('20_final_vs_average.png')

# P3_21: 관광소비추이 중분류별
cons_df = pd.read_csv(os.path.join(base_dir, '업종별_지출액_통합_전처리.csv'))
if not cons_df.empty and '중분류 지출액 비율' in cons_df.columns:
    plt.figure(figsize=(10,6))
    top_cat = cons_df.groupby('중분류')['중분류 지출액 비율'].mean().sort_values(ascending=False).head(10)
    sns.barplot(x=top_cat.values, y=top_cat.index)
    plt.title('업종별 관광 지출액 비율 (참고 지표)')
    save_fig('21_consumption_categories.png')

print(f"Top 3 Candidates: {', '.join(cand_names)}")
print(f"Final Selection: {final_name}")

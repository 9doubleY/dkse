import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Mac 폰트 설정
plt.rc('font', family='AppleGothic')
plt.rc('axes', unicode_minus=False)

def main():
    # 1. 데이터 로드
    csv_path = '/Users/g-goubley/Desktop/2nd Project/민섭님자료/지역축제_2023_2026_최종분석용.csv'
    df = pd.read_csv(csv_path)

    # 방문객합계, 예산합계 컬럼명 찾기
    visit_col = [c for c in df.columns if '방문객합계' in c][0]
    bug_col = [c for c in df.columns if '예산합계' in c][0]
    nat_bug_col = [c for c in df.columns if '국비' in c and '백만' in c][0]
    loc_bug_col = [c for c in df.columns if '지방비' in c and '백만' in c][0]
    oth_bug_col = [c for c in df.columns if '기타' in c and '백만' in c][0]
    forn_col = [c for c in df.columns if '외국인' in c and '前' in c][0]

    # 문자열 내 쉼표 제거 수치 변환
    def to_num(x):
        try:
            return float(str(x).replace(',', ''))
        except:
            return np.nan

    df['총방문객'] = df[visit_col].apply(to_num)
    df['총예산_백만'] = df[bug_col].apply(to_num)
    df['국비_백만'] = df[nat_bug_col].apply(to_num)
    df['지방비_백만'] = df[loc_bug_col].apply(to_num)
    df['기타_백만'] = df[oth_bug_col].apply(to_num)
    df['외국인방문객'] = df[forn_col].apply(to_num)

    # 2. 파생 지표 도출
    # 외국인 비중(%)
    df['외국인비중_재산출'] = np.where(df['총방문객'] > 0, (df['외국인방문객'] / df['총방문객']) * 100, 0)
    
    # 국비 의존도(%) & 자립도(%)
    df['국비의존도_재산출'] = np.where(df['총예산_백만'] > 0, (df['국비_백만'] / df['총예산_백만']) * 100, 0)
    df['자체자립도_비율'] = np.where(df['총예산_백만'] > 0, ((df['지방비_백만'].fillna(0) + df['기타_백만'].fillna(0)) / df['총예산_백만']) * 100, 0)
    
    # 개최일수 파싱 (날짜 기반 파싱, 여기선 간단히 운영연수 등의 보완 또는 기본값 3 사용)
    # df 안개최기간 텍스트를 파싱하긴 무거우므로 월, 계절 등으로 일평균 대략 산출 (있는 컬럼 사용)
    # CSV에 일수 컬럼이 따로 없다면, 임의로 파싱
    def get_days(x):
        x = str(x)
        if '~' in x:
            parts = x.split('~')
            # rough estimation, if error assume 3 days
            return 3
        return 1
    df['개최일수_추정'] = df['개최기간'].apply(get_days)

    # 효율 지표
    df['예산효율_명_백만'] = np.where(df['총예산_백만'] > 0, df['총방문객'] / df['총예산_백만'], np.nan)
    df['1인당투입예산_원'] = np.where(df['총방문객'] > 0, (df['총예산_백만'] * 1000000) / df['총방문객'], np.nan)
    df['일평균방문객'] = df['총방문객'] / 3.0 # 단순 3일 고정분 평균 가정
    df['일평균투입예산_백만'] = df['총예산_백만'] / 3.0

    # 지속성 지표
    df['전담조직_유무'] = np.where(df['전담조직명'].notna() & (df['전담조직명'] != '-'), 1, 0)
    df['국비지원_여부'] = np.where(df['국비_백만'] > 0, 1, 0)

    # 분위수 등급 (방문객 및 효율)
    # 결측/0 제외 후 5분위 산출
    v_valid = df[df['총방문객'] > 0]['총방문객']
    if len(v_valid) > 0:
        df.loc[df['총방문객'] > 0, '규모등급_5단계'] = pd.qcut(v_valid, 5, labels=['5등급(소규모)', '4등급', '3등급', '2등급', '1등급(초대형)'], duplicates='drop')
    
    e_valid = df[df['예산효율_명_백만'] > 0]['예산효율_명_백만']
    if len(e_valid) > 0:
        df.loc[df['예산효율_명_백만'] > 0, '투자효율등급'] = pd.qcut(e_valid, 5, labels=['낮음', '다소낮음', '보통', '다소높음', '높음'], duplicates='drop')

    # 새로운 폴더 생성
    plot_dir = '/Users/g-goubley/Desktop/2nd Project/민섭님자료/eda_plots'
    os.makedirs(plot_dir, exist_ok=True)
    
    # 3. 시각화 (20종 이상)
    def save_fig(name):
        plt.tight_layout()
        plt.savefig(os.path.join(plot_dir, f"{name}.png"), dpi=150, bbox_inches='tight')
        plt.close()

    # 1) 연도별 총 축제 건수 추이
    plt.figure(figsize=(8,5))
    sns.countplot(x='연도', data=df, palette='viridis')
    plt.title('01. 연도별 지역축제 개최 추이')
    save_fig('01_annual_festivals_count')

    # 2) 광역시도별 빈도
    plt.figure(figsize=(10,6))
    cnt = df['광역시도'].value_counts().reset_index()
    sns.barplot(y='광역시도', x='count', data=cnt, palette='plasma')
    plt.title('02. 광역시도별 개최 축제 건수')
    save_fig('02_sido_count_bar')

    # 3) 총 방문객 분포 (KDE 플롯 - 상위 제한)
    plt.figure(figsize=(8,5))
    sub = df[df['총방문객'] < df['총방문객'].quantile(0.98)]
    sns.histplot(sub['총방문객'], bins=50, kde=True, color='skyblue')
    plt.title('03. 총 방문객 분포 (상위 2% 극단치 제외)')
    save_fig('03_visitor_distribution')

    # 4) 예산 분포
    plt.figure(figsize=(8,5))
    sub_b = df[df['총예산_백만'] < df['총예산_백만'].quantile(0.98)]
    sns.histplot(sub_b['총예산_백만'].dropna(), bins=50, kde=True, color='salmon')
    plt.title('04. 총 예산(백만원) 분포 (상위 2% 제외)')
    save_fig('04_budget_distribution')

    # 5) 외국인 비중 분포
    plt.figure(figsize=(8,5))
    sns.histplot(df[df['외국인비중_재산출'] > 0]['외국인비중_재산출'], bins=40, color='gold')
    plt.title('05. 외국인 방문객 비중 (%) - 유효 축제 대상')
    save_fig('05_foreign_visitor_ratio')

    # 6) 국비 의존도 비율 박스플롯
    plt.figure(figsize=(8,5))
    sns.boxplot(y=df[df['국비의존도_재산출'] > 0]['국비의존도_재산출'], color='lightgreen')
    plt.title('06. 국비 지원 축제의 의존도(%) 분포')
    save_fig('06_budget_dependency')

    # 7) 자체 자립도
    plt.figure(figsize=(8,5))
    sns.histplot(df[df['자체자립도_비율']>0]['자체자립도_비율'], kde=True, color='teal')
    plt.title('07. 지자체 자체 예산 자립도(%) 밀도')
    save_fig('07_financial_independence')

    # 8) 규모등급별 빈도
    plt.figure(figsize=(8,5))
    sns.countplot(x='규모등급_5단계', data=df, palette='coolwarm')
    plt.title('08. 방문객 기준 규모 등급별 건수')
    save_fig('08_visitor_rank_count')

    # 9) 규모등급별 1인당 투입예산 비교
    plt.figure(figsize=(10,6))
    sub_p = df[df['1인당투입예산_원'] < df['1인당투입예산_원'].quantile(0.95)]
    sns.boxplot(x='규모등급_5단계', y='1인당투입예산_원', data=sub_p, palette='coolwarm')
    plt.title('09. 규모 등급별 1인당 투입예산(원) (상위 5% 이상치 제외)')
    save_fig('09_per_capita_budget_by_rank')

    # 10) 월별 축제 건수
    plt.figure(figsize=(8,5))
    if '시작월' in df.columns:
        sns.countplot(x=df['시작월'].dropna().astype(int), palette='tab10')
        plt.title('10. 월별 개최 건수 (시작월 기준)')
    save_fig('10_monthly_density')

    # 11) 축제 유형 파이
    plt.figure(figsize=(8,8))
    if '유형' in df.columns:
        ty_cnt = df['유형'].value_counts().head(7)
        plt.pie(ty_cnt, labels=ty_cnt.index, autopct='%1.1f%%', startangle=140)
        plt.title('11. 주요 축제 유형 비율')
    save_fig('11_festival_type_pie')

    # 12) 전담조직 유무별 평균 예산
    plt.figure(figsize=(8,5))
    sns.barplot(x='전담조직_유무', y='총예산_백만', data=df, estimator=np.nanmean, ci=None)
    plt.xticks([0, 1], ['조직 없음', '조직 있음'])
    plt.title('12. 전담조직 유무에 따른 평균 예산 규모(백만)')
    save_fig('12_org_vs_budget')

    # 13) 전담조직 유무별 평균 방문객
    plt.figure(figsize=(8,5))
    sns.barplot(x='전담조직_유무', y='총방문객', data=df, estimator=np.nanmean, ci=None)
    plt.xticks([0, 1], ['조직 없음', '조직 있음'])
    plt.title('13. 전담조직 유무에 따른 평균 방문객(명)')
    save_fig('13_org_vs_visitor')

    # 14) 국비지원 여부에 따른 예산효율 차이
    plt.figure(figsize=(8,5))
    sns.boxplot(x='국비지원_여부', y='예산효율_명_백만', data=df[df['예산효율_명_백만'] < df['예산효율_명_백만'].quantile(0.95)])
    plt.xticks([0, 1], ['국비 미지원', '국비 지원'])
    plt.title('14. 국비 지원 여부에 따른 예산 투자효율 (명/백만)')
    save_fig('14_national_support_efficiency')

    # 15) 인구감소지역 vs 기타지역 방문객 차이
    plt.figure(figsize=(8,5))
    if '인구감소지역_여부' in df.columns:
        sns.barplot(x='인구감소지역_여부', y='총방문객', data=df, ci=None)
        plt.xticks([0, 1], ['비감소지역', '인구감소지역'])
        plt.title('15. 인구감소지역 지정 여부별 평균 방문객 규모')
    save_fig('15_pop_decline_visitor')

    # 16) 인구감소지역 예산효율
    plt.figure(figsize=(8,5))
    if '인구감소지역_여부' in df.columns:
        sns.boxplot(x='인구감소지역_여부', y='예산효율_명_백만', data=df[df['예산효율_명_백만'] < df['예산효율_명_백만'].quantile(0.95)])
        plt.xticks([0, 1], ['비감소지역', '인구감소지역'])
        plt.title('16. 인구감소지역 지정 여부별 예산효율 비교')
    save_fig('16_pop_decline_efficiency')

    # 17) 문화관광축제 지정여부방문객 규모
    plt.figure(figsize=(8,5))
    if '문화관광축제_지정여부' in df.columns:
        sns.barplot(x='문화관광축제_지정여부', y='총방문객', data=df, ci=None)
        plt.xticks([0, 1], ['일반 축제', '문체부 지정축제'])
        plt.title('17. 문체부 지정 축제의 평균 방문객 압도율')
    save_fig('17_culture_festival_visitor')

    # 18) 문광축제 예산
    plt.figure(figsize=(8,5))
    if '문화관광축제_지정여부' in df.columns:
        sns.barplot(x='문화관광축제_지정여부', y='총예산_백만', data=df, ci=None)
        plt.xticks([0, 1], ['일반 축제', '문체부 지정축제'])
        plt.title('18. 문체부 지정 축제의 단위 예산 갭')
    save_fig('18_culture_festival_budget')

    # 19) 방문객 vs 예산 산점도 (Log 스케일)
    plt.figure(figsize=(8,6))
    sns.scatterplot(x='총방문객', y='총예산_백만', data=df, hue='문화관광축제_지정여부', alpha=0.6)
    plt.xscale('log')
    plt.yscale('log')
    plt.title('19. 방문객 vs 총예산 산점도 (Log-Log Scale)')
    save_fig('19_visitor_vs_budget_scatter')

    # 20) 연수구간(신규/단기/장기) 분포
    plt.figure(figsize=(8,5))
    if '연수구간' in df.columns:
        sns.countplot(x='연수구간', data=df, order=['신규(1년)', '단기(2~5년)', '중기(6~20년)', '장기(21년+)'])
        plt.title('20. 축제 역사(연수구간) 비중')
    save_fig('20_festival_history_bar')

    # 21) 상관관계 히트맵
    plt.figure(figsize=(9,7))
    cols = ['총방문객', '총예산_백만', '국비_백만', '외국인비중_재산출', '예산효율_명_백만', '1인당투입예산_원']
    corr = df[cols].corr()
    sns.heatmap(corr, annot=True, cmap='RdBu', fmt='.2f', vmin=-1, vmax=1)
    plt.title('21. 수치형 변수 상관관계 (Correlation Matrix)')
    save_fig('21_correlation_matrix')

    df.to_csv(csv_path.replace('.csv', '_추가파생.csv'), index=False)
    print("EDA Visualizations created in:", plot_dir)

if __name__ == "__main__":
    main()

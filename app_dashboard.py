import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------------
# 1. 페이지 및 환경 설정 (Rich Aesthetics)
# ------------------------------------------------------------------
st.set_page_config(
    page_title="대한민국 지역축제 통합 대시보드",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS를 이용한 프리미엄 디자인
st.markdown("""
<style>
    .main {
        background-color: #F8F9FA;
    }
    .stMetric {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.05);
    }
    h1, h2, h3 {
        color: #1F2937;
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 2. 데이터 로드 로직 (캐싱 적용을 통해 속도 향상)
# ------------------------------------------------------------------
import os

@st.cache_data
def load_data():
    # 현재 스크립트 앱(app_dashboard.py)이 실행된 위치를 기준으로 같은 폴더 내의 CSV 파일 조회
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '지역축제_2023_2026_최종분석용_추가파생.csv')
    
    if not os.path.exists(csv_path):
        st.error(f"🚨 CSV 파일을 찾을 수 없습니다! Github에 파일 업로드가 누락되었거나 이름이 잘못되었습니다.")
        st.info(f"📁 현재 서버 폴더({base_dir})에 업로드된 파일 목록은 아래와 같습니다:")
        st.write(os.listdir(base_dir))
        st.stop()
        
    df = pd.read_csv(csv_path)
    # 데이터 정리: 숫자형이 아닌 쉼표 포함 문자열 등을 위해 강제 매핑 및 클렌징은 이미 파생파일에서 진행됨
    # 그러나 NaN 처리 등 시각화 시 오류 방지를 위해 0 보간
    df['연도'] = df['연도'].astype(str)
    return df

df = load_data()

# ------------------------------------------------------------------
# 3. 사이드바 (Sidebar) - 다중 필터 기능 세팅
# ------------------------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3233/3233483.png", width=60)
st.sidebar.title("데이터 필터링")
st.sidebar.markdown("원하시는 조건을 선택하여 맞춤형 데이터 인사이트를 확인하세요.")

# 필터 1: 연도 (다중 선택)
years = sorted(df['연도'].dropna().unique().tolist())
selected_years = st.sidebar.multiselect("🗓 개최 연도", options=years, default=years)

# 필터 2: 광역시도 (다중 선택)
sidos = sorted(df['광역시도'].dropna().unique().tolist())
selected_sidos = st.sidebar.multiselect("📌 광역시도", options=sidos, default=sidos)

# 필터 3: 문화관광축제 지정 여부
festival_status = st.sidebar.radio("🎖 문화관광축제 여부", ["전체보기", "지정 축제만 보기", "일반 축제만 보기"])

# 필터링 적용
filtered_df = df.copy()
if selected_years:
    filtered_df = filtered_df[filtered_df['연도'].isin(selected_years)]
if selected_sidos:
    filtered_df = filtered_df[filtered_df['광역시도'].isin(selected_sidos)]
if festival_status == "지정 축제만 보기":
    filtered_df = filtered_df[filtered_df['문화관광축제_지정여부'] == 1]
elif festival_status == "일반 축제만 보기":
    filtered_df = filtered_df[filtered_df['문화관광축제_지정여부'] == 0]

st.sidebar.markdown("---")
st.sidebar.info(f"선택된 축제 건수: **{len(filtered_df):,}** 건")


# ------------------------------------------------------------------
# 4. 상단 KPI 카드 (핵심 통계)
# ------------------------------------------------------------------
st.title("🎉 대한민국 지역축제 통합 대시보드 (2023~2026)")
st.markdown("정부/행안부/문체부 개방 데이터를 종합하여 추출된 **방문객 및 예산 성과 분석 지표**입니다.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_fests = len(filtered_df)
    st.metric(label="총 축제 개최 건수", value=f"{total_fests:,} 건")

with col2:
    total_visitors = filtered_df['총방문객'].sum()
    st.metric(label="총 누적 방문객", value=f"{int(total_visitors):,} 명" if not pd.isna(total_visitors) else "0 명")

with col3:
    total_budget = filtered_df['총예산_백만'].sum()
    # 억 단위 표시
    budget_eok = total_budget / 100
    st.metric(label="총 투입 예산 (억원)", value=f"{budget_eok:,.0f} 억" if not pd.isna(budget_eok) else "0 억")

with col4:
    avg_efficiency = filtered_df['예산효율_명_백만'].mean()
    st.metric(label="평균 예산 효율 (명/백만원)", value=f"{avg_efficiency:,.1f}" if not pd.isna(avg_efficiency) else "0")

st.markdown("<br>", unsafe_allow_html=True)


# ------------------------------------------------------------------
# 5. 탭(Tab)별 인터랙티브 시각화 구성
# ------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🌎 발생 및 지역 요약", "💰 예산 및 투자효율", "🎯 지역 소멸 및 정책 효과", "📑 원천 데이터 (Raw)", "📝 데이터 메타데이터", "🏆 지정축제 상세 프로필"])

# ====== TAB 1. 요약 및 지리적 분포 ======
with tab1:
    st.header("지역별 규모 및 개최 트렌드")
    c1, c2 = st.columns(2)
    
    with c1:
        # 연도별 건수
        annual_cnt = filtered_df['연도'].value_counts().reset_index()
        annual_cnt.columns = ['연도', '개최건수']
        fig1 = px.bar(annual_cnt.sort_values('연도'), x='연도', y='개최건수', color='개최건수',
                      title='연도별 축제 기획 건수 트렌드', color_continuous_scale='blues')
        st.plotly_chart(fig1, width='stretch')
    
    with c2:
        # 지역별 건수
        sido_cnt = filtered_df.groupby('광역시도').size().reset_index(name='개최건수').sort_values('개최건수', ascending=True)
        fig2 = px.bar(sido_cnt, y='광역시도', x='개최건수', orientation='h', title='광역시도별 개최 건수 비교',
                      color='개최건수', color_continuous_scale='sunset')
        st.plotly_chart(fig2, width='stretch')

    # 방문객 규모 등급 분포
    if '규모등급_5단계' in filtered_df.columns:
        fig3 = px.pie(filtered_df, names='규모등급_5단계', title='전국 축제 방문객 규모 등급 분포', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig3, width='stretch')


# ====== TAB 2. 예산 및 투자효율 ======
with tab2:
    st.header("예산 효율성 집중 분석")
    st.markdown("축제의 투입 예산 대비 산출(방문객)의 관계를 확인하세요. 아웃라이어가 너무 클 경우 플롯의 옵션에서 확대를 이용하세요.")
    
    # 방문객 vs 예산 산점도 (Log scale 권장, 마우스 오버 툴팁)
    # 0 인건 Scatter 에서 제외되거나 에러를 발생하므로 필터링
    scatter_df = filtered_df[(filtered_df['총방문객'] > 0) & (filtered_df['총예산_백만'] > 0)]
    
    fig_scatter = px.scatter(scatter_df, x="총방문객", y="총예산_백만", size="총방문객", color="광역시도",
                             hover_name="축제명", hover_data=["기초지자체", "1인당투입예산_원"],
                             title="방문객 규모와 투입예산 상관관계 (마우스 오버로 축제 확인)",
                             log_x=True, log_y=True, size_max=40)
    st.plotly_chart(fig_scatter, width='stretch')

    c1, c2 = st.columns(2)
    with c1:
        # 국비 지원 여부에 따른 의존도
        fig_box = px.box(filtered_df[filtered_df['국비의존도_재산출']>0], x="연도", y="국비의존도_재산출", color="연도",
                         title="연도별 국비 의존도(%) 분포 (미지원 제외)")
        st.plotly_chart(fig_box, width='stretch')
    with c2:
        # 전담조직 유무 vs 평균 투입 예산
        org_budget = filtered_df.groupby('전담조직_유무')['총예산_백만'].mean().reset_index()
        org_budget['전담조직_유무'] = org_budget['전담조직_유무'].map({0: '조직 없음', 1: '전담조직 존재'})
        fig_bar = px.bar(org_budget, x='전담조직_유무', y='총예산_백만', text_auto='.0f', title='전담조직 유무별 평균 투입 총예산(백만원)', color='전담조직_유무', color_discrete_sequence=['#94a3b8', '#3b82f6'])
        st.plotly_chart(fig_bar, use_container_width=True)


# ====== TAB 3. 지역 소멸 및 정책 효과 ======
with tab3:
    st.header("인구 정책 및 국가 지원 성과 비교")
    
    colA, colB = st.columns(2)
    with colA:
        if '인구감소지역_여부' in filtered_df.columns:
            decline_df = filtered_df.groupby('인구감소지역_여부')[['총방문객', '예산효율_명_백만']].mean().reset_index()
            decline_df['인구감소지역_여부'] = decline_df['인구감소지역_여부'].map({0:'일반 지역', 1:'89개 인구감소지역'})
            
            fig_dec = px.bar(decline_df, x='인구감소지역_여부', y='예산효율_명_백만', 
                             title='인구감소지역 지정 여부별 예산 효율 (명/백만원)',
                             color='인구감소지역_여부', color_discrete_sequence=['#10b981', '#f43f5e'])
            st.plotly_chart(fig_dec, use_container_width=True)

    with colB:
        if '문화관광축제_지정여부' in filtered_df.columns:
            cult_df = filtered_df.groupby('문화관광축제_지정여부')['총방문객'].mean().reset_index()
            cult_df['문화관광축제_지정여부'] = cult_df['문화관광축제_지정여부'].map({0:'비지정 일반축제', 1:'문체부 파급(문화관광축제)'})
            
            fig_cult = px.bar(cult_df, x='문화관광축제_지정여부', y='총방문객', 
                              title='국가 지정 문화관광축제의 방문객 동원력 비교 (명)',
                              color='문화관광축제_지정여부', color_discrete_sequence=['#cbd5e1', '#f59e0b'])
            st.plotly_chart(fig_cult, use_container_width=True)


# ====== TAB 4. 원천 데이터(Raw Data) 검색 및 열람 ======
with tab4:
    st.header("통계 데이터베이스 조회")
    st.markdown("대시보드 사이드바의 **검색 및 필터링 결과가 반영된 통계 원본 데이터**입니다. 항목을 정렬하거나 직접 스크롤하여 세부 데이터를 확인하실 수 있습니다.")
    
    # 텍스트 검색 기능
    search_keyword = st.text_input("🔍 특정 축제명 또는 텍스트 검색", "")
    if search_keyword:
        mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_keyword, case=False)).any(axis=1)
        search_result_df = filtered_df[mask]
    else:
        search_result_df = filtered_df

    # 다운로드하기 좋게 DataFrame 출력
    st.dataframe(search_result_df, use_container_width=True, height=500)
    
    # CSV 다운로드 버튼
    csv_data = search_result_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="📥 현재 조회중인 데이터 다운로드 (CSV)",
        data=csv_data,
        file_name='Filtered_Festival_Data.csv',
        mime='text/csv'
    )

# ====== TAB 5. 데이터 기준 및 메타데이터 ======
with tab5:
    st.header("📝 데이터 기준 및 파생지수 도출 기준")
    import preprocess_integration as pp
    
    st.subheader("1. 문체부 공식 지정 '문화관광축제' 적용 목록 (총 65여 개)")
    st.markdown("아래 목록은 2025 문화관광축제 평가보고서에서 추출하여 데이터 매핑에 활용한 공식 축제명입니다. 띄어쓰기 등 일부 차이를 무시하고 유연한 매칭(Fuzzy)을 적용하였습니다.")
    st.write(pp.festival_list)
    
    st.subheader("2. 행안부 고시 '인구감소지역' 리스트 (총 89개)")
    st.markdown("정부 행정안전부 지정 고시(제2024-15호 등) 기반, 지역축제의 기초지자체 이름과 아래 목록을 교차 대응하여 '인구감소지역_여부' 식별을 진행하였습니다.")
    
    # decline_areas 리스트 이쁘게 보여주기
    decline_df = pd.DataFrame(list(pp.decline_set), columns=['광역시도', '기초지자체']).sort_values(['광역시도', '기초지자체']).reset_index(drop=True)
    st.dataframe(decline_df, use_container_width=True, height=250)

    st.subheader("3. 파생 변수(지수) 연산 로직 (EDA 기초)")
    st.markdown("""
    대시보드와 분석 모델에서 활용된 **핵심 파생 변수**들은 원본 결측치/이상값 전처리 후 다음과 같이 도출되었습니다.
    *   **외국인 방문객 비중 (%)**: `(외국인 방문객 합계 / 방문객 합계) × 100`
    *   **국비 의존도 비율 (%)**: `(국비 지원액 / 총 예산) × 100` (예산이 0 또는 미기재 시 결측)
    *   **자체 예산 자립도 (%)**: `((지방비 + 기타 수입) / 총 예산) × 100`
    *   **행사 1인당 투입예산 (원)**: `(총예산(백만) × 1,000,000) / 총 방문객수` (방문객 규모의 경제 확인용)
    *   **예산투자 효율성 지수 (명/백만원)**: `총 방문객수 / 예산 총합(백만)` (효율이 낮을수록 비용만 많이 듦)
    *   **규모 등급(5단계)** & **투자효율 등급(5단계)**: 전체 샘플에 대해 방문객 수 및 예산투자 효율성을 백분위 기준 5등분(Pandas `qcut` 적용, 1등급이 최우수)
    """)

# ====== TAB 6. 문체부 지정축제 상세 프로필 ======
with tab6:
    st.header("🏆 문체부 지정 문화관광축제 상세 프로필 (개별 파생지수)")
    st.markdown("정부 공식 지정 축제들의 실적을 하나씩 상세히 들여다볼 수 있는 성적표 뷰(View)입니다.")
    
    # 1. 문체부 지정 축제들만 필터링
    designated_df = filtered_df[filtered_df['문화관광축제_지정여부'] == 1].copy()
    
    if designated_df.empty:
        st.warning("선택하신 필터(연도/지역 등) 조건에 해당하는 '문체부 지정 축제'가 없습니다. 좌측 사이드바 설정을 확인해주세요.")
    else:
        # 축제명 리스트 추출
        fest_names = sorted(designated_df['축제명'].dropna().unique().tolist())
        selected_fest = st.selectbox("🔎 열람하실 축제를 선택하세요:", fest_names)
        
        # 선택된 축제 데이터
        fest_data = designated_df[designated_df['축제명'] == selected_fest].iloc[0] # 가장 최근 또는 첫번째 행
        
        st.markdown("---")
        st.subheader(f"📍 {selected_fest} ({fest_data.get('연도', 'N/A')}년 기준)")
        st.markdown(f"**개최 지역:** {fest_data.get('광역시도', '')} {fest_data.get('기초지자체', '')} &nbsp;|&nbsp; **축제 유형:** {fest_data.get('유형', '기타')} &nbsp;|&nbsp; **역사:** {fest_data.get('연수구간', '정보없음')} &nbsp;|&nbsp; **전담조직 유무:** {'있음' if fest_data.get('전담조직_유무')==1 else '없음'}")
        
        # 성적표 (지수들)
        st.markdown("#### 📊 방문객 및 규모 실적")
        r1_c1, r1_c2, r1_c3 = st.columns(3)
        with r1_c1:
            st.metric(label="누적 방문객 규모", value=f"{fest_data.get('총방문객', 0):,.0f} 명")
        with r1_c2:
            st.metric(label="외국인 방문객 비중 (%)", value=f"{fest_data.get('외국인비중_재산출', 0):,.2f} %")
        with r1_c3:
             # 규모 등급
             st.metric(label="방문객 규모 등급", value=str(fest_data.get('규모등급_5단계', '미분류')))
             
        st.markdown("#### 💰 예산 구조 및 투자 효율 지수")
        r2_c1, r2_c2, r2_c3 = st.columns(3)
        with r2_c1:
            st.metric(label="투입 총 예산", value=f"{fest_data.get('총예산_백만', 0):,.0f} 백만원")
        with r2_c2:
            st.metric(label="국비 의존도 비율 (%)", value=f"{fest_data.get('국비의존도_재산출', 0):,.2f} %")
        with r2_c3:
            st.metric(label="자체 예산 자립도 (%)", value=f"{fest_data.get('자체자립도_비율', 0):,.2f} %")
            
        r3_c1, r3_c2, r3_c3 = st.columns(3)
        with r3_c1:
            st.metric(label="1인당 투입예산 (원)", value=f"{fest_data.get('1인당투입예산_원', 0):,.0f} 원")
        with r3_c2:
            st.metric(label="예산투자 효율성 (명/백만원)", value=f"{fest_data.get('예산효율_명_백만', 0):,.1f} 명")
        with r3_c3:
            st.metric(label="종합 투자효율 등급", value=str(fest_data.get('투자효율등급', '미분류')))
        
        # 부가 정보 (레이더 차트 혹은 추가 지표)
        # Radar Chart for performance comparison inside the subset of designated festivals
        st.markdown("#### ✨ 동급 지정 축제 평균 대비 퍼포먼스 (백분위 기준)")
        # Calculate percentiles for this specific festival against ALL designated_df
        def get_percentile(col, val):
            if pd.isna(val) or val == 0: return 0
            series = designated_df[col].dropna()
            if len(series) == 0: return 0
            return (series < val).mean() * 100
        
        categories = ['총 방문객', '총 예산', '예산투자효율(1백만원당 명)', '지방비/자체자립도', '외국인 유입력']
        selected_scores = [
            get_percentile('총방문객', fest_data.get('총방문객')),
            get_percentile('총예산_백만', fest_data.get('총예산_백만')),
            get_percentile('예산효율_명_백만', fest_data.get('예산효율_명_백만')),
            get_percentile('자체자립도_비율', fest_data.get('자체자립도_비율')),
            get_percentile('외국인비중_재산출', fest_data.get('외국인비중_재산출'))
        ]
        
        fig = go.Figure(data=go.Scatterpolar(
            r=selected_scores,
            theta=categories,
            fill='toself',
            name=selected_fest,
            line=dict(color='#3b82f6')
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=False,
            title='문체부 지정축제 그룹 내 지표별 백분위(Percentile, 100에 가까울수록 그룹 내 1등)'
        )
        st.plotly_chart(fig, use_container_width=True)

    
st.markdown("---")
st.markdown("Made with ✨ Streamlit & Plotly by Antigravity AI")


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

import os
import unicodedata

@st.cache_data
def load_data():
    # 현재 스크립트 앱(app_dashboard.py)이 실행된 위치를 기준으로 같은 폴더 내의 CSV 파일 조회
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # macOS(NFD)와 Linux/Windows(NFC) 간의 한글 자음/모음 분리 문제 해결
    target_filename = '지역축제_2023_2026_최종분석용_추가파생.csv'
    target_nfc = unicodedata.normalize('NFC', target_filename)
    
    csv_path = None
    for f in os.listdir(base_dir):
        if unicodedata.normalize('NFC', f) == target_nfc:
            csv_path = os.path.join(base_dir, f)
            break
    
    if csv_path is None or not os.path.exists(csv_path):
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🌎 발생 및 지역 요약", "💰 예산 및 투자효율", "🎯 지역 소멸 및 정책 효과", "📑 원천 데이터 (Raw)", "📝 데이터 메타데이터", "🏆 지정축제 상세 프로필", "🔍 축제 효과 분석 (A↔B)"])

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

    
# ====== TAB 7. 축제 효과 분석 (A↔B 매트릭스) ======
with tab7:
    st.header("🔍 축제 효과 분석 — 2축 매트릭스 & A↔B 성과 비교")
    st.markdown("문체부 2025 평가보고서 45개 축제 중 **정량 데이터 매칭 + 예산 2억 이상 + 실제 개최** 조건을 통과한 **38개 축제**를 예산효율(X) × 성장률(Y) 기준으로 배치한 매트릭스입니다.")

    # ── 38개 매트릭스 데이터
    matrix_raw = [
        ("위기","동래읍성역사축제","부산","동래구","예비","전통역사",1006,192381,191.2,-19.9,31),
        ("위기","정남진장흥물축제","전남","장흥군","현행","자연생태",2600,493165,189.7,-25.1,19),
        ("위기","광안리어방축제","부산","수영구","현행","전통역사",1527,174253,114.1,-29.7,25),
        ("위기","임실N치즈축제","전북","임실군","현행","지역특산물",1200,130422,108.7,-77.5,11),
        ("위기","광주김치축제","광주","(광역)","예비","지역특산물",600,57000,95.0,-16.5,32),
        ("위기","한산모시문화제","충남","서천군","현행","전통역사",1074,101000,94.0,-27.9,37),
        ("위기","영암왕인문화축제","전남","영암군","현행","전통역사",1760,163706,93.0,-90.8,29),
        ("위기","진안홍삼축제","전북","진안군","현행","지역특산물",1163,77066,66.3,-35.7,13),
        ("스타","보성다향대축제","전남","보성군","현행","지역특산물",1010,610000,604.0,193.0,51),
        ("스타","여주오곡나루축제","경기","여주시","예비","지역특산물",1050,408405,389.0,36.1,28),
        ("스타","청송사과축제","경북","청송군","예비","지역특산물",955,310317,324.9,25.6,22),
        ("스타","목포항구축제","전남","목포시","현행","문화예술",740,240000,324.3,0.0,20),
        ("스타","곡성세계장미축제","전남","곡성군","예비","자연생태",800,248982,311.2,3.0,28),
        ("스타","음성품바축제","충북","음성군","현행","전통역사",1100,328190,298.4,9.3,26),
        ("스타","수원화성문화제","경기","수원시","현행","전통역사",2443,709154,290.3,187.6,62),
        ("스타","괴산고추축제","충북","괴산군","예비","지역특산물",1090,311152,285.5,17.1,25),
        ("스타","부평풍물대축제","인천","부평구","현행","전통역사",840,230282,274.1,10.7,29),
        ("안정","소래포구축제","인천","남동구","예비","지역특산물",600,460000,766.7,-8.0,25),
        ("안정","강릉커피축제","강원","강릉시","현행","지역특산물",800,520000,650.0,-38.1,17),
        ("안정","태화강마두희축제","울산","중구","예비","전통역사",830,293000,353.0,-4.2,12),
        ("안정","부천국제만화축제","경기","부천시","예비","문화예술",300,100109,333.7,-27.9,28),
        ("안정","대구치맥페스티벌","대구","(광역)","현행","지역특산물",2380,745000,313.0,-4.0,13),
        ("안정","대구약령시한방문화축제","대구","(광역)","예비","전통역사",359,100602,280.2,-25.0,48),
        ("안정","장수한우랑사과랑축제","전북","장수군","예비","지역특산물",1220,320000,262.3,-46.7,19),
        ("안정","평창송어축제","강원","평창군","현행","자연생태",898,227725,253.6,-43.0,19),
        ("안정","대전효문화뿌리축제","대전","(광역)","예비","전통역사",1076,238864,222.0,-0.5,18),
        ("안정","논산딸기축제","충남","논산시","예비","지역특산물",1700,350000,205.9,-22.2,29),
        ("경계","김해분청도자기축제","경남","김해시","예비","전통역사",300,57833,192.8,57.0,30),
        ("경계","밀양아리랑축제","경남","밀양시","현행","전통역사",2590,416065,160.6,1.0,69),
        ("경계","울산옹기축제","울산","울주군","현행","전통역사",1140,160000,140.4,23.1,25),
        ("경계","철원한탄강얼음트레킹축제","강원","철원군","예비","자연생태",1199,150000,125.1,50.0,13),
        ("경계","인천펜타포트음악축제","인천","(광역)","현행","문화예술",2000,150000,75.0,0.0,21),
        ("경계","정선아리랑제","강원","정선군","현행","전통역사",2690,145364,54.0,29.9,50),
        ("경계","탐라문화제","제주","(광역)","예비","전통역사",1440,75101,52.2,35.4,64),
        ("경계","순창장류축제","전북","순창군","현행","지역특산물",1319,53459,40.5,0.0,20),
        ("경계","안성맞춤남사당바우덕이축제","경기","안성시","현행","전통역사",21826,603622,27.7,6.2,25),
    ]

    df_m = pd.DataFrame(matrix_raw, columns=["사분면","축제명","광역","기초","구분","유형","예산_백만","방문객","효율","성장률","운영연수"])

    crisis_news = {
        "임실N치즈축제":("2025년 개막 첫날 주차 대란·음식 품질 민원 폭주. 주차장 2시간 30분 대기, 안내 인력 전무 등 운영 역량 문제 노출.","https://www.munhwa.com/article/11538275"),
        "광주김치축제":("김치타운 하루 평균 40명 방문(연간 운영비 17억), 바가지 요금 SNS 논란, 혁신적 콘텐츠 부재 지적.","https://www.ohmynews.com/NWS_Web/View/at_pg.aspx?CNTN_CD=A0003070545"),
        "한산모시문화제":("2025년 자체 '지역사회 목소리를 듣다' 토론회 개최 — 운영 주체 스스로 공론화 필요성 인정.","https://hansanmosi.kr/"),
        "정남진장흥물축제":("2025년 방문객 전년 대비 18만명 추가 감소(약 50만명). 집중호우 외 콘텐츠 차별성 부족 지속.","https://v.daum.net/v/20250810181800248"),
        "광안리어방축제":("전담조직 없이 어방민속마을 조성과 일반행사 운영을 분리 외부 위탁 — 통합 운영 역량 부재.","https://www.suyeong.go.kr/festival/index.suyeong"),
        "동래읍성역사축제":("방문객 감소 대응으로 야외방탈출·몰입형 영상 신규 추가 시도. 외부 비판 기사 미발견이나 성장률 -19.9% 지속.","https://korean.visitkorea.or.kr/kfes/detail/fstvlDetail.do?fstvlCntntsId=78db2649-69d9-4710-a0d3-3c8f91c26720"),
        "진안홍삼축제":("외부 비판 보도 전무 — 홍보성 자료만 존재. 트로트 스타 의존형 구성 반복. 관심 부재 자체가 신호.","https://www.jinan.go.kr/festival/"),
        "영암왕인문화축제":("성장률 -90.8% — 구제역 취소 이력 이후 방문객 회복 실패. 29년 역사 대비 사실상 붕괴 수준.",""),
    }

    pairs = [
        {"rank":"1순위","note":"예산 17% 차이 · 운영연수 2년 차이 — 가장 조건이 통제된 비교",
         "A":"동래읍성역사축제","B":"부평풍물대축제",
         "point":"역사 재현형 vs 시민 퍼레이드형 — 콘텐츠 방식과 시민 참여 구조의 차이"},
        {"rank":"2순위","note":"예산 6% 차이 — 내륙 소도시 건강식품 소재 동일",
         "A":"진안홍삼축제","B":"괴산고추축제",
         "point":"자원 미활용 vs 유기농 특화 포지셔닝 — 콘텐츠 기획력 차이"},
        {"rank":"3순위","note":"예산 2% 차이 — 충청권 전통문화 동일",
         "A":"한산모시문화제","B":"음성품바축제",
         "point":"유네스코 무형유산 보유에도 외부 유치 실패 vs 독창적 서브컬처 현대화 성공"},
    ]

    # ── 섹션 1: 2축 산점도
    st.subheader("① 2축 매트릭스 전체 — 38개 축제 포지셔닝")
    color_map_m = {"위기":"#E74C3C","스타":"#27AE60","안정":"#E67E22","경계":"#95A5A6"}
    symbol_map_m = {"지역특산물":"circle","전통역사":"diamond","자연생태":"square","문화예술":"triangle-up"}

    fig_matrix = px.scatter(
        df_m, x="효율", y="성장률",
        color="사분면", color_discrete_map=color_map_m,
        symbol="유형", symbol_map=symbol_map_m,
        size="방문객", size_max=45,
        hover_name="축제명",
        hover_data={"예산_백만":True,"방문객":True,"효율":True,"성장률":True,"운영연수":True,"사분면":False},
        labels={"효율":"예산효율 (명/백만원)","성장률":"성장률 (%)"},
        height=520,
    )
    fig_matrix.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.6,
                         annotation_text="성장률 0% 기준", annotation_position="right")
    fig_matrix.add_vline(x=206, line_dash="dot", line_color="gray", opacity=0.6,
                         annotation_text="효율 206 기준", annotation_position="top right")
    fig_matrix.add_annotation(x=100, y=-65, text="🔴 위기 사분면 (표A)", showarrow=False, font=dict(color="#E74C3C", size=12))
    fig_matrix.add_annotation(x=480, y=160, text="⭐ 스타 사분면 (표B)", showarrow=False, font=dict(color="#27AE60", size=12))
    fig_matrix.add_annotation(x=480, y=-65, text="🟡 안정 사분면", showarrow=False, font=dict(color="#E67E22", size=12))
    fig_matrix.add_annotation(x=100, y=160, text="⬜ 경계 사분면", showarrow=False, font=dict(color="#888", size=12))
    fig_matrix.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_matrix, use_container_width=True)
    st.caption("※ 원 크기 = 방문객 수 / 모양 = 축제 유형 / X기준 206 = 38개 중앙값 / 효율·성장률 모두 전년 실적 기준")

    st.markdown("---")

    # ── 섹션 2: 개별 축제 성과 카드
    st.subheader("② 개별 축제 성과 카드")
    crisis_names = df_m[df_m["사분면"]=="위기"]["축제명"].tolist()
    others_names = [n for n in df_m["축제명"].tolist() if n not in crisis_names]
    sel_fest = st.selectbox("축제 선택 (위기 축제 상단 정렬)", crisis_names + others_names)
    row = df_m[df_m["축제명"]==sel_fest].iloc[0]

    quad_icon = {"위기":"🔴","스타":"⭐","안정":"🟡","경계":"⬜"}
    st.markdown(f"**{quad_icon.get(row['사분면'],'')} {row['사분면']} 사분면** | {row['유형']} | {row['광역']} {row['기초']} | {row['구분']} 축제")

    mc1,mc2,mc3,mc4 = st.columns(4)
    mc1.metric("예산",f"{row['예산_백만']:,} 백만원")
    mc2.metric("방문객 (前년)",f"{int(row['방문객']):,} 명")
    mc3.metric("예산효율",f"{row['효율']} 명/백만")
    mc4.metric("성장률",f"{row['성장률']}%",
               delta=f"{row['성장률']}%p",
               delta_color="inverse" if row["성장률"]<0 else "normal")

    col_radar, col_news = st.columns([1,1])
    with col_radar:
        def pct(col, val):
            s = df_m[col].dropna()
            if pd.isna(val) or len(s)==0: return 0
            return round((s<val).mean()*100, 1)

        r_cats = ["예산효율","방문객 규모","예산 규모","운영 역량(연수)"]
        r_scores = [pct("효율",row["효율"]), pct("방문객",row["방문객"]),
                    pct("예산_백만",row["예산_백만"]), pct("운영연수",row["운영연수"])]
        line_col = "#27AE60" if row["사분면"]=="스타" else "#E74C3C" if row["사분면"]=="위기" else "#E67E22"

        fig_r = go.Figure(go.Scatterpolar(
            r=r_scores+[r_scores[0]], theta=r_cats+[r_cats[0]],
            fill="toself", line_color=line_col, name=sel_fest
        ))
        fig_r.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,100])),
            showlegend=False, height=300,
            title=dict(text="38개 축제 내 백분위 (100=최상위)", font=dict(size=12))
        )
        st.plotly_chart(fig_r, use_container_width=True)

    with col_news:
        st.markdown("**🚨 성장 둔화 신호 / 외부 이슈**")
        if sel_fest in crisis_news:
            body, url = crisis_news[sel_fest]
            st.warning(body)
            if url: st.markdown(f"[📰 관련 기사 / 출처 바로가기]({url})")
        else:
            st.info("수집된 외부 이슈 없음. 성장률 및 매트릭스 위치를 참고하세요.")

        효율_rank = int((df_m["효율"]<row["효율"]).sum())+1
        성장_rank = int((df_m["성장률"]<row["성장률"]).sum())+1
        st.markdown(f"""
**38개 매트릭스 내 순위**
- 예산효율: **{효율_rank}위** / 38개
- 성장률: **{성장_rank}위** / 38개
- 운영연수: **{row['운영연수']}년** ({row['구분']} 축제)
        """)

    st.markdown("---")

    # ── 섹션 3: A↔B 페어링 비교
    st.subheader("③ 추천 A↔B 페어링 — 같은 조건, 다른 결과")
    st.markdown("예산·유형·소재가 유사한 조합을 비교하여 콘텐츠·전략 차이를 확인합니다.")

    for pair in pairs:
        a_name, b_name = pair["A"], pair["B"]
        row_a = df_m[df_m["축제명"]==a_name].iloc[0]
        row_b = df_m[df_m["축제명"]==b_name].iloc[0]
        예산차 = abs(row_a["예산_백만"]-row_b["예산_백만"])/max(row_a["예산_백만"],row_b["예산_백만"])*100
        효율배 = row_b["효율"]/row_a["효율"] if row_a["효율"]>0 else 0

        with st.expander(f"**{pair['rank']}** — {a_name} vs {b_name}　　{pair['note']}", expanded=(pair["rank"]=="1순위")):
            st.caption(f"📌 비교 포인트: {pair['point']}")
            bg1,bg2,bg3 = st.columns(3)
            bg1.metric("예산 차이",f"{예산차:.0f}%")
            bg2.metric("효율 배율",f"{효율배:.1f}배")
            bg3.metric("성장률 차이",f"{row_b['성장률']-row_a['성장률']:+.1f}%p")

            col_a, col_sep, col_b = st.columns([5,1,5])
            with col_a:
                st.markdown(f"#### 🔴 {a_name}")
                st.markdown(f"*{row_a['광역']} {row_a['기초']} · {row_a['유형']} · {row_a['운영연수']}년*")
                a1,a2 = st.columns(2)
                a1.metric("예산",f"{row_a['예산_백만']:,} 백만")
                a2.metric("방문객",f"{int(row_a['방문객']):,} 명")
                a3,a4 = st.columns(2)
                a3.metric("예산효율",f"{row_a['효율']} 명/백만")
                a4.metric("성장률",f"{row_a['성장률']}%",delta=f"{row_a['성장률']}%",delta_color="inverse")
                if a_name in crisis_news:
                    body, url = crisis_news[a_name]
                    st.error(f"⚠️ {body[:80]}{'...' if len(body)>80 else ''}")
                    if url: st.markdown(f"[출처]({url})")
            with col_sep:
                st.markdown("<div style='text-align:center;font-size:28px;padding-top:60px'>vs</div>", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"#### ⭐ {b_name}")
                st.markdown(f"*{row_b['광역']} {row_b['기초']} · {row_b['유형']} · {row_b['운영연수']}년*")
                b1,b2 = st.columns(2)
                b1.metric("예산",f"{row_b['예산_백만']:,} 백만")
                b2.metric("방문객",f"{int(row_b['방문객']):,} 명",delta=f"+{int(row_b['방문객']-row_a['방문객']):,}")
                b3,b4 = st.columns(2)
                b3.metric("예산효율",f"{row_b['효율']} 명/백만",delta=f"+{row_b['효율']-row_a['효율']:.1f}")
                b4.metric("성장률",f"{row_b['성장률']}%",delta=f"{row_b['성장률']:+.1f}%",delta_color="normal")

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(name=f"🔴 {a_name}",x=["예산효율(명/백만)","성장률(%)","운영연수(년)"],
                                     y=[row_a["효율"],row_a["성장률"],row_a["운영연수"]],
                                     marker_color="#E74C3C",text=[row_a["효율"],row_a["성장률"],row_a["운영연수"]],textposition="outside"))
            fig_bar.add_trace(go.Bar(name=f"⭐ {b_name}",x=["예산효율(명/백만)","성장률(%)","운영연수(년)"],
                                     y=[row_b["효율"],row_b["성장률"],row_b["운영연수"]],
                                     marker_color="#27AE60",text=[row_b["효율"],row_b["성장률"],row_b["운영연수"]],textposition="outside"))
            fig_bar.update_layout(barmode="group",height=300,showlegend=True,
                                  legend=dict(orientation="h",yanchor="bottom",y=1.02),
                                  margin=dict(t=40,b=20))
            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # ── 섹션 4: 나머지 페어링 적절성 요약
    st.subheader("④ 나머지 페어링 적절성 요약")
    summary_df = pd.DataFrame({
        "페어링":["임실N치즈 vs 청송사과","정남진장흥물 vs 곡성세계장미","광주김치 vs 보성다향","광안리어방 vs 수원화성"],
        "분류":["조건부 사용","조건부 사용","비교 지양","비교 지양"],
        "예산차이(%)": [20,69,41,37],
        "효율배율(B÷A)":[3.0,1.6,6.4,2.5],
        "주요 제한 사유":[
            "임실N치즈 방문객 수치 5배 괴리(PDF 61만 vs DB 13만) — 데이터 검증 선행 필요",
            "예산 3.3배 차이 + 방문객 역전(A>B) — 예산 효율성 논의로만 활용",
            "효율 6.4배 차이 + 운영연수 19년 차이 — 광역시 vs 소도시 구조 상이",
            "운영연수 37년 차이(25년 vs 62년) — 성숙도·브랜드 자산 차원이 다름",
        ]
    })

    def highlight_summary(row):
        if row["분류"]=="비교 지양":
            return ["background-color:#fff0f0;color:#8B0000"]*len(row)
        elif row["분류"]=="조건부 사용":
            return ["background-color:#fffbeb;color:#7c4f00"]*len(row)
        return [""]*len(row)

    st.dataframe(summary_df.style.apply(highlight_summary, axis=1), use_container_width=True, hide_index=True)
    st.caption("🔴 비교 지양: 조건 차이가 커서 인과 추론 어려움 / 🟡 조건부 사용: 정성 분석 중심으로 제한적 활용")


st.markdown("---")
st.markdown("Made with ✨ Streamlit & Plotly by Antigravity AI")

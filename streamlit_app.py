import streamlit as st
import json
import io
from logic import get_unfollowers_data, parse_instagram_json

# ── 페이지 설정 ───────────────────────────────────────────────
st.set_page_config(
    page_title="Instagram Unfollower Tracker",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 커스텀 CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* 배경 */
.stApp {
    background: linear-gradient(135deg, #0d0d0d 0%, #1a0a1e 100%);
}

/* 헤더 그라디언트 텍스트 */
.grad-title {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0;
}

/* 업로드 박스 */
.upload-card {
    background: #1a1a1a;
    border: 1px solid #2d2d2d;
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}

/* 통계 카드 */
.stat-card {
    background: #1a1a1a;
    border: 1px solid #2d2d2d;
    border-radius: 12px;
    padding: 16px 12px;
    text-align: center;
}
.stat-number {
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0;
}
.stat-label {
    font-size: 0.78rem;
    color: #888;
    margin: 0;
}

/* 결과 탭 */
.user-row {
    background: #1a1a1a;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 4px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border: 1px solid #2a2a2a;
}
.user-row:hover { border-color: #e1306c44; }

.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
}

/* Streamlit 기본 요소 커스터마이징 */
.stFileUploader > div {
    background: #1a1a1a !important;
    border: 1px dashed #444 !important;
    border-radius: 12px !important;
}
div[data-testid="stFileUploaderDropzone"] {
    background: #1a1a1a !important;
}
.stButton > button {
    background: linear-gradient(90deg, #e1306c, #833ab4);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 32px;
    font-size: 1rem;
    font-weight: 700;
    width: 100%;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }
.stButton > button:disabled { opacity: 0.4; cursor: not-allowed; }
.stTabs [data-baseweb="tab"] {
    color: #888;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    color: #e1306c !important;
    border-bottom-color: #e1306c !important;
}

/* 사이드바 스타일 */
[data-testid="stSidebar"] {
    background: #111111;
}
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e1306c;
}

/* 스텝 배지 */
.step-badge {
    display: inline-block;
    background: #e1306c;
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 6px;
    margin-right: 8px;
}
</style>
""", unsafe_allow_html=True)


# ── 헤더 ─────────────────────────────────────────────────────
st.markdown('<p class="grad-title">📸 Instagram Unfollower Tracker</p>', unsafe_allow_html=True)
st.markdown('<p style="color:#888; margin-top:4px;">Instagram 공식 데이터 내보내기로 언팔로워를 찾아보세요. 계정 정보는 서버에 저장되지 않습니다.</p>', unsafe_allow_html=True)
st.markdown("---")


# ── 사이드바: 사용 방법 (2025년 최신 Instagram UI 기준) ──────
with st.sidebar:
    st.markdown("### 📖 사용 방법")
    st.markdown("""
**① Instagram 앱에서 데이터 요청:**

<span class="step-badge">Step 1</span> 프로필 탭(우측 하단) → 우측 상단 **메뉴(☰)**

<span class="step-badge">Step 2</span> **설정 및 개인정보** → 하단 **계정 센터**

<span class="step-badge">Step 3</span> **내 정보 및 권한** → **내 정보 다운로드** → **다운로드 또는 전송**

<span class="step-badge">Step 4</span> 계정 선택 → **일부 정보 선택** → **팔로워 및 팔로잉**만 체크

<span class="step-badge">Step 5</span> 형식: **JSON** / 기간: **전체 기간** → **파일 만들기**

<span class="step-badge">Step 6</span> 알림·이메일 수신 후 같은 메뉴에서 **ZIP 다운로드 → 압축 해제**

<span class="step-badge">Step 7</span> `connections/followers_and_following/` 폴더에서  
`followers_1.json` 과 `following.json` 두 파일을 **드래그하거나 클릭해서 업로드**

> ⚠️ 파일 준비까지 최대 48시간 소요될 수 있습니다.
""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("🔒 **개인정보 안내**  \n업로드한 파일은 분석 후 즉시 삭제되며 서버에 저장되지 않습니다.")

    st.markdown("---")
    # 새 분석 시작 버튼 (사이드바에서도 초기화 가능)
    if st.button("🔄 새 분석 시작", key="sidebar_reset"):
        for key in ["results"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


# ── 파일 업로드 ───────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📂 followers_1.json")
    st.caption("나를 팔로우하는 사람 목록 — 드래그하거나 클릭해서 업로드")
    followers_file = st.file_uploader(
        "followers_1.json",
        type=["json"],
        key="followers",
        label_visibility="collapsed",
        help="ZIP 압축 해제 후 connections/followers_and_following/followers_1.json",
    )
    if followers_file:
        st.success(f"✅ {followers_file.name} 선택됨")

with col2:
    st.markdown("#### 📂 following.json")
    st.caption("내가 팔로우하는 사람 목록 — 드래그하거나 클릭해서 업로드")
    following_file = st.file_uploader(
        "following.json",
        type=["json"],
        key="following",
        label_visibility="collapsed",
        help="ZIP 압축 해제 후 connections/followers_and_following/following.json",
    )
    if following_file:
        st.success(f"✅ {following_file.name} 선택됨")


# ── 분석 버튼 ─────────────────────────────────────────────────
st.markdown("")
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    analyze_clicked = st.button(
        "🔍  분석 시작",
        disabled=(followers_file is None or following_file is None),
    )


# ── 분석 실행 ─────────────────────────────────────────────────
def parse_uploaded(file):
    """업로드된 파일 객체에서 유저명 집합을 반환."""
    raw = json.loads(file.read().decode("utf-8"))
    usernames = set()
    items = []
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict):
        for val in raw.values():
            if isinstance(val, list):
                items = val
                break

    for item in items:
        if not isinstance(item, dict):
            if isinstance(item, str):
                usernames.add(item.strip())
            continue
        found = False
        if 'string_list_data' in item:
            sld = item['string_list_data']
            if isinstance(sld, list) and sld:
                v = sld[0].get('value', '').strip()
                if v:
                    usernames.add(v)
                    found = True
        if found:
            continue
        for key in ('value', 'title', 'username'):
            if key in item:
                v = str(item[key]).strip()
                if v:
                    usernames.add(v)
                    break
        if 'user' in item and isinstance(item['user'], dict):
            v = item['user'].get('username', '').strip()
            if v:
                usernames.add(v)
    return usernames


if analyze_clicked:
    # 이전 결과 초기화
    if "results" in st.session_state:
        del st.session_state["results"]

    with st.spinner("분석 중..."):
        try:
            followers_file.seek(0)
            following_file.seek(0)
            followers = parse_uploaded(followers_file)
            following_file.seek(0)
            following = parse_uploaded(following_file)

            if not followers and not following:
                st.error("두 파일 모두 유저를 파싱하지 못했습니다. 올바른 Instagram JSON 파일인지 확인하세요.")
                st.stop()

            followers_l = {u.lower(): u for u in followers}
            following_l = {u.lower(): u for u in following}
            f_set, g_set = set(followers_l.keys()), set(following_l.keys())

            unfollowers = sorted([following_l[k] for k in g_set - f_set])
            fans        = sorted([followers_l[k] for k in f_set - g_set])
            mutuals     = sorted([followers_l[k] for k in f_set & g_set])

            st.session_state["results"] = {
                "unfollowers": unfollowers,
                "fans": fans,
                "mutuals": mutuals,
                "following_count": len(following),
                "followers_count": len(followers),
            }
        except Exception as e:
            st.error(f"❌ 분석 실패: {e}")
            st.stop()


# ── 결과 표시 ─────────────────────────────────────────────────
if "results" in st.session_state:
    r = st.session_state["results"]

    st.markdown("---")
    st.markdown("### 📊 분석 결과")

    # 통계 카드 행
    c1, c2, c3, c4, c5 = st.columns(5)
    stats = [
        (c1, str(r["following_count"]),    "팔로잉",    "#4fc3f7"),
        (c2, str(r["followers_count"]),    "팔로워",    "#bc1888"),
        (c3, str(len(r["unfollowers"])),   "언팔로워",  "#e1306c"),
        (c4, str(len(r["fans"])),          "나만의 팬", "#f77f00"),
        (c5, str(len(r["mutuals"])),       "맞팔",      "#25d366"),
    ]
    for col, num, label, color in stats:
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <p class="stat-number" style="color:{color}">{num}</p>
                <p class="stat-label">{label}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("")

    # 결과 다운로드 버튼
    txt_content = (
        "=== Instagram Unfollower 분석 결과 ===\n\n"
        f"팔로잉: {r['following_count']}명\n"
        f"팔로워: {r['followers_count']}명\n"
        f"맞팔:   {len(r['mutuals'])}명\n\n"
        f"--- 언팔로워 ({len(r['unfollowers'])}명) ---\n"
        + ("\n".join(r["unfollowers"]) or "(없음)") + "\n\n"
        f"--- 나만의 팬 ({len(r['fans'])}명) ---\n"
        + ("\n".join(r["fans"]) or "(없음)") + "\n"
    )
    _, dl_col, _ = st.columns([2, 1, 2])
    with dl_col:
        st.download_button(
            label="💾  결과 TXT 다운로드",
            data=txt_content.encode("utf-8"),
            file_name="instagram_unfollowers.txt",
            mime="text/plain",
        )

    # 탭: 언팔로워 / 팬 / 맞팔
    tab1, tab2, tab3 = st.tabs([
        f"🚫 언팔로워 ({len(r['unfollowers'])}명)",
        f"⭐ 나만의 팬 ({len(r['fans'])}명)",
        f"🤝 맞팔 ({len(r['mutuals'])}명)",
    ])

    def render_list(tab, users, accent, empty_msg):
        with tab:
            if not users:
                st.info(empty_msg)
                return
            search = st.text_input("🔍 검색", key=f"search_{accent}", placeholder="유저명 검색...")
            filtered = [u for u in users if search.lower() in u.lower()] if search else users
            st.caption(f"{len(filtered)}명 표시 중")
            for u in filtered:
                st.markdown(
                    f'<div class="user-row">'
                    f'<span style="color:#ccc">@{u}</span>'
                    f'<a href="https://www.instagram.com/{u}/" target="_blank" '
                    f'style="color:{accent};font-size:0.8rem;text-decoration:none;">프로필 보기 →</a>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    render_list(tab1, r["unfollowers"], "#e1306c", "언팔로워가 없습니다! 🎉 모두 맞팔이에요.")
    render_list(tab2, r["fans"],        "#f77f00", "나만의 팬이 없습니다.")
    render_list(tab3, r["mutuals"],     "#25d366", "맞팔인 친구가 없습니다.")

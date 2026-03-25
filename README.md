# 📸 Instagram Unfollower Tracker

나를 팔로우하지 않는 사람(언팔로워)을 찾아주는 웹앱입니다.  
Instagram 공식 데이터 내보내기 JSON 파일만 사용하므로 **계정 정보 입력이 필요 없습니다.**

🔗 **[온라인에서 바로 사용하기](https://your-app.streamlit.app)** ← 배포 후 주소 입력

---

## 사용 방법

1. Instagram 앱 → 프로필 → 메뉴(☰) → 설정 및 개인정보 → 계정 센터
2. 내 정보 및 권한 → 내 정보 다운로드 → 일부 정보 선택
3. **팔로워 및 팔로잉** 체크 → 형식: **JSON** → 요청
4. 이메일로 온 링크에서 ZIP 다운로드 → 압축 해제
5. `connections/followers_and_following/` 폴더에서  
   `followers_1.json`과 `following.json`을 웹앱에 업로드

---

## 로컬 실행

```bash
pip install streamlit
streamlit run streamlit_app.py
```

## 기능

- 언팔로워 / 나만의 팬 / 맞팔 분석
- 유저명 검색
- 프로필 바로가기 링크
- 결과 TXT 파일 다운로드
- 업로드 파일 서버 미저장 (개인정보 안전)

# 📡 NAS / 외부 URL 배포 가이드

Instagram Unfollower Tracker를 NAS(시놀로지, QNAP 등)나 서버에 올려서
외부에서 URL로 접근하는 방법입니다.

---

## 방법 1 — NAS (시놀로지 Synology 기준)

### 준비사항
- 시놀로지 NAS에 Python 3 패키지 설치 (패키지 센터에서 "Python 3" 설치)
- SSH 접속 활성화 (제어판 → 터미널 및 SNMP)

### 설치 및 실행

```bash
# SSH로 NAS 접속
ssh admin@<NAS-IP>

# 프로젝트 폴더로 이동 (예: /volume1/homes/admin/)
cd /volume1/homes/admin/
git clone https://github.com/loves1005/instagram-unfollower-tracker.git
cd instagram-unfollower-tracker

# pip로 패키지 설치
pip3 install -r requirements.txt

# Streamlit 서버 실행 (외부 접근용)
streamlit run streamlit_app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.headless true \
  --browser.gatherUsageStats false
```

### 외부 접속 URL
- 내부 네트워크: `http://<NAS-IP>:8501`
- 외부 접속: 공유기에서 포트포워딩 8501 설정 후 `http://<공인IP>:8501`
- DDNS 사용 시: `http://<DDNS주소>:8501`

---

## 방법 2 — 자동 재시작 (NAS 재부팅 후에도 유지)

시놀로지 작업 스케줄러에 등록하거나, `/etc/rc.local`에 추가:

```bash
nohup streamlit run /volume1/homes/admin/instagram-unfollower-tracker/streamlit_app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.headless true \
  --browser.gatherUsageStats false &
```

또는 `start_streamlit.sh` 스크립트로 관리:

```bash
#!/bin/bash
cd /volume1/homes/admin/instagram-unfollower-tracker
nohup streamlit run streamlit_app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.headless true \
  --browser.gatherUsageStats false \
  > /tmp/streamlit.log 2>&1 &
echo "Streamlit 시작됨 (PID: $!)"
```

---

## 방법 3 — 무료 클라우드 배포 (Streamlit Community Cloud)

1. GitHub에 이 프로젝트 push
2. [share.streamlit.io](https://share.streamlit.io) 접속
3. GitHub 계정 연결 → 저장소 선택 → `streamlit_app.py` 지정
4. Deploy! → `https://<앱이름>.streamlit.app` 같은 URL 발급

> ⚠️ Community Cloud는 무료지만 슬립 모드(15분 미사용 시 절전)가 있습니다.  
> 항상 켜두려면 NAS 또는 VPS 서버를 권장합니다.

---

## 방법 4 — Windows PC에서 로컬 실행 후 외부 공유

```powershell
# PowerShell에서 실행
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

같은 공유기 내부에서는 `http://<PC-IP>:8501`로 접속 가능.
외부 접속은 공유기 포트포워딩 필요.

---

## 보안 주의사항

- 외부에 공개 시 HTTPS 설정 권장 (Nginx 리버스 프록시 + Let's Encrypt)
- 개인 Instagram 데이터는 브라우저 메모리에서만 처리되며 서버에 저장되지 않음
- 불특정 다수에게 공개하지 말고 개인/가족 용도로만 사용 권장

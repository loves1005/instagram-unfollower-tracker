@echo off
chcp 65001 > nul
echo.
echo === GitHub 업로드 시작 ===
echo.

cd /d "c:\Users\loves\Crawling_mer\InstagramUnfollowerTracker"

echo [1/5] git init...
git init

echo [2/5] 기존 remote 제거 후 재등록...
git remote remove origin 2>nul
git remote add origin https://github.com/loves1005/instagram-unfollower-tracker.git

echo [3/5] 파일 추가...
git add .

echo [4/5] 커밋...
git commit -m "Instagram Unfollower Tracker - Streamlit web app"

echo [5/5] GitHub에 push...
git branch -M main
git push -u origin main

echo.
echo === 완료! GitHub 저장소를 새로고침하세요 ===
echo https://github.com/loves1005/instagram-unfollower-tracker
echo.
pause

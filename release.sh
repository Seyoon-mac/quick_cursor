#!/usr/bin/env bash
# 사용법: ./release.sh 1.1 "상대 매핑 배율 조정"
set -e
VER="$1"; MSG="$2"
if [ -z "$VER" ] || [ -z "$MSG" ]; then
  echo '사용법: ./release.sh <버전> "<변경 내용>"'; exit 1
fi
# index.html 안의 APP_VERSION 값을 새 버전으로 교체 (macOS sed)
sed -i '' "s/const APP_VERSION = '[^']*'/const APP_VERSION = '$VER'/" index.html
grep -q "const APP_VERSION = '$VER'" index.html || { echo "APP_VERSION 교체 실패"; exit 1; }
git pull --rebase
git add -A
git commit -m "v$VER: $MSG"
git tag "v$VER"
git push && git push --tags
echo "v$VER 배포 완료. 1~2분 뒤 https://seyoon-mac.github.io/quick_cursor/ 에 반영됩니다."

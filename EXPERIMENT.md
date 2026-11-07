# QuickCursor 실험 앱 작업 문서

CSE333 HCI Team 8 프로젝트 QuickCursor의 iPad 실험용 웹앱입니다. 이 문서는 VS Code에서 이어서 개발하고, 새 버전을 터미널에서 바로 커밋·배포하기 위한 기준 문서입니다.

## 1. 프로젝트 개요

QuickCursor는 엄지 근처의 작은 패드로 화면 전체의 커서를 조작하는 기법입니다. 패드의 위치가 화면의 같은 상대 위치에 대응합니다(Full-Screen Spatial Mapping).

| 항목 | 내용 |
|---|---|
| 저장소 | https://github.com/Seyoon-mac/quick_cursor |
| 실험 주소 | https://seyoon-mac.github.io/quick_cursor/ |
| 결과 저장 | Google Apps Script 웹 앱 → Google Drive `QuickCursor_Results` 폴더 |
| 실행 기기 | iPad (Safari, 홈 화면에 추가해 전체 화면으로 실행) |

## 2. 실험 설계

**자세**: 참가자는 펼친 기기의 양옆을 양손으로 잡은 자세에서 시작합니다.

**사전 설문**: 터치스크린을 주로 쓰는 손(오른손 / 왼손 / 양손).

**조건 5개** (참가자 내 설계)

| 코드 | 이름 | 설명 |
|---|---|---|
| DT | Direct Touch | 기준 조건. 목표를 손가락으로 직접 누름 |
| REL_L | Relative – Left Hand | 왼쪽 아래 패드, 트랙패드식 상대 이동 |
| REL_R | Relative – Right Hand | 오른쪽 아래 패드, 상대 이동 |
| ABS_L | Absolute – Left Hand | 왼쪽 아래 패드, 패드 위치 ↔ 화면 위치 1:1 대응 |
| ABS_R | Absolute – Right Hand | 오른쪽 아래 패드, 절대 매핑 |

**조건 순서**: 참가자 번호의 숫자로 균형 라틴방격(Williams design, 10가지 순서)을 배정합니다. 번호에 숫자가 없으면 무작위로 정합니다.

**과제**: 9×6 회색 격자에서 빨간 목표 칸을 선택합니다.
- 조건마다 안내 → 연습(기본 5회) → 본 실험 순서로 진행합니다.
- 본 실험은 모든 칸이 한 번씩 나오며, 같은 칸이 연속으로 나오지 않게 섞습니다.
- 기본값은 조건당 54회, 전체 270회입니다.

**선택 방식**(패드 조건): 기본값은 반대 손으로 클릭 버튼을 누르는 방식입니다. 설정에서 "손가락 떼면 선택"으로 바꿀 수 있습니다.

**사후 설문**: 5개 조건을 편한 순서대로 순위를 매깁니다(1 = 가장 편함).

**분석 계획**: 조건별로 격자 위치에 따른 히트맵 두 가지를 그립니다.
- 선택 속도(`movement_time_ms`)
- 자세 변경 빈도(`grip_marks`)

## 3. 파일 구조

```
quick_cursor/
├── index.html      # 실험 앱 전체 (HTML + CSS + JS 한 파일, 외부 의존성 없음)
├── EXPERIMENT.md   # 이 문서
├── release.sh      # 버전 올리기 + 커밋 + push
├── .gitignore      # Code.gs 등 제외
└── README.md
```

`Code.gs`(Apps Script)는 **저장소에 올리지 않습니다.** 안에 `TOKEN`이 들어 있고 저장소가 Public이기 때문입니다. 올려야 한다면 `TOKEN = 'CHANGE_ME'`로 바꾼 사본만 올리세요.

### index.html 주요 구성

| 부분 | 역할 |
|---|---|
| `COND` | 조건 정의 (이름, 매핑 방식, 패드 쪽 손) |
| `DEF` / `CFG` | 기본 설정값과 기기에 저장된 설정 (`localStorage: qc_cfg`) |
| `williams()`, `orderFor()` | 조건 순서 배정 |
| `layout()` | 격자, 패드, 클릭 버튼 배치. 패드 세로 길이 = 가로 × 화면 비율 |
| `presentTrial()`, `select()`, `complete()` | 시행 진행, 판정, 기록 |
| pointer 이벤트 처리부 | 멀티터치 처리. 패드 손가락은 `run.padId`로, 클릭 버튼은 별도 포인터로 추적 |
| `upload()`, `filesFor()` | Drive 업로드. 조건이 끝날 때마다 누적본을 덮어씀 |
| `COLS` | trials CSV 열 순서 |

세션 데이터는 `localStorage`의 `qc_ses_<세션ID>`에 매 시행마다 저장됩니다. 그래서 앱이 꺼져도 "이어서 진행"이 가능합니다.

## 4. 기록 데이터

Drive에는 참가자마다 `QuickCursor_<참가자>_<시각>_trials.csv`, `_survey.csv`, `_meta.json` 세 파일이 생깁니다.

trials.csv의 주요 열은 다음과 같습니다. 좌표 단위는 iPad의 pt(CSS px)입니다.

| 열 | 의미 |
|---|---|
| `condition`, `mapping`, `pad_hand`, `condition_position` | 조건 코드, 매핑 방식, 패드 쪽 손, 수행 순서 |
| `block`, `trial` | `practice` / `main`, 블록 안 시행 번호 |
| `target_row`, `target_col` | 목표 칸 위치 (1부터) |
| `movement_time_ms` | 목표가 나타난 뒤 정확히 선택할 때까지 걸린 시간 |
| `reaction_time_ms` | 목표가 나타난 뒤 첫 터치까지 걸린 시간 |
| `errors`, `first_attempt_hit`, `miss_points` | 오선택 횟수, 첫 시도에 맞혔는지, 오선택 좌표 |
| `pad_touches` | 패드에 손가락을 댄 횟수 (클러칭) |
| `cursor_path_px` | 커서 이동 거리 |
| `stray_touches` | 패드·클릭 버튼 밖을 누른 횟수 |
| `grip_marks` | 실험자가 키보드 G 키로 표시한 자세 변경 횟수 |
| `gain`, `select_mode`, `pad_w`, `pad_h` | 해당 시행에 적용된 설정 |

## 5. 처음 한 번: VS Code로 가져오기

```bash
cd ~/Documents            # 원하는 위치
git clone https://github.com/Seyoon-mac/quick_cursor.git
cd quick_cursor
code .                    # VS Code로 열기
```

`code` 명령이 없으면 VS Code에서 `Cmd+Shift+P` → **Shell Command: Install 'code' command in PATH**를 실행하세요.

push할 때 GitHub 로그인을 요구하면 둘 중 하나로 인증합니다.

```bash
brew install gh && gh auth login     # 추천: 브라우저로 로그인
```

`gh`를 쓰지 않으면 GitHub → Settings → Developer settings에서 Personal access token을 만들어 비밀번호 대신 입력합니다.

## 6. 개발하면서 로컬에서 테스트하기

```bash
python3 -m http.server 8000
```

- Mac 브라우저에서는 `http://localhost:8000`으로 엽니다.
- iPad에서는 Mac과 같은 Wi‑Fi에 연결하고 `http://<Mac IP>:8000`으로 엽니다. Mac IP는 `ipconfig getifaddr en0`으로 확인합니다.

마우스로도 동작은 확인할 수 있지만, 멀티터치(패드를 누른 채 클릭)는 iPad에서 확인해야 합니다. 빠른 테스트를 하려면 실험 설정에서 격자를 3×2, 연습 1회로 줄이세요.

## 7. 새 버전 커밋·배포

### 매번 하는 기본 흐름

```bash
git pull                                  # 다른 팀원 변경 먼저 받기
# ... index.html 수정 ...
git add index.html
git commit -m "v1.1: 상대 매핑 기본 배율 3 → 2.5"
git push
```

push하면 GitHub Pages가 1~2분 안에 자동으로 다시 배포합니다. 진행 상황은 저장소의 **Actions** 탭에서 볼 수 있습니다.

### 한 줄로 버전 올리고 배포하기 (release.sh)

저장소 루트의 `release.sh`가 버전 교체, 커밋, 태그, push를 한 번에 합니다. 처음 한 번 `chmod +x release.sh`로 실행 권한을 주세요. 내용은 다음과 같습니다.

```bash
#!/usr/bin/env bash
# 사용법: ./release.sh 1.1 "상대 매핑 배율 조정"
set -e
VER="$1"; MSG="$2"
if [ -z "$VER" ] || [ -z "$MSG" ]; then
  echo '사용법: ./release.sh <버전> "<변경 내용>"'; exit 1
fi
# index.html 안의 APP_VERSION 값을 새 버전으로 교체
sed -i '' "s/const APP_VERSION = '[^']*'/const APP_VERSION = '$VER'/" index.html
grep -q "const APP_VERSION = '$VER'" index.html || { echo "APP_VERSION 교체 실패"; exit 1; }
git pull --rebase
git add -A
git commit -m "v$VER: $MSG"
git tag "v$VER"
git push && git push --tags
echo "v$VER 배포 완료. 1~2분 뒤 https://seyoon-mac.github.io/quick_cursor/ 에 반영됩니다."
```

사용 예시:

```bash
./release.sh 1.1 "클릭 버튼 투명도 조정"
```

`index.html`에는 `const APP_VERSION = '1.0';`이 들어 있습니다. 스크립트가 이 값을 바꿔 주고, 바뀐 버전은 첫 화면 제목 아래와 `_meta.json`의 `appVersion`에 기록됩니다. 그래서 파일럿과 본 실험 데이터를 구분할 수 있습니다.

### 버전 규칙

| 변경 종류 | 버전 | 예 |
|---|---|---|
| 문구, 색, 버그 수정 (데이터 형식 그대로) | 1.0 → 1.1 | 안내 문구 수정 |
| 측정 방식이나 CSV 열이 바뀜 | 1.x → 2.0 | 새 열 추가, 판정 방식 변경 |

**본 실험을 시작한 뒤에는 실험 조건에 영향을 주는 변경을 하지 않습니다.** 꼭 바꿔야 하면 메이저 버전을 올리고, 그 전 참가자 데이터와 분리해서 분석합니다.

### 되돌리기

```bash
git log --oneline              # 이전 커밋 확인
git revert <커밋해시>           # 해당 변경을 되돌리는 새 커밋 생성
git push
```

## 8. iPad에 새 버전 반영하기

홈 화면 앱은 이전 버전을 캐시하고 있을 수 있습니다. 배포 후에는 이렇게 확인하세요.

1. 홈 화면 앱을 완전히 종료합니다(앱 전환기에서 위로 밀기).
2. 다시 실행합니다.
3. 반영이 안 됐으면 Safari에서 같은 주소를 열고 새로고침한 뒤 다시 실행합니다.

실험 설정, Drive 주소, 토큰은 기기의 `localStorage`에 있으므로 새 버전을 배포해도 유지됩니다.

## 9. Apps Script 수신기

- Drive 연결은 iPad 웹앱의 **Google Drive 연결**에서 설정합니다. `…/exec`로 끝나는 웹 앱 URL과 토큰을 넣습니다.
- `Code.gs`를 수정했다면 Apps Script 편집기에서 **배포 관리 → 수정 → 버전: 새 버전**으로 다시 배포합니다. 이렇게 하면 URL이 유지됩니다.
- 앱에서 보내는 데이터 형식은 다음과 같습니다.
  - 업로드: `{ token, files: [{ name, content, mimeType }] }`
  - 연결 확인: `{ token, ping: true }`
- 수신기는 같은 이름의 파일이 있으면 내용을 덮어씁니다.

## 10. 남은 할 일

- [ ] 첫 커밋 후 `git tag v1.0 && git push --tags`
- [ ] 파일럿 테스트: 패드 크기, 상대 매핑 배율, 연습 횟수 조정
- [ ] 자세 변경 측정 방식 확정 (실험자 G 키 / 영상 코딩)
- [ ] 결과 CSV → 조건별 히트맵 분석 스크립트
- [ ] 본 실험 전에 버전 고정

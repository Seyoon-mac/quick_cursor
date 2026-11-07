#!/usr/bin/env python3
"""
QuickCursor 히트맵 분석
  python3 heatmap.py                       # 현재 폴더의 *_trials.csv 전부
  python3 heatmap.py P01_*.csv P02_*.csv   # 파일 지정

출력: heatmap_YYYYMMDD_HHMMSS.xlsx
  - 조건별 시트: 셀당 평균 선택 시간 (초, 소숫점 4자리)
  - 초록 = 빠름 / 빨강 = 느림

필요 패키지: pip install pandas openpyxl
"""

import sys
import glob
from datetime import datetime

try:
    import pandas as pd
    import numpy as np
    import openpyxl
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError as e:
    print(f"패키지 오류: {e}")
    print("pip install pandas openpyxl  를 먼저 실행하세요.")
    sys.exit(1)

CONDITIONS = ['DT', 'REL_L', 'REL_R', 'ABS_L', 'ABS_R']
COND_NAMES = {
    'DT':    'DT – Direct Touch (직접 터치)',
    'REL_L': 'REL_L – Relative Left (상대, 왼손)',
    'REL_R': 'REL_R – Relative Right (상대, 오른손)',
    'ABS_L': 'ABS_L – Absolute Left (절대, 왼손)',
    'ABS_R': 'ABS_R – Absolute Right (절대, 오른손)',
}


def heat_color(t: float) -> str:
    """t: 0.0(빠름, 초록) → 1.0(느림, 빨강). 반환: RRGGBB hex."""
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        r = int(t * 2 * 220)
        g = 200
    else:
        r = 220
        g = int((1.0 - (t - 0.5) * 2) * 200)
    return f"{r:02X}{g:02X}00"


def thin_border():
    s = Side(border_style='thin', color='BBBBBB')
    return Border(left=s, right=s, top=s, bottom=s)


def write_condition_sheet(ws, pivot: 'pd.DataFrame', cond: str, n_parts: int):
    n_rows, n_cols = pivot.shape

    title = (f"{COND_NAMES.get(cond, cond)}  |  "
             f"참가자 {n_parts}명  |  평균 선택 시간 (초, 소숫점 4자리)")
    ws['A1'] = title
    ws['A1'].font = Font(bold=True, size=12)
    ws.merge_cells(f'A1:{get_column_letter(n_cols + 1)}1')
    ws.row_dimensions[1].height = 22

    hdr_fill = PatternFill(fill_type='solid', fgColor='E0E0E0')

    ws['A2'] = '행＼열'
    ws['A2'].font = Font(bold=True, size=10)
    ws['A2'].alignment = Alignment(horizontal='center', vertical='center')
    ws['A2'].border = thin_border()
    ws['A2'].fill = hdr_fill
    ws.row_dimensions[2].height = 18

    for c in range(n_cols):
        cell = ws.cell(row=2, column=c + 2)
        cell.value = c + 1
        cell.font = Font(bold=True, size=10)
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border()
        cell.fill = hdr_fill

    flat = pivot.values.flatten()
    flat = flat[~np.isnan(flat)]
    vmin, vmax = (float(flat.min()), float(flat.max())) if len(flat) >= 2 else (0.0, 1.0)

    for r in range(n_rows):
        hdr = ws.cell(row=r + 3, column=1)
        hdr.value = r + 1
        hdr.font = Font(bold=True, size=10)
        hdr.alignment = Alignment(horizontal='center', vertical='center')
        hdr.border = thin_border()
        hdr.fill = hdr_fill
        ws.row_dimensions[r + 3].height = 20

        for c in range(n_cols):
            val = pivot.iloc[r, c]
            cell = ws.cell(row=r + 3, column=c + 2)
            cell.border = thin_border()
            cell.alignment = Alignment(horizontal='center', vertical='center')
            if np.isnan(val):
                cell.value = '—'
                cell.fill = PatternFill(fill_type='solid', fgColor='F0F0F0')
            else:
                cell.value = round(float(val), 4)
                cell.number_format = '0.0000'
                t = (val - vmin) / (vmax - vmin) if vmax > vmin else 0.5
                cell.fill = PatternFill(fill_type='solid', fgColor=heat_color(t))

    ws.column_dimensions['A'].width = 7
    for c in range(n_cols):
        ws.column_dimensions[get_column_letter(c + 2)].width = 9


def main():
    files = sys.argv[1:] if len(sys.argv) > 1 else sorted(glob.glob('*_trials.csv'))
    if not files:
        print("trials CSV 파일을 찾을 수 없습니다.")
        print("사용법: python3 heatmap.py [파일1.csv 파일2.csv ...]")
        return

    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f, encoding='utf-8-sig')
            dfs.append(df)
            print(f"읽음: {f}  ({len(df)}행)")
        except Exception as e:
            print(f"건너뜀: {f}  ({e})")

    if not dfs:
        print("읽을 수 있는 파일이 없습니다.")
        return

    df = pd.concat(dfs, ignore_index=True)
    df = df[df['block'] == 'main'].copy()
    df['movement_time_s'] = df['movement_time_ms'] / 1000.0

    total_rows = int(df['target_row'].max())
    total_cols = int(df['target_col'].max())
    print(f"\n본 시행 합계: {len(df)}개  ({df['participant'].nunique()}명, 격자 {total_rows}행×{total_cols}열)")

    wb = openpyxl.Workbook()
    created = 0

    for cond in CONDITIONS:
        sub = df[df['condition'] == cond]
        if sub.empty:
            continue
        pivot = (
            sub.groupby(['target_row', 'target_col'])['movement_time_s']
            .mean()
            .unstack('target_col')
            .reindex(index=range(1, total_rows + 1), columns=range(1, total_cols + 1))
        )
        n_parts = sub['participant'].nunique()
        ws = wb.create_sheet(title=cond)
        write_condition_sheet(ws, pivot, cond, n_parts)
        print(f"  {cond}: {len(sub)}시행, {n_parts}명")
        created += 1

    if not created:
        print("조건 데이터가 없습니다.")
        return

    if 'Sheet' in wb.sheetnames:
        del wb['Sheet']

    out = f"heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    wb.save(out)
    print(f"\n저장 완료: {out}")


if __name__ == '__main__':
    main()

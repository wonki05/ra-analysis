# 누락 파일 점검 결과

점검 시각 기준: 2012~2026 전 연도에 대해 아래 3종 입력 파일의 존재를 확인함.

| 연도 | zip (`[연도]_RA_improved_outputs.zip`) | 원본 PDF (`[연도]_LEET_추리논증_문제지(홀수형).pdf`) | 검수보고서 |
|---|---|---|---|
| 2012~2026 | 모두 존재 | 모두 존재 | 2012-2016 / 2017-2021 / 2022-2026 보고서로 전 연도 커버 |

**결론: 누락된 입력 파일 없음.** 모든 연도에서 zip 압축해제·PDF 대조·검수보고서 발췌가 정상 수행되었습니다.

- 검색 경로/패턴:
  - zip: `converted-files_GPTdraft/[연도]_RA_improved_outputs.zip`
  - PDF: `docs_problems/[연도]_LEET_추리논증_문제지(홀수형).pdf` (glob `docs_problems/[연도]_*.pdf` 병행)
  - 보고서: `converted-files_GPTdraft/review-reports/*_RA_review_report.md`

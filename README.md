# 1. 프로그램 기획
## 티스토리 자동 포스팅

쿠팡파트너스 를 위한 티스토리 포스팅 -> 티스토리를 통한 google 노출  
쿠팡파트너스에서는 키워드를 기반으로 제휴링크를 제공 받을 수 있음.  

사용자가 엑셀에 키워드를 여러개 설정해두면,  
1. 키워드 기반 AI 글 생성 -> 제품 설명 위주로
2. 키워드를 쿠팡 API를 통해 제휴링크 생성

결과물: 쿠팡 제휴링크와 AI글을 활용한 포스팅  
기대효과: 사람이 작성한 것과 비슷하게 자연스러운 구조 배치  
자동반복: 키워드만 여러개 설정해두면 자동으로 포스팅되는 구조  

# 2. 현재 진행 상황
1. 티스토리 로그인 및 글 작성 화면 진입  
2. csv 파일을 읽어와서 내부 메모리에 저장 (키워드만 한 줄로 저장)  
3. Gemini API를 사용하여 키워드 기반 제품 설명 글 생성
4. 쿠팡 파트너스 API를 활용하여 상품 검색 시 상품 목록 받기 (리스트)
5. 쿠팡 파트너스 API를 활용하여 이미지를 로컬에 저장

# 3. 완성해야 할 사항들
1. 저장한 이미지에 테두리 입히기 (동일한 카테고리에서는 동일한 테두리로 설정)
2. 생성한 글과 사진을 티스토리 블로그에 포스팅
3. 이 작업을 5번 이상 진행했을 시 이상 없음을 확인 (테스트)

# 4. 주의사항 및 참고사항
1. 쿠팡 상품 검색 시 API 콜 리밋은 1분에 50회
2. 사진이 너무 겹치는 경우, 상품 상세 페이지에서 가져올 수 있는 방법 연구  
   (현재는 미리보기 사진만 가져와서 테두리 입힌 후 복붙)

# 5. 레퍼런스
https://cafe.naver.com/fcbarcelonatip18/3521?art=ZXh0ZXJuYWwtc2VydmljZS1uYXZlci1zZWFyY2gtY2FmZS1wcg.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjYWZlVHlwZSI6IkNBRkVfVVJMIiwiY2FmZVVybCI6ImZjYmFyY2Vsb25hdGlwMTgiLCJhcnRpY2xlSWQiOjM1MjEsImlzc3VlZEF0IjoxNzM5OTQyODkyMTIwfQ.VjotjCL2Di9Bl_iDZ5ZRuFq_hl3ueqmFO-o8QEvLtd4
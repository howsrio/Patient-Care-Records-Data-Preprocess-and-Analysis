## 대면-비대면 진료에 따른 감량비교에 관한 연구
- 프로젝트 기간
	- 2024.06~2024.07
- 프로젝트 개요 및 목표
	- 비정형 데이터를 전처리하고, 대면 환자와 비대면 환자를 분류하여 두 집단사이의 감량 결과 비교가 있는지 확인한다
- 데이터
	- 누베베 7개지점 2022.11~2024.05 방문 데이터
- 사용된 기술 및 도구
	- 파이썬, pandas, matplotlib
- 본인의 역할 및 기여
	- 72만개의 방문 데이터를 환자별로 정리하여 13만개의 데이터로 처리
	- 초진차트를 분류하여 ProgressNote 안에서 다양한 정보를 추출하여 정형 데이터로 변환
	- 데이터 흐름도 제작
	- 대면-비대면 환자를 분류하고 6주, 12주 감량 결과가 있는 환자 추출하여 두 집단간의 비교
	- 비교 결과 시각화
- 프로젝트 결과 및 성과
	- 차트 데이터를 정형화 시켜 이후 연구에서도 활용할 수 있음
	- 대면-비대면 간의 감량 차이가 크게 없음을 확인

!(./대면비대면정리.png)
## 재방문 유형에 따른 감량경과 및 특성 비교
- 프로젝트 기간
	- 2024.07~2024.08
- 프로젝트 개요 및 목표
	- 감량 경과, 초진 특성 등을 조사하여, 재방문 유형별 특성들을 조사한다.
- 데이터
	- 누베베 한의원 7개지점 2022.11~2024.05 방문 데이터
- 사용된 기술 및 도구
	- 파이썬, pandas, matplotlib, 다중 선형 회귀, 클러스터링
- 본인의 역할 및 기여
	- 프로젝트 단독 연구
	- 재접수 유형별 군집화
	- 군집별 특성 조사
- 프로젝트 결과 및 성과
	- 연구 설계 및 데이터 분석을 통해 재구매를 바로 하는 군집, 시간이 지나고 재구매를 하는 군집, 재구매를 하지 않는 유형간의 차이를 확인
!(./방문유형정리.png)
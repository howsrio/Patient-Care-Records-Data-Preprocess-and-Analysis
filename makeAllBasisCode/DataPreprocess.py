import numpy as np
import pandas as pd
import os
import sys
import time
import matplotlib.pyplot as plt
import shutil

class DataPreprocess:
    def __init__(self, region):
        self.path = os.getcwd()[:-5] + f'\\region\\{region}'  # '\\region\\{}'.format(region)
        self.region = region

    def makeDir(self):
        self.newPath = os.path.join(f'{self.path}\\PreprocessData')

        if not os.path.exists(self.newPath):
            os.makedirs(os.path.join(f'{self.path}\\PreprocessData'))
        else:
            print('이미 존재합니다.')

    def delDir(self):
        self.newPath = os.path.join(f'{self.path}\\PreprocessData')
        # 'PreprocessData' 폴더가 존재하는지 확인하고 삭제
        if os.path.exists(self.newPath) and os.path.isdir(self.newPath):
            try:
                shutil.rmtree(self.newPath)
                print(f"'{self.newPath}' 폴더가 성공적으로 삭제되었습니다.")
            except Exception as e:
                print(f"폴더를 삭제하는 중 오류가 발생했습니다: {e}")
        else:
            print(f"'{self.newPath}' 폴더가 존재하지 않습니다.")

    def dataSet(self):
        # filelist 부분을 합침
        self.fileList = os.listdir(self.path)
        file_list = []
        for filename in self.fileList:
            # 파일명이 문자열을 포함하는지 확인
            if self.region in filename:
                file_list.append(filename)
        self.fileList = file_list
        self.dataDict = {}
        for i in self.fileList:
            self.dataDict[i] = pd.read_csv(self.path + '\\{}'.format(i), encoding='utf-16', index_col=0)
        print('All files are added')
        return self.dataDict

    # Tmedication에는 환자정보와 시간이 없어서 만들기위해 TMedicalRecord와 MedicalRecordID를 key로서 사용하여 연결
    def Tmedication(self):

        # 2024 버전의 데이터에 맞춰 변경
        temp = self.dataDict[f'{self.region}_tmedicalrecord.csv'][['MedicalRecordID', 'PatientID', 'ConsultTime']]

        # 저장하는 형식으로 코드 수정
        self.dataDict['{}_tmedication.csv'.format(self.region)] = \
            pd.merge(temp, self.dataDict['{}_tmedication.csv'.format(self.region)], how='inner', on='MedicalRecordID')

    def patientChartNo(self):
        self.dataDict[f'{self.region}_tpatientpersonal.csv'] = \
            self.dataDict[f'{self.region}_tpatientpersonal.csv'].loc[
                self.dataDict[f'{self.region}_tpatientpersonal.csv']['PatientChartNo'].notnull()]

    def countUniquePatientID(self):
        for i in self.dataDict.keys():
            sheetPatientIDSet = self.dataDict[i]['PatientID']
            print(f'{i} sheetPatientIDSet,{len(sheetPatientIDSet)}')
            sheetPatientIDSet = set(self.dataDict[i]['PatientID'])
            print(f'{i} sheetPatientIDSet,{len(sheetPatientIDSet)}')


    def makeInbody(self):

        # 파일 리스트를 만들고 문제가 있는 파일 제거
        # impedence와 measurement는 plat작업이 필요
        # obestity는 인덱스 에러(?)

        inbody_file_names = [filename for filename in self.fileList if
                             isinstance(filename, str) and 'inbody' in filename.lower()]
        inbody_file_names.remove(f'{self.region}_tinbodyimpedence.csv')
        inbody_file_names.remove(f'{self.region}_tinbodymeasurement.csv')
        inbody_file_names.remove(f'{self.region}_tinbodyobesitydiagnosis.csv')

        for i, name in enumerate(inbody_file_names):
            df = self.dataDict[name]
            # print()
            # print(i, name, len(df))
            df['MeasureDate'] = pd.to_datetime(df['MeasureDate'], format='%Y%m%d%H%M%S')
            df = df.sort_values(by=['PatientID', 'MeasureDate']).reset_index(drop=True)
    
            if name == f'{self.region}_tinbodychildgrowth.csv':
                continue
            
            if i == 0:
                inbody_total_df = df

            else:
                df.drop(columns=['ReadingID'], inplace=True)
                df_columns = set(df.columns)
                total_columns = set(inbody_total_df.columns)
                common_feature = list(df_columns & total_columns)
                # print(common_feature)
                inbody_total_df = pd.merge(inbody_total_df, df, on=common_feature)
                # print(len(inbody_total_df))

        # measurment part
        df = self.dataDict[f'{self.region}_tinbodymeasurement.csv']
        df['MeasureDate'] = pd.to_datetime(df['MeasureDate'], format='%Y%m%d%H%M%S')
        df = df.sort_values(by=['PatientID', 'MeasureDate']).reset_index(drop=True)
        df = df.iloc[:, 1:12]

        # measurment feature 생성
        feature_names = df.columns[3:]
        neck_feature_names = ['neck_' + name for name in feature_names]
        chest_feature_names = ['chest_' + name for name in feature_names]
        abdomen_feature_names = ['abdomen_' + name for name in feature_names]
        hip_feature_names = ['hip_' + name for name in feature_names]
        Larm_feature_names = ['Larm_' + name for name in feature_names]
        Rarm_feature_names = ['Rarm_' + name for name in feature_names]
        Lleg_feature_names = ['Lleg_' + name for name in feature_names]
        Rleg_feature_names = ['Rleg_' + name for name in feature_names]

        for i in range(len(df)):
            if i % 8 == 0:
                imsi_dict = {'PatientID': df.loc[0, 'PatientID'], 'MeasureDate': df.loc[0, 'MeasureDate']}
                imsi_list = list(df.loc[i][3:])
                imsi_dict2 = {neck_feature_names[i]: [imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)
            elif i % 8 == 1:
                imsi_list = list(df.loc[i][3:])
                imsi_dict2 = {chest_feature_names[i]: [imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)
            elif i % 8 == 2:
                imsi_list = list(df.loc[i][3:])
                imsi_dict2 = {abdomen_feature_names[i]: [imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)
            elif i % 8 == 3:
                imsi_list = list(df.loc[i][3:])
                imsi_dict2 = {hip_feature_names[i]: [imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)
            elif i % 8 == 4:
                imsi_list = list(df.loc[i][3:])
                imsi_dict2 = {Larm_feature_names[i]: [imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)
            elif i % 8 == 5:
                imsi_list = list(df.loc[i][3:])
                imsi_dict2 = {Rarm_feature_names[i]: [imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)
            elif i % 8 == 6:
                imsi_list = list(df.loc[i][3:])
                imsi_dict2 = {Lleg_feature_names[i]: [imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)
            elif i % 8 == 7:
                imsi_list = list(df.loc[i][3:])
                imsi_dict2 = {Rleg_feature_names[i]: [imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)

            if i < 7:
                continue
            elif i == 7:
                mesurment_df = pd.DataFrame(imsi_dict)
            elif i % 8 == 7:
                imsi_df = pd.DataFrame(imsi_dict)
                mesurment_df = pd.concat([mesurment_df, imsi_df])
            mesurment_df.reset_index(inplace=True, drop=True)

        # print(mesurment_df.shape)
        # print(mesurment_df.head())

        # 병합
        inbody_total_df = pd.concat([inbody_total_df, mesurment_df.iloc[:, 2:]], axis=1)

        # impedence part
        df = self.dataDict[f'{self.region}_tinbodyimpedence.csv']
        df['MeasureDate'] = pd.to_datetime(df['MeasureDate'], format='%Y%m%d%H%M%S')
        df = df.sort_values(by=['PatientID', 'MeasureDate']).reset_index(drop=True)

        # freq 기준으로 feature 만듬
        feature_names = df.columns[4:9]
        feature_names1 = ['1_' + name for name in feature_names]
        feature_names5 = ['5_' + name for name in feature_names]
        feature_names50 = ['50_' + name for name in feature_names]
        feature_names250 = ['250_' + name for name in feature_names]
        feature_names500 = ['500_' + name for name in feature_names]
        feature_names1000 = ['1000_' + name for name in feature_names]

        for i in range(len(df)):
            if i % 6 == 0:
                imsi_dict = {'PatientID': df.loc[0, 'PatientID'], 'MeasureDate': df.loc[0, 'MeasureDate']}
                imsi_list = list(df.loc[i][4:9])
                imsi_dict2 = {feature_names1[i]: [imsi_list[i]] for i in range(5)}
                imsi_dict.update(imsi_dict2)
            elif i % 6 == 1:
                imsi_list = list(df.loc[i][4:9])
                imsi_dict2 = {feature_names5[i]: [imsi_list[i]] for i in range(5)}
                imsi_dict.update(imsi_dict2)
            elif i % 6 == 2:
                imsi_list = list(df.loc[i][4:9])
                imsi_dict2 = {feature_names50[i]: [imsi_list[i]] for i in range(5)}
                imsi_dict.update(imsi_dict2)
            elif i % 6 == 3:
                imsi_list = list(df.loc[i][4:9])
                imsi_dict2 = {feature_names250[i]: [imsi_list[i]] for i in range(5)}
                imsi_dict.update(imsi_dict2)
            elif i % 6 == 4:
                imsi_list = list(df.loc[i][4:9])
                imsi_dict2 = {feature_names500[i]: [imsi_list[i]] for i in range(5)}
                imsi_dict.update(imsi_dict2)
            elif i % 6 == 5:
                imsi_list = list(df.loc[i][4:9])
                imsi_dict2 = {feature_names1000[i]: [imsi_list[i]] for i in range(5)}
                imsi_dict.update(imsi_dict2)

            if i < 5:
                continue
            elif i == 5:
                impedence_df = pd.DataFrame(imsi_dict)
            elif i % 6 == 5:
                imsi_df = pd.DataFrame(imsi_dict)
                impedence_df = pd.concat([impedence_df, imsi_df])

        impedence_df.reset_index(inplace=True, drop=True)
        # print(impedence_df.shape)
        # print(impedence_df.head())
        inbody_total_df = pd.concat([inbody_total_df, impedence_df.iloc[:, 2:]], axis=1)

        # obesitydiagnosis part
        df = self.dataDict[f'{self.region}_tinbodyobesitydiagnosis.csv']
        df['MeasureDate'] = pd.to_datetime(df['MeasureDate'], format='%Y%m%d%H%M%S')
        df = df.sort_values(by=['PatientID', 'MeasureDate']).reset_index(drop=True)
        df.drop(columns=['ReadingID'], inplace=True)
        df = df.drop('PSMM', axis=1)
        df = df.drop('PWeight', axis=1)
        df = df.drop('Weight', axis=1)
        df = df.drop('ReadingID_ORG', axis=1)

        inbody_total_df = pd.merge(inbody_total_df, df, on=['MeasureDate', 'PatientID'])
        # print(inbody_total_df.shape)
        # print(inbody_total_df.head())
        
        self.inbody_df = inbody_total_df[inbody_total_df['PatientID'] != 0]
        print(f'inbody_df 완료: {inbody_df.shape}')
        
        return self.inbody_df

    def makeMedical(self):

        # 데이터 업로드
        medrec_df = self.dataDict[f'{self.region}_tmedicalrecord.csv']
        medication_df = self.dataDict[f'{self.region}_tmedication.csv']
        # 시간 조정
        medrec_df['ConsultTime'] = pd.to_datetime(medrec_df['ConsultTime'], format='%Y%m%d%H%M%S')
        medrec_df = medrec_df.sort_values(by=['PatientID', 'ConsultTime']).reset_index(drop=True)
        # 주요변수 리스트
        medication_group = medication_df.groupby('MedicalRecordID')
        MedicineName_vec = medication_group.apply(lambda x: list(x['MedicineName']))
        code_vec = medication_group.apply(lambda x: list(x['MedicineCode']))
        Memo_vec = medication_group.apply(lambda x: list(x['Memo']))
        combine_df = pd.concat([MedicineName_vec, code_vec, Memo_vec], axis=1)
        # 나머지 변수 데이터프레임화
        imsi_df = medication_group.first()
        imsi_df.drop('MedicineCode', axis=1, inplace=True)
        imsi_df.drop('MedicineName', axis=1, inplace=True)
        imsi_df.drop('Memo', axis=1, inplace=True)
        # 데이터 병합
        imsi_df = pd.merge(combine_df, imsi_df, on='MedicalRecordID')
        imsi_df = imsi_df.reset_index()  # 인덱스 재설정
        medication_df = imsi_df.rename(columns={0: 'MedicineName', 1: 'MedicineCode', 2: 'Memo'})
        self.medical_df = pd.merge(medrec_df, medication_df, on='MedicalRecordID', how='outer')

        print(f'medical_df 완료: {self.medical_df.shape}')
        #print(self.medical_df.head())

        return self.medical_df

    def makeVital(self):

        # 데이터 프레임 로드및 정리
        # vitalvalue1만 상용하고 2는 인바디 데이터로 따로 저장하지 않았음
        # 코드 3: 최고혈압, 코드 4: 최저 혈압, 코드 6: 맥박
        vital_df = self.dataDict[f'{self.region}_tpatientvitaltemp.csv']
        vital_df.sort_values(by='PatientID')
        vital_df['CheckDate'] = pd.to_datetime(vital_df['CheckDate'], format='%Y%m%d%H%M%S')
        vital_df['CrTime'] = pd.to_datetime(vital_df['CrTime'], format='%Y%m%d%H%M%S')
        vital_df.drop('VitalValue2', axis=1, inplace=True)
        vital_df.drop('VitalID_ORG', axis=1, inplace=True)
        vital_df.drop('VitalID', axis=1, inplace=True)

        MaxVital_df = vital_df[vital_df['Code'] == 3]
        MinVital_df = vital_df[vital_df['Code'] == 4]
        Pulse_df = vital_df[vital_df['Code'] == 6]
        MaxVital_df.drop('Code', axis=1, inplace=True)
        MaxVital_df['MaxVital'] = MaxVital_df['VitalValue']
        MaxVital_df.drop('VitalValue', axis=1, inplace=True)
        MinVital_df.drop('Code', axis=1, inplace=True)
        Pulse_df.drop('Code', axis=1, inplace=True)
        MinVital_df['MinVital'] = MinVital_df['VitalValue']
        Pulse_df['Pulse'] = Pulse_df['VitalValue']
        MinVital_df.drop('VitalValue', axis=1, inplace=True)
        Pulse_df.drop('VitalValue', axis=1, inplace=True)

        imsi_df = pd.merge(MaxVital_df, MinVital_df, on=['PatientID', 'CheckDate', 'CrTime'])
        imsi_df = pd.merge(imsi_df, Pulse_df, on=['PatientID', 'CheckDate', 'CrTime'])

        self.vital_df = imsi_df
        print(f'vital_df 완료:{vital_df.shape}')
        
        return self.vital_df

    def saveDataFrame(self):
        self.newPath = os.path.join(f'{self.path}\\PreprocessData')

        # inbody
        self.inbody_df.to_csv(f'{self.newPath}\\{self.region}_inbody.csv', index=False)
        self.inbody_df.to_excel(f'{self.newPath}\\{self.region}_inbody.xlsx', index=False)
        print(f'{self.region}_inbody_df 저장완료')

        # medical
        self.medical_df.to_csv(f'{self.newPath}\\{self.region}_medical.csv', index=False)
        self.medical_df.to_excel(f'{self.newPath}\\{self.region}_medical.xlsx', index=False)
        print(f'{self.region}_medical_df 저장완료')

        # vital
        self.vital_df.to_csv(f'{self.newPath}\\{self.region}_vital.csv', index=False)
        self.vital_df.to_excel(f'{self.newPath}\\{self.region}_vital.xlsx', index=False)
        print(f'{self.region}_vital_df 저장완료')

    def saveMergeData(self):
        # merge
        self.merge_df.to_csv(f'{self.newPath}\\{self.region}_merge.csv', index=False)
        self.merge_df.to_excel(f'{self.newPath}\\{self.region}_merge.xlsx', index=False)
        print(f'{self.region}_merge_df 저장완료')

    def loadPreprocessData(self):

        self.newPath = os.path.join(f'{self.path}\\PreprocessData')
        try:
            self.inbody_df = pd.read_csv(f'{self.newPath}\\{self.region}_inbody.csv')
            print(f"{self.region}_inbody_df 로드 완료")
        except Exception as e:
            # 에러 발생 시 실행할 코드 작성
            print(f"{self.region}_inbody_df 로드 실패")
            pass

        try:
            self.medical_df = pd.read_csv(f'{self.newPath}\\{self.region}_medical.csv')
            print(f"{self.region}_medical_df 로드 완료")
        except Exception as e:
            # 에러 발생 시 실행할 코드 작성
            print(f"{self.region}_medical_df 로드 실패")
            pass

        try:
            self.vital_df = pd.read_csv(f'{self.newPath}\\{self.region}_vital.csv')
            print(f"{self.region}_vital_df 로드 완료")
        except Exception as e:
            # 에러 발생 시 실행할 코드 작성
            print(f"{self.region}_vital_df 로드 실패")
            pass

        try:
            self.merge_df = pd.read_csv(f'{self.newPath}\\{self.region}_merge.csv')
            print(f"{self.region}_merge_df 로드 완료")
        except Exception as e:
            # 에러 발생 시 실행할 코드 작성
            print(f"{self.region}_merge_df 로드 실패")
            pass

    def makeMerge(self):

        # 데이터 로드
        # 저장된 파일을 로드하지 않으면 timestamp error가 발생생
        inbody_df = self.inbody_df
        medical_df = self.medical_df
        vital_df = self.vital_df

        # 전처리
        medical_df.drop('CrTime', axis=1, inplace=True)
        medical_df.drop('Weight', axis=1, inplace=True)
        medical_df['Date'] = medical_df['ConsultTime'].apply(lambda x: x.split()[0])
        inbody_df['Date'] = inbody_df['MeasureDate'].apply(lambda x: x.split()[0])
        vital_df['Date'] = vital_df['CheckDate'].apply(lambda x: x.split()[0])
        merge_df = pd.merge(medical_df, inbody_df, on=['PatientID', 'Date'], how='outer')
        merge_df = pd.merge(merge_df, vital_df, on=['PatientID', 'Date'], how='outer')

        # 반복측정 제거 과
        group_df = merge_df.groupby(['PatientID', 'Date'])
        group_size = merge_df.groupby(['PatientID', 'Date']).size()
        overlab_list = group_size[group_size != 1].index.tolist()

        copy_df = merge_df.copy()

        for ID, Date in overlab_list:
            imsi_df = merge_df[merge_df['PatientID'] == ID][merge_df['Date'] == Date]
            remove_date_list = list(imsi_df['MeasureDate'])
            max_index = imsi_df['MeasureDate'].max()
            remove_date_list.remove(max_index)
            copy_df = copy_df[~((copy_df['PatientID'] == ID) & (copy_df['Date'] == Date) & (
                copy_df['MeasureDate'].isin(remove_date_list)))]

        self.merge_df = copy_df

        return self.merge_df


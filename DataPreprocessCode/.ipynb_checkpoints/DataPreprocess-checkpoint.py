import numpy as np
import pandas as pd
import os 
import sys
import time
import matplotlib.pyplot as plt


class DataPreprocess:
    
    def __init__(self, region):
        
        self.path = os.getcwd()
        self.path = os.path.dirname(self.path)
        self.path = os.path.dirname(self.path)
        self.path= self.path + f'\\region\\{region}' #'\\region\\{}'.format(region) 
        self.region = region
        
    def makeDir(self):
        self.newPath = os.path.join(f'{self.path}\\PreprocessData') 
         
        if not os.path.exists(self.newPath):
            os.makedirs(os.path.join(f'{self.path}\\PreprocessData'))
        else:
            print('이미 존재합니다.')
        
        # 0_ 은 파일리스트 뽑을 때 commonPatientID 디렉토리를 맨 앞에 두기 위해서 해놓음.
    
    def dataSet(self):
        #filelist 부분을 합침
        self.fileList = os.listdir(self.path)
        file_list = []
        for filename in self.fileList:
            # 파일명이 문자열을 포함하는지 확인
            if self.region in filename:
                file_list.append(filename)
        self.fileList = file_list
        self.dataDict = {}
        for i in self.fileList:
            self.dataDict[i] = pd.read_csv(self.path+'\\{}'.format(i), encoding = 'utf-16', index_col = 0)
        print('All files are added')
        return self.dataDict
    
    # Tmedication에는 환자정보와 시간이 없어서 만들기위해 TMedicalRecord와 MedicalRecordID를 key로서 사용하여 연결
    def Tmedication(self):
        
        #2024 버전의 데이터에 맞춰 변경
        temp = self.dataDict[f'{self.region}_tmedicalrecord.csv'][['MedicalRecordID','PatientID','ConsultTime']]

        
        #저장하는 형식으로 코드 수정
        self.dataDict['{}_tmedication.csv'.format(self.region)] = \
            pd.merge(temp,self.dataDict['{}_tmedication.csv'.format(self.region)], how = 'inner', on = 'MedicalRecordID')

        
        
    def patientChartNo(self):
        self.dataDict[f'{self.region}_tpatientpersonal.csv'] = \
        self.dataDict[f'{self.region}_tpatientpersonal.csv'].loc[self.dataDict[f'{self.region}_tpatientpersonal.csv']['PatientChartNo'].notnull()]

    def countUniquePatientID(self):
        for i in self.dataDict.keys():
            sheetPatientIDSet = self.dataDict[i]['PatientID']
            print(f'{i} sheetPatientIDSet,{len(sheetPatientIDSet)}')
            sheetPatientIDSet = set(self.dataDict[i]['PatientID'])
            print(f'{i} sheetPatientIDSet,{len(sheetPatientIDSet)}')

    def vennDiagram(self):
        self.inbodySet        = set(self.dataDict['{}_tinbodyadditionaldata.csv'.format(self.region)]['PatientID'])
        self.privateSet       = set(self.dataDict[f'{self.region}_tpatientpersonal.csv']['PatientID'])
        self.medicationSet    = set(self.dataDict['{}_tmedication.csv'.format(self.region)]['PatientID'])
        self.medicalRecordSet = set(self.dataDict['{}_tmedicalrecord.csv'.format(self.region)]['PatientID'])
        self.vitalTempSet     = set(self.dataDict['{}_tpatientvitaltemp.csv'.format(self.region)]['PatientID'])
    
        self.labels = venn.get_labels([self.inbodySet,self.privateSet,self.medicationSet,self.medicalRecordSet,self.vitalTempSet])
        # augument 로 fill을 안써도 되는구나 ( pilot 보면 여기에 써놓음)
        plt.figure(figsize=(12,8))
        fig,ax = venn.venn5(self.labels,names = ['inbody','private','medication','medicalRecord','vitalTemp'])
        plt.title(f'{self.region}')
        plt.show()
        plt.close()

    def makeInbody(self):
        
        df_path = os.path.join(f'{self.path}\\PreprocessData\\{self.region}_inbody.csv')
        # if os.path.exists(df_path):
        #     raise FileExistsError(f"'inbody' 파일이 {self.region} PreprocessData 디렉토리에 이미 존재합니다.")

                
        
        #파일 리스트를 만들고 문제가 있는 파일 제거
        #impedence와 measurement는 plat작업이 필요
        #obestity는 인덱스 에러(?)
        
        inbody_file_names = [filename for filename in self.fileList if isinstance(filename, str) and 'inbody' in filename.lower()]
        inbody_file_names.remove(f'{self.region}_tinbodyimpedence.csv')
        inbody_file_names.remove(f'{self.region}_tinbodymeasurement.csv')
        inbody_file_names.remove(f'{self.region}_tinbodyobesitydiagnosis.csv')

        for i, name in enumerate(inbody_file_names):
            df = self.dataDict[name]
            print()
            print(i, name, len(df))
            df['MeasureDate'] = pd.to_datetime(df['MeasureDate'], format='%Y%m%d%H%M%S')
            df = df.sort_values(by=['PatientID', 'MeasureDate']).reset_index(drop=True)

            
            if i == 0 :
                inbody_total_df = df
                
            if name == f'{self.region}_tinbodychildgrowth.csv':
                continue
        
            else:
                df.drop(columns=['ReadingID'], inplace=True)
                df_columns = set(df.columns)
                total_columns = set(inbody_total_df.columns)
                common_feature = list(df_columns & total_columns)
                print(common_feature)
                inbody_total_df =pd.merge(inbody_total_df, df, on = common_feature)
                print(len(inbody_total_df))

        self.inbody_imsi_df = inbody_total_df
        #measurment part
        df = self.dataDict[f'{self.region}_tinbodymeasurement.csv']
        df['MeasureDate'] = pd.to_datetime(df['MeasureDate'], format='%Y%m%d%H%M%S')
        df = df.sort_values(by=['PatientID', 'MeasureDate']).reset_index(drop=True)
        df = df.iloc[:,1:12]

        #measurment feature 생성
        feature_names = df.columns[3:]
        neck_feature_names = ['neck_'+ name for name in feature_names]
        chest_feature_names = ['chest_'+ name for name in feature_names]
        abdomen_feature_names = ['abdomen_'+ name for name in feature_names]
        hip_feature_names = ['hip_'+ name for name in feature_names]
        Larm_feature_names = ['Larm_'+ name for name in feature_names]
        Rarm_feature_names = ['Rarm_'+ name for name in feature_names]
        Lleg_feature_names = ['Lleg_'+ name for name in feature_names]
        Rleg_feature_names = ['Rleg_'+ name for name in feature_names]

        for i in range(len(df)):
            if i % 8 == 0:
                imsi_dict = {'PatientID': df.loc[0,'PatientID'], 'MeasureDate' : df.loc[0,'MeasureDate']}
                imsi_list=list(df.loc[i][3:])
                imsi_dict2 = {neck_feature_names[i]:[imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)
            elif i % 8 == 1:
                imsi_list=list(df.loc[i][3:])
                imsi_dict2 = {chest_feature_names[i]:[imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)
            elif i % 8 == 2:
                imsi_list=list(df.loc[i][3:])
                imsi_dict2 = {abdomen_feature_names[i]:[imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)
            elif i % 8 == 3:
                imsi_list=list(df.loc[i][3:])
                imsi_dict2 = {hip_feature_names[i]:[imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)
            elif i % 8 == 4:
                imsi_list=list(df.loc[i][3:])
                imsi_dict2 = {Larm_feature_names[i]:[imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)
            elif i % 8 == 5:
                imsi_list=list(df.loc[i][3:])
                imsi_dict2 = {Rarm_feature_names[i]:[imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)
            elif i % 8 == 6:
                imsi_list=list(df.loc[i][3:])
                imsi_dict2 = {Lleg_feature_names[i]:[imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)
            elif i % 8 == 7:
                imsi_list=list(df.loc[i][3:])
                imsi_dict2 = {Rleg_feature_names[i]:[imsi_list[i]] for i in range(8)}
                imsi_dict.update(imsi_dict2)
                
            if i < 7:
                continue
            elif i == 7:
                mesurment_df = pd.DataFrame(imsi_dict)
            elif i % 8 == 7:
                imsi_df = pd.DataFrame(imsi_dict)
                mesurment_df = pd.concat([mesurment_df, imsi_df])
            mesurment_df.reset_index(inplace=True, drop=True)
        self.measurment_df = mesurment_df
            
        print(mesurment_df.shape)
        print(mesurment_df.head())

        #병합
        inbody_total_df =pd.concat([inbody_total_df,mesurment_df.iloc[:,2:]], axis =1)

        #impedence part
        df = self.dataDict[f'{self.region}_tinbodyimpedence.csv']        
        df['MeasureDate'] = pd.to_datetime(df['MeasureDate'], format='%Y%m%d%H%M%S')
        df = df.sort_values(by=['PatientID', 'MeasureDate']).reset_index(drop=True)

        print(df.head())

        #freq 기준으로 feature 만듬
        feature_names = df.columns[4:9]
        feature_names1 = ['1_'+ name for name in feature_names]
        feature_names5 = ['5_'+ name for name in feature_names]
        feature_names50 = ['50_'+ name for name in feature_names]
        feature_names250 = ['250_'+ name for name in feature_names]
        feature_names500 = ['500_'+ name for name in feature_names]
        feature_names1000 = ['1000_'+ name for name in feature_names]

        for i in range(len(df)):
            if i % 6 == 0:
                imsi_dict = {'PatientID': df.loc[0,'PatientID'], 'MeasureDate' : df.loc[0,'MeasureDate']}
                imsi_list=list(df.loc[i][4:9])
                imsi_dict2 = {feature_names1[i]:[imsi_list[i]] for i in range(5)}
                imsi_dict.update(imsi_dict2)
            elif i % 6 == 1:
                imsi_list=list(df.loc[i][4:9])
                imsi_dict2 = {feature_names5[i]:[imsi_list[i]] for i in range(5)}
                imsi_dict.update(imsi_dict2)
            elif i % 6 == 2:
                imsi_list=list(df.loc[i][4:9])
                imsi_dict2 = {feature_names50[i]:[imsi_list[i]] for i in range(5)}
                imsi_dict.update(imsi_dict2)
            elif i % 6 == 3:
                imsi_list=list(df.loc[i][4:9])
                imsi_dict2 = {feature_names250[i]:[imsi_list[i]] for i in range(5)}
                imsi_dict.update(imsi_dict2)
            elif i % 6 == 4:
                imsi_list=list(df.loc[i][4:9])
                imsi_dict2 = {feature_names500[i]:[imsi_list[i]] for i in range(5)}
                imsi_dict.update(imsi_dict2)
            elif i % 6 == 5:
                imsi_list=list(df.loc[i][4:9])
                imsi_dict2 = {feature_names1000[i]:[imsi_list[i]] for i in range(5)}
                imsi_dict.update(imsi_dict2)
                
            if i < 5:
                continue
            elif i == 5:
                impedence_df = pd.DataFrame(imsi_dict)
            elif i % 6 == 5:
                imsi_df = pd.DataFrame(imsi_dict)
                impedence_df = pd.concat([impedence_df, imsi_df])
        

        impedence_df.reset_index(inplace=True, drop=True)
        inbody_total_df = pd.concat([inbody_total_df, impedence_df.iloc[:,2:]], axis = 1)
        self.impedence_df = impedence_df

        #obesitydiagnosis part
        df = self.dataDict[f'{self.region}_tinbodyobesitydiagnosis.csv']
        df['MeasureDate'] = pd.to_datetime(df['MeasureDate'], format='%Y%m%d%H%M%S')
        df = df.sort_values(by=['PatientID', 'MeasureDate']).reset_index(drop=True)
        df.drop(columns=['ReadingID'], inplace=True)
        df = df.drop('PSMM', axis=1)
        df = df.drop('PWeight', axis=1)
        df = df.drop('Weight', axis=1)
        df = df.drop('ReadingID_ORG', axis=1)

        self.obesity_df = df

        inbody_total_df = pd.merge(inbody_total_df, df, on = ['MeasureDate', 'PatientID'])
        print(inbody_total_df.shape)
        print(inbody_total_df.head())

        self.inbody_df = inbody_total_df
        return self.inbody_df


    def makeMedical(self):
        df_path = os.path.join(f'{self.path}\\PreprocessData\\{self.region}_medical.csv')
        if os.path.exists(df_path):
            raise FileExistsError(f"'medical' 파일이 {self.region} PreprocessData 디렉토리에 이미 존재합니다.")
        
        #데이터 업로드
        medrec_df = self.dataDict[f'{self.region}_tmedicalrecord.csv']
        medication_df =self.dataDict[f'{self.region}_tmedication.csv']
        #시간 조정
        medrec_df['ConsultTime'] = pd.to_datetime(medrec_df['ConsultTime'], format='%Y%m%d%H%M%S')
        medrec_df = medrec_df.sort_values(by=['PatientID', 'ConsultTime']).reset_index(drop=True)
        #주요변수 리스트
        medication_group= medication_df.groupby('MedicalRecordID')
        MedicineName_vec = medication_group.apply(lambda x: list(x['MedicineName']))
        code_vec = medication_group.apply(lambda x: list(x['MedicineCode']))
        Memo_vec = medication_group.apply(lambda x: list(x['Memo']))
        combine_df = pd.concat([MedicineName_vec,code_vec,Memo_vec], axis =1)
        #나머지 변수 데이터프레임화
        imsi_df = medication_group.first()
        imsi_df.drop('MedicineCode', axis = 1, inplace = True)
        imsi_df.drop('MedicineName', axis = 1, inplace = True)
        imsi_df.drop('Memo', axis = 1, inplace = True)
        #데이터 병합
        imsi_df =pd.merge(combine_df, imsi_df, on ='MedicalRecordID')
        imsi_df=imsi_df.reset_index() #인덱스 재설정
        medication_df = imsi_df.rename(columns={0: 'MedicineName',1:'MedicineCode', 2:'Memo'})
        self.medical_df = pd.merge(medrec_df, medication_df, on = 'MedicalRecordID', how= 'outer')

        print(self.medical_df.shape)
        print(self.medical_df.head())
        
        return self.medical_df

    def makeVital(self):
        
        df_path = os.path.join(f'{self.path}\\PreprocessData\\{self.region}_vital.csv')
        if os.path.exists(df_path):
            raise FileExistsError(f"'vital' 파일이 {self.region} PreprocessData 디렉토리에 이미 존재합니다.")
        
        #데이터 프레임 로드및 정리
        #vitalvalue1만 상용하고 2는 인바디 데이터로 따로 저장하지 않았음
        #코드 3: 최고혈압, 코드 4: 최저 혈압, 코드 6: 맥박
        vital_df = self.dataDict[f'{self.region}_tpatientvitaltemp.csv']        
        vital_df.sort_values(by = 'PatientID')
        vital_df['CheckDate'] = pd.to_datetime(vital_df['CheckDate'], format='%Y%m%d%H%M%S')
        vital_df['CrTime'] = pd.to_datetime(vital_df['CrTime'], format='%Y%m%d%H%M%S')
        vital_df.drop('VitalValue2',axis =1, inplace = True)
        vital_df.drop('VitalID_ORG',axis =1, inplace = True)
        vital_df.drop('VitalID',axis =1, inplace = True)

        MaxVital_df = vital_df[vital_df['Code']==3]
        MinVital_df = vital_df[vital_df['Code']==4]
        if self.region == 'bundang': #분당만 14임 22~24 기준
            Pulse_df = vital_df[vital_df['Code']==14]
        else:
            Pulse_df = vital_df[vital_df['Code']==6]
        MaxVital_df.drop('Code', axis =1, inplace = True)
        MaxVital_df['MaxVital']= MaxVital_df['VitalValue']
        MaxVital_df.drop('VitalValue', axis =1, inplace = True)
        MinVital_df.drop('Code', axis = 1, inplace =True)
        Pulse_df.drop('Code', axis = 1, inplace =True)
        MinVital_df['MinVital'] = MinVital_df['VitalValue']
        Pulse_df['Pulse'] = Pulse_df['VitalValue']
        MinVital_df.drop('VitalValue', axis = 1, inplace =True)
        Pulse_df.drop('VitalValue', axis = 1, inplace =True)

        imsi_df = pd.merge(MaxVital_df, MinVital_df, on = ['PatientID', 'CheckDate', 'CrTime'])
        imsi_df = pd.merge(imsi_df, Pulse_df, on = ['PatientID', 'CheckDate', 'CrTime'])

        self.vital_df = imsi_df
        return self.vital_df



    def saveDataFrame(self):            
        self.newPath = os.path.join(f'{self.path}\\PreprocessData')
        
        #inbody
        self.inbody_df.to_csv(f'{self.newPath}\\{self.region}_inbody.csv', index=False)
        self.inbody_df.to_excel(f'{self.newPath}\\{self.region}_inbody.xlsx', index=False)
        print(f'{self.region}_inbody_df 저장완료')
        
        #medical
        self.medical_df.to_csv(f'{self.newPath}\\{self.region}_medical.csv', index=False)
        self.medical_df.to_excel(f'{self.newPath}\\{self.region}_medical.xlsx', index=False)
        print(f'{self.region}_medical_df 저장완료')
        
        #vital    
        self.vital_df.to_csv(f'{self.newPath}\\{self.region}_vital.csv', index=False)
        self.vital_df.to_excel(f'{self.newPath}\\{self.region}_vital.xlsx', index=False)
        print(f'{self.region}_vital_df 저장완료')

    def saveMergeData(self):
        #merge
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

        # try:
        #     self.merge_df = pd.read_csv(f'{self.newPath}\\{self.region}_merge.csv')
        #     print(f"{self.region}_merge_df 로드 완료")
        # except Exception as e:
        #     # 에러 발생 시 실행할 코드 작성
        #     print(f"{self.region}_merge_df 로드 실패")
        #     pass 
            
    def makeMerge(self):

        
        #데이터 로드
        #저장된 파일을 로드하지 않으면 timestamp error가 발생생
        inbody_df = self.inbody_df
        medical_df = self.medical_df
        vital_df = self.vital_df

        #전처리
        medical_df.drop('CrTime',axis =1, inplace =True)
        medical_df.drop('Weight',axis =1, inplace =True)
        medical_df['Date'] = medical_df['ConsultTime'].apply(lambda x: x.split()[0])
        inbody_df['Date'] = inbody_df['MeasureDate'].apply(lambda x: x.split()[0])
        vital_df['Date'] = vital_df['CheckDate'].apply(lambda x: x.split()[0])
        merge_df = pd.merge(medical_df, inbody_df, on=['PatientID', 'Date'], how = 'outer')
        merge_df = pd.merge(merge_df, vital_df, on=['PatientID', 'Date'], how = 'outer')
        

        #반복측정 제거 과정
        df_unique = merge_df.drop_duplicates(subset=['PatientID', 'Date'], keep='first')
        self.merge_df = df_unique

        return self.merge_df
        
                
        
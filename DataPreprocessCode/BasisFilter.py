from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
import copy

class BasisFilter:
    
    def __init__(self):
        self.path = os.getcwd() 
        self.path =os.path.abspath(os.path.join(self.path, "..", ".."))
        self.newPath = os.path.join(f'{self.path}\\filtered_data')
        self.region_list = ['bundang', 'gangnam', 'hongdae', 'jamsil', 'bucheon', 'busan', 'incheon']
        self.index_level_2= ['Date', 'ProgressNote', 'MedicineName','Memo','체중','골격근량','체지방량','BMI','혈압(고)','혈압(저)','맥박수','체지방률','Height','근육량',
            'InterCellWater','ExtraCellWater','TotalBodyWater','ProteinMass','MineralMass','FatFreeMass','Osseus','ECW_TBW','ECF_TBF','VFA','WHR',
            'WeightControl','FatControl','MuscleControl','BMR','FitnessScore']

    def make_dir(self):
        if not os.path.exists(self.newPath):
            os.makedirs(os.path.join(f'{self.path}\\filtered_data'))
        else:
            print('이미 존재합니다.')

    def del_dir(self):
        # 'PreprocessData' 폴더가 존재하는지 확인하고 삭제
        if os.path.exists(self.newPath) and os.path.isdir(self.newPath):
            try:
                shutil.rmtree(self.newPath)
                print(f"'{self.newPath}' 폴더가 성공적으로 삭제되었습니다.")
            except Exception as e:
                print(f"폴더를 삭제하는 중 오류가 발생했습니다: {e}")
        else:
            print(f"'{self.newPath}' 폴더가 존재하지 않습니다.")

    def load_basis(self):
        self.basis = pd.read_csv(f'{self.path}\\MergeRegionData\\basis_for_filter.csv', encoding='utf-8')
        # date_columns = ['PatientFirstDate'] + ['Date'] + ['Date.'+str(i) for i in range(1,28)]
        # for col in date_columns:
        #     self.basis[col] = pd.to_datetime(self.basis[col],format='%Y%m%d')
        return self.basis

    def first_visit_filter(self, df):
        
        pattern = r'\[1\]\s*기본\s*상담*'
        # 각 ProgressNote 열에서 두 가지 패턴을 모두 만족하는 행 필터링
        filtered_df = df[
            df['ProgressNote_1'].str.contains(pattern, regex=True) |
            df['ProgressNote_2'].str.contains(pattern, regex=True) |
            df['ProgressNote_3'].str.contains(pattern, regex=True) |
            df['ProgressNote_4'].str.contains(pattern, regex=True)
        ]
        # 필터링된 행의 PatientID 추출
        result_patient_ids = filtered_df['PatientID'].tolist()
        filtered_df = filtered_df['2022-11-06'<filtered_df['PatientFirstDate']]
        return filtered_df
        
    def save_csv(self, df, name):
        df.to_csv(f'{self.newPath}\\{name}.csv', index =False)
        
    def save_excel(self, df, name):
        df.to_excel(f'{self.newPath}\\{name}.xlsx', index =False)

    def load_csv(self, name):
        df = pd.read_csv(f'{self.newPath}\\{name}.csv', encoding ='utf-8')
        return df

    def make_inbody2up_dict(self, df):
        idx_list = df.index.tolist()
        
        Weight_list = ['Weight_'+str(i) for i in range(1,28)]
        inbody2up_dict = {}
        for idx in idx_list:
            inbody_weights = pd.DataFrame(df.loc[idx,Weight_list].dropna()).transpose()
            Date_list = ['Date_' + weight_col.split('_')[-1] for weight_col in inbody_weights.columns.tolist()]
            inbody_dates = df.loc[idx,Date_list]
            if len(inbody_dates) > 1:
                inbody2up_dict[idx] = list(inbody_dates)
        self.inbody2up_idx = list(inbody2up_dict.keys())
        self.inbody2up_dict = inbody2up_dict
        return self.inbody2up_dict

    def make_return_dict(self, df, dict, day_range): #day range는 리스트형태로 [a, b]의 형태로 입력
        return_dict = {}
        for idx in dict.keys():
            for date in dict[idx][1:]:
                day = (datetime.strptime(date, '%Y-%m-%d') - datetime.strptime(dict[idx][0], '%Y-%m-%d')).days
                if day_range[0] <= day < day_range[1]:
                    return_dict[idx] = date
        self.return_dict = return_dict
        self.return_idx = list(return_dict.keys())
        return self.return_dict

    def make_medicine_dict(self, df, inbody2up_dict, return_dict):
        #record_dict은 gambi에 대한 정보만을 저장
        #allmed는 같이 사용된 약의 정보까지 모두 저장
        self.record_dict ={}
        self.allmed_dict ={}
        nan = 0
        for idx in return_dict.keys():
            return_day = return_dict[idx]
            return_day = datetime.strptime(return_day, '%Y-%m-%d')
            first_day = inbody2up_dict[idx][0]
            first_day = datetime.strptime(first_day, '%Y-%m-%d')
            target = 0
            record_list =[]
            med_list = []
            
            for i in range(1,32):
                med = f'MedicineName_{i}'
                date = f'Date_{i}'
                memo = f'Memo_{i}'
                if pd.isna(df.loc[idx,date]):
                    continue 
                day = datetime.strptime(df.loc[idx,date], '%Y-%m-%d')
                if return_day - timedelta(days=1) <= day:
                    break
                if first_day - timedelta(days=1) > day:
                    break
                if pd.isna(df.loc[idx,med]):
                    continue
                else:
                    for j, medicine in enumerate(eval(df.loc[idx,med])):
                        if 'Gambi' in medicine:
                            if 'Tab' in medicine:
                                memo_list =eval(df.loc[idx,memo])[j]
                                if memo_list =='2-1':
                                    record_list.append([day,medicine,'2-1'])
                                    target = target + 1
                                    med_list.append(eval(df.loc[idx,med]))
                                if memo_list =='2-2':
                                    record_list.append([day,medicine,'2-2'])
                                    target = target + 1
                                    med_list.append(eval(df.loc[idx,med]))
            if target > 1:
                #print(idx, target, return_day)
                self.record_dict[idx] = record_list
                self.allmed_dict[idx] = med_list

    def make_FR_df(self, df, medicine_idx, return_dict, inbody2up_dict):
        
        concat_df = pd.DataFrame()
        df_info = df[['Region','PatientChartNo','PatientAddr11','PatientFirstDate','Age','PatientSex','Description']]
        dates = ['Date_'+str(i) for i in range(1,28)]
        for idx in medicine_idx:
            #print(inbody2up_dict[idx][0],return_dict[idx])
            F = int(df[dates].loc[idx, df.loc[idx] == inbody2up_dict[idx][0]].index.tolist()[0].split('_')[-1])
            R = int(df[dates].loc[idx, df.loc[idx] == return_dict[idx]].index.tolist()[0].split('_')[-1])
            df_info_i = pd.DataFrame(df_info.loc[idx]).transpose()
            #print(df_info_i)
            Fs_idx = df.columns.get_loc('Date_'+str(F))
            Fl_idx = df.columns.get_loc('Date_'+str(F+1))
            Rs_idx = df.columns.get_loc('Date_'+str(R))
            Rl_idx = df.columns.get_loc('Date_'+str(R+1))
            F_df = pd.DataFrame(df.iloc[:, Fs_idx:Fl_idx].loc[idx]).transpose()
            F_col =F_df.columns.tolist()
            F_col =['_'.join(col.split('_')[:-1]+['F']) for col in F_col]
            F_df = F_df.set_axis(F_col, axis = 'columns')
            R_df = pd.DataFrame(df.iloc[:, Rs_idx:Rl_idx].loc[idx]).transpose()
            R_col =R_df.columns.tolist()
            R_col =['_'.join(col.split('_')[:-1]+['R']) for col in R_col]
            R_df = R_df.set_axis(R_col, axis = 'columns')
            FR_df = pd.concat([F_df,R_df], axis = 1)
            FR_df = pd.concat([df_info_i,FR_df], axis = 1)
        
            concat_df = pd.concat([concat_df,FR_df], axis = 0)
        self.FR_df = concat_df
        return self.FR_df

    def medicine_rename(self, basis):
        MedicineName_list = [col for col in basis.columns.tolist() if 'MedicineName' in col]
        Memo_list = [col for col in basis.columns.tolist() if 'Memo' in col]
        nan = ''
        for i in range(1,len(Memo_list)):
            print(MedicineName_list[i-1])
            for k, med_list in enumerate(basis[MedicineName_list[i-1]]):
                #print(med_list)
                if pd.isna(med_list):
                    continue
                if ''== med_list:
                    continue
                new_med=''
                new_memo=''
                for j, med in enumerate(eval(med_list)): # 감비와 비움만을 남기고 양식에서 대괄호와 ''을 지움
                    if 'Gambi' in med:
                        if new_med == '' :
                            new_med = new_med + med
                            new_memo = new_memo + eval(basis.loc[k,Memo_list[i-1]])[j]
        
                        else:
                            new_med = new_med +', ' +med
                            new_memo = new_memo +', '+ eval(basis.loc[k,Memo_list[i-1]])[j]
        
                    elif '비움' in med:
                        if new_med == '' :
                            new_med = new_med + med
                            new_memo = new_memo + eval(basis.loc[k,Memo_list[i-1]])[j]
        
                        else:
                            new_med = new_med +', ' +med
                            new_memo = new_memo +', '+ eval(basis.loc[k,Memo_list[i-1]])[j]
                        
        
                basis.loc[k,MedicineName_list[i-1]] = new_med
                basis.loc[k,Memo_list[i-1]] = new_memo
        return basis
                    
        

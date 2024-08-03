import pandas as pd


# 加载Parquet文件
data = pd.read_parquet('E:/data/emrqa-msquad_data/data/validation-00000-of-00001.parquet')

# 将Parquet文件转换为CSV
data.to_csv('E:/data/emrqa-msquad_data/data/validation-00000-of-00001.csv', index=False)
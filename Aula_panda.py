import pandas as pd

df = pd.read_csv("alunos_desempenho.csv")
df.columns
columns = ['aluno','curso','periodo']
df[columns]



pd.read_excel("alunos_localidade_carro_merge.xlsx")
import pandas as pd

df = pd.read_excel("PETR4_evolucao.xlsx")
print(df)
df["valor"].max()
df["valor"].min()
df["valor"].mean()
df["valor"].std()
df[0:5]
colunas = ["conta", "valor"]
df[23:24][colunas]
linhas = df["trimestre"] == "20262T"
df[linhas][colunas]
linhas = df["conta"] == "lucro"
df[linhas][colunas]
linhas = df["conta"] == "lucro"
colunas = ["valor"]
df[linhas][colunas].mean()

import seaborn as sns
import matplotlib.pyplot as plt
linhas = df["conta"] == "lucro"
colunas = ["trimestre", "valor"]
dados = df[linhas][colunas]
sns.lineplot(dados, x= "trimestre", y="valor")
plt.title("Gráfico do Lucro")
plt.xticks(rotation=45)


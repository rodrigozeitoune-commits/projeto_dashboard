
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# --------------------------------------------------

st.set_page_config(
    page_title="Dashboard | PETR4",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# ESTILO VISUAL
# --------------------------------------------------

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    h1, h2, h3 {
        color: #202923;
        font-weight: 600;
    }

    [data-testid="stMetric"] {
        background-color: #F5F7F5;
        border: 1px solid #E6EAE6;
        padding: 18px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] {
        color: #647067;
    }

    [data-testid="stMetricValue"] {
        color: #285B45;
    }

    div[data-baseweb="tab-list"] {
        gap: 12px;
    }

    button[data-baseweb="tab"] {
        font-size: 15px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #E6EAE6;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

sns.set_theme(
    style="whitegrid",
    rc={
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        "grid.color": "#E9EDE9",
        "axes.edgecolor": "#E9EDE9",
        "font.family": "sans-serif"
    }
)

# --------------------------------------------------
# LEITURA DOS ARQUIVOS
# --------------------------------------------------

@st.cache_data
def carregar_excel(arquivo):
    return pd.read_excel(arquivo)

try:
    df_petr4 = carregar_excel("PETR4_evolucao.xlsx")
    df_b3 = carregar_excel("planilhao_b3.xlsx")

except FileNotFoundError:
    st.error(
        "Não encontrei as planilhas. "
        "Coloque PETR4_evolucao.xlsx e planilhao_b3.xlsx "
        "na mesma pasta do arquivo painel.py."
    )
    st.stop()

# --------------------------------------------------
# CABEÇALHO
# --------------------------------------------------

st.title("Dashboard Financeiro")
st.caption("PETR4 e mercado de ações | Painel de análise de dados")

st.divider()

# --------------------------------------------------
# ABAS
# --------------------------------------------------

aba1, aba2 = st.tabs([
    "Desempenho financeiro",
    "Empresas por setor"
])

# --------------------------------------------------
# ABA 1 — PETR4
# --------------------------------------------------

with aba1:
    st.subheader("Evolução do lucro")
    st.caption("Acompanhamento dos resultados por trimestre.")

    colunas_necessarias = {"conta", "trimestre", "valor"}

    if not colunas_necessarias.issubset(df_petr4.columns):
        st.error(
            "A planilha PETR4_evolucao.xlsx precisa conter "
            "as colunas: conta, trimestre e valor."
        )
    else:
        dados = df_petr4[
            df_petr4["conta"].astype(str).str.strip().str.lower()
            == "lucro"
        ][["trimestre", "valor"]].copy()

        dados["valor"] = pd.to_numeric(
            dados["valor"], errors="coerce"
        )
        dados = dados.dropna(subset=["valor", "trimestre"])

        if dados.empty:
            st.warning("Não foram encontrados dados de lucro.")
        else:
            # Permite selecionar os períodos
            periodos = dados["trimestre"].astype(str).drop_duplicates().tolist()

            selecionados = st.multiselect(
                "Selecione os trimestres",
                options=periodos,
                default=periodos
            )

            dados = dados[
                dados["trimestre"].astype(str).isin(selecionados)
            ]

            if dados.empty:
                st.info("Selecione ao menos um trimestre.")
            else:
                dados = dados.sort_values("trimestre")

                primeiro = dados["valor"].iloc[0]
                ultimo = dados["valor"].iloc[-1]

                variacao = (
                    ((ultimo / abs(primeiro)) - 1) * 100
                    if primeiro != 0
                    else None
                )

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Lucro mais recente",
                    f"{ultimo:,.2f}"
                )

                c2.metric(
                    "Variação no período",
                    f"{variacao:+.2f}%"
                    if variacao is not None
                    else "N/D"
                )

                c3.metric(
                    "Trimestres analisados",
                    len(dados)
                )

                st.markdown("### Histórico do lucro")

                fig, ax = plt.subplots(figsize=(11, 4.5))

                sns.lineplot(
                    data=dados,
                    x="trimestre",
                    y="valor",
                    marker="o",
                    linewidth=2.5,
                    color="#43866D",
                    ax=ax
                )

                ax.set_xlabel("")
                ax.set_ylabel("Valor")
                ax.set_title("")
                ax.tick_params(axis="x", rotation=35)
                ax.spines[["top", "right"]].set_visible(False)
                ax.grid(axis="x", visible=False)
                fig.tight_layout()

                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

                with st.expander("Consultar dados detalhados"):
                    st.dataframe(
                        dados,
                        use_container_width=True,
                        hide_index=True
                    )

# --------------------------------------------------
# ABA 2 — EMPRESAS POR SETOR
# --------------------------------------------------

with aba2:
    st.subheader("Distribuição de empresas por setor")
    st.caption("Visão geral das empresas presentes na base da B3.")

    if "setor" not in df_b3.columns:
        st.error(
            "A planilha planilhao_b3.xlsx precisa conter "
            "uma coluna chamada setor."
        )
    else:
        df_b3["setor"] = (
            df_b3["setor"]
            .astype("string")
            .str.strip()
        )

        df_b3 = df_b3.dropna(subset=["setor"])
        df_b3 = df_b3[df_b3["setor"] != ""]

        contagem = (
            df_b3.groupby("setor")
            .size()
            .sort_values(ascending=False)
        )

        if contagem.empty:
            st.warning("Não foram encontrados setores na planilha.")
        else:
            c1, c2 = st.columns(2)

            c1.metric("Empresas na base", len(df_b3))
            c2.metric("Setores identificados", len(contagem))

            st.markdown("### Quantidade por setor")

            fig, ax = plt.subplots(
                figsize=(11, max(4, len(contagem) * 0.35))
            )

            sns.barplot(
                x=contagem.values,
                y=contagem.index,
                color="#18EAA4",
                ax=ax
            )

            ax.set_xlabel("Quantidade de empresas")
            ax.set_ylabel("")
            ax.spines[["top", "right", "left"]].set_visible(False)
            ax.grid(axis="y", visible=False)
            ax.grid(axis="x", color="#E9EDE9")
            fig.tight_layout()

            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

            tabela = pd.DataFrame({
                "Setor": contagem.index,
                "Quantidade de empresas": contagem.values,
                "Participação (%)": (
                    contagem.values / contagem.sum() * 100
                ).round(2)
            })

            with st.expander("Consultar tabela por setor"):
                st.dataframe(
                    tabela,
                    use_container_width=True,
                    hide_index=True
                )

# --------------------------------------------------
# RODAPÉ
# --------------------------------------------------

st.divider()
st.caption("Dashboard desenvolvido em Python com Streamlit.")


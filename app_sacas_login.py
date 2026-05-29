import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

st.set_page_config(page_title="J&T Controle de Sacas", page_icon="📦", layout="wide")

DB_NAME = "controle_sacas.db"
LOGO_PATH = "assets/logo_jt.png"
MASCOTE_PATH = "assets/maomao.png"

SC_LISTA = [
    "MG CGE", "BA FEC", "PE JGS", "PR SJS", "RJ SJM", "CE FOR",
    "SN RAO", "SC BNU", "PI THE", "DC SRR-ES", "RS NSR", "MT CGB",
    "GO GYN", "DF BSB", "RO PVH", "SE AJU", "BA VDC", "PA STM",
    "PA MRB", "TO PMW", "MS CGR", "ES SRR"
]

USUARIOS = {
    "admin": {"senha": "admin123", "perfil": "admin", "sc": "TODOS"},
    "CGE": {"senha": "cge123", "perfil": "sc", "sc": "MG CGE"},
    "FEC": {"senha": "fec123", "perfil": "sc", "sc": "BA FEC"},
    "JGS": {"senha": "jgs123", "perfil": "sc", "sc": "PE JGS"},
    "SJS": {"senha": "sjs123", "perfil": "sc", "sc": "PR SJS"},
    "SJM": {"senha": "sjm123", "perfil": "sc", "sc": "RJ SJM"},
    "FOR": {"senha": "for123", "perfil": "sc", "sc": "CE FOR"},
    "RAO": {"senha": "rao123", "perfil": "sc", "sc": "SN RAO"},
    "BNU": {"senha": "bnu123", "perfil": "sc", "sc": "SC BNU"},
    "THE": {"senha": "the123", "perfil": "sc", "sc": "PI THE"},
    "SRRES": {"senha": "srres123", "perfil": "sc", "sc": "DC SRR-ES"},
    "NSR": {"senha": "nsr123", "perfil": "sc", "sc": "RS NSR"},
    "CGB": {"senha": "cgb123", "perfil": "sc", "sc": "MT CGB"},
    "GYN": {"senha": "gyn123", "perfil": "sc", "sc": "GO GYN"},
    "BSB": {"senha": "bsb123", "perfil": "sc", "sc": "DF BSB"},
    "PVH": {"senha": "pvh123", "perfil": "sc", "sc": "RO PVH"},
    "AJU": {"senha": "aju123", "perfil": "sc", "sc": "SE AJU"},
    "VDC": {"senha": "vdc123", "perfil": "sc", "sc": "BA VDC"},
    "STM": {"senha": "stm123", "perfil": "sc", "sc": "PA STM"},
    "MRB": {"senha": "mrb123", "perfil": "sc", "sc": "PA MRB"},
    "PMW": {"senha": "pmw123", "perfil": "sc", "sc": "TO PMW"},
    "CGR": {"senha": "cgr123", "perfil": "sc", "sc": "MS CGR"},
    "SRR": {"senha": "srr123", "perfil": "sc", "sc": "ES SRR"},
}

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f2f2f2 0%, #ffffff 55%, #eeeeee 100%);
}
.main-title {
    font-size: 40px;
    font-weight: 900;
    color: #e60012;
    margin-bottom: 0px;
}
.sub-title {
    font-size: 17px;
    color: #555555;
    margin-top: 0px;
}
div.stButton > button {
    background-color: #e60012;
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: 800;
}
div.stButton > button:hover {
    background-color: #b0000e;
    color: white;
}
[data-testid="stSidebar"] {
    background-color: #ffffff;
}
</style>
""", unsafe_allow_html=True)


def conectar():
    return sqlite3.connect(DB_NAME)


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sc TEXT NOT NULL,
            quantidade_meta INTEGER NOT NULL,
            data_cadastro TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devolucoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_devolucao TEXT NOT NULL,
            sc TEXT NOT NULL,
            id_retorno TEXT NOT NULL,
            placa TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            usuario TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def inserir_meta(sc, quantidade):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO metas 
        (sc, quantidade_meta, data_cadastro) 
        VALUES (?, ?, ?)
        """,
        (sc, int(quantidade), str(date.today()))
    )

    conn.commit()
    conn.close()


def inserir_devolucao(data_devolucao, sc, id_retorno, placa, quantidade, usuario):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO devolucoes 
        (data_devolucao, sc, id_retorno, placa, quantidade, usuario)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            str(data_devolucao),
            sc,
            id_retorno.strip(),
            placa.upper().strip(),
            int(quantidade),
            usuario
        )
    )

    conn.commit()
    conn.close()


def carregar_metas():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM metas", conn)
    conn.close()
    return df


def carregar_devolucoes():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM devolucoes", conn)
    conn.close()
    return df


def gerar_resumo():
    metas = carregar_metas()
    devolucoes = carregar_devolucoes()

    if metas.empty:
        return pd.DataFrame(columns=[
            "sc", "quantidade_meta", "quantidade_devolvida",
            "saldo_pendente", "percentual_devolvido", "status"
        ])

    metas_resumo = metas.groupby("sc", as_index=False)["quantidade_meta"].sum()

    if devolucoes.empty:
        metas_resumo["quantidade_devolvida"] = 0
    else:
        dev_resumo = devolucoes.groupby("sc", as_index=False)["quantidade"].sum()
        metas_resumo = metas_resumo.merge(dev_resumo, on="sc", how="left")
        metas_resumo.rename(columns={"quantidade": "quantidade_devolvida"}, inplace=True)
        metas_resumo["quantidade_devolvida"] = metas_resumo["quantidade_devolvida"].fillna(0).astype(int)

    metas_resumo["saldo_pendente"] = metas_resumo["quantidade_meta"] - metas_resumo["quantidade_devolvida"]

    metas_resumo["percentual_devolvido"] = (
        metas_resumo["quantidade_devolvida"] / metas_resumo["quantidade_meta"]
    ) * 100

    metas_resumo["percentual_devolvido"] = metas_resumo["percentual_devolvido"].fillna(0).round(2)

    metas_resumo["status"] = metas_resumo["saldo_pendente"].apply(
        lambda x: "Concluído" if x <= 0 else "Pendente"
    )

    return metas_resumo


def normalizar_sc(sc):
    sc = str(sc).strip().upper()
    mapa = {x.upper(): x for x in SC_LISTA}

    if sc in mapa:
        return mapa[sc]

    for item in SC_LISTA:
        codigo = item.split()[-1].upper()
        if sc == codigo:
            return item

    return None


def cabecalho():
    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        st.image(LOGO_PATH, width=180)

    with col2:
        st.markdown(
            '<p class="main-title">Controle de Devolução de Sacas</p>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<p class="sub-title">Gestão Nacional • Meta x Devolvido • Dashboard Executivo</p>',
            unsafe_allow_html=True
        )

    with col3:
        st.image(MASCOTE_PATH, width=120)

    st.divider()


def login():
    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.image(LOGO_PATH, width=260)

        st.markdown("## 📦 Controle de Sacas")
        st.markdown("### Login do Sistema")

        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar", use_container_width=True):
            usuario_digitado = usuario.strip()

            if usuario_digitado.lower() == "admin":
                usuario_digitado = "admin"
            else:
                usuario_digitado = usuario_digitado.upper()

            if usuario_digitado in USUARIOS and senha == USUARIOS[usuario_digitado]["senha"]:
                st.session_state["logado"] = True
                st.session_state["usuario"] = usuario_digitado
                st.session_state["perfil"] = USUARIOS[usuario_digitado]["perfil"]
                st.session_state["sc"] = USUARIOS[usuario_digitado]["sc"]
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")


def sair():
    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()


def dashboard_admin():
    st.subheader("📊 Dashboard Executivo")

    resumo = gerar_resumo()

    if resumo.empty:
        st.warning("Nenhuma meta cadastrada ainda.")
        return

    total_meta = int(resumo["quantidade_meta"].sum())
    total_devolvido = int(resumo["quantidade_devolvida"].sum())
    total_pendente = int(resumo["saldo_pendente"].sum())

    percentual_geral = 0
    if total_meta > 0:
        percentual_geral = round((total_devolvido / total_meta) * 100, 2)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total a devolver", f"{total_meta:,}".replace(",", "."))
    c2.metric("Total devolvido", f"{total_devolvido:,}".replace(",", "."))
    c3.metric("Saldo pendente", f"{total_pendente:,}".replace(",", "."))
    c4.metric("% Devolvido", f"{percentual_geral}%")

    st.progress(min(percentual_geral / 100, 1.0))
    st.divider()

    filtro = st.selectbox("Filtrar SC", ["Todos"] + SC_LISTA)
    resumo_filtrado = resumo.copy()

    if filtro != "Todos":
        resumo_filtrado = resumo_filtrado[resumo_filtrado["sc"] == filtro]

    st.subheader("📋 Resumo por Base")
    st.dataframe(resumo_filtrado, use_container_width=True)

    st.subheader("📉 Saldo pendente por SC")
    if not resumo_filtrado.empty:
        st.bar_chart(resumo_filtrado.set_index("sc")["saldo_pendente"])

    st.subheader("🚨 Ranking Bases Ofensoras")
    ranking = resumo.sort_values(by="saldo_pendente", ascending=False)
    ranking = ranking[ranking["saldo_pendente"] > 0][[
        "sc", "quantidade_meta", "quantidade_devolvida",
        "saldo_pendente", "percentual_devolvido", "status"
    ]]
    st.dataframe(ranking, use_container_width=True)


def cadastrar_meta():
    st.subheader("📝 Cadastrar Quantidade a Devolver")

    with st.form("form_meta"):
        sc = st.selectbox("SC", SC_LISTA)
        quantidade = st.number_input("Quantidade que precisa devolver", min_value=1, step=1)
        salvar = st.form_submit_button("Salvar quantidade")

        if salvar:
            inserir_meta(sc, quantidade)
            st.success(f"Meta cadastrada para {sc}: {quantidade} sacas.")


def cadastro_massivo():
    st.subheader("📥 Cadastro Massivo de Metas")

    st.info("Você pode colar os dados no formato: SC;quantidade")

    texto = st.text_area(
        "Cole aqui as bases e quantidades",
        height=300,
        placeholder="SP BRE;300\nMG CGE;200\nBA FEC;300"
    )

    if st.button("Processar texto colado"):
        linhas = texto.splitlines()
        total = 0
        erros = []

        for linha in linhas:
            if not linha.strip():
                continue

            try:
                partes = linha.split(";")

                sc_original = partes[0].strip().upper()
                quantidade = int(partes[1].strip())

                inserir_meta(sc_original, quantidade)
                total += 1

            except Exception as e:
                erros.append(f"Erro na linha: {linha}")

        if total > 0:
            st.success(f"{total} metas cadastradas com sucesso.")

        if erros:
            st.warning("Algumas linhas não foram importadas:")
            st.write(erros)

    st.divider()

    st.subheader("📤 Importar arquivo CSV")

    st.markdown("""
    O arquivo CSV deve estar assim:

    ```text
    sc;quantidade
    SP BRE;300
    MG CGE;200
    BA FEC;300
    ```
    """)

    arquivo = st.file_uploader(
        "Selecione o arquivo CSV",
        type=["csv"]
    )

    if arquivo is not None:
        try:
            df = pd.read_csv(arquivo, sep=";")
            df.columns = [c.strip().lower() for c in df.columns]

            st.write("Pré-visualização:")
            st.dataframe(df, use_container_width=True)

            if st.button("Importar CSV"):
                total = 0

                for _, row in df.iterrows():
                    sc = str(row["sc"]).strip().upper()
                    quantidade = int(row["quantidade"])

                    inserir_meta(sc, quantidade)
                    total += 1

                st.success(f"{total} metas importadas via CSV.")

        except Exception as e:
            st.error(f"Erro ao importar CSV: {e}")


def lancar_devolucao(sc_usuario=None):
    st.subheader("🚚 Lançar Devolução")

    if st.session_state["perfil"] == "admin":
        sc = st.selectbox("SC", SC_LISTA)
    else:
        sc = sc_usuario
        st.info(f"Base logada: {sc}")

    with st.form("form_dev"):
        data_devolucao = st.date_input("Data da devolução", value=date.today())
        id_retorno = st.text_input("ID de retorno / transferência")
        placa = st.text_input("Placa do veículo")
        quantidade = st.number_input("Quantidade devolvida", min_value=1, step=1)
        salvar = st.form_submit_button("Salvar devolução")

        if salvar:
            if not id_retorno.strip() or not placa.strip():
                st.error("Preencha o ID de retorno e a placa do veículo.")
            else:
                inserir_devolucao(
                    data_devolucao,
                    sc,
                    id_retorno,
                    placa,
                    quantidade,
                    st.session_state["usuario"]
                )
                st.success("Devolução lançada com sucesso.")


def historico():
    st.subheader("📋 Histórico de Devoluções")

    df = carregar_devolucoes()

    if df.empty:
        st.warning("Nenhuma devolução registrada.")
        return

    if st.session_state["perfil"] == "sc":
        df = df[df["sc"] == st.session_state["sc"]]
    else:
        filtro = st.selectbox("Filtrar SC", ["Todos"] + SC_LISTA)

        if filtro != "Todos":
            df = df[df["sc"] == filtro]

    st.dataframe(df, use_container_width=True)

def limpar_metas():
    st.subheader("🧹 Limpeza do Sistema")

    st.warning("Use com cuidado. As ações abaixo não podem ser desfeitas.")

    opcao = st.radio(
        "Escolha o que deseja limpar:",
        [
            "Limpar apenas metas",
            "Reset total - limpar metas e devoluções"
        ]
    )

    confirmar = st.checkbox("Confirmo que desejo executar esta limpeza")

    if confirmar:

        if opcao == "Limpar apenas metas":
            if st.button("🧹 LIMPAR APENAS METAS"):
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM metas")
                conn.commit()
                conn.close()

                st.success("Metas removidas com sucesso. Histórico de devoluções mantido.")

        elif opcao == "Reset total - limpar metas e devoluções":
            senha_reset = st.text_input("Digite a senha admin para confirmar", type="password")

            if senha_reset == "admin123":
                if st.button("🗑️ RESET TOTAL DO SISTEMA"):
                    conn = conectar()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM metas")
                    cursor.execute("DELETE FROM devolucoes")
                    conn.commit()
                    conn.close()

                    st.success("Reset total realizado. Sistema zerado para novo lançamento.")
            elif senha_reset:
                st.error("Senha admin incorreta.")


def exportar():
    st.subheader("📤 Exportar Bases")

    resumo = gerar_resumo()
    devolucoes = carregar_devolucoes()
    metas = carregar_metas()

    st.write("### Resumo consolidado")
    st.dataframe(resumo, use_container_width=True)

    st.download_button(
        "Baixar resumo CSV",
        data=resumo.to_csv(index=False, sep=";").encode("utf-8-sig"),
        file_name="resumo_sacas.csv",
        mime="text/csv"
    )

    st.write("### Base de metas")
    st.dataframe(metas, use_container_width=True)

    st.download_button(
        "Baixar metas CSV",
        data=metas.to_csv(index=False, sep=";").encode("utf-8-sig"),
        file_name="metas_sacas.csv",
        mime="text/csv"
    )

    st.write("### Base de devoluções")
    st.dataframe(devolucoes, use_container_width=True)

    st.download_button(
        "Baixar devoluções CSV",
        data=devolucoes.to_csv(index=False, sep=";").encode("utf-8-sig"),
        file_name="devolucoes_sacas.csv",
        mime="text/csv"
    )


def painel_sc():
    sc = st.session_state["sc"]

    st.subheader(f"🏢 Meu Painel - {sc}")

    resumo = gerar_resumo()
    resumo_sc = resumo[resumo["sc"] == sc]

    if resumo_sc.empty:
        st.warning("Sua base ainda não possui quantidade a devolver cadastrada.")
        return

    meta = int(resumo_sc["quantidade_meta"].iloc[0])
    devolvido = int(resumo_sc["quantidade_devolvida"].iloc[0])
    pendente = int(resumo_sc["saldo_pendente"].iloc[0])

    percentual = 0
    if meta > 0:
        percentual = round((devolvido / meta) * 100, 2)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Precisa devolver", f"{meta:,}".replace(",", "."))
    c2.metric("Já devolveu", f"{devolvido:,}".replace(",", "."))
    c3.metric("Falta devolver", f"{pendente:,}".replace(",", "."))
    c4.metric("% Devolvido", f"{percentual}%")

    st.progress(min(percentual / 100, 1.0))

    if pendente <= 0:
        st.success("Base sem pendência de devolução.")
    else:
        st.error(f"Atenção: ainda falta devolver {pendente} sacas.")


criar_tabelas()

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    login()

else:
    cabecalho()

    st.sidebar.image(MASCOTE_PATH, width=120)

    st.sidebar.title("📦 Controle de Sacas")
    st.sidebar.write(f"Usuário: **{st.session_state['usuario']}**")
    st.sidebar.write(f"Perfil: **{st.session_state['perfil'].upper()}**")

    if st.session_state["perfil"] == "sc":
        st.sidebar.write(f"Base: **{st.session_state['sc']}**")

    sair()

    if st.session_state["perfil"] == "admin":
        menu = st.sidebar.radio(
            "Menu Admin",
            [
                "Dashboard",
                "Cadastrar quantidade",
                "Cadastro massivo",
                "Lançar devolução",
                "Histórico",
                "Limpar metas",
                "Exportar"
            ]
        )

        if menu == "Dashboard":
            dashboard_admin()
        elif menu == "Cadastrar quantidade":
            cadastrar_meta()
        elif menu == "Cadastro massivo":
            cadastro_massivo()
        elif menu == "Lançar devolução":
            lancar_devolucao()
        elif menu == "Histórico":
            historico()
        elif menu == "Limpar metas":
            limpar_metas()
        elif menu == "Exportar":
            exportar()

    else:
        menu = st.sidebar.radio(
            "Menu SC",
            [
                "Meu Painel",
                "Lançar devolução",
                "Meu Histórico"
            ]
        )

        if menu == "Meu Painel":
            painel_sc()
        elif menu == "Lançar devolução":
            lancar_devolucao(st.session_state["sc"])
        elif menu == "Meu Histórico":
            historico()
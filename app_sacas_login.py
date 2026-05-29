import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

st.set_page_config(page_title="OpsControl - 袋类管控 Controle de Sacas", page_icon="📦", layout="wide")

DB_NAME = "controle_sacas.db"
LOGO_PATH = "assets/logo_jt.png"
MASCOTE_PATH = "assets/maomao.png"

SC_LISTA = [
    "MG CGE", "BA FEC", "PE JGS", "PR SJS", "RJ SJM", "CE FOR",
    "SN RAO", "SC BNU", "PI THE", "DC SRR-ES", "RS NSR", "MT CGB",
    "GO GYN", "DF BSB", "RO PVH", "SE AJU", "BA VDC", "PA STM",
    "PA MRB", "TO PMW", "MS CGR", "ES SRR","DC SRR-ES"

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
    "dcsrr": {"senha": "dcsrr123", "perfil": "sc", "sc": "DC ES SRR"},
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
            "SC 基地", "目标数量 Quantidade Meta", "已退回 Quantidade Devolvida",
            "待退回 Saldo Pendente", "退回率 Percentual Devolvido", "状态 Status"
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
        lambda x: "已完成 Concluído" if x <= 0 else "待处理 Pendente"
    )

    metas_resumo = metas_resumo.rename(columns={
        "sc": "SC 基地",
        "quantidade_meta": "目标数量 Quantidade Meta",
        "quantidade_devolvida": "已退回 Quantidade Devolvida",
        "saldo_pendente": "待退回 Saldo Pendente",
        "percentual_devolvido": "退回率 Percentual Devolvido",
        "status": "状态 Status"
    })

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
            '<p class="main-title">袋类管控 Controle de Devolução de Sacas</p>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<p class="sub-title">全国管理 • 目标 x 已退回 • 管理仪表板 | Gestão Nacional • Meta x Devolvido • Dashboard Executivo</p>',
            unsafe_allow_html=True
        )

    with col3:
        st.image(MASCOTE_PATH, width=120)

    st.divider()


def login():
    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.image(LOGO_PATH, width=260)

        st.markdown("## 📦 袋类管控 Controle de Sacas")
        st.markdown("### 登录 Login do Sistema")

        usuario = st.text_input("用户 Usuário")
        senha = st.text_input("密码 Senha", type="password")

        if st.button("进入 Entrar", use_container_width=True):
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
                st.error("用户名或密码无效 Usuário ou senha inválidos.")


def sair():
    if st.sidebar.button("退出 Sair"):
        st.session_state.clear()
        st.rerun()


def dashboard_admin():
    st.subheader("📊 管理仪表板 Dashboard Executivo")

    resumo = gerar_resumo()

    if resumo.empty:
        st.warning("尚未登记目标数量 Nenhuma meta cadastrada ainda.")
        return

    total_meta = int(resumo["目标数量 Quantidade Meta"].sum())
    total_devolvido = int(resumo["已退回 Quantidade Devolvida"].sum())
    total_pendente = int(resumo["待退回 Saldo Pendente"].sum())

    percentual_geral = 0
    if total_meta > 0:
        percentual_geral = round((total_devolvido / total_meta) * 100, 2)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("应退回总量 Total a devolver", f"{total_meta:,}".replace(",", "."))
    c2.metric("已退回总量 Total devolvido", f"{total_devolvido:,}".replace(",", "."))
    c3.metric("待退回数量 Saldo pendente", f"{total_pendente:,}".replace(",", "."))
    c4.metric("退回率 % Devolvido", f"{percentual_geral}%")

    st.progress(min(percentual_geral / 100, 1.0))
    st.divider()

    filtro = st.selectbox("筛选SC Filtrar SC", ["Todos"] + SC_LISTA)
    resumo_filtrado = resumo.copy()

    if filtro != "Todos":
        resumo_filtrado = resumo_filtrado[resumo_filtrado["SC 基地"] == filtro]

    st.subheader("📋 各基地汇总 Resumo por Base")
    st.dataframe(resumo_filtrado, use_container_width=True)

    st.subheader("📉 各SC待退回数量 Saldo pendente por SC")
    if not resumo_filtrado.empty:
        st.bar_chart(resumo_filtrado.set_index("SC 基地")["待退回 Saldo Pendente"])

    st.subheader("🚨 问题基地排名 Ranking Bases Ofensoras")
    ranking = resumo.sort_values(by="待退回 Saldo Pendente", ascending=False)
    ranking = ranking[ranking["待退回 Saldo Pendente"] > 0][[
        "SC 基地",
        "目标数量 Quantidade Meta",
        "已退回 Quantidade Devolvida",
        "待退回 Saldo Pendente",
        "退回率 Percentual Devolvido",
        "状态 Status"
    ]]
    st.dataframe(ranking, use_container_width=True)


def cadastrar_meta():
    st.subheader("📝 登记应退回数量 Cadastrar Quantidade a Devolver")

    with st.form("form_meta"):
        sc = st.selectbox("SC 基地", SC_LISTA)
        quantidade = st.number_input("应退回数量 Quantidade que precisa devolver", min_value=1, step=1)
        salvar = st.form_submit_button("保存数量 Salvar quantidade")

        if salvar:
            inserir_meta(sc, quantidade)
            st.success(f"目标已登记 Meta cadastrada para {sc}: {quantidade} sacas.")


def cadastro_massivo():
    st.subheader("📥 批量登记目标 Cadastro Massivo de Metas")

    st.info("格式 Formato: SC;quantidade. 示例 Exemplo: MG CGE;250 ou CGE;250")

    texto = st.text_area(
        "粘贴目标数据 Cole as metas aqui",
        height=230,
        placeholder="MG CGE;250\nBA FEC;100\nPE JGS;300"
    )

    if st.button("处理粘贴文本 Processar texto colado"):
        linhas = texto.splitlines()
        total = 0
        erros = []

        for linha in linhas:
            if not linha.strip():
                continue

            try:
                partes = linha.replace(",", ";").split(";")

                if len(partes) < 2:
                    erros.append(f"无效行 Linha inválida: {linha}")
                    continue

                sc_original = partes[0].strip()
                qtd = int(float(str(partes[1]).strip().replace(".", "").replace(",", ".")))

                sc_final = normalizar_sc(sc_original)

                if sc_final is None:
                    erros.append(f"SC未找到 SC não localizado: {sc_original}")
                    continue

                inserir_meta(sc_final, qtd)
                total += 1

            except Exception as e:
                erros.append(f"行错误 Erro na linha: {linha} | {e}")

        if total > 0:
            st.success(f"{total} 个目标导入成功 metas importadas com sucesso.")

        if erros:
            st.warning("部分行未导入 Algumas linhas não foram importadas:")
            st.write(erros)

    st.divider()

    st.subheader("📤 导入CSV Importar CSV")

    st.markdown("""
    CSV文件必须包含以下列 O CSV deve conter as colunas:

    ```text
    sc;quantidade
    MG CGE;250
    BA FEC;100
    ```
    """)

    arquivo = st.file_uploader("选择CSV文件 Selecione o arquivo CSV", type=["csv"])

    if arquivo is not None:
        try:
            try:
                df = pd.read_csv(arquivo, sep=";")
            except Exception:
                arquivo.seek(0)
                df = pd.read_csv(arquivo, sep=",")

            df.columns = [str(c).strip().lower() for c in df.columns]

            if "sc" not in df.columns or "quantidade" not in df.columns:
                st.error("CSV必须包含列: sc 和 quantidade | O CSV precisa ter as colunas: sc e quantidade")
                return

            st.write("文件预览 Pré-visualização do arquivo:")
            st.dataframe(df, use_container_width=True)

            if st.button("导入CSV到系统 Importar CSV para o sistema"):
                total = 0
                erros = []

                for _, row in df.iterrows():
                    sc_original = row["sc"]
                    qtd = int(row["quantidade"])
                    sc_final = normalizar_sc(sc_original)

                    if sc_final is None:
                        erros.append(f"SC未找到 SC não localizado: {sc_original}")
                        continue

                    inserir_meta(sc_final, qtd)
                    total += 1

                if total > 0:
                    st.success(f"{total} 个目标通过CSV导入 metas importadas via CSV.")

                if erros:
                    st.warning("部分行未导入 Algumas linhas não foram importadas:")
                    st.write(erros)

        except Exception as e:
            st.error(f"导入CSV错误 Erro ao importar CSV: {e}")


def lancar_devolucao(sc_usuario=None):
    st.subheader("🚚 退回登记 Lançar Devolução")

    if st.session_state["perfil"] == "admin":
        sc = st.selectbox("SC 基地", SC_LISTA)
    else:
        sc = sc_usuario
        st.info(f"当前基地 Base logada: {sc}")

    with st.form("form_dev"):
        data_devolucao = st.date_input("退回日期 Data da devolução", value=date.today())
        id_retorno = st.text_input("退回ID / 调拨ID ID de retorno / transferência")
        placa = st.text_input("车辆牌照 Placa do veículo")
        quantidade = st.number_input("退回数量 Quantidade devolvida", min_value=1, step=1)
        salvar = st.form_submit_button("保存退回 Salvar devolução")

        if salvar:
            if not id_retorno.strip() or not placa.strip():
                st.error("请填写退回ID和车辆牌照 Preencha o ID de retorno e a placa do veículo.")
            else:
                inserir_devolucao(
                    data_devolucao,
                    sc,
                    id_retorno,
                    placa,
                    quantidade,
                    st.session_state["usuario"]
                )
                st.success("退回登记成功 Devolução lançada com sucesso.")


def historico():
    st.subheader("📋 退回历史 Histórico de Devoluções")

    df = carregar_devolucoes()

    if df.empty:
        st.warning("暂无退回记录 Nenhuma devolução registrada.")
        return

    if st.session_state["perfil"] == "sc":
        df = df[df["sc"] == st.session_state["sc"]]
    else:
        filtro = st.selectbox("筛选SC Filtrar SC", ["Todos"] + SC_LISTA)

        if filtro != "Todos":
            df = df[df["sc"] == filtro]

    df = df.rename(columns={
        "id": "ID 编号",
        "data_devolucao": "退回日期 Data Devolução",
        "sc": "SC 基地",
        "id_retorno": "退回ID ID Retorno",
        "placa": "车辆牌照 Placa",
        "quantidade": "数量 Quantidade",
        "usuario": "用户 Usuário"
    })

    st.dataframe(df, use_container_width=True)


def limpar_metas():
    st.subheader("🧹 系统清理 Limpeza do Sistema")

    st.warning(
        "谨慎使用。清理目标不会删除退回历史。 "
        "Use com cuidado. Limpar metas não apaga o histórico de devoluções."
    )

    opcao = st.radio(
        "选择清理类型 Escolha o que deseja limpar:",
        [
            "仅清理目标 Limpar apenas metas",
            "全部重置 - 清理目标和退回记录 Reset total - limpar metas e devoluções"
        ]
    )

    confirmar = st.checkbox("确认执行清理 Confirmo que desejo executar esta limpeza")

    if confirmar:
        if opcao == "仅清理目标 Limpar apenas metas":
            if st.button("🧹 仅清理目标 LIMPAR APENAS METAS"):
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM metas")
                conn.commit()
                conn.close()

                st.success("目标已清理，退回历史已保留. Metas removidas, histórico mantido.")

        elif opcao == "全部重置 - 清理目标和退回记录 Reset total - limpar metas e devoluções":
            senha_reset = st.text_input("输入管理员密码 Digite a senha admin para confirmar", type="password")

            if senha_reset == "admin123":
                if st.button("🗑️ 全部重置 RESET TOTAL DO SISTEMA"):
                    conn = conectar()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM metas")
                    cursor.execute("DELETE FROM devolucoes")
                    conn.commit()
                    conn.close()

                    st.success("系统已全部清空 Sistema zerado com sucesso.")
            elif senha_reset:
                st.error("管理员密码错误 Senha admin incorreta.")


def exportar():
    st.subheader("📤 导出数据 Exportar Bases")

    resumo = gerar_resumo()
    devolucoes = carregar_devolucoes()
    metas = carregar_metas()

    st.write("### 汇总数据 Resumo consolidado")
    st.dataframe(resumo, use_container_width=True)

    st.download_button(
        "下载汇总CSV Baixar resumo CSV",
        data=resumo.to_csv(index=False, sep=";").encode("utf-8-sig"),
        file_name="resumo_sacas.csv",
        mime="text/csv"
    )

    st.write("### 目标数据 Base de metas")
    st.dataframe(metas, use_container_width=True)

    st.download_button(
        "下载目标CSV Baixar metas CSV",
        data=metas.to_csv(index=False, sep=";").encode("utf-8-sig"),
        file_name="metas_sacas.csv",
        mime="text/csv"
    )

    st.write("### 退回数据 Base de devoluções")
    st.dataframe(devolucoes, use_container_width=True)

    st.download_button(
        "下载退回CSV Baixar devoluções CSV",
        data=devolucoes.to_csv(index=False, sep=";").encode("utf-8-sig"),
        file_name="devolucoes_sacas.csv",
        mime="text/csv"
    )


def painel_sc():
    sc = st.session_state["sc"]

    st.subheader(f"🏢 我的面板 Meu Painel - {sc}")

    resumo = gerar_resumo()
    resumo_sc = resumo[resumo["SC 基地"] == sc]

    if resumo_sc.empty:
        st.warning("您的基地尚未登记应退回数量 Sua base ainda não possui quantidade a devolver cadastrada.")
        return

    meta = int(resumo_sc["目标数量 Quantidade Meta"].iloc[0])
    devolvido = int(resumo_sc["已退回 Quantidade Devolvida"].iloc[0])
    pendente = int(resumo_sc["待退回 Saldo Pendente"].iloc[0])

    percentual = 0
    if meta > 0:
        percentual = round((devolvido / meta) * 100, 2)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("应退回 Precisa devolver", f"{meta:,}".replace(",", "."))
    c2.metric("已退回 Já devolveu", f"{devolvido:,}".replace(",", "."))
    c3.metric("待退回 Falta devolver", f"{pendente:,}".replace(",", "."))
    c4.metric("退回率 % Devolvido", f"{percentual}%")

    st.progress(min(percentual / 100, 1.0))

    if pendente <= 0:
        st.success("基地无退回待处理 Base sem pendência de devolução.")
    else:
        st.error(f"注意：仍需退回 {pendente} 个 sacas. Atenção: ainda falta devolver {pendente} sacas.")


criar_tabelas()

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    login()

else:
    cabecalho()

    st.sidebar.image(MASCOTE_PATH, width=120)

    st.sidebar.title("📦 袋类管控 Controle de Sacas")
    st.sidebar.write(f"用户 Usuário: **{st.session_state['usuario']}**")
    st.sidebar.write(f"权限 Perfil: **{st.session_state['perfil'].upper()}**")

    if st.session_state["perfil"] == "sc":
        st.sidebar.write(f"基地 Base: **{st.session_state['sc']}**")

    sair()

    if st.session_state["perfil"] == "admin":
        menu = st.sidebar.radio(
            "管理员菜单 Menu Admin",
            [
                "仪表板 Dashboard",
                "登记数量 Cadastrar quantidade",
                "批量登记 Cadastro massivo",
                "退回登记 Lançar devolução",
                "历史 Histórico",
                "清理数据 Limpar metas",
                "导出 Exportar"
            ]
        )

        if menu == "仪表板 Dashboard":
            dashboard_admin()
        elif menu == "登记数量 Cadastrar quantidade":
            cadastrar_meta()
        elif menu == "批量登记 Cadastro massivo":
            cadastro_massivo()
        elif menu == "退回登记 Lançar devolução":
            lancar_devolucao()
        elif menu == "历史 Histórico":
            historico()
        elif menu == "清理数据 Limpar metas":
            limpar_metas()
        elif menu == "导出 Exportar":
            exportar()

    else:
        menu = st.sidebar.radio(
            "SC菜单 Menu SC",
            [
                "我的面板 Meu Painel",
                "退回登记 Lançar devolução",
                "我的历史 Meu Histórico"
            ]
        )

        if menu == "我的面板 Meu Painel":
            painel_sc()
        elif menu == "退回登记 Lançar devolução":
            lancar_devolucao(st.session_state["sc"])
        elif menu == "我的历史 Meu Histórico":
            historico()
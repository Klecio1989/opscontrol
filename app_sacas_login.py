import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client
import uuid

st.set_page_config(
    page_title="OpsControl - 袋类管控 Controle de Sacas",
    page_icon="📦",
    layout="wide"
)

LOGO_PATH = "assets/logo_jt.png"
MASCOTE_PATH = "assets/maomao.png"

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
SUPABASE_BUCKET = st.secrets["SUPABASE_BUCKET"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

VALOR_UNITARIO_SACA = 3.00

SC_LISTA = [
    "MG CGE", "BA FEC", "PE JGS", "PR SJS", "RJ SJM", "CE FOR",
    "SN RAO", "SC BNU", "PI THE", "DC SRR-ES", "RS NSR", "MT CGB",
    "GO GYN", "DF BSB", "RO PVH", "SE AJU", "BA VDC", "PA STM",
    "PA MRB", "TO PMW", "MS CGR", "ES SRR","PA ANA"

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
    "ana": {"senha": "ana123", "perfil": "sc", "sc": "PA ANA"}
}

st.markdown("""
<style>

/* =========================
   FUNDO GERAL
========================= */
.stApp {
    background-color: #f4f4f4;
    color: #222222 !important;
}

section[data-testid="stSidebar"] * {
    color: #222222 !important;
}

/* =========================
   SIDEBAR
========================= */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e5e5e5;
}

/* =========================
   CABEÇALHO
========================= */
.ops-header {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* =========================
   TITULOS
========================= */
.main-title {
    font-size: 32px;
    font-weight: 900;
    color: #e60012 !important;
    text-align: center;
    margin-bottom: 5px;
}

.sub-title {
    font-size: 16px;
    color: #555555 !important;
    font-weight: 600;
    text-align: center;
}

/* =========================
   TEXTO GERAL
========================= */
h1,h2,h3,h4,h5,h6,p,label,span {
    color: #222222 !important;
}

/* =========================
   INPUTS
========================= */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
textarea {
    background-color: white !important;
    color: black !important;
    border-radius: 8px;
}

/* =========================
   SELECTBOX
========================= */
[data-baseweb="select"] {
    background-color: white !important;
    color: black !important;
}

/* =========================
   RADIO
========================= */
div[role="radiogroup"] {
    background-color: white;
    padding: 10px;
    border-radius: 10px;
}

/* =========================
   MÉTRICAS
========================= */
[data-testid="metric-container"] {
    background-color: white;
    border-radius: 12px;
    padding: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}

/* =========================
   DATAFRAMES
========================= */
[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 10px;
}

/* =========================
   BOTÕES
========================= */
.stButton > button {
    background-color: #e60012;
    color: white !important;
    border: none;
    border-radius: 10px;
    font-weight: bold;
    height: 45px;
}

.stButton > button:hover {
    background-color: #c70010;
    color: white !important;
}

/* =========================
   ALERTAS
========================= */
[data-testid="stAlert"] {
    border-radius: 10px;
}

/* =========================
   MOBILE
========================= */
@media (max-width: 768px) {

    .main-title {
        font-size: 22px;
    }

    .sub-title {
        font-size: 11px;
    }

    .ops-header {
        padding: 12px;
    }

    [data-testid="metric-container"] {
        padding: 8px;
    }

    .stButton > button {
        width: 100%;
    }
}

</style>

""", unsafe_allow_html=True)

def inserir_meta(sc, quantidade):
    supabase.table("metas").insert({
        "sc": sc,
        "quantidade_meta": int(quantidade),
        "data_cadastro": str(date.today())
    }).execute()


def inserir_devolucao(data_devolucao, sc, id_retorno, placa, quantidade, usuario, foto_url):
    supabase.table("devolucoes").insert({
        "data_devolucao": str(data_devolucao),
        "sc": sc,
        "id_retorno": id_retorno.strip(),
        "placa": placa.upper().strip(),
        "quantidade": int(quantidade),
        "usuario": usuario,
        "foto_url": foto_url,
        "observacao": observacao,
        
    }).execute()


def carregar_metas():
    res = supabase.table("metas").select("*").execute()
    return pd.DataFrame(res.data)


def carregar_devolucoes():
    res = supabase.table("devolucoes").select("*").execute()
    return pd.DataFrame(res.data)


def upload_foto(arquivo, sc, id_retorno):
    if arquivo is None:
        return ""

    extensao = arquivo.name.split(".")[-1].lower() if "." in arquivo.name else "jpg"

    sc_limpo = sc.replace(" ", "_").replace("/", "_")
    id_limpo = id_retorno.replace(" ", "_").replace("/", "_")

    nome_arquivo = f"{sc_limpo}/{id_limpo}_{uuid.uuid4()}.{extensao}"
    conteudo = arquivo.getvalue()

    try:
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=nome_arquivo,
            file=conteudo,
            file_options={
                "content-type": arquivo.type,
                "upsert": "true"
            }
        )

        return supabase.storage.from_(SUPABASE_BUCKET).get_public_url(nome_arquivo)

    except Exception as e:
        st.error(f"Erro ao enviar foto para o Supabase: {e}")
        return ""


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
        (metas_resumo["quantidade_devolvida"] / metas_resumo["quantidade_meta"]) * 100
    ).fillna(0).round(2)

    metas_resumo["valor_financeiro"] = (
    metas_resumo["saldo_pendente"] * VALOR_UNITARIO_SACA
    ).round(2)

    metas_resumo["status"] = metas_resumo["saldo_pendente"].apply(
        lambda x: "已完成 Concluído" if x <= 0 else "待处理 Pendente"
    )

    return metas_resumo.rename(columns={
        "sc": "SC 基地",
        "quantidade_meta": "目标数量 Quantidade Meta",
        "quantidade_devolvida": "已退回 Quantidade Devolvida",
        "saldo_pendente": "待退回 Saldo Pendente",
        "percentual_devolvido": "退回率 Percentual Devolvido",
        "valor_financeiro": "💰 Valor Financeiro",
        "status": "状态 Status"
        
    })


def normalizar_sc(sc):
    sc = str(sc).strip().upper()
    mapa = {x.upper(): x for x in SC_LISTA}

    if sc in mapa:
        return mapa[sc]

    for item in SC_LISTA:
        if sc == item.split()[-1].upper():
            return item

    return None


def cabecalho():

    st.markdown("""
    <div class="ops-header">
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,4,1])

    with col1:
        st.image(LOGO_PATH, width=140)

    with col2:
        st.markdown("""
        <div class="main-title">
        袋类管控 Controle de Sacas
        </div>

        <div class="sub-title">
        Gestão Nacional de Devolução de Sacas
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.image(MASCOTE_PATH, width=90)

    st.markdown("</div>", unsafe_allow_html=True)


def login():
    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:

        st.image(LOGO_PATH, width=260)

        st.markdown("""
        <div style="
        background:white;
        padding:15px;
        border-radius:12px;
        text-align:center;
        margin-bottom:15px;
        box-shadow:0px 2px 8px rgba(0,0,0,0.08);
        ">

        <h2 style="color:#e60012;">
        📦 袋类管控 Controle de Sacas
        </h2>

        <h4 style="color:#333333;">
        登录 Login do Sistema
        </h4>

        </div>
        """, unsafe_allow_html=True)

        usuario = st.text_input("用户 Usuário")
        senha = st.text_input("密码 Senha", type="password")

        if st.button("进入 Entrar", use_container_width=True):

            usuario_digitado = usuario.strip()

            usuario_digitado = (
                "admin"
                if usuario_digitado.lower() == "admin"
                else usuario_digitado.upper()
            )

            if (
                usuario_digitado in USUARIOS
                and senha == USUARIOS[usuario_digitado]["senha"]
            ):

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
    percentual_geral = round((total_devolvido / total_meta) * 100, 2) if total_meta > 0 else 0
    total_valor = resumo["💰 Valor Financeiro"].sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("应退回总量 Total a devolver", f"{total_meta:,}".replace(",", "."))
    c2.metric("已退回总量 Total devolvido", f"{total_devolvido:,}".replace(",", "."))
    c3.metric("待退回数量 Saldo pendente", f"{total_pendente:,}".replace(",", "."))
    c4.metric("退回率 % Devolvido", f"{percentual_geral}%")
    c5.metric("💰 金融风险 Risco Financeiro", f"R$ {total_valor:,.2f}")

    st.progress(min(percentual_geral / 100, 1.0))
    st.divider()

    filtro = st.selectbox("筛选SC Filtrar SC", ["Todos"] + SC_LISTA)
    resumo_filtrado = resumo if filtro == "Todos" else resumo[resumo["SC 基地"] == filtro]

    st.subheader("📋 各基地汇总 Resumo por Base")
    st.dataframe(resumo_filtrado, use_container_width=True)

    st.subheader("📉 各SC待退回数量 Saldo pendente por SC")
    if not resumo_filtrado.empty:
        st.bar_chart(resumo_filtrado.set_index("SC 基地")["待退回 Saldo Pendente"])

    st.subheader("🚨 问题基地排名 Ranking Bases Ofensoras")
    ranking = resumo.sort_values(by="待退回 Saldo Pendente", ascending=False)
    ranking = ranking[ranking["待退回 Saldo Pendente"] > 0]
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
        total = 0
        erros = []

        for linha in texto.splitlines():
            if not linha.strip():
                continue

            try:
                partes = linha.replace(",", ";").split(";")
                sc_final = normalizar_sc(partes[0].strip())
                qtd = int(float(str(partes[1]).strip().replace(".", "").replace(",", ".")))

                if sc_final is None:
                    erros.append(f"SC未找到 SC não localizado: {partes[0]}")
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

            st.dataframe(df, use_container_width=True)

            if st.button("导入CSV到系统 Importar CSV para o sistema"):
                total = 0
                erros = []

                for _, row in df.iterrows():
                    sc_final = normalizar_sc(row["sc"])

                    if sc_final is None:
                        erros.append(f"SC未找到 SC não localizado: {row['sc']}")
                        continue

                    inserir_meta(sc_final, int(row["quantidade"]))
                    total += 1

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

    data_devolucao = st.date_input("退回日期 Data da devolução", value=date.today())
    id_retorno = st.text_input("退回ID / 调拨ID ID de retorno / transferência")
    placa = st.text_input("车辆牌照 Placa do veículo")
    quantidade = st.number_input("退回数量 Quantidade devolvida", min_value=1, step=1)
    observacao = st.text_area(
    "📝 Observação",
    placeholder="Digite alguma observação sobre a devolução..."
)

    st.markdown("### 📷 照片证据 Evidência da Devolução")

    st.markdown("### 📷 Foto Obrigatória da Devolução")



    if "abrir_camera" not in st.session_state:
     st.session_state["abrir_camera"] = False

    if st.button("📷 Abrir câmera para tirar foto"):
     st.session_state["abrir_camera"] = True

    foto_final = None

    if st.session_state["abrir_camera"]:
     foto_final = st.camera_input("📷 Tire a foto da devolução")

    if foto_final is not None:
        st.image(
            foto_final,
            caption="Pré-visualização da foto",
            use_container_width=True
        )

    if st.button("保存退回 Salvar devolução"):
        if not id_retorno.strip():
            st.error("Informe o ID de retorno.")
            return

        if not placa.strip():
            st.error("Informe a placa.")
            return

        if foto_final is None:
            st.error("照片必填 - A foto é obrigatória.")
            return

        foto_url = upload_foto(foto_final, sc, id_retorno)

        if not foto_url:
            st.error("Erro ao salvar a foto. A devolução não foi registrada.")
            return

        inserir_devolucao(
            data_devolucao,
            sc,
            id_retorno,
            placa,
            quantidade,
            st.session_state["usuario"],
            foto_url,
            observacao
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

    if "foto_url" in df.columns:
        df["证据 Evidência"] = df["foto_url"].apply(lambda x: "🔗 Ver foto" if x else "")

    st.dataframe(df, use_container_width=True)

    st.subheader("🔍 查看照片证据 Visualizar Evidência")

    fotos = df[df["foto_url"].notna() & (df["foto_url"] != "")] if "foto_url" in df.columns else pd.DataFrame()

    if not fotos.empty:
        opcoes = {
            f"{row['sc']} | {row['id_retorno']} | {row['placa']} | {row['data_devolucao']}": row["foto_url"]
            for _, row in fotos.iterrows()
        }

        escolha = st.selectbox("选择记录 Selecione o registro", list(opcoes.keys()))
        st.image(opcoes[escolha], caption=escolha, use_container_width=True)
        st.link_button("打开照片 Abrir foto", opcoes[escolha])
    else:
        st.info("暂无照片证据 Nenhuma evidência com foto registrada.")


def limpar_metas():
    st.subheader("🧹 系统清理 Limpeza do Sistema")

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
                supabase.table("metas").delete().neq("id", -1).execute()
                st.success("目标已清理，退回历史已保留. Metas removidas, histórico mantido.")

        elif opcao == "全部重置 - 清理目标和退回记录 Reset total - limpar metas e devoluções":
            senha_reset = st.text_input("输入管理员密码 Digite a senha admin para confirmar", type="password")

            if senha_reset == "admin123":
                if st.button("🗑️ 全部重置 RESET TOTAL DO SISTEMA"):
                    supabase.table("metas").delete().neq("id", -1).execute()
                    supabase.table("devolucoes").delete().neq("id", -1).execute()
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
        resumo.to_csv(index=False, sep=";").encode("utf-8-sig"),
        "resumo_sacas.csv",
        "text/csv"
    )

    st.write("### 目标数据 Base de metas")
    st.dataframe(metas, use_container_width=True)

    st.download_button(
        "下载目标CSV Baixar metas CSV",
        metas.to_csv(index=False, sep=";").encode("utf-8-sig"),
        "metas_sacas.csv",
        "text/csv"
    )

    st.write("### 退回数据 Base de devoluções")
    st.dataframe(devolucoes, use_container_width=True)

    st.download_button(
        "下载退回CSV Baixar devoluções CSV",
        devolucoes.to_csv(index=False, sep=";").encode("utf-8-sig"),
        "devolucoes_sacas.csv",
        "text/csv"
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
    percentual = round((devolvido / meta) * 100, 2) if meta > 0 else 0
    risco_financeiro = pendente * VALOR_UNITARIO_SACA

    c1, c2, c3, c4,c5 = st.columns(5)
    c1.metric("应退回 Precisa devolver", f"{meta:,}".replace(",", "."))
    c2.metric("已退回 Já devolveu", f"{devolvido:,}".replace(",", "."))
    c3.metric("待退回 Falta devolver", f"{pendente:,}".replace(",", "."))
    c4.metric("退回率 % Devolvido", f"{percentual}%")
    c5.metric("💰金融风险 Risco Financeiro", f"R$ {risco_financeiro:,.2f}")

    st.progress(min(percentual / 100, 1.0))

    if pendente <= 0:
        st.success("基地无退回待处理 Base sem pendência de devolução.")
    else:
        st.error(f"注意：仍需退回 {pendente} 个 sacas. Atenção: ainda falta devolver {pendente} sacas.")


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

import streamlit as st
import datetime
import pandas as pd
from fpdf import FPDF
from PIL import Image
import io

# Configuração da página web/móvel
st.set_page_config(page_title="AEP Digital - MTE NR 1 & NR 17", layout="centered")

st.title("📱 Sistema AEP Digital")
st.subheader("Avaliação Ergonômica Preliminar Ocupacional")
st.caption("Versão Premium - Com Termo de Conformidade e Evidência Fotográfica")

# 1. IDENTIFICAÇÃO DO POSTO
st.markdown("### 1. Identificação do Posto e Grupo de Exposição")
empresa = st.text_input("Empresa / Unidade:", value="Indústrias Alfa S.A.")
setor_posto = st.text_input("Setor e Posto Avaliado:", value="Atendimento ao Cliente")
cargo = st.text_input("Cargo(s) Avaliado(s) / Função:", value="Operador de Telemarketing")
trabalhadores = st.number_input("Nº de Trabalhadores Expostos (GHE/GHO):", min_value=1, value=12)
avaliador = st.text_input("Nome do Avaliador / Responsável Técnico:", value="Eng. Carlos Silva")

# REQUISITO EXCLUSIVO: Evidência fotográfica por câmera ou arquivo
st.markdown("### 📷 Evidência Fotográfica do Posto")
foto_modo = st.radio("Como deseja anexar a foto?", ["Usar a Câmera do Celular", "Carregar da Galeria/Arquivo", "Não anexar foto"])

foto_processada = None
if foto_modo == "Usar a Câmera do Celular":
    foto_capturada = st.camera_input("Tire a foto do posto de trabalho:")
    if foto_capturada:
        foto_processada = Image.open(foto_capturada)
elif foto_modo == "Carregar da Galeria/Arquivo":
    foto_carregada = st.file_uploader("Escolha a imagem do posto:", type=["png", "jpg", "jpeg"])
    if foto_carregada:
        foto_processada = Image.open(foto_carregada)

severidade_opcoes = {1: "1 - Leve", 2: "2 - Moderada", 3: "3 - Significativa", 4: "4 - Severa"}
probabilidade_opcoes = {1: "1 - Rara", 2: "2 - Remota", 3: "3 - Possível", 4: "4 - Frequente"}

# CHECKLIST COMPLETO NR 17
riscos_nr17 = {
    "NR 17.5 - Levantamento, Transporte e Descarga Manual de Cargas": [
        "Levantamento de cargas com peso superior aos limites recomendados pela NR 17",
        "Transporte manual de cargas por distância ou frequência excessiva sem pausas",
        "Posturas críticas, flexão extrema ou rotação severa do tronco na movimentação"
    ],
    "NR 17.6 - Mobiliário dos Postos de Trabalho": [
        "Superfície de trabalho (bancada/mesa) com altura ou dimensões inadequadas",
        "Falta de espaço livre para as pernas e pés na zona inferior da mesa",
        "Assentos sem sistemas ajustáveis de altura, inclinação ou sem apoio lombar"
    ],
    "NR 17.7 - Equipamentos e Ferramentas de Trabalho": [
        "Ferramentas que exigem força excessiva ou compressão mecânica nos tecidos da mão",
        "Monitores, telas ou painéis posicionados fora da zona de alcance visual ótimo"
    ],
    "NR 17.8 - Condições Ambientais de Trabalho": [
        "Níveis de ruído contínuo ou intermitente gerando desconforto ou fadiga cognitiva",
        "Índice de temperatura, umidade ou velocidade do ar fora da zona de conforto térmico",
        "Iluminamento geral ou localizado insuficiente ou excessivo no campo de trabalho"
    ],
    "NR 17.4 - Organização do Trabalho e Fatores Psicossociais": [
        "Exigência de ritmo de trabalho excessivo imposto por máquinas, sistemas ou chefia",
        "Cobrança rígida de metas de produtividade com monitoramento individual contínuo",
        "Ausência de autonomia ou controle do trabalhador sobre seus métodos e pausas"
    ]
}

st.markdown("### 2. Avaliação de Fatores de Risco (Matriz do MTE)")
riscos_avaliados = []

for bloco, itens in riscos_nr17.items():
    with st.expander(bloco, expanded=False):
        for item in itens:
            check = st.checkbox(f"Detectado: {item}", key=item)
            if check:
                col1, col2 = st.columns(2)
                with col1:
                    sev = st.selectbox("Severidade:", options=[1, 2, 3, 4], format_func=lambda x: severidade_opcoes[x], key=f"sev_{item}")
                with col2:
                    prob = st.selectbox("Probabilidade:", options=[1, 2, 3, 4], format_func=lambda x: probabilidade_opcoes[x], key=f"prob_{item}")
                nivel_risco = sev * prob
                classificacao = "Baixo" if nivel_risco <= 3 else "Médio" if nivel_risco <= 8 else "Alto" if nivel_risco <= 12 else "Crítico"
                riscos_avaliados.append({"Risco": item, "Severidade": sev, "Probabilidade": prob, "Nível": nivel_risco, "Classe": classificacao})

# 3. PLANO DE AÇÃO
st.markdown("### 3. Plano de Ação Preventivo / Corretivo")
plano_acoes = []
risks_needed = [r for r in riscos_avaliados if r["Nível"] >= 4]

if risks_needed:
    for r in risks_needed:
        st.markdown(f"**Medida para:** *{r['Risco']}*")
        col1, col2 = st.columns(2)
        with col1:
            oque = st.text_input("O que fazer? (Medida)", value="Implantar melhoria de engenharia / adequação", key=f"act_{r['Risco']}")
            quem = st.text_input("Responsável:", value="Engenharia / SESMT", key=f"who_{r['Risco']}")
        with col2:
            prazo = st.text_input("Prazo:", value="30 dias", key=f"praz_{r['Risco']}")
            status = st.selectbox("Status:", ["Pendente", "Em Andamento"], key=f"st_{r['Risco']}")
        plano_acoes.append({"Risco": r["Risco"], "Medida": oque, "Quem": quem, "Prazo": prazo, "Status": status})

# 4. EXPORTAÇÃO E GERAÇÃO DE PDF
st.markdown("### 4. Emissão do Laudo Técnico")

class PDFLaudoMTE(FPDF):
    def header(self):
        self.set_fill_color(18, 38, 58)
        self.rect(0, 0, 210, 24, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 12)
        self.set_y(5)
        self.cell(190, 6, "AVALIAÇÃO ERGONÔMICA PRELIMINAR (AEP) - INVENTÁRIO PGR", ln=True, align="C")
        self.set_font("Arial", "I", 8.5)
        self.cell(190, 5, "Documento Técnico Integrado - NR 1 & NR 17", ln=True, align="C")
        self.set_y(28)
        
    def footer(self):
        self.set_y(-12)
        self.set_font("Arial", "I", 7.5)
        self.set_text_color(120, 120, 120)
        self.cell(95, 6, f"Emitido em: {datetime.date.today().strftime('%d/%m/%Y')}", align="L")
        self.cell(95, 6, f"Página {self.page_no()}", align="R")

if st.button("Gerar e Validar PDF Oficial"):
    pdf = PDFLaudoMTE()
    pdf.add_page()
    pdf.set_text_color(60, 60, 60)
    
    # Bloco 1: Dados Cadastrais
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(18, 38, 58)
    pdf.cell(190, 6, "1. DADOS DE IDENTIFICAÇÃO E RASTREABILIDADE", ln=True)
    pdf.set_text_color(60, 60, 60)
    
    pdf.set_font("Arial", "B", 8)
    pdf.cell(35, 5, " Empresa / Unidade:", border=1)
    pdf.set_font("Arial", size=8)
    pdf.cell(155, 5, f" {empresa}", border=1, ln=True)
    
    pdf.set_font("Arial", "B", 8)
    pdf.cell(35, 5, " Setor / Posto:", border=1)
    pdf.set_font("Arial", size=8)
    pdf.cell(65, 5, f" {setor_posto}", border=1)
    pdf.set_font("Arial", "B", 8)
    pdf.cell(35, 5, " Cargo Avaliado:", border=1)
    pdf.set_font("Arial", size=8)
    pdf.cell(55, 5, f" {cargo}", border=1, ln=True)
    
    # Inserção inteligente da imagem no bloco de identificação
    y_pos_antes_foto = pdf.get_y()
    if foto_processada:
        # Salva a imagem temporariamente em formato JPEG para o FPDF injetar
        img_byte_arr = io.BytesIO()
        foto_processada.convert('RGB').save(img_byte_arr, format='JPEG', quality=80)
        img_byte_arr.seek(0)
        # Posiciona a imagem ao lado direito
        pdf.image(img_byte_arr, x=145, y=y_pos_antes_foto + 2, w=55, h=38)
        largura_campo_info = 100
    else:
        largura_campo_info = 155

    pdf.set_font("Arial", "B", 8)
    pdf.cell(35, 5, " Efetivo Exposto:", border=1)
    pdf.set_font("Arial", size=8)
    pdf.cell(largura_campo_info, 5, f" {trabalhadores} trabalhadores", border=1, ln=True)
    
    pdf.set_font("Arial", "B", 8)
    pdf.cell(35, 5, " Resp. Técnico:", border=1)
    pdf.set_font("Arial", size=8)
    pdf.cell(largura_campo_info, 5, f" {avaliador}", border=1, ln=True)
    
    # Garante o espaçamento correto caso a foto tenha sido impressa
    if foto_processada:
        pdf.set_y(y_pos_antes_foto + 43)
    else:
        pdf.ln(5)
        
    # Bloco 2: Inventário / Termo de Conformidade
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(18, 38, 58)
    pdf.cell(190, 6, "2. INVENTÁRIO DE RISCOS OCUPACIONAIS (DIRETRIZES NR 17)", ln=True)
    
    if risks_needed or riscos_avaliados:
        pdf.set_fill_color(35, 65, 95)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 8)
        pdf.cell(130, 6, " Perigo / Fator de Risco Mapeado", border=1, fill=True)
        pdf.cell(15, 6, "S x P", border=1, fill=True, align="C")
        pdf.cell(45, 6, " Nível de Risco / Classificação", border=1, fill=True, align="C")
        pdf.ln(6)
        
        pdf.set_text_color(60, 60, 60)
        pdf.set_font("Arial", size=7.5)
        for r in riscos_avaliados:
            y_i = pdf.get_y()
            pdf.set_xy(10, y_i)
            pdf.multi_cell(130, 4.5, f" {r['Risco']}", border=1)
            y_f = pdf.get_y()
            h_c = y_f - y_i
            pdf.set_xy(140, y_i)
            pdf.cell(15, h_c, f"{r['Severidade']} x {r['Probabilidade']}", border=1, align="C")
            pdf.set_xy(155, y_i)
            pdf.set_fill_color(225, 245, 225) if r['Classe'] == "Baixo" else pdf.set_fill_color(255, 240, 215) if r['Classe'] == "Médio" else pdf.set_fill_color(255, 225, 225)
            pdf.cell(45, h_c, f"{r['Nível']} - {r['Classe']}", border=1, fill=True, align="C")
            pdf.set_text_color(60, 60, 60)
            pdf.set_y(y_f)
    else:
        # COMBINAÇÃO PERFEITA: GERA O TERMO DE CONFORMIDADE SE NADA FOR SELECIONADO
        pdf.set_fill_color(230, 245, 235)
        pdf.set_font("Arial", "B", 9)
        pdf.set_text_color(25, 80, 45)
        pdf.cell(190, 7, " DECLARAÇÃO DE CONFORMIDADE ERGONÔMICA PRELIMINAR", border=1, ln=True, fill=True, align="C")
        pdf.set_font("Arial", size=8.2)
        pdf.set_text_color(60, 60, 60)
        texto_conformidade = (
            "Após análise preliminar 'in loco' e aplicação rigorosa dos checklists da NR 17 (Abrangendo os itens 17.4, 17.5, "
            "17.6, 17.7 e 17.8), constatou-se que o posto avaliado NÃO apresenta fatores de risco com nível de criticidade "
            "superior ao aceitável. O ambiente atende aos critérios de conforto e segurança vigentes, estando dispensado "
            "de plano de ação corretiva imediato e enquadrado em monitoramento periódico passivo."
        )
        pdf.ln(1)
        pdf.multi_cell(190, 4.5, texto_conformidade, border=1)
        
    pdf.ln(5)
    
    # Bloco 3: Plano de Ação
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(18, 38, 58)
    pdf.cell(190, 6, "3. PLANO DE AÇÃO PREVENTIVO E CORRETIVO (REQUISITO NR 1)", ln=True)
    
    if plano_acoes:
        pdf.set_fill_color(90, 95, 100)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 8)
        pdf.cell(90, 6, " Medida de Controle Proposta / Referência", border=1, fill=True)
        pdf.cell(36, 6, " Responsável", border=1, fill=True)
        pdf.cell(28, 6, " Prazo", border=1, fill=True, align="C")
        pdf.cell(36, 6, " Status", border=1, fill=True, align="C")
        pdf.ln(6)
        pdf.set_text_color(60, 60, 60)
        pdf.set_font("Arial", size=7.5)
        for p in plano_acoes:
            y_i = pdf.get_y()
            pdf.set_xy(10, y_i)
            pdf.multi_cell(90, 4.5, f" {p['Medida']}\n [Ref: {p['Risco']}]", border=1)
            y_f = pdf.get_y()
            h_c = y_f - y_i
            pdf.set_xy(100, y_i)
            pdf.cell(36, h_c, f" {p['Quem']}", border=1)
            pdf.set_xy(136, y_i)
            pdf.cell(28, h_c, f" {p['Prazo']}", border=1, align="C")
            pdf.set_xy(164, y_i)
            pdf.cell(36, h_c, f" {p['Status']}", border=1, align="C")
            pdf.set_y(y_f)
    else:
        pdf.set_font("Arial", "I", 8.5)
        pdf.cell(190, 6, " Nenhuma ação pendente. Posto mantido em conformidade sob monitoramento.", border=1, ln=True)
        
    # Assinatura
    pdf.ln(10)
    pdf.set_font("Arial", "B", 8)
    pdf.cell(190, 4, "________________________________________________________", ln=True, align="C")
    pdf.cell(190, 4, f"{avaliador}", ln=True, align="C")
    pdf.set_font("Arial", "I", 7.5)
    pdf.cell(190, 4, "Responsável Técnico - Emitido via Validador Mobile AEP Digital", ln=True, align="C")
    
    nome_arquivo = "Laudo_AEP_Oficial_MTE.pdf"
    pdf.output(nome_arquivo)
    
    with open(nome_arquivo, "rb") as f:
        st.download_button(
            label="📥 CLIQUE PARA DOWNLOAD DO RELATÓRIO OFICIAL",
            data=f,
            file_name=f"Laudo_AEP_{setor_posto.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    st.success("Documento gerado com sucesso!")

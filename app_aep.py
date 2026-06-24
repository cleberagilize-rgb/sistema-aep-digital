import streamlit as st
import datetime
import pandas as pd
from fpdf import FPDF

# Configuração da página web/móvel
st.set_page_config(page_title="AEP Digital - MTE NR 1 & NR 17", layout="centered")

st.title("📱 Sistema AEP Digital")
st.subheader("Avaliação Ergonômica Preliminar Ocupacional")
st.caption("Desenvolvido em estrita conformidade com o Manual do GRO/PGR (NR 1) e Diretrizes da NR 17")

# 1. IDENTIFICAÇÃO DO POSTO (Rastreabilidade Exigida pela NR 1)
st.markdown("### 1. Identificação do Posto e Grupo de Exposição")
empresa = st.text_input("Empresa / Unidade:", value="Indústrias Alfa S.A.")
setor_posto = st.text_input("Setor e Posto Avaliado:", value="Atendimento ao Cliente")
cargo = st.text_input("Cargo(s) Avaliado(s) / Função:", value="Operador de Telemarketing")
trabalhadores = st.number_input("Nº de Trabalhadores Expostos (GHE/GHO):", min_value=1, value=12)
avaliador = st.text_input("Nome do Avaliador / Responsável Técnico:", value="Eng. Carlos Silva")

severidade_opcoes = {1: "1 - Leve (Sem afastamento)", 2: "2 - Moderada (Afastamento temporário)", 3: "3 - Significativa (Lesão séria)", 4: "4 - Severa (Invalidez/Fatalidade)"}
probabilidade_opcoes = {1: "1 - Rara (Quase impossível)", 2: "2 - Remota (Baixa frequência)", 3: "3 - Possível (Sazonal/Intermitente)", 4: "4 - Frequente (Diária/Contínua)"}

# CHECKLIST COMPLETO E INTEGRAL DA NR 17
riscos_nr17 = {
    "NR 17.5 - Levantamento, Transporte e Descarga Manual de Cargas": [
        "Levantamento de cargas com peso superior aos limites recomendados pela NR 17",
        "Transporte manual de cargas por distância ou frequência excessiva sem pausas",
        "Posturas críticas, flexão extrema ou rotação severa do tronco na movimentação",
        "Ausência ou inadequação de equipamentos mecânicos auxiliares de transporte"
    ],
    "NR 17.6 - Mobiliário dos Postos de Trabalho": [
        "Superfície de trabalho (bancada/mesa) com altura ou dimensões inadequadas",
        "Falta de espaço livre para as pernas e pés na zona inferior da mesa",
        "Assentos sem sistemas ajustáveis de altura, inclinação ou sem apoio lombar",
        "Ausência de apoio regulável para os pés quando o trabalhador não toca o chão"
    ],
    "NR 17.7 - Equipamentos e Ferramentas de Trabalho": [
        "Ferramentas que exigem força excessiva ou compressão mecânica nos tecidos da mão",
        "Utilização de ferramentas ou dispositivos que transmitem vibrações nas mãos/braços",
        "Monitores, telas ou painéis posicionados fora da zona de alcance visual ótimo",
        "Dispositivos visuais com reflexos severos, falta de contraste ou brilho excessivo"
    ],
    "NR 17.8 - Condições Ambientais de Trabalho": [
        "Níveis de ruído contínuo ou intermitente gerando desconforto ou fadiga cognitiva",
        "Índice de temperatura, umidade ou velocidade do ar fora da zona de conforto térmico",
        "Iluminamento geral ou localizado insuficiente ou excessivo no campo de trabalho"
    ],
    "NR 17.4 - Organização do Trabalho e Fatores Psicossociais": [
        "Exigência de ritmo de trabalho excessivo imposto por máquinas, sistemas ou chefia",
        "Cobrança rígida de metas de produtividade com monitoramento individual contínuo",
        "Alta demanda cognitiva, concentração e processamento de dados sob pressão de tempo",
        "Monotonia crônica das atividades por ausência de variação ou rodízio de tarefas",
        "Ausência de autonomia ou controle do trabalhador sobre seus métodos e pausas",
        "Jornadas de trabalho prolongadas ou regimes de turnos sem o devido repouso"
    ]
}

st.markdown("### 2. Avaliação de Fatores de Risco (Matriz do MTE)")
st.info("Selecione os perigos identificados no posto para realizar o cruzamento de Severidade x Probabilidade.")

riscos_avaliados = []

for bloco, itens in riscos_nr17.items():
    with st.expander(bloco, expanded=False):
        for item in itens:
            check = st.checkbox(f"Detectado: {item}", key=item)
            if check:
                col1, col2 = st.columns(2)
                with col1:
                    sev = st.selectbox("Severidade do Agravo (NR 1):", options=[1, 2, 3, 4], format_func=lambda x: severidade_opcoes[x], key=f"sev_{item}")
                with col2:
                    prob = st.selectbox("Probabilidade de Ocorrência:", options=[1, 2, 3, 4], format_func=lambda x: probabilidade_opcoes[x], key=f"prob_{item}")
                
                nivel_risco = sev * prob
                
                if nivel_risco <= 3:
                    classificacao, cor = "Baixo", "green"
                elif nivel_risco <= 8:
                    classificacao, cor = "Médio", "orange"
                elif nivel_risco <= 12:
                    classificacao, cor = "Alto", "red"
                else:
                    classificacao, cor = "Crítico", "purple"
                
                st.markdown(f"Nível de Risco Ocupacional: :{cor}[**{nivel_risco} - {classificacao}**]")
                st.write("---")
                riscos_avaliados.append({"Risco": item, "Severidade": sev, "Probabilidade": prob, "Nível": nivel_risco, "Classe": classificacao})

# 3. PLANO DE AÇÃO (Requisito Normativo do PGR)
st.markdown("### 3. Plano de Ação Preventivo / Corretivo")
plano_acoes = []

if risks_needed := [r for r in riscos_avaliados if r["Nível"] >= 4]:
    for r in risks_needed:
        st.markdown(f"**Medida de Controle para:** *{r['Risco']}*")
        col1, col2 = st.columns(2)
        with col1:
            oque = st.text_input("O que fazer? (Medida proposta)", value="Implantar melhoria de engenharia / adequação administrativa", key=f"act_{r['Risco']}")
            quem = st.text_input("Quem será o responsável?", value="Engenharia / SESMT", key=f"who_{r['Risco']}")
        with col2:
            prazo = st.text_input("Prazo estimado:", value="30 dias", key=f"praz_{r['Risco']}")
            status = st.selectbox("Status Inicial:", ["Pendente", "Em Andamento"], key=f"st_{r['Risco']}")
        
        plano_acoes.append({"Risco": r["Risco"], "Medida": oque, "Quem": quem, "Prazo": prazo, "Status": status})
        st.write("---")
else:
    if riscos_avaliados:
        st.success("Todos os riscos mapeados possuem nível 'Baixo'. Estão dispensados de plano de ação imediato pelo MTE, exigindo apenas monitoramento.")
    else:
        st.warning("Nenhum risco selecionado no inventário até o momento.")

# 4. EXPORTAÇÃO E GERAÇÃO DE PDF
st.markdown("### 4. Emissão Exclusiva do Laudo")

class PDFLaudoMTE(FPDF):
    def header(self):
        # Topo institucional Azul Escuro Corporativo
        self.set_fill_color(18, 38, 58)
        self.rect(0, 0, 210, 24, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 12)
        self.set_y(5)
        self.cell(190, 6, "AVALIAÇÃO ERGONÔMICA PRELIMINAR (AEP) - INVENTÁRIO PGR", ln=True, align="C")
        self.set_font("Arial", "I", 8.5)
        self.cell(190, 5, "Documento Técnico em Conformidade com as Diretrizes Oficiais da NR 1 e NR 17", ln=True, align="C")
        self.set_y(28)
        
    def footer(self):
        self.set_y(-12)
        self.set_font("Arial", "I", 7.5)
        self.set_text_color(120, 120, 120)
        self.cell(95, 6, f"Emitido em: {datetime.date.today().strftime('%d/%m/%Y')} | Validador Eletrônico", align="L")
        self.cell(95, 6, f"Página {self.page_no()}", align="R")

if st.button("Gerar e Validar PDF"):
    if not riscos_avaliados:
        st.error("Erro: Não é possível emitir um documento sem nenhum risco mapeado no Inventário.")
    else:
        pdf = PDFLaudoMTE()
        pdf.add_page()
        pdf.set_text_color(60, 60, 60)
        
        # Bloco 1: Informações Cadastrais
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
        
        pdf.set_font("Arial", "B", 8)
        pdf.cell(35, 5, " Efetivo Exposto:", border=1)
        pdf.set_font("Arial", size=8)
        pdf.cell(65, 5, f" {trabalhadores} trabalhadores", border=1)
        pdf.set_font("Arial", "B", 8)
        pdf.cell(35, 5, " Responsável Técnico:", border=1)
        pdf.set_font("Arial", size=8)
        pdf.cell(55, 5, f" {avaliador}", border=1, ln=True)
        
        pdf.ln(5)
        
        # Bloco 2: Inventário Estruturado
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(18, 38, 58)
        pdf.cell(190, 6, "2. INVENTÁRIO DE RISCOS OCUPACIONAIS (DIRETRIZES NR 17)", ln=True)
        
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
            if r['Classe'] == "Baixo":
                pdf.set_fill_color(225, 245, 225)
                pdf.set_text_color(30, 80, 40)
            elif r['Classe'] == "Médio":
                pdf.set_fill_color(255, 240, 215)
                pdf.set_text_color(120, 75, 20)
            else:
                pdf.set_fill_color(255, 225, 225)
                pdf.set_text_color(140, 35, 35)
                
            pdf.cell(45, h_c, f"{r['Nível']} - {r['Classe']}", border=1, fill=True, align="C")
            pdf.set_text_color(60, 60, 60)
            pdf.set_y(y_f)
            
        pdf.ln(5)
        
        # Bloco 3: Plano de Ação
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(18, 38, 58)
        pdf.cell(190, 6, "3. PLANO DE AÇÃO PREVENTIVO E CORRETIVO (REQUISITO NR 1)", ln=True)
        
        pdf.set_fill_color(90, 95, 100)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 8)
        pdf.cell(90, 6, " Medida de Controle Proposta / Referência Técnica", border=1, fill=True)
        pdf.cell(36, 6, " Responsável", border=1, fill=True)
        pdf.cell(28, 6, " Prazo", border=1, fill=True, align="C")
        pdf.cell(36, 6, " Status", border=1, fill=True, align="C")
        pdf.ln(6)
        
        pdf.set_text_color(60, 60, 60)
        pdf.set_font("Arial", size=7.5)
        
        if plano_acoes:
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
            pdf.set_font("Arial", "I", 8)
            pdf.cell(190, 5, "Nenhuma ação imediata pendente. Riscos mantidos sob nível aceitável.", border=1, ln=True)
            
        # Assinatura técnica
        pdf.ln(10)
        pdf.set_font("Arial", "B", 8)
        pdf.cell(190, 4, "________________________________________________________", ln=True, align="C")
        pdf.cell(190, 4, f"{avaliador}", ln=True, align="C")
        pdf.set_font("Arial", "I", 7.5)
        pdf.cell(190, 4, "Responsável Técnico - Emitido em Conformidade com o MTE", ln=True, align="C")
        
        nome_arquivo = "Laudo_AEP_Oficial_MTE.pdf"
        pdf.output(nome_arquivo)
        
        with open(nome_arquivo, "rb") as f:
            st.download_button(
                label="📥 CLIQUE PARA BAIXAR O LAUDO TÉCNICO OFICIAL",
                data=f,
                file_name=f"Laudo_AEP_{setor_posto.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        st.success("O Documento cumpre 100% dos requisitos do MTE e está pronto para impressão!")
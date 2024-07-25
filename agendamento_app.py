import streamlit as st
import pandas as pd
from fpdf import FPDF
import pickle
import base64
import os
from io import BytesIO

# File paths for storing data
ALUNOS_FILE = 'alunos.pkl'
AULAS_FILE = 'aulas.pkl'

# Function to load data
def carregar_dados():
    try:
        with open(ALUNOS_FILE, 'rb') as f:
            alunos = pickle.load(f)
    except FileNotFoundError:
        alunos = []
    
    try:
        with open(AULAS_FILE, 'rb') as f:
            aulas = pickle.load(f)
    except FileNotFoundError:
        aulas = []
    
    return alunos, aulas

# Function to save data
def salvar_dados(alunos, aulas):
    with open(ALUNOS_FILE, 'wb') as f:
        pickle.dump(alunos, f)
    
    with open(AULAS_FILE, 'wb') as f:
        pickle.dump(aulas, f)

# Load data at the start
alunos, aulas = carregar_dados()

# Function to add a new student
def cadastrar_aluno(nome, pacote, valor):
    alunos.append({'Nome': nome, 'Pacote': pacote, 'Valor': valor})
    salvar_dados(alunos, aulas)

# Function to schedule a class
def agendar_aula(nome, data, hora):
    aulas.append({'Nome': nome, 'Data': data, 'Hora': hora})
    salvar_dados(alunos, aulas)

# Function to generate PDF report
def gerar_relatorio(nome, mes):
    # Convert MM-AAAA to AAAA-MM for internal processing
    mes_parts = mes.split('-')
    mes_interno = f"{mes_parts[1]}-{mes_parts[0]}"
    
    aluno_aulas = [aula for aula in aulas if aula['Nome'] == nome and aula['Data'].startswith(mes_interno)]
    aluno_info = next((aluno for aluno in alunos if aluno['Nome'] == nome), None)
    
    if aluno_info:
        total_aulas = len(aluno_aulas)
        total_valor = aluno_info['Valor']
        
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", size = 12)
        pdf.cell(200, 10, txt = f"Relatório de Aulas - {nome}", ln = True, align = 'C')
        pdf.cell(200, 10, txt = f"Mês: {mes}", ln = True, align = 'C')
        
        pdf.set_font("Arial", size = 10)
        pdf.cell(200, 10, txt = f"Total de Aulas no Mês: {total_aulas}", ln = True)
        pdf.cell(200, 10, txt = f"Valor Total das Aulas: R${total_valor:.2f}", ln = True)
        pdf.cell(200, 10, txt = f"Valor do Pacote Mensal: R${aluno_info['Valor']:.2f}", ln = True)
        
        pdf.cell(200, 10, txt = "Detalhes das Aulas:", ln = True)
        for aula in aluno_aulas:
            pdf.cell(200, 10, txt = f"Data: {aula['Data']} - Hora: {aula['Hora']}", ln = True)
        
        pdf_file = BytesIO()
        temp_pdf_path = f"Relatorio_{nome}_{mes}.pdf"
        pdf.output(temp_pdf_path)
        
        with open(temp_pdf_path, "rb") as f:
            pdf_file = f.read()
        
        os.remove(temp_pdf_path)
        
        return pdf_file
    else:
        st.error("Aluno não encontrado.")
        return None

# Function to clear all data
def zerar_dados():
    global alunos, aulas
    alunos = []
    aulas = []
    salvar_dados(alunos, aulas)

# Streamlit UI
st.title("Sistema de Gerenciamento de Aulas")

# Form to register students
st.header("Cadastro de Alunos")
nome = st.text_input("Nome do Aluno")
pacote = st.number_input("Pacote de Aulas Semanais", min_value=1)
valor = st.number_input("Valor do Pacote (R$)", min_value=0.0)

if st.button("Cadastrar Aluno"):
    cadastrar_aluno(nome, pacote, valor)
    st.success(f"Aluno {nome} cadastrado com sucesso!")

# Form to schedule classes
st.header("Agendamento de Aulas")
if alunos:
    nome_aula = st.selectbox("Selecione o Aluno", [aluno['Nome'] for aluno in alunos])
    data = st.date_input("Data da Aula")
    hora = st.time_input("Hora da Aula")
    
    if st.button("Agendar Aula"):
        agendar_aula(nome_aula, str(data), str(hora))
        st.success(f"Aula agendada para {nome_aula} em {data} às {hora}")
else:
    st.warning("Cadastre pelo menos um aluno para agendar aulas.")

# Form to generate reports
st.header("Gerar Relatório")
if alunos:
    nome_relatorio = st.selectbox("Selecione o Aluno para o Relatório", [aluno['Nome'] for aluno in alunos])
    mes = st.text_input("Mês (MM-AAAA)")
    
    if st.button("Gerar Relatório"):
        if mes:
            pdf_file = gerar_relatorio(nome_relatorio, mes)
            if pdf_file:
                b64 = base64.b64encode(pdf_file).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="Relatorio_{nome_relatorio}_{mes}.pdf">Clique aqui para baixar o relatório</a>'
                st.markdown(href, unsafe_allow_html=True)
        else:
            st.error("Por favor, insira um mês válido (MM-AAAA).")
else:
    st.warning("Cadastre pelo menos um aluno para gerar relatórios.")

# Button to clear all data
st.header("Zerar Dados")
if st.button("Zerar Todos os Dados"):
    zerar_dados()
    st.success("Todos os dados foram zerados.")

# Form to consult schedule by student name
st.header("Consultar Agenda")
if alunos:
    nome_consulta = st.selectbox("Selecione o Aluno para Consultar a Agenda", [aluno['Nome'] for aluno in alunos])
    
    if st.button("Consultar Agenda"):
        aluno_aulas = [aula for aula in aulas if aula['Nome'] == nome_consulta]
        if aluno_aulas:
            st.write(pd.DataFrame(aluno_aulas))
        else:
            st.warning("Nenhuma aula agendada para este aluno.")
else:
    st.warning("Cadastre pelo menos um aluno para consultar a agenda.")

# Display students and classes
st.header("Alunos Cadastrados")
st.write(pd.DataFrame(alunos))

st.header("Aulas Agendadas")
st.write(pd.DataFrame(aulas))

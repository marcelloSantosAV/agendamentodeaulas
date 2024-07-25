import streamlit as st
import pandas as pd
from fpdf import FPDF

# Data storage (in a real application, this would be a database)
alunos = []
aulas = []

# Function to add a new student
def cadastrar_aluno(nome, pacote, valor):
    alunos.append({'Nome': nome, 'Pacote': pacote, 'Valor': valor})

# Function to schedule a class
def agendar_aula(nome, data, hora):
    aulas.append({'Nome': nome, 'Data': data, 'Hora': hora})

# Function to generate PDF report
def gerar_relatorio(nome, mes):
    aluno_aulas = [aula for aula in aulas if aula['Nome'] == nome and aula['Data'].startswith(mes)]
    total_valor = len(aluno_aulas) * [aluno['Valor'] for aluno in alunos if aluno['Nome'] == nome][0]
    
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", size = 12)
    pdf.cell(200, 10, txt = f"Relatório de Aulas - {nome}", ln = True, align = 'C')
    
    pdf.set_font("Arial", size = 10)
    for aula in aluno_aulas:
        pdf.cell(200, 10, txt = f"Data: {aula['Data']}, Hora: {aula['Hora']}", ln = True)
    
    pdf.cell(200, 10, txt = f"Valor Total Mensal: R${total_valor}", ln = True, align = 'C')
    
    pdf.output(f"Relatorio_{nome}_{mes}.pdf")

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
nome_aula = st.selectbox("Selecione o Aluno", [aluno['Nome'] for aluno in alunos])
data = st.date_input("Data da Aula")
hora = st.time_input("Hora da Aula")

if st.button("Agendar Aula"):
    agendar_aula(nome_aula, str(data), str(hora))
    st.success(f"Aula agendada para {nome_aula} em {data} às {hora}")

# Form to generate reports
st.header("Gerar Relatório")
nome_relatorio = st.selectbox("Selecione o Aluno para o Relatório", [aluno['Nome'] for aluno in alunos])
mes = st.text_input("Mês (AAAA-MM)")

if st.button("Gerar Relatório"):
    gerar_relatorio(nome_relatorio, mes)
    st.success(f"Relatório gerado para {nome_relatorio} do mês {mes}")

# Display students and classes
st.header("Alunos Cadastrados")
st.write(pd.DataFrame(alunos))

st.header("Aulas Agendadas")
st.write(pd.DataFrame(aulas))

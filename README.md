# 📊 Sistema Integrado de gestão contábil: Python + n8n + AI

Este projeto apresenta uma solução "end-to-end" (ponta a ponta) para automação de processos contábeis. Ele une o poder de processamento do Python com a orquestração inteligente do n8n para transformar dados brutos em feedbacks estratégicos.

## 🔗 Links do Projeto
* **Aplicação Web (Streamlit):** https://relatorio-contabil-py.streamlit.app/
* **Workflow de Automação:** `automation_n8n.json` (neste repositório)

---

## 🏗️ Arquitetura da Solução

O ecossistema funciona em um ciclo de duas camadas:

### 1️⃣ Camada de Dados (Python & Streamlit)
Uma interface web desenvolvida para que o gestor possa consolidar bases de dados do Gestta (Gerenciador de tarefas vinculado a ferramenta Dominio Web da Thomson Reuters) e metas semanais de entregas de balancetes contábeis.
* **Funcionalidade:** Processa planilhas `.xlsx`, faz o de/para de metas e gera um relatório de desempenho visual (HTML).
* **Output:** O arquivo processado é enviado para o **Microsoft OneDrive**, servindo de gatilho para a automação.

### 2️⃣ Camada de Inteligência (n8n & OpenAI)
Um workflow automatizado que monitora o OneDrive e utiliza IA para análise crítica.
* **Processamento:** O n8n detecta o novo relatório e utiliza o modelo **OpenAI o3-mini** para ler o desempenho da equipe.
* **Persona "Renato":** A IA assume o papel de um gestor contábil experiente, redigindo feedbacks humanizados que citam clientes e prazos reais.
* **Entrega:** Envio automático de e-mails via **Microsoft Outlook** com o feedback formatado e relatórios anexados.

## 🛠️ Tecnologias Utilizadas
- **Linguagem Principal:** Python (Pandas e Streamlit)
- **Automação (iPaaS):** n8n
- **Inteligência Artificial:** OpenAI API (Reasoning Models)
- **Infraestrutura Cloud:** Microsoft 365 (OneDrive/Outlook)
- **Lógica de Dados:** JavaScript (no n8n para tratamento de binários)

---
*Desenvolvido por Paulo Renato - Foco em Automação, Eficiência Operacional e IA.*

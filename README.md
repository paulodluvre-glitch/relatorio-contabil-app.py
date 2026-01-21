# 📊 Gerador de Relatórios Contábeis

Ferramenta web para automação e padronização dos relatórios semanais de desempenho e status.

## 🔗 Acesso Rápido
**Clique aqui para acessar:** [COLOQUE_O_LINK_DO_SEU_STREAMLIT_AQUI]

> **Não é necessário instalar nada.** A ferramenta roda direto no seu navegador.

---

## 📝 Como Usar

A ferramenta funciona em **3 etapas simples** (navegue pelo menu lateral):

### 1️⃣ Gerar Base de Dados
O primeiro passo é consolidar as planilhas soltas da semana em um arquivo mestre.

1.  **Arquivos:** Arraste todas as planilhas `.xlsx` da semana para a área de upload.
2.  **Rótulos:** Ajuste as datas da "Semana Atual" e "Passada" para saírem corretas no título.
3.  **Dados Anteriores:** Cole a linha de porcentagens do relatório anterior (copie do Excel e cole direto).
4.  **Gerar:** Clique no botão e **baixe o arquivo** `BASE_DE_DADOS_PARA_IA.xlsx`.

> 💾 **Guarde este arquivo!** Você vai usá-lo nas próximas etapas.

---

### 2️⃣ Relatório de Desempenho (Com Metas)
Gera o relatório visual comparando o realizado vs. metas, com classificação automática de prazos.

**Arquivos Necessários:**
1.  **Base de Dados:** O arquivo gerado na etapa 1.
2.  **Arquivo de Metas:** Planilha Excel ou CSV contendo as colunas: `Responsável`, `Empresa` e `Data Meta`.

**Legenda do Relatório:**
* ✅ **Verde (No Prazo):** Entregou a competência atual dentro da data estipulada.
* ⚠️ **Amarelo (Atrasado):** Entregou a competência atual, mas depois da data da meta.
* ☑️ **Azul (Competência Anterior):** Entregou competências de meses passados (regularização).
* ❌ **Vermelho (Pendente):** Estava na meta do período, mas não foi entregue.

**Como Gerar:**
1. Suba a Base e o Arquivo de Metas.
2. Selecione no **Calendário** o período exato da semana analisada (Segunda a Sexta/Sábado).
3. Selecione os colaboradores que devem aparecer.
4. Clique em **Gerar HTML** e baixe o relatório final.

---

### 3️⃣ Relatório de Status (Dono Atual)
Gera uma visão geral ("mapa de calor") de todas as empresas e seus responsáveis atuais.

1.  Suba a Base de Dados.
2.  Filtre os colaboradores desejados.
3.  Baixe o relatório em HTML.

---

## ❓ Dúvidas Comuns

**1. O nome do arquivo importa?**
Não. Você pode salvar os arquivos com qualquer nome (`relatorio_final.xlsx`, `dados_joao.csv`), o sistema lê o conteúdo interno.

**2. Precisa padronizar maiúsculas/minúsculas?**
Não. O sistema entende que `Responsável`, `responsavel` e `RESPONSAVEL` são a mesma coisa.

**3. O que acontece se a meta não tiver data?**
O sistema vai considerar a meta como pendente se não for feita, mas não calculará atraso (não ficará amarelo, apenas vermelho ou verde).

---

*Desenvolvido para agilizar a rotina contábil.* 🚀

<!-- Banner / Logo -->
<p align="center">
  <img src="assets/logo_mentoria_risco_credito.png" width="260" alt="Mentoria Risco de Crédito logo" />
</p>

<h1 align="center">Mentoria em Ciência de Dados <br> aplicada ao Risco de Crédito</h1>

<p align="center">
  🚀 Programa 100 % gratuito &nbsp;|&nbsp; Hands-on &nbsp;|&nbsp; Basel II/III • IFRS 9 • Resolução 4.966
</p>

<div align="center">
  <a href="https://github.com/joaaomaia/Mentoria_Ciencia_Dados_Risco_Credito/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/joaaomaia/Mentoria_Ciencia_Dados_Risco_Credito/ci.yml?label=CI%20build" alt="CI Status">
  </a>
  <img src="https://img.shields.io/badge/python-3.11%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/licen%C3%A7a-MIT-green" alt="MIT License">
</div>

---

## 📑 Visão geral

Esta mentoria é uma jornada **prática** e **estruturada** para profissionais que dominam o básico de Python e querem:

* **Conectar teoria regulatória a código**  
  ↳ decomposição da **ECL** (`ECL = PD × LGD × EAD`), _staging_ (1-2-3) e provisão forward-looking.  
* **Construir targets** (Ever 90m12 × Over 90m12) e **avaliar curvas de cura** com enfoque de negócio.  
* **Engenharia de variáveis**: estáticas, históricas e binning supervisionado com _OptimalBinning_.  
* **Modelar PD/LGD/EAD** usando Regressão Logística, Gradient Boosting e ajuste macroeconômico.  
* **Explicabilidade & segmentação**: Árvores, SHAP, clustering de grupos homogêneos.  
* **MLOps leve**: versionamento, MLflow e integração contínua no GitHub.  

> 🗓 **Calendário**: 6 semanas • encontros remotos de ±2 h todo sábado  
> 📂 **Material**: cada pasta `ENCONTRO_X/` (slides, cadernos, gabaritos) é publicada logo após a aula.

---

## 🚦 Roteiro dos encontros

| Semana | Tópicos principais | Artefatos |
|--------|-------------------|-----------|
| 0 | **Kick-off**: setup, Anaconda/VS Code, tour do repositório | `env_mentoria.yml`, slide deck de boas-vindas |
| 1 | **Fundamentos & Regulação**: IFRS 9, Res. 4.966, ECL, Estágios | `resumo_aula1_risco_credito.md` + questionário |
| 2 | **Targets e Curva de Cura**: Ever vs Over, amostragem snapshot × painel | notebook `target_ever_over.ipynb` |
| 3 | **Feature Engineering**: OptimalBinning “na unha”, métricas IV/WoE | notebook `feature_binning.ipynb` |
| 4 | **Modelagem PD & LGD**: Logit, XGBoost, Optuna, backtesting | notebooks de modelagem + MLflow |
| 5 | **Forward-Looking & Governança**: cenários macro, stress test, dashboards | template Streamlit + checklist de validação |

---

## ⚙️ Configuração rápida

```bash
# clone
git clone https://github.com/joaaomaia/Mentoria_Ciencia_Dados_Risco_Credito.git
cd Mentoria_Ciencia_Dados_Risco_Credito

# ambiente (Conda >= 23)
conda env create -f env_mentoria.yml
conda activate mentoria_rc

# testes rápidos
pytest -q

# Mentoria — Risco de Crédito & Ciência de Dados  
_Resumo técnico da **1ª aula** (dois encontros)_

---

## Sumário
- [Mentoria — Risco de Crédito \& Ciência de Dados](#mentoria--risco-de-crédito--ciência-de-dados)
  - [Sumário](#sumário)
  - [1. Objetivo do material](#1-objetivo-do-material)
  - [2. Fundamentos de risco de crédito](#2-fundamentos-de-risco-de-crédito)
  - [3. Panorama regulatório](#3-panorama-regulatório)
  - [4. Arquitetura de Perda Esperada (ECL)](#4-arquitetura-de-perda-esperada-ecl)
  - [5. Parâmetros quantitativos](#5-parâmetros-quantitativos)
    - [5.1 PD](#51pd)
    - [5.2 LGD](#52lgd)
    - [5.3 EAD](#53ead)
  - [6. Estágios de risco (IFRS 9 / Res. 4.966)](#6-estágios-de-risco-ifrs9--res4966)
  - [7. Construção de targets \& Curva de cura](#7-construção-de-targets--curva-de-cura)
    - [7.1 Alvos Ever × Over](#71alvos-everover)
    - [7.2 Curva de cura](#72curva-de-cura)
  - [8. Segmentação em Grupos Homogêneos](#8-segmentação-em-grupos-homogêneos)
    - [Técnicas comuns](#técnicas-comuns)
  - [9. Modelagem estatística](#9-modelagem-estatística)
  - [10. Amostragem de dados](#10-amostragem-de-dados)
  - [11. Ajustes macroeconômicos (_Forward‑Looking_)](#11-ajustes-macroeconômicos-forwardlooking)
  - [12. Fluxo de cálculo \& monitoramento](#12-fluxo-de-cálculo--monitoramento)
  - [13. Boas práticas \& armadilhas comuns](#13-boas-práticas--armadilhas-comuns)
  - [14. Bibliografia indicada](#14-bibliografia-indicada)

---

<a name="objetivo"></a>
## 1. Objetivo do material  
Criar um guia de referência para que os participantes:

* Reforcem conceitos‑chave de **risco de crédito** alinhados à **Resolução 4.966/21** (Brasil) e ao **IFRS 9**;  
* Entendam a estrutura de **Perda Esperada (Expected Credit Loss, ECL)**;  
* Conheçam o vocabulário técnico usado em modelagem de **PD, LGD e EAD**;  
* Visualizem como os tópicos se conectam ao ciclo completo de **Ciência de Dados** (pré‑processamento, modelagem, validação e governance).  

---

<a name="fundamentos"></a>
## 2. Fundamentos de risco de crédito
* **Risco de crédito**: incerteza associada ao não recebimento dos fluxos de caixa pactuados.  
* **Objetivo**: antecipar perdas, garantindo solvência e estabilidade do sistema financeiro.  
* **Abordagens históricas**  
  * _Perdas Incorridas_ (IAS 39 / Res. 2.682) – baseadas apenas em atraso já ocorrido.  
  * _Perdas Esperadas_ (IFRS 9 / Res. 4.966) – projeção prospectiva, incorporando cenários macroeconômicos.  

---

<a name="regulacao"></a>
## 3. Panorama regulatório

| Norma | Foco | Horizonte | Gatilhos‑chave |
|-------|------|-----------|----------------|
| **Res. 2.682/1999** | Perdas Incorridas | Passado | Enquadramento **A–H** por dias em atraso |
| **IFRS 9 (2014)** | Perdas Esperadas | Futuro | Stages 1‑2‑3, ECL 12 m × Lifetime |
| **Res. 4.966/2021** | Convergência IFRS 9 no Brasil | Futuro | Implementa ECL, exige Stages e Forward‑Looking |

**Principais diferenças**  
* Reconhecimento **mais cedo** da perda (antes do default materializar‑se).  
* Necessidade de **cenário macro** (base, otimista, pessimista).  
* Exigência de **governança de modelo**: gestão do ciclo completo, auditoria interna e supervisão externa.

---

<a name="ecl"></a>
## 4. Arquitetura de Perda Esperada (ECL)

> ECL = PD × LGD × EAD

* **PD (Probability of Default)** — probabilidade de entrar em default dentro de determinado horizonte.  
* **LGD (Loss Given Default)** — porcentagem da exposição que permanecerá perdida após recuperação.  
* **EAD (Exposure at Default)** — valor exposto no momento do default, incluindo limites não utilizados esperados.

---

<a name="parametros"></a>
## 5. Parâmetros quantitativos

### 5.1 PD  
* **Horizontes comuns**  
  * **12 meses** (Stage 1)  
  * **Lifetime** (Stages 2 & 3)  
* **Métodos de modelagem**  
  * Regressão logística (linear); árvores de decisão, gradient boosting (não lineares).  
* **Seleção de variáveis**: monotonicidade, VIF < 5, WoE/IV, OptimalBinning.

### 5.2 LGD  
* **Fórmula simplificada**

> LGD = 1 - (Caixa Recuperado / EAD)

* Componentes: garantias (colaterais), custos de cobrança, tempo de recuperação, taxa de desconto (taxa efetiva do contrato).  
* **Forward‑Looking LGD**: aplica fatores macroeconômicos aos fluxos de recuperação.

### 5.3 EAD  
* Saldo devedor + parcelas vincendas + limites rotativos prováveis de uso (CCF).  
* Deve refletir a **exposição máxima provável** no ponto de default, não apenas o saldo atual.

---

<a name="stages"></a>
## 6. Estágios de risco (IFRS 9 / Res. 4.966)

| Stage | Critério abreviado | Horizonte de PD | Juros reconhecidos sobre | Observações |
|-------|-------------------|-----------------|--------------------------|-------------|
| **1** | Sem aumento significativo de risco | 12 m PD | **Saldo bruto** | Atraso < 30 d |
| **2** | Aumento significativo de risco | Lifetime PD | **Saldo bruto** | Atraso ≥ 30 d ou downgrades internos |
| **3** | Crédito deteriorado (default) | PD = 1 | **Saldo líquido** | Atraso ≥ 90 d ou critérios qualitativos |

---

<a name="targets"></a>
## 7. Construção de targets & Curva de cura

### 7.1 Alvos Ever × Over  

| Tipo | Definição | Sensibilidade | Uso típico |
|------|-----------|---------------|-----------|
| **Ever 90 m 12** | Qualquer ocorrência de atraso ≥ 90 dentro de 12 m | **Alta** (mais positivos) | Estratégias de _early warning_, precificação |
| **Over 90 m 12** | Contrato **encerra** o período de 12 m em atraso ≥ 90 d | **Baixa** (menos positivos) | Provisionamento, cobrança estratégica |

A escolha depende de **custo operacional**, **tempo de cura** e **apetite de risco**.

### 7.2 Curva de cura  
* Monitora % de contratos que retornam ao status **performing** após o default.  
* Curvas rápidas → favorecem **Ever**; curas lentas → favorecem **Over**.  
* A cura só é validada após período _“time‑to‑heal”_ (ex.: 3 meses) sem novo atraso.

---

<a name="grupos"></a>
## 8. Segmentação em Grupos Homogêneos
Objetivo: sintetizar riscos similares para facilitar:

* **Parametrização de limites**  
* **Monitoramento** (matrizes de transição)  
* **Explicabilidade** (reportes gerenciais)

### Técnicas comuns  
1. **Árvores de decisão** – nós terminais tornam‑se grupos.  
2. **OptimalBinning supervisionado** (PD ou LGD como alvo).  
3. **Clustering não supervisionado** (quando não se quer usar o alvo).  

**Boas práticas**  
* Volumes mínimos por grupo (≥ 5 % do portfólio).  
* Estabilidade temporal: acompanhar _drift_ de performance por grupo.

---

<a name="modelagem"></a>
## 9. Modelagem estatística

| Aspecto | Modelos Lineares | Modelos Não Lineares |
|---------|-----------------|----------------------|
| Exemplo | Regressão Logística | Gradient Boosting, Random Forest, Redes |
| Prós | Transparência, coeficientes interpretáveis | Capturam interações e não‑linearidades |
| Contras | Requer forte tratamento de variáveis, sensível a multicolinearidade | Explicabilidade exige técnicas SHAP/PD |
| Quando usar | Relações aproximadamente lineares, requisitos regulatórios estritos | Portfólios complexos, grande volume de dados |

---

<a name="amostragem"></a>
## 10. Amostragem de dados
* **Snapshot** – observação estática de cada contrato; adequada a modelos comportamentais.  
* **Panel / Rolling Window** – várias janelas por contrato; captura dinâmicas temporais.  
* Escolha deve preservar **independência temporal** e evitar **look‑ahead bias**.

---

<a name="forward"></a>
## 11. Ajustes macroeconômicos (_Forward‑Looking_)  
1. Definir **cenários** (base, otimista, pessimista) com probabilidades ponderadas.  
2. Projetar **variáveis macro** relevantes (PIB, desemprego, inflação, taxa básica).  
3. Aplicar ao PD, LGD ou diretamente ao fator ECL, conforme materialidade.  
4. Revisar periodicamente as probabilidades de cada cenário.  

---

<a name="fluxo"></a>
## 12. Fluxo de cálculo & monitoramento

```
[Base de dados] → limpeza & feature engineering
               → Modelos (PD, LGD, EAD)
               → Segmentação em Grupos Homogêneos
               → Cálculo ECL (cenário base ± ajustes)
               → Relatórios e dashboards
               → Backtesting & validação (estabilidade, poder preditivo)
               → Governança (documentação, auditoria, challenge)
```

* **Backtesting** anual mínimo; validações independentes recomendadas.  
* Métricas‑chave: KS, Gini, PSI, Stability Index de grupos, erro de previsão de ECL.

---

<a name="boaspraticas"></a>
## 13. Boas práticas & armadilhas comuns
| Tema | Boas práticas | Erros frequentes |
|------|---------------|------------------|
| Origem dos dados | Excluir contratos já problemáticos do _training set_ | Treinar modelo com atraso presente |
| Curva de cura | Validar “time‑to‑heal” antes de reclassificar contrato | Considerar acordo como cura imediata |
| Variáveis | Checar VIF, monotonicidade, WoE | Usar features altamente correlacionadas |
| Estágios | Automação de migração Stage 1→2→3 | Regras manuais sem governança |
| Forward‑Looking | Documentar premissas macro | Ajustes ad‑hoc sem base estatística |

---

<a name="bibliografia"></a>
## 14. Bibliografia indicada
* **Resolução CMN 4.966/21** – Banco Central do Brasil.  
* **IFRS 9 – Financial Instruments**, IASB (2014).  
* World Bank (2023) _Accounting Provisioning under the Expected Credit Loss Framework_.  
* PwC (2022) _Instrumentos financeiros e Res. 4.966/21 – perguntas & respostas_.  
* Redcliffe Training (2025) _IFRS 9 Expected Credit Losses – 3 Stages Made Simple_.  

---
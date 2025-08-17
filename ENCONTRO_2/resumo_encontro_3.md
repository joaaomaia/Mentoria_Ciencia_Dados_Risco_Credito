# Mentoria em Risco de Crédito e Ciência de Dados

## Resumo Técnico das Aulas 1 & 2

---

### Índice

1. [Objetivo do Material](#objetivo)
2. [Panorama Geral do Risco de Crédito](#panorama)
3. [Principais Conceitos e Métricas](#conceitos)
4. [Preparação & Elegibilidade dos Dados](#dados)
5. [Construção de Targets](#targets)
6. [Amostragem & Balanceamento](#amostragem)
7. [LGD – Workout & Cure](#lgd)
8. [Validação & Monitoramento](#validacao)
9. [Boas Práticas & Armadilhas Comuns](#boas-praticas)
10. [Exercícios Propostos](#exercicios)
11. [Referências Essenciais](#referencias)

---

## 1. Objetivo do Material

Este documento resume, de forma **estruturada e técnica**, os conteúdos sobre *Risco de Crédito* e *Ciência de Dados* apresentados nas primeiras aulas da mentoria. Ele foi depurado para:

* **Corrigir imprecisões técnicas** detectadas em aula.
* **Remover nomes próprios, empresas e comentários irrelevantes** ou sensíveis.
* Servir como **base de estudo** para alunos e como **guia de implementação** em projetos reais.

---

## 2. Panorama Geral do Risco de Crédito

> *“Todo modelo responde a uma única pergunta.”* – Princípio adotado na mentoria.

Os modelos de risco de crédito são classificados, de forma simplificada, em:

| Abreviação                      | Pergunta que responde                                   | Horizonte típico    |
| ------------------------------- | ------------------------------------------------------- | ------------------- |
| **PD** (Probability of Default) | Qual a probabilidade de o contrato entrar em *default*? | 12 m ↦ PD12         |
| **LGD** (Loss Given Default)    | Dado o *default*, quanto será perdido?                  | Vida da recuperação |
| **EAD** (Exposure at Default)   | Qual a exposição financeira no instante do *default*?   | Instantâneo         |

Além disso, o **IFRS 9** e a **Res. Bacen 4.966/2021** exigem estimativas de **Perda Esperada (EL)** em diferentes estágios:
$EL = PD \times LGD \times EAD$

---

## 3. Principais Conceitos e Métricas

### 3.1 *Default* & Buckets de Atraso

* **Default regulatório** (varejo): atraso ≥ 90 dias.
* Buckets usuais: `0‑15`, `16‑30`, `31‑60`, `61‑90`, `>90` dias.

### 3.2 Flags Auxiliares

| Flag             | Significado                                                            | Uso principal                                     |
| ---------------- | ---------------------------------------------------------------------- | ------------------------------------------------- |
| **Flag\_Acordo** | Renegociação devedor *problemática* (concessão de benefício relevante) | Amplia o target “Mal” mesmo sem 90 dias de atraso |
| **Flag\_Óbito**  | Óbito sem seguro prestamista                                           | Pode antecipar *default*                          |
| **Spell\_ID**    | “Vida” do contrato após curing                                         | Permite múltiplas vidas no painel                 |

### 3.3 Targets de **PD**

| Notação         | Definição (janelada)                              | Sensibilidade                               |
| --------------- | ------------------------------------------------- | ------------------------------------------- |
| **Over 90 M12** | Atraso ≥ 90 d **no último** mês da janela de 12 m | Baixa (captura inadimplências persistentes) |
| **Ever 90 M12** | Atraso ≥ 90 d em **qualquer** mês da janela       | Alta                                        |
| **MAL**         | `Ever 90 M12 OR Flag_Acordo`                      | Abrange acordos ruins                       |

### 3.4 **Workout** & **Cure** (para LGD)

1. **Default**: atraso ≥ 90 d (ou ativo problemático).
2. **Workout**: fase em que há **esforço de cobrança** e/ou pagamentos parciais.
3. **Cure**: período *sem atraso* após o workout.

   * Prática de mercado: **≥ 3 meses** (varejo); pode ser maior em atacado.

---

## 4. Preparação & Elegibilidade dos Dados

### 4.1 Grupo **Perform** por Modelo

| Modelo  | Registros elegíveis                                     |
| ------- | ------------------------------------------------------- |
| **PD**  | Contratos **sem** *default* atual nem `Flag_Acordo`.    |
| **LGD** | Registros **em default** + **Workout** (exclui *Cure*). |
| **EAD** | Mesmos de PD **+** primeiro registro em *default*.      |

### 4.2 Teste de Continuidade

1. **Detectar quebras** de histórico (*gaps*) por contrato.
2. Classificar impacto: `imaterial (<1 %)` vs `material`.
3. Ações: *fill‑forward*, exclusão pontual ou solicitar correção na base‑fonte.

### 4.3 Tratamento de *“Re-aging”* (zeragem de atraso após acordo)

* **Proibido** zerar *days past due* sem período de *Cure*.
* Manter vínculo via `ID_Contrato_Original`.

---

## 5. Construção de Targets

1. **Criar coluna \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*`Over_90`**: `1` se `DPD ≥ 90`, caso contrário `0`.
2. \*\*Derivar \*\***`Ever_90_M12`** com *rolling window* de 12 meses.
3. **Montar \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*`MAL`**: `MAL = (Ever_90_M12 == 1) or (Flag_Acordo == 1)`.
4. \*\*Gerar \*\***`Target_PD`** (Ever ou Over) conforme requisito regulatório.

### Exemplo (Python pandas)

```python
# suposição: df ordenado por ID_Contrato & Data_Referencia
df['Over_90'] = (df['dpd'] >= 90).astype(int)
# janela móvel de 12 linhas (mensal)
df['Ever_90_M12'] = (
    df.groupby('id_contrato')['Over_90']
      .transform(lambda x: x.rolling(12, min_periods=1).max())
)
# MAL
df['MAL'] = np.where((df['Ever_90_M12'] == 1) | (df['Flag_Acordo'] == 1), 1, 0)
```

---

## 6. Amostragem & Balanceamento

### 6.1 Painel × Snapshot

| Critério        | **Painel** (filme)                | **Snapshot** (foto)                      |
| --------------- | --------------------------------- | ---------------------------------------- |
| Modelo indicado | Behavorial (PD, LGD)              | Concessão (Application Score)            |
| Vantagens       | Mantém variáveis históricas       | Simples & leve                           |
| Riscos          | *Overfitting* em contratos longos | **Viés de recência** e perda de história |

**Recomendação** da mentoria: usar **Painel** e só recorrer a Snapshot para datasets enormes ou uso exploratório.

### 6.2 Técnicas de Balanceamento

* **Sample Weights** (preferencial)

  * Ponderar a classe minoritária (`MAL = 1`).
  * Permite granularidade (e.g., peso por *recência*).
* **Class Weight = "balanced"** (rápido, porém menos flexível).
* **Reamostragem** (undersampling/oversampling)

  * Usar com moderação; evita‑se *SMOTE* para risco de crédito.

> **Dica:** Otimize hiper‑parâmetros **e** pesos de classe conjuntamente (e.g., *Optuna*).

---

## 7. LGD – Workout & Cure

### 7.1 Definindo o Período de Workout

1. Traçar a **curva cumulativa de recuperação** pós‑default.
2. Identificar o **plateau** (∆ < 1 % por ≥ 3 meses).
3. Fixar **horizonte LGD** até esse ponto.

### 7.2 Estimativa de LGD

$LGD_t = 1 - \frac{\text{Recuperação Acumulada}_t}{\text{EAD}_0}$

* **LGD final**: valor no término do workout.
* **Modelagem**: regressão Beta ou Gradient Boosting com logit.

---

## 8. Validação & Monitoramento

| Métrica                        | Uso                                 | Referência          |
| ------------------------------ | ----------------------------------- | ------------------- |
| **KS (Kolmogorov–Smirnov)**    | Discriminante entre *good* vs *bad* | ≥ 0.30 (varejo)     |
| **AUC / Gini**                 | Rankeamento                         | Gini = 2·AUC – 1    |
| **PSI** (Population Stability) | Drift de entrada                    | ≤ 0.10 (aceitável)  |
| **Brier Score**                | Calibração PD                       | Quanto menor melhor |

Procedimento de *Backtesting* (ex.: Res. 4.966)

1. Congelar parámetros.
2. Projetar 12 m.
3. Comparar PD‑real vs PD‑estimado.

---

## 9. Boas Práticas & Armadilhas Comuns

* **Documentação** minuciosa do *data lineage*.
* **Não “zerar” DPD** após renegociação sem *Cure*.
* **Evitar SMOTE** e geradores sintéticos em risco de crédito.
* **Sempre** separar *train / validation / test* em corte temporal (evitar *data leakage*).
* **Monitorar** entradas & saídas do modelo mensalmente.

---

## 10. Exercícios Propostos

1. **Teste de Continuidade**: identifique contratos com *gaps* > 1 m e proponha correção.
2. \*\*Construção do \*\***MAU em Python usando a base sintética fornecida.**
3. **Painel vs Snapshot**: compare AUC e PSI de ambos os métodos em 3 horizontes.
4. **Workout Analyzer**: plote curva de recuperação e determine `t_cure`.

---

## 11. Referências Essenciais

* Basel Committee on Banking Supervision – *IRB Approach: Guidance on PD, LGD & EAD*.
* European Banking Authority – *Guidelines on PD Estimation, LGD Estimation & Treatment of Defaulted Exposures* (EBA/GL/2017/16).
* Resolução CMN 4.966/2021 – *Modelos Internos de Risco de Crédito*.
* *Credit Risk Modelling* – Körner & Zimmermann (2022).
* *Elements of Statistical Learning* – Hastie, Tibshirani & Friedman (chap. 12).

---

> **© 2025 RiskPilot Mentoria em Risco de Crédito** – Conteúdo de uso exclusivo dos alunos.

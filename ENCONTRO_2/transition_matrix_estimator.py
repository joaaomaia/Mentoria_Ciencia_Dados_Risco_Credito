"""Estimate empirical transition matrices from panel data and plot them.

Usage example
--------------
>>> from transition_matrix_estimator import TransitionMatrixLearner
>>> learner = TransitionMatrixLearner(buckets=[0,15,30,60,90])
>>> learner.fit(df_panel,
...              id_col="id_contrato",
...              time_col="data_ref",
...              bucket_col="dias_atraso",
...              group_col="grupo_homogeneo")
>>> learner.plot_heatmaps(["global", "grupo_homogeneo", "stage"])

The method will create one seaborn heatmap per requested modality and return the
list of matplotlib Figure objects (useful for saving in notebooks).
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger("creditlab.tm")
logger.setLevel(logging.INFO)

__all__ = ["TransitionMatrixLearner"]


class TransitionMatrixLearner:
    """Learn transition matrices and provide quick seaborn visualisation."""

    def __init__(
        self,
        *,
        buckets: List[int],
        alpha: float = 1.0,
        auto_rebin: bool = False,
        drop_empty: bool = False,
        min_count: int = 10,
        rebin_window: int = 7,
    ):
        if auto_rebin and drop_empty:
            raise ValueError("Only one of auto_rebin or drop_empty can be True")
        self.buckets = sorted(buckets)
        self.alpha = alpha
        self.auto_rebin = auto_rebin
        self.drop_empty = drop_empty
        self.min_count = int(min_count)
        self.rebin_window = int(rebin_window)
        self.n = len(self.buckets)
        self.cleaned_buckets: List[int] = self.buckets.copy()
        self._mat_global: np.ndarray | None = None
        self._mat_by_gh: Dict[str, np.ndarray] = {}
        self._mat_by_stage: Dict[int, np.ndarray] = {}
        self.logger = logger.getChild(self.__class__.__name__)

    # ------------------------------------------------------------------
    def fit(
        self,
        panel: pd.DataFrame,
        *,
        id_col: str,
        time_col: str,
        bucket_col: str,
        group_col: str | None = None,
    ) -> "TransitionMatrixLearner":
        """Count transitions (t -> t+1 month) per modality and normalise."""
        panel = panel[[id_col, time_col, bucket_col] + ([group_col] if group_col else [])].copy()
        panel[time_col] = pd.to_datetime(panel[time_col])
        panel = panel.sort_values([id_col, time_col])

        # create shifted df to align t and t+1
        shifted = panel.copy()
        shifted[time_col] += pd.DateOffset(months=1)
        merged = panel.merge(
            shifted,
            on=[id_col, time_col],
            suffixes=("_t", "_t1"),
            how="inner",
        )

        # global matrix
        counts_global = self._count_matrix(
            merged[bucket_col + "_t"], merged[bucket_col + "_t1"]
        )
        self._mat_global = self._clean_matrix(counts_global)

        # by GH
        if group_col:
            for gh, grp in merged.groupby(group_col + "_t"):
                counts = self._count_matrix(
                    grp[bucket_col + "_t"], grp[bucket_col + "_t1"]
                )
                self._mat_by_gh[gh] = self._clean_matrix(counts)

        # by stage (current bucket)
        for idx, grp in merged.groupby(bucket_col + "_t"):
            counts = self._count_matrix(
                grp[bucket_col + "_t"], grp[bucket_col + "_t1"]
            )
            self._mat_by_stage[int(idx)] = self._clean_matrix(counts)
        return self

    # ------------------------------------------------------------------
    def _count_matrix(self, col_from: pd.Series, col_to: pd.Series) -> np.ndarray:
        mat = np.zeros((self.n, self.n), dtype=float)
        for src, dst in zip(col_from, col_to):
            i = np.searchsorted(self.buckets, src, side="right") - 1
            j = np.searchsorted(self.buckets, dst, side="right") - 1
            mat[i, j] += 1
        return mat

    # ------------------------------------------------------------------
    def _clean_matrix(self, mat: np.ndarray) -> np.ndarray:
        row_sums = mat.sum(axis=1)

        if self.auto_rebin:
            non_empty = [i for i, s in enumerate(row_sums) if s >= self.min_count]
            for i, s in enumerate(row_sums):
                if s < self.min_count:
                    if not non_empty:
                        continue
                    candidates = [x for x in non_empty if abs(self.buckets[x] - self.buckets[i]) <= self.rebin_window]
                    if not candidates:
                        candidates = non_empty
                    j = min(candidates, key=lambda x: abs(self.buckets[x] - self.buckets[i]))
                    mat[j] += mat[i]
                    mat[:, j] += mat[:, i]
                    mat[i] = 0
                    mat[:, i] = 0
                    row_sums[j] += s
                    row_sums[i] = 0
                    self.logger.info(
                        "[TM] Empty bucket %d -> re-binned into %d (%d transitions moved)",
                        self.buckets[i],
                        self.buckets[j],
                        int(s),
                    )
            # buckets unchanged
            self.cleaned_buckets = self.buckets.copy()

        elif self.drop_empty:
            keep = [s >= self.min_count for s in row_sums]
            for idx, (k, s) in enumerate(zip(keep, row_sums)):
                if not k:
                    self.logger.info(
                        "[TM] Dropped bucket %d (total count=%d)",
                        self.buckets[idx],
                        int(s),
                    )
            mat = mat[np.ix_(keep, keep)]
            self.cleaned_buckets = [b for b, k in zip(self.buckets, keep) if k]
        else:
            self.cleaned_buckets = self.buckets.copy()

        # apply Laplace only to non-empty rows
        final = np.zeros_like(mat, dtype=float)
        for i in range(mat.shape[0]):
            if mat[i].sum() > 0:
                row = mat[i] + self.alpha
                final[i] = row / row.sum()
        return final

    # ------------------------------------------------------------------
    def get_matrix(self, *, gh: str | None = None, stage: int | None = None) -> np.ndarray:
        if gh is None and stage is None:
            if self._mat_global is None:
                raise RuntimeError("fit() not called yet")
            return self._mat_global
        if gh is not None:
            return self._mat_by_gh[gh]
        if stage is not None:
            return self._mat_by_stage[stage]
        raise ValueError("Specify either gh or stage (or neither for global)")

    # ------------------------------------------------------------------

    def plot_heatmaps(self, modes: List[str] | None = None) -> List[plt.Figure]:
        """
        Plot heatmaps for requested modalities.

        Parameters
        ----------
        modes : list[str] | None
            Options: "global", "grupo_homogeneo", "stage". Default = ["global"].

        Returns
        -------
        list[matplotlib.figure.Figure]
        """
        if modes is None:
            modes = ["global"]

        figs: List[plt.Figure] = []
        cmap = sns.color_palette("Blues", as_cmap=True)
        xt = yt = [str(b) for b in self.cleaned_buckets]

        def _prep(mat: np.ndarray, thr: float = 0.5) -> pd.DataFrame:
            """
            Converte a matriz em percentuais e substitui por NaN
            todos os valores abaixo do limiar 'thr' (em pontos-percentuais).
            """
            perc = mat * 100
            perc[perc < thr] = np.nan        # “apaga” zeros (e ≈0) para não aparecerem
            return pd.DataFrame(perc, index=yt, columns=xt)


        # 1. Global
        if "global" in modes:
            df = _prep(self._mat_global)
            mask = df.isna()
            fig, ax = plt.subplots(figsize=(6, 5))
            sns.heatmap(
                df,
                mask=df.isna(),   # células < thr ficam brancas
                annot=True,
                fmt=".0f",
                cmap=cmap,
                ax=ax,
                xticklabels=xt,
                yticklabels=yt,
            )
            ax.set_title("Matriz de Transição Global (%)")
            ax.set_xlabel("Bucket Atraso - Próxima Safra")
            ax.set_ylabel("Bucket Atraso - Safra Atual")
            figs.append(fig)

        # 2. Grupo homogêneo
        if "grupo_homogeneo" in modes:
            for gh, mat in self._mat_by_gh.items():
                df = _prep(mat)
                mask = df.isna()
                fig, ax = plt.subplots(figsize=(6, 5))
                sns.heatmap(
                    df,
                    mask=df.isna(),   # células < thr ficam brancas
                    annot=True,
                    fmt=".0f",
                    cmap=cmap,
                    ax=ax,
                    xticklabels=xt,
                    yticklabels=yt,
                )
                ax.set_title(f"Transition Matrix – {gh} (%)")
                ax.set_xlabel("Next bucket")
                ax.set_ylabel("Current bucket")
                figs.append(fig)

        # 3. Stage atual
        if "stage" in modes:
            for stage, mat in self._mat_by_stage.items():
                df = _prep(mat)
                mask = df.isna()
                fig, ax = plt.subplots(figsize=(6, 5))
                sns.heatmap(
                    df,
                    mask=df.isna(),   # células < thr ficam brancas
                    annot=True,
                    fmt=".0f",
                    cmap=cmap,
                    ax=ax,
                    xticklabels=xt,
                    yticklabels=yt,
                )
                ax.set_title(f"Transition Matrix – current bucket {stage} (%)")
                ax.set_xlabel("Next bucket")
                ax.set_ylabel("Current bucket")
                figs.append(fig)

        return figs



# # ---------------------------------------------------------------------------
# if __name__ == "__main__":
#     # Tiny example with random data (for ad‑hoc run)
#     ids = np.repeat(np.arange(5), 6)
#     dates = pd.date_range("2020-01-01", periods=6, freq="M").tolist() * 5
#     delays = np.random.choice([0, 15, 30, 60, 90], size=len(ids))
#     df_demo = pd.DataFrame({"id_contrato": ids, "data_ref": dates, "dias_atraso": delays})

#     learner = TransitionMatrixLearner(buckets=[0, 15, 30, 60, 90])
#     learner.fit(df_demo)
#     print("Global matrix:\n", learner.get_matrix())

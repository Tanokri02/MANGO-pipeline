"""Plot V- and J-gene family counts using the project reference design."""

import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plot_common as pc


def _read_inputs(file_paths):
    if isinstance(file_paths, (str, Path)):
        file_paths = [file_paths]
    return pd.concat([pd.read_csv(path) for path in file_paths], ignore_index=True)


def plot_all_embedder_genes(file_paths, out_figure, out_data, dpi=200):
    df = _read_inputs(file_paths)

    required_cols = ["v_gene", "j_gene", "embedder"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"The CSV must contain the column {col!r}.")

    def club_v_family(gene):
        if pd.isna(gene):
            return None
        gene_str = str(gene).upper()
        match = re.search(r"V(\d+)", gene_str)
        if match:
            return f"IGV{match.group(1)}"
        return None

    def club_j_family(gene):
        if pd.isna(gene):
            return None
        gene_str = str(gene).upper()
        match = re.search(r"J(\d+)", gene_str)
        if match:
            return f"IGJ{match.group(1)}"
        return None

    df["v_family"] = df["v_gene"].apply(club_v_family)
    df["j_family"] = df["j_gene"].apply(club_j_family)
    df_plot = df.dropna(subset=["v_family", "j_family"])

    if df_plot.empty:
        raise RuntimeError("No valid V or J gene families could be extracted.")

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))

    v_order = df_plot["v_family"].value_counts().index
    j_order = df_plot["j_family"].value_counts().index

    sns.countplot(
        data=df_plot,
        x="v_family",
        hue="embedder",
        palette="colorblind",
        ax=axes[0],
        order=v_order,
    )
    axes[0].set_title("All v_gene Families by Embedder", fontsize=14, pad=15)
    axes[0].set_xlabel("V Gene Family", fontsize=12)
    axes[0].set_ylabel("Count", fontsize=12)
    axes[0].tick_params(axis="x", rotation=45)

    sns.countplot(
        data=df_plot,
        x="j_family",
        hue="embedder",
        ax=axes[1],
        order=j_order,
        palette="colorblind",
    )
    axes[1].set_title("All j_gene Families by Embedder", fontsize=14, pad=15)
    axes[1].set_xlabel("J Gene Family", fontsize=12)
    axes[1].set_ylabel("Count", fontsize=12)
    axes[1].tick_params(axis="x", rotation=45)

    handles, legend_labels = axes[0].get_legend_handles_labels()
    for ax in axes:
        legend = ax.get_legend()
        if legend is not None:
            legend.remove()
    fig.legend(
        handles,
        legend_labels,
        title="Embedder",
        loc="lower center",
        bbox_to_anchor=(0.5, -0.01),
        ncol=min(4, len(legend_labels)),
        frameon=False,
    )

    pc.save(fig, df_plot, out_figure, out_data, dpi)


def main():
    smk = globals().get("snakemake")
    if smk is None:
        raise RuntimeError("plot_genes.py is intended to run through Snakemake")
    plot_all_embedder_genes(
        list(smk.input.metrics),
        smk.output.figure,
        smk.output.data,
        smk.params.dpi,
    )


if __name__ == "__main__":
    main()

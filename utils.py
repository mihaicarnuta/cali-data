import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


def plot_numeric_bin_vs_mean(df, bin_col, value_col):
    # Try converting both columns to numeric
    try:
        df[bin_col] = pd.to_numeric(df[bin_col], errors="coerce")
        df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    except Exception as e:
        st.warning(f"Could not convert '{bin_col}' or '{value_col}' to numeric: {e}")
        return

    # Drop rows with missing values
    df_clean = df.dropna(subset=[bin_col, value_col])

    # If not enough unique values for binning, skip
    if df_clean[bin_col].nunique() < 4:
        st.warning(f"Not enough unique values in '{bin_col}' to create quartiles.")
        return

    # Create quartile bins with readable labels
    bin_series, bin_edges = pd.qcut(df_clean[bin_col], q=4, retbins=True, precision=0, duplicates='drop')
    bin_labels = [
        f"{int(bin_edges[i])}–{int(bin_edges[i + 1] - 1)}"
        for i in range(len(bin_edges) - 1)
    ]
    df_clean["range_bin"] = pd.qcut(df_clean[bin_col], q=4, labels=bin_labels, duplicates='drop')

    # Group by bins and calculate mean of value_col
    grouped = df_clean.groupby("range_bin")[value_col].mean().reset_index()

    # Plot
    fig4, ax4 = plt.subplots(figsize=(5, 3))
    fig4.patch.set_facecolor("black")
    ax4.set_facecolor("black")

    bars = ax4.bar(grouped["range_bin"], grouped[value_col], color="skyblue", edgecolor="white")

    # Add value labels on top
    for bar in bars:
        height = bar.get_height()
        ax4.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.01,
            f"{height:.2f}",
            ha="center",
            va="bottom",
            color="white",
            fontsize=7
        )

    # Style axes and title
    ax4.set_title(f"Mean {value_col} by Binned {bin_col}", color="white", fontsize=12)
    ax4.set_xlabel(f"{bin_col} (quartile bins)", color="white")
    ax4.set_ylabel(f"Mean {value_col}", color="white")
    ax4.tick_params(colors="white")

    for spine in ["top", "right"]:
        ax4.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax4.spines[spine].set_color("white")

    st.pyplot(fig4, use_container_width=False)



def plot_dichotomous_numeric_bar(df, cat_col, num_col):
    # Validate: check that cat_col has 2 unique values (excluding nulls)
    if df[cat_col].dropna().nunique() != 2:
        st.warning(f"Column '{cat_col}' is not dichotomous (needs exactly 2 unique values).")
        return

    # Validate: try converting num_col to numeric
    try:
        df[num_col] = pd.to_numeric(df[num_col], errors="coerce")
    except Exception as e:
        st.warning(f"Could not convert '{num_col}' to numeric: {e}")
        return

    # Drop rows with missing values in either column
    df_clean = df.dropna(subset=[cat_col, num_col])

    # Group and compute mean
    grouped = df_clean.groupby(cat_col)[num_col].mean().reset_index()

    # If boolean, map to more readable strings
    if pd.api.types.is_bool_dtype(df[cat_col]):
        grouped[cat_col] = grouped[cat_col].map({True: "True", False: "False"})
    elif grouped[cat_col].nunique() == 2:
        grouped[cat_col] = grouped[cat_col].astype(str)

    # Plot
    fig3, ax = plt.subplots(figsize=(5, 3))
    fig3.patch.set_facecolor("black")
    ax.set_facecolor("black")

    bars = ax.bar(grouped[cat_col], grouped[num_col], color="skyblue", edgecolor="white")

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.01,
            f"{height:.2f}",
            ha="center",
            va="bottom",
            color="white",
            fontsize=7
        )

    # Style
    ax.set_title(f"Mean {num_col} by {cat_col}", color="white", fontsize=12)
    ax.set_xlabel(cat_col, color="white")
    ax.set_ylabel(f"Mean {num_col}", color="white")
    ax.tick_params(colors="white")

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("white")

    # Show plot
    st.pyplot(fig3, use_container_width=False)



def plot_categorical_numeric_bar(df, cat_col, num_col):
    # Validate: check if categorical column has at least 2 unique values
    unique_values = df[cat_col].dropna().unique()
    if len(unique_values) < 2:
        st.warning(f"Column '{cat_col}' must have at least 2 unique values to plot.")
        return

    # Convert num_col to numeric if needed
    try:
        df[num_col] = pd.to_numeric(df[num_col], errors="coerce")
    except Exception as e:
        st.warning(f"Could not convert '{num_col}' to numeric: {e}")
        return

    # Drop rows with missing values
    df_clean = df.dropna(subset=[cat_col, num_col])

    # Group and compute mean
    grouped = df_clean.groupby(cat_col)[num_col].mean().reset_index()

    # Convert categories to string for plotting
    grouped[cat_col] = grouped[cat_col].astype(str)

    # Sort by value if desired (optional)
    grouped = grouped.sort_values(by=num_col, ascending=False)

    # Plot
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    bars = ax.bar(grouped[cat_col], grouped[num_col], color="skyblue", edgecolor="white")

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.01,
            f"{height:.2f}",
            ha="center",
            va="bottom",
            color="white",
            fontsize=8
        )

    # Style
    ax.set_title(f"Mean {num_col} by {cat_col}", color="white", fontsize=12)
    ax.set_xlabel(cat_col, color="white")
    ax.set_ylabel(f"Mean {num_col}", color="white")
    ax.tick_params(colors="white", rotation=45)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("white")

    st.pyplot(fig, use_container_width=False)


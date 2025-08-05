import pandas as pd
import plotly.express as px
import pycountry
import streamlit as st
from scipy import stats

from utils import plot_dichotomous_numeric_bar, plot_numeric_bin_vs_mean, plot_categorical_numeric_bar

st.set_page_config(page_title="CaliData App", layout="wide")

st.title("Reply Rate by SMS Content Length Ranges")

# Load and clean data
df = pd.read_parquet("all_sms_data.parquet")
# st.write("Unique countries:", sorted(df["Country_of_recipients"].dropna().unique()))
print(df["Country_of_recipients"].apply(type).value_counts())
st.write("Data type of Country_of_recipients:", df["Country_of_recipients"].dtype)
st.write("Sample of actual Python types in column:")
st.write(df["Country_of_recipients"].apply(type).value_counts())

st.write("Top 10 most frequent countries:")
st.dataframe(df["Country_of_recipients"].value_counts().head(10))

# Filter for string entries
is_str = df["Country_of_recipients"].apply(lambda x: isinstance(x, str))
num_non_str = (~is_str).sum()

# Get 15 longest unique string values (drop duplicates and NaNs)
longest_strings = df.loc[is_str, "Country_of_recipients"] \
    .dropna() \
    .drop_duplicates() \
    .sort_values(key=lambda s: s.str.len(), ascending=False) \
    .head(15)

# Streamlit display
st.subheader("📍 Country_of_recipients: Longest Values")
st.write(f"🧾 Number of non-string entries in `Country_of_recipients`: **{num_non_str}**")
st.write("📏 **Top 15 longest string values:**")

# Display as a table
longest_df = pd.DataFrame({
    "Country Name": longest_strings.values,
    "Length": longest_strings.str.len().values
})
st.dataframe(longest_df, use_container_width=True)

new_df = df[df["Country_of_recipients"].apply(lambda x: isinstance(x, str) and len(x) == 2)]



unique_2letter_codes = sorted(new_df["Country_of_recipients"].unique())

# Display
# st.subheader("🌐 Unique 2-letter Country Codes")
# st.write(f"🧾 Found **{len(unique_2letter_codes)}** unique 2-letter codes:")
# st.write(unique_2letter_codes)
#
# st.subheader("🔝 Top 10 Rows of new_df")
# st.dataframe(new_df.head(10))
#
# st.subheader("🔚 Bottom 10 Rows of new_df")
# st.dataframe(new_df.tail(10))

mean_rates = new_df.groupby("Country_of_recipients")["Delivery_rate"].mean().sort_values(ascending=False)

# Plot top 20
# top_n = 20
# st.subheader(f"📊 Top {top_n} Countries by Mean Delivery Rate")
#
# fig, ax = plt.subplots(figsize=(10, 5))
# mean_rates.head(top_n).plot(kind="bar", color="skyblue", edgecolor="white", ax=ax)
# ax.set_title("Top Countries by Delivery Rate")
# ax.set_ylabel("Mean Delivery Rate")
# ax.set_xlabel("Country")
# ax.set_facecolor("black")
# fig.patch.set_facecolor("black")
# ax.tick_params(colors="white")
# for spine in ax.spines.values():
#     spine.set_color("white")
# st.pyplot(fig)


color_scale = "Viridis"
# Convert 2-letter ISO to 3-letter ISO
def iso2_to_iso3(code):
    try:
        return pycountry.countries.get(alpha_2=code).alpha_3
    except:
        return None

df_iso = new_df.copy()
df_iso["iso_alpha3"] = df_iso["Country_of_recipients"].apply(iso2_to_iso3)
df_iso["iso_alpha2"] = df_iso["Country_of_recipients"]

# Step 2: Clean numeric column
df_iso = df_iso.dropna(subset=["iso_alpha3", "Delivery_rate"])
df_iso["Delivery_rate"] = pd.to_numeric(df_iso["Delivery_rate"], errors="coerce")
df_iso = df_iso.dropna(subset=["Delivery_rate"])

# Step 3: Group by country, aggregate mean and count
grouped = df_iso.groupby(["iso_alpha3", "iso_alpha2"]).agg(
    avg_delivery_rate=("Delivery_rate", "mean"),
    case_count=("Delivery_rate", "count")
).reset_index()

# Step 4: Plot
fig = px.choropleth(
    grouped,
    locations="iso_alpha3",
    color="avg_delivery_rate",
    color_continuous_scale=color_scale,
    locationmode="ISO-3",
    custom_data=["iso_alpha2", "avg_delivery_rate", "case_count"],
    title="Average Delivery Rate by Country"
)

# Step 5: Hover info with ISO-2 and number of cases
fig.update_traces(
    hovertemplate=(
        "<b>Country (ISO-2):</b> %{customdata[0]}<br>"
        "<b>Avg Delivery Rate:</b> %{customdata[1]:.2f}<br>"
        "<b>Cases:</b> %{customdata[2]}<extra></extra>"
    )
)

fig.update_layout(
    width=1400,
    height=900
)

st.plotly_chart(fig, use_container_width=False)


df_iso_reply = new_df.copy()
df_iso_reply["iso_alpha3"] = df_iso_reply["Country_of_recipients"].apply(iso2_to_iso3)
df_iso_reply["iso_alpha2"] = df_iso_reply["Country_of_recipients"]
df_iso_reply = df_iso_reply.dropna(subset=["iso_alpha3", "Reply_rate"])
df_iso_reply["Reply_rate"] = pd.to_numeric(df_iso_reply["Reply_rate"], errors="coerce")
df_iso_reply = df_iso_reply.dropna(subset=["Reply_rate"])

# Step 3: Group by country, aggregate mean and count
grouped_reply = df_iso_reply.groupby(["iso_alpha3", "iso_alpha2"]).agg(
    avg_reply_rate=("Reply_rate", "mean"),
    case_count=("Reply_rate", "count")
).reset_index()

# Step 4: Plot
figx = px.choropleth(
    grouped_reply,
    locations="iso_alpha3",
    color="avg_reply_rate",
    # color_continuous_scale="Viridis",
    color_continuous_scale=color_scale,
    locationmode="ISO-3",
    custom_data=["iso_alpha2", "avg_reply_rate", "case_count"],
    title="Average Reply Rate by Country"
)

# Step 5: Hover info with ISO-2 and number of cases
figx.update_traces(
    hovertemplate=(
        "<b>Country (ISO-2):</b> %{customdata[0]}<br>"
        "<b>Avg Reply Rate:</b> %{customdata[1]:.2f}<br>"
        "<b>Cases:</b> %{customdata[2]}<extra></extra>"
    )
)
figx.update_layout(
    width=1400,
    height=900
)

st.plotly_chart(figx, use_container_width=True)



# df_iso = new_df.copy()
# df_iso["iso_alpha3"] = df_iso["Country_of_recipients"].apply(iso2_to_iso3)
# df_iso["iso_alpha2"] = df_iso["Country_of_recipients"]
#
# st.markdown(f'Single country values df shape: {df_iso.shape}')
# st.dataframe(df_iso.head(15))
#
# # Drop invalid rows
# df_iso = df_iso.dropna(subset=["iso_alpha3", "Delivery_rate"])
# df_iso["Delivery_rate"] = pd.to_numeric(df_iso["Delivery_rate"], errors="coerce")
# df_iso = df_iso.dropna(subset=["Delivery_rate"])
#
# # Group by 3-letter code and keep 2-letter code for hover
# grouped = df_iso.groupby(["iso_alpha3", "iso_alpha2"])["Delivery_rate"].mean().reset_index()
#
# # Plot with hover info
# fig = px.choropleth(
#     grouped,
#     locations="iso_alpha3",
#     color="Delivery_rate",
#     color_continuous_scale="Blues",
#     locationmode="ISO-3",
#     custom_data=["iso_alpha2", "Delivery_rate"],
#     title="Average Delivery Rate by Country"
# )
#
# # Custom hover template
# fig.update_traces(
#     hovertemplate="<b>ISO-2:</b> %{customdata[0]}<br><b>Delivery rate:</b> %{customdata[1]:.2f}<extra></extra>"
# )
#
# st.plotly_chart(fig, use_container_width=True)


plot_numeric_bin_vs_mean(df, "SMS_content_length", "Delivery_rate")
plot_numeric_bin_vs_mean(df, "SMS_content_length", "Reply_rate")

plot_dichotomous_numeric_bar(df, "Contains_link", "Delivery_rate")
plot_dichotomous_numeric_bar(df, "Contains_link", "Reply_rate")

plot_dichotomous_numeric_bar(df, "Contains_emojis", "Delivery_rate")
plot_dichotomous_numeric_bar(df, "Contains_emojis", "Reply_rate")

plot_dichotomous_numeric_bar(df, "Contains_personalization", "Delivery_rate")
plot_dichotomous_numeric_bar(df, "Contains_personalization", "Reply_rate")

# plot_categorical_numeric_bar(df, "Country_of_recipients", "Reply_rate")
plot_categorical_numeric_bar(df, "Day_of_Week_sent", "Delivery_rate")
plot_categorical_numeric_bar(df, "Day_of_Week_sent", "Reply_rate")

plot_categorical_numeric_bar(new_df, "Country_of_recipients", "Delivery_rate")
plot_categorical_numeric_bar(new_df, "Country_of_recipients", "Reply_rate")


# Create quartile bins with readable labels
bin_series, bin_edges = pd.qcut(df["SMS_content_length"], q=4, retbins=True, precision=0)
bin_labels = [
    f"{int(bin_edges[i])}–{int(bin_edges[i + 1] - 1)}"
    for i in range(len(bin_edges) - 1)
]

df["length_range"] = pd.qcut(df["SMS_content_length"], q=4, labels=bin_labels)
# Group the data by the bins
groups = [
    group["Reply_rate"].dropna().values
    for _, group in df.groupby("length_range")
]

# Run ANOVA
f_stat, p_value = stats.f_oneway(*groups)

st.subheader("ANOVA Test")
st.write(f"F-statistic: {f_stat:.3f}")
st.write(f"P-value: {p_value:.4f}")

if p_value < 0.05:
    st.success("✅ Statistically significant differences found between groups (p < 0.05).")
else:
    st.info("ℹ️ No statistically significant differences between groups (p ≥ 0.05).")

from scipy.stats import kruskal

# Same grouping
groups = [
    group["Reply_rate"].dropna().values
    for _, group in df.groupby("length_range")
]

# Run Kruskal-Wallis test
stat, p_value = kruskal(*groups)

st.subheader("Kruskal-Wallis Test")
st.write(f"H-statistic: {stat:.3f}")
st.write(f"P-value: {p_value:.4f}")

from statsmodels.stats.multicomp import pairwise_tukeyhsd

# Run Tukey HSD
tukey = pairwise_tukeyhsd(
    endog=df["Reply_rate"],
    groups=df["length_range"],
    alpha=0.05
)

# Display results in Streamlit
st.subheader("Tukey HSD Post-hoc Test Results")
st.text(tukey.summary())

# List of your groups
# groups = df['length_range'].unique()
#
# def cliffs_delta(x, y):
#     n_x, n_y = len(x), len(y)
#     more = sum(i > j for i in x for j in y)
#     less = sum(i < j for i in x for j in y)
#     delta = (more - less) / (n_x * n_y)
#     return delta
#
#
# for g1, g2 in itertools.combinations(groups, 2):
#     x = df[df['length_range'] == g1]['Reply_rate']
#     y = df[df['length_range'] == g2]['Reply_rate']
#     d = cliffs_delta(x, y)
#     print(f"{g1} vs {g2}: Cliff's Delta = {d:.3f}")



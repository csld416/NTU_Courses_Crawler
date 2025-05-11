import pandas as pd
import matplotlib.pyplot as plt

# File mappings
file_mapping = {
    "人工智慧": "人工智慧_ntu_courses.csv",
    "機器學習": "機器學習_ntu_courses.csv",
    "深度學習": "深度學習_ntu_courses.csv",
    "強化學習": "強化學習_ntu_courses.csv"
}

# Alias mapping
alias_mapping = {
    "人工智慧": "AI",
    "機器學習": "ML",
    "深度學習": "DL",
    "強化學習": "RL"
}

# Collect counts
yearly_counts = {}
for label, path in file_mapping.items():
    df = pd.read_csv(path)
    df["Year"] = df["Term"].str.extract(r"(\d+)-")[0].astype(int)
    counts = df.groupby("Year").size()
    yearly_counts[alias_mapping[label]] = counts

# Combine and sort numerically
result_df = pd.DataFrame(yearly_counts).fillna(0).astype(int)
result_df = result_df.sort_index()

# Plot
plt.figure(figsize=(12, 6))
for label in result_df.columns:
    plt.plot(result_df.index, result_df[label], label=label)
    plt.text(result_df.index[-1], result_df[label].iloc[-1], label, fontsize=10,
             verticalalignment='center', horizontalalignment='left')

plt.title("NTU Course Trends by Topic (Aggregated by Academic Year)")
plt.xlabel("Academic Year")
plt.ylabel("Number of Courses")
plt.grid(True)
plt.xticks(result_df.index, rotation=45)
plt.tight_layout()
plt.show()

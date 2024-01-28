import pandas as pd
import plotly.graph_objects as go

# Install required libraries
# !pip install pandas plotly kaleido

# Load data
exit_survey_data = pd.read_csv("dummy_exit_survey_data.csv", usecols=["Question Text", "Response Answer"], encoding='mac-roman')
engagement_survey_data = pd.read_csv("dummy_staff_engagement_survey_data.csv", usecols=["Question Text", "Response Answer"], encoding='mac-roman')
mapping_data = pd.read_csv("Mapping_file.csv", usecols=["Question Text", "Question category 1", "Question category 2 ", "Question category 3"], encoding='mac-roman')

# Preprocess mapping data
mapping_data = mapping_data.dropna().drop_duplicates()
mapping_data['Question category 2 '] = mapping_data['Question category 2 '].replace('Performance and growth', 'Performance & growth')

# Merge survey data
merged_survey_data = pd.concat([exit_survey_data, engagement_survey_data])

# Merge survey data with mapping data
df_survey_data_mapped_category = pd.merge(merged_survey_data, mapping_data, on='Question Text', how='left').drop(['Question Text'], axis=1)
df_survey_data_mapped_category.columns = ['answer', 'category_1', 'category_2', 'category_3']

# Retrieve labels and parents for sunburst chart
df_all_categories = df_survey_data_mapped_category[["category_1", "category_2", "category_3"]]
labels, parents = [], []

for row in df_all_categories.values:
    for j, category in enumerate(row):
        label = f"{category}"
        if label not in labels:
            labels.append(label)
            parents.append("") if j == 0 else parents.append(f"{row[j-1]}")

# Create a dataframe with 2 columns, answer and category
merged_categories_data = pd.concat([df_survey_data_mapped_category[["answer", f"category_{i}"]].rename(columns={f"category_{i}": 'category'}) for i in range(1, 4)])

# Reduce 6 distinct answers to 3
merged_categories_data.replace({'Strongly Agree': 'Agree', 'Strongly Disagree': 'Disagree', 'Prefer not to say': 'Not Answered'}, inplace=True)

# Iterate over labels and calculate percentages
color_map = {}
percent_lists = {'Agree': [], 'Disagree': [], 'Unanswered': []}

for label in labels:
    for answer_type in percent_lists.keys():
        count = len(merged_categories_data[(merged_categories_data['answer'] == answer_type) & (merged_categories_data['category'] == label)])
        total_count = len(merged_categories_data[merged_categories_data['category'] == label])
        percent = round((count * 100) / total_count)
        percent_lists[answer_type].append(percent)

    # Assign colors based on percentages
    if percent_lists['Agree'][-1] >= 80:
        color_map[label] = "Green"
    elif percent_lists['Disagree'][-1] >= 20:
        color_map[label] = "Red"
    elif percent_lists['Unanswered'][-1] >= 80:
        color_map[label] = "Grey"
    else:
        color_map[label] = "Orange"

# Create a dataframe with category percentages
df_category_percent_data = pd.DataFrame({'Category': labels, 'Agree Percentage': percent_lists['Agree'], 'Disagree Percentage': percent_lists['Disagree'], 'Unanswered Percentage': percent_lists['Unanswered']})

# Save category percentage data as CSV
df_category_percent_data.to_csv('category_percent_data.csv', index=False)

# Create sunburst chart
fig = go.Figure(go.Sunburst(
    labels=labels,
    parents=parents,
    marker=dict(colors=[color_map[label] for label in labels], line=dict(color='white', width=0.5)),
))

# Update layout
fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))

# Show the chart
fig.show()

# Save the chart as an image
fig.write_image("sunburst.png")

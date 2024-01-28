'''
The code preprocess survey data and generates a sunburst chart using plotly

Requirements to run the code

1. Please place the survey files and mapping file in the same folder as code.
2. The code will require 3 python libraries; namely pandas, plotly and kaleido
'''

# Load libraries
import pandas as pd
import plotly.graph_objects as go

# Install required libraries
# !pip install pandas plotly kaleido

# Load the data (exit survey, engagement survey and mapping data)
exit_survey_data = pd.read_csv("dummy_exit_survey_data.csv", usecols=["Question Text", "Response Answer"], encoding='mac-roman')
engagement_survey_data = pd.read_csv("dummy_staff_engagement_survey_data.csv", usecols=["Question Text", "Response Answer"], encoding='mac-roman')
mapping_data = pd.read_csv("Mapping_file.csv", usecols=["Question Text", "Question category 1", "Question category 2 ", "Question category 3"], encoding='mac-roman')

# remove duplicate rows and rows with NaN
mapping_data = mapping_data.dropna().drop_duplicates()

# replacing 'Performance and growth' with 'Performance & growth' in Question category 2 to make it distinct from 'Performance and growth' in Question category 1
mapping_data['Question category 2 '] = mapping_data['Question category 2 '].replace('Performance and growth', 'Performance & growth')

# Merge exit and engagement survey data
merged_survey_data = pd.concat([exit_survey_data, engagement_survey_data])

# Merge survey data with mapping data
df_survey_data_mapped_category = pd.merge(merged_survey_data, mapping_data, on='Question Text', how='left')

# Dropping column 'Question Text'
df_survey_data_mapped_category = df_survey_data_mapped_category.drop(['Question Text'], axis=1)

# Assigning easy column names
df_survey_data_mapped_category.columns = ['answer', 'category_1', 'category_2', 'category_3']

''' Retrieve labels and parents from df_survey_data_mapped_category to be used in sunburst chart '''

df_all_categories = df_survey_data_mapped_category[["category_1", "category_2", "category_3"]]

# Initialize labels and parents lists
labels = []
parents = []

# Iterate over rows and append labels and parents
for i, row in enumerate(df_all_categories.values):
    for j, category in enumerate(row):
        label = f"{category}"
        if label not in labels:
            labels.append(label)
        
            if j == 0:
                parents.append("")
            else:
                parents.append(f"{row[j-1]}")

''' Create a dataframe with 2 columns, answer and category '''
df1 = df_survey_data_mapped_category[["answer", "category_1"]]
df1.columns = ['answer', 'category']

df2 = df_survey_data_mapped_category[["answer", "category_2"]]
df2.columns = ['answer', 'category']

df3 = df_survey_data_mapped_category[["answer", "category_3"]]
df3.columns = ['answer', 'category']

merged_categories_data = pd.concat([df1, df2, df3])

# Reduced 6 distinct answers to 3
merged_categories_data.replace(to_replace={'Strongly Agree': 'Agree'}, inplace=True)
merged_categories_data.replace(to_replace={'Strongly Disagree': 'Disagree'}, inplace=True)
merged_categories_data.replace(to_replace={'Prefer not to say': 'Not Answered'}, inplace=True)

color_map = {}
agree_percent_list = []
disagree_percent_list = []
unanswered_percent_list = []

''' Iterate over labels and found counts for agree, disagree, unswered and then found the percentage of each. 
The Green, Red, Orange and Grey colors are assigned based on values of percentages.
Green = Agree
Red = Disagree
Orange = A mixed response with both Agree & Disagree
Grey = Unanswered
'''

for label in labels:
    agree_count = len(merged_categories_data[(merged_categories_data['answer'] == 'Agree') & (merged_categories_data['category'] == label)])
    disagree_count = len(merged_categories_data[(merged_categories_data['answer'] == 'Disagree') & (merged_categories_data['category'] == label)])
    unanswered_count = len(merged_categories_data[(merged_categories_data['answer'] == 'Not Answered') & (merged_categories_data['category'] == label)])
    total_count = len(merged_categories_data[(merged_categories_data['category'] == label)])
    
    agree_percent = round((agree_count * 100) / total_count)
    disagree_percent = round((disagree_count * 100) / total_count)
    unanswered_percent = round((unanswered_count * 100) / total_count)
    
    agree_percent_list.append(agree_percent)
    disagree_percent_list.append(disagree_percent)
    unanswered_percent_list.append(unanswered_percent)
    
    if agree_percent >= 80:
        color_map[label] = "Green"
    elif disagree_percent >= 20:
        color_map[label] = "Red"
    elif unanswered_percent >= 80:
        color_map[label] = "Grey"
    else:
        color_map[label] = "Orange"

# dataframe is created for each category and its corresponding values of agree, disagree and unanswered percentage
df_category_percent_data = pd.DataFrame({'Caregory': labels, 'Agree Percentage': agree_percent_list, 'Disagree Percentage': disagree_percent_list, 'Unanswered Percentage': unanswered_percent_list})

# df_category_percent_data is saved as csv
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

# Download image
fig.write_image("sunburst.png")

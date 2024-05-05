import pandas as pd
from summary import summary_of_pdf
from authors import authors
from title_of_pdf import title
# Load the existing Excel file into a DataFrame

# Sample new data
new_data = [
    {'Title': title(), 'Authors': authors(), 'Summary': summary_of_pdf()}
]
df = pd.DataFrame(new_data)
# Append new data to the DataFrame
# for item in new_data:
#     df = df.append(item, ignore_index=True)

# Save the updated DataFrame to Excel
df.to_excel('sample.xlsx', index=False)

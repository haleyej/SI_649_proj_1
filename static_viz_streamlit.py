import pandas as pd
import numpy as np 
import os
import html5lib
import altair as alt
import streamlit as st

pd.options.mode.chained_assignment = None
st.set_page_config(layout="wide")


# manipulate data
type_dfs = []
files = [f for f in os.listdir("data") if f.endswith('html')]

for file in files:
    by_disability = pd.read_html(f"data/{file}")[-2]
    by_disability['year'] = int(file.split("_")[-1][:4])
    type_dfs.append(by_disability)

disability_df = pd.concat(type_dfs).reset_index(drop = True)
disability_df['pct_uninsured'] = 1.0 - disability_df['Percent'].astype(float) / 100.0
disability_df = disability_df.rename(columns = {'Disability Type': 'type'})

# create visualization 
# fix rules at certain years
aca_df = pd.DataFrame({'year': [2010]})
aca_effect_df = pd.DataFrame({'year': [2014]})

# color scheme for types plot 
type_colors = ['lightblue', 'lightblue', 'lightblue', 'lightblue']

all_lines = alt.Chart(disability_df).transform_filter(
    alt.datum.type == 'Any Disability'
).mark_line(
    strokeWidth = 5
).encode(
    x = alt.X('year:O', axis = alt.Axis(title = 'Year', labelFontSize = 12, titleFontSize = 15)), 
    y = alt.Y('pct_uninsured:Q', 
              axis = alt.Axis(format = '%', title = 'Percent Uninsured', labelFontSize = 12, titleFontSize = 15)), 
    color = alt.Color('type:N', scale = alt.Scale(range = ['#712ac7']), 
                      legend = alt.Legend(title = 'Type of Disability', titleFontSize = 15, 
                                          labelFontSize = 12, labelFontWeight = 'bold', 
                                          symbolStrokeWidth = 10, symbolSize = 200,
                                          orient = "none", legendX = 805, legendY = 0))
)

type_lines = alt.Chart(disability_df).transform_filter(
    (alt.datum.type != 'Any Disability') & (alt.datum.type != 'No Disability') & 
    (alt.datum.type != 'Self-Care') & (alt.datum.type != 'Independent Living')
).mark_line(
    strokeWidth = 1.5
).encode(
    x = alt.X('year:O', axis = alt.Axis(title = 'Year')), 
    y = alt.Y('pct_uninsured:Q', axis = alt.Axis(format = '%', title = 'Percent Uninsured')), 
    color = alt.Color('type:N', scale = alt.Scale(range = type_colors), legend = None), 
    
    shape = alt.Shape('type:N', scale = alt.Scale(range = ['cross', 'circle','triangle-right', 'diamond']), 
                       legend = alt.Legend(title = '', labelFontSize = 12, labelOffset = 11,
                                           symbolFillColor = 'lightblue', symbolSize = 150,
                                           symbolStrokeColor = 'lightblue', orient = "none", 
                                           legendX = 809, legendY = 59)
                     )
)

aca_passage = alt.Chart(aca_df).mark_rule( 
    color = "#4254f5",
    size = 3
).encode(
    x = alt.X('year:O')
)

aca_passage_text = alt.Chart(aca_df).mark_text(
    lineBreak = r'\n',
    text = r"2010: Passage of \nthe Affordable Care Act",
    align = 'left',
    fontSize = 13.5, 
    fontWeight = 'bold',
    dy = -40,
    dx = -265
)

aca_effect = alt.Chart(aca_effect_df).mark_rule(
    color = "#4254f5",
    size = 3
).encode(
    x = alt.X('year:O')
)

aca_effect_text = alt.Chart(aca_effect_df).mark_text(
    lineBreak = r'\n',
    text = r'2014: Most ACA \nProvisions Go Into Effect', 
    align = 'left',
    fontSize = 13.5, 
    fontWeight = 'bold',
    dy = 100,
    dx = 45
)

layers = alt.layer(
    type_lines, all_lines, aca_passage, aca_effect, aca_passage_text, aca_effect_text
).resolve_scale(
    color = 'independent'
).properties(
    width = 1000, 
    height = 700
).configure_point(size = 90)


# set up streamlit
st.title("Percent of Disabled Americans Without Insurance")
st.write("The percent of disabled people without insurnace has decreased by nearly 50% since the passage of the Affordable Care Act")
st.write("Haley Johnson, SI 649")
layers
st.write( r'''The Affordable Care Act, also known as Obamacare, was passed by congress in 2010. The ACA made it illegal 
    for insurance companies to deny coverage based on pre-existing conditions, including disabilities and other chronic health 
    conditions. Likewise, under ACA rules insurance providers cannot charge higher premiums to individuals with disabilities. 
    The ACA has significantly expanded insurance options for Americans with disabilities — more flexibility will help improve 
    access to low-cost, high-quality care from providers who are informed about disabilities. It is also a case study in how 
    policy tools can improve healthcare access and outcomes for Americans with disabilities.''')

st.write('''See more at: https://tinyurl.com/ACADisability''')

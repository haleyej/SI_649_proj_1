import pandas as pd
import numpy as np 
import os
import altair as alt
import streamlit as st 

pd.options.mode.chained_assignment = None
st.set_page_config(layout="wide")


# Data Manipulation
df = pd.read_csv("data/preventitive_care.csv")
df = df.drop(columns = ['FootnoteText', 'Url', 'FootnoteType'])
preventitive_care = df[(df.Category == 'Prevention & Screenings') & (df.Year == 2020.0) & (df.Response == 'Yes')]
preventitive_care['Data_Value'] = preventitive_care.Data_Value / 100
preventitive_care['High_Confidence_Limit'] = preventitive_care.High_Confidence_Limit / 100
preventitive_care['Low_Confidence_Limit'] = preventitive_care.Low_Confidence_Limit / 100
preventitive_care['margin_of_error'] = preventitive_care['High_Confidence_Limit'] - preventitive_care['Data_Value']

# Shorten Question Labels
preventitive_care['short_question'] = preventitive_care['Question'].replace('Mammogram in the past 2 years among females 50 to 74 years of age', 'Mammograms')
preventitive_care.short_question = preventitive_care.short_question.replace('Up-to-date cervical cancer screening among females 21 to 65 years of age', 'Cervical Cancer Screening')
preventitive_care.short_question = preventitive_care.short_question.replace('Up-to-date colorectal cancer screening among adults 50 to 75 years of age', 'Colorectcal Cancer Screening')
preventitive_care.short_question = preventitive_care.short_question.replace('Routine check-up in the past year among adults 18 years of age or older', 'Routine Check Up')
preventitive_care.short_question = preventitive_care.short_question.replace('Visited a dentist in the past year among adults 18 years of age or older', 'Dentist Visit')
preventitive_care.short_question = preventitive_care.short_question.replace('Had a flu vaccine in the past 12 months among adults 18 years of age or older', 'Flu Vaccine')


# Visualization 
sorting = ['Any Disability', 'Cognitive Disability', 'Hearing Disability', 'Mobility Disability',
           'Vision Disability', 'No Disability']


main_title = alt.TitleParams("Many Disabled People Aren't Up To Date on Important Preventitive Care", 
                         subtitle = '''Average population-adjusted rate of preventitive care''',
                         anchor = 'start',
                         dx = 45, 
                         fontSize = 22, 
                         subtitleFontSize = 16, 
                         subtitlePadding = 6)

strats = list(preventitive_care.Stratification1.unique())
strats_dropdown = alt.binding_select(options = strats, name = "Ability Type: ")
strats_select = alt.selection_single(fields = ['Stratification1'], init = {'Stratification1' : 'Any Disability'}, empty = 'none')

coords = alt.selection_single(encodings = ['x', 'y'], on = 'mouseover', nearest = True, empty = 'none')


lines = alt.Chart(preventitive_care).add_selection(
    strats_select
).mark_rule(
    size = 6, 
    color = '#4676f0'
).encode(
    alt.Y('short_question:N', axis = alt.Axis(title = 'Care Type', labelFontSize = 11.5, titleFontSize = 13.5)), 
    alt.X('High_Confidence_Limit:Q', scale = alt.Scale(domain = [0.35, 0.87], zero = False), 
          axis = alt.Axis(title = 'Percent Up To Date', format = '.0%', labelFontSize = 11.5, titleFontSize = 13.5)), 
    alt.X2('Low_Confidence_Limit:Q'),
    tooltip = [alt.Tooltip('Data_Value:Q', title = 'Percent Up To Date', format = '.2%'), 
               alt.Tooltip('margin_of_error:Q', title = 'Margin of Error', format = '.2%')]
).transform_filter(strats_select)

mean = alt.Chart(preventitive_care).add_selection(
    coords
).mark_point(
    filled = True,
    size = 125, 
    color = '#4676f0', 
    opacity = 1.0
).encode(
    y = alt.Y('short_question:N', axis = alt.Axis(labelFontSize = 100)), 
    x = alt.X('Data_Value:Q'), 
    tooltip = [alt.Tooltip('Data_Value:Q', title = 'Percent Up To Date', format = '.2%'), 
               alt.Tooltip('margin_of_error:Q', title = 'Margin of Error', format = '.2%')]
).transform_filter(strats_select)

top = alt.layer(lines, mean
).properties(
    width = 850, 
    height = 350
).interactive()


text_base = alt.Chart(preventitive_care).mark_rect(
    color = '#fff'
).encode(
    y = alt.Y('short_question:N', axis = alt.Axis(title = 'Care Type', labelFontSize = 10.5, titleFontSize = 13)),
    x = alt.X('Stratification1:N', sort = sorting, axis = alt.Axis(title = '', labelFontSize = 10.5)), 
    color = alt.condition(coords, alt.value('#7396f0'), alt.value('#f7f9fc'))
)

text_marks = alt.Chart(preventitive_care).mark_text(
    baseline = 'middle'
).encode(
    y = alt.Y('short_question:N'), 
    x = alt.X('Stratification1:N', sort = sorting),
    text = alt.Text('Data_Value:Q', format = ".1%"),
)

bottom_title = alt.TitleParams('Data Table:', anchor = 'start', fontSize = 14, dx = 162, dy = -2)
bottom = alt.layer(text_base, text_marks).properties(width = 850, height = 150, title = bottom_title)

chart = alt.vconcat(top, bottom).configure_axisX(labelAngle = 0).configure_axis(labelLimit = 300)


# Page Set Up 
st.title("Many Disabled People Aren't Up To Date on Important Preventitive Care")
st.write("Population-adjusted prevelance of preventitive care")
st.write("Haley Johnson, SI 649")
chart

st.write('''Population adjusted figures reflect the fact that certain type of preventitive care are only recommended for certain segments of the population.
            For example, mamograms are only required for females aged 50-74. Population adjusted figures show what the up-to-date rates would be if everyone 
            in the "standard population" needed this preventitive care.'''
)
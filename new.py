import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import mplcyberpunk
import plotly.io as pio


# function to display a Sankey diagram
def display_sankey_diagram():
    # Load the data
    data = pd.read_csv("Results_21Mar2022.csv")
    # Convert relevant columns to category types
    data['sex'] = data['sex'].astype('category')
    data['diet_group'] = data['diet_group'].astype('category')
    data['age_group'] = data['age_group'].astype('category')
    # Calculate the weighted average of GHG emissions for each diet group
    weighted_mean_ghg = data.groupby('diet_group').apply(
        lambda x: (x['mean_ghgs'] * x['n_participants']).sum() / x['n_participants'].sum()
    ).reset_index(name='WeightedMeanGHG').sort_values('diet_group')
    # Calculate the sum of n_participants for each combination of gender and age group
    values_gender_to_age = data.groupby(['sex', 'age_group']).n_participants.sum().reset_index()
    # Calculate the sum of n_participants for each combination of age group and diet group
    values_age_to_diet = data.groupby(['age_group', 'diet_group']).n_participants.sum().reset_index()
    # Create lists for labels and colors for each node category
    gender_labels = ['Female', 'Male']
    age_labels = ['20-29', '30-39', '40-49', '50-59', '60-69', '70-79']
    diet_labels = ['fish', 'meat50', 'meat100', 'meat', 'vegan', 'veggie']
    # Adding weighted mean GHG emissions to node titles for diet groups
    diet_labels_with_ghg = [f"{label}\n(GHG: {round(ghg, 2)})" for label, ghg in zip(diet_labels, weighted_mean_ghg['WeightedMeanGHG'])]
    # Updated labels with GHG information for diet groups
    all_labels = gender_labels + age_labels + diet_labels_with_ghg
    # Calculate the index offsets for gender, age, and diet labels
    gender_offset = 0
    age_offset = len(gender_labels)
    diet_offset = age_offset + len(age_labels)
    # Combine sources and targets using previously calculated offsets
    sources = (
        [i + gender_offset for i in range(len(gender_labels)) for _ in range(len(age_labels))] +
        [i + age_offset for i in range(len(age_labels)) for _ in range(len(diet_labels))]
    )
    targets = (
        [i + age_offset for _ in range(len(gender_labels)) for i in range(len(age_labels))] +
        [i + diet_offset for _ in range(len(age_labels)) for i in range(len(diet_labels))]
    )
    # Combine values for the connections
    values = list(values_gender_to_age['n_participants']) + list(values_age_to_diet['n_participants'])
    # Define colors for genders and age groups
    gender_colors = ['#f72585', '#3a0ca3']  # Colors for Female and Male, respectively
    age_group_colors = ['#bbd0ff', '#b8c0ff', '#c8b6ff', '#e7c6ff', '#ffd6ff', '#f8edeb']  # Different shades of gray for age groups
    # Define the diet node colors
    diet_node_colors = [
        "#7ed2cc",  # fish
        "#cf364c",  # meat50
        "#9c0319",  # meat100
        "#c91d35",  # meat
        "#427343",  # vegan
        "#73c875"   # veggie
    ]
    # Create a list of colors for the nodes
    node_colors = gender_colors + age_group_colors + diet_node_colors
    # Create a list of colors for the links
    # Links from gender to age groups will have the same color as the gender
    link_colors_gender_to_age = [gender_colors[0] for _ in values_gender_to_age['n_participants'][::2]] + \
                            [gender_colors[1] for _ in values_gender_to_age['n_participants'][1::2]]
    # Links from age groups to diet groups will have colors corresponding to the age groups
    link_colors_age_to_diet = age_group_colors * len(diet_labels)
    
    # Combine the two lists of link colors
    link_colors = link_colors_gender_to_age + link_colors_age_to_diet
    # Update the 'color' attribute in both 'node' and 'link' dictionaries
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(width=0.5),
            label=all_labels,
            color=node_colors  # Updated node colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors  # Updated link colors
        ))])   
    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)


# Function to display lollipop chart
def display_lollipop_chart():
    # Load the dataset
    data_path = 'Nutrient+Info+By+LCA+Category+24April2020.csv'
    data = pd.read_csv(data_path)
    # Select columns for beneficial and detrimental nutrients, excluding rows with missing values
    beneficial_cols = ['Protein', 'Dietary.Fiber', 'Vitamin.C', 'Vitamin.A', 'Folate', 'Iron', 'Calcium']
    detrimental_cols = ['Saturated.FA', 'Sodium']
    # Handling missing values by filling with the mean
    data[beneficial_cols + detrimental_cols] = data[beneficial_cols + detrimental_cols].fillna(data[beneficial_cols + detrimental_cols].mean())
    # Standardize all selected nutrient data
    scaler = StandardScaler()
    beneficial_scaled = scaler.fit_transform(data[beneficial_cols])
    detrimental_scaled = scaler.fit_transform(data[detrimental_cols])
    # Calculate the scores
    positive_score = beneficial_scaled.sum(axis=1)
    negative_score = detrimental_scaled.sum(axis=1)
    # Calculate the Health Index
    data['Health_Index'] = positive_score - negative_score
    # Sort data by Health Index
    data_sorted = data.sort_values(by='Health_Index', ascending=False)
    # Select the top 10 and bottom 10 foods by Health Index
    top_10 = data_sorted.head(10)
    bottom_10 = data_sorted.tail(10)
    # Combine the two dataframes
    top_and_bottom_20 = pd.concat([top_10, bottom_10])
    # Create a horizontal lollipop chart by reversing the x and y axes
    fig3, ax3 = plt.subplots(figsize=(10, 8))
    ax3.hlines(y=top_and_bottom_20['food.group'], xmin=0, xmax=top_and_bottom_20['Health_Index'], color='skyblue')
    ax3.plot(top_and_bottom_20['Health_Index'], top_and_bottom_20['food.group'], "o")
    ax3.set_title('Top 10 Best and Worst Food Items by Health Index')
    ax3.set_xlabel('Health Index')
    ax3.set_ylabel('Food Group')
    # Disable grid
    ax3.grid(False)  # Disable grid
    # Show the plot in Streamlit
    st.pyplot(fig3)


# Function to display a Bubble map
def display_bubble_map():
    # Load the dataset
    data = pd.read_csv('jp_lca_dat.csv', encoding='ISO-8859-1')
    # Aggregate GHG emissions by country
    ghg_by_country = data.groupby('Country')['GHG Emissions (kg CO2eq, IPCC2013 incl CC feedbacks)'].sum().reset_index()
    # Create a bubble map
    fig = px.scatter_geo(ghg_by_country, locations="Country", locationmode='country names',
                         size="GHG Emissions (kg CO2eq, IPCC2013 incl CC feedbacks)", 
                         hover_name="Country",
                         projection="natural earth",
                         color_discrete_sequence=['purple'],
                         size_max=25)
    # Adjust margins to shift the plot left
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=20)) # Adjust left margin to 0, increase right margin if needed
    # Add country borders to the map
    fig.update_geos(showcountries=True)
    fig.update_traces(marker=dict(line=dict(width=0)))  # Remove marker border
    fig.update_traces(marker=dict(color='purple', opacity=0.8))  # Change marker color and opacity
    fig.update_traces(marker=dict(size=ghg_by_country["GHG Emissions (kg CO2eq, IPCC2013 incl CC feedbacks)"]))  # Set marker size relative to GHG emissions
    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)


def display_3d_bubble_plot():
    # Load the dataset
    data = pd.read_csv('Results_21Mar2022.csv')
    # Check required columns and calculate needed values
    if 'diet_group' in data.columns and 'mean_ghgs' in data.columns and 'n_participants' in data.columns:
        data['total_ghg'] = data['mean_ghgs'] * data['n_participants']
        data['avg_ghg_per_participant'] = data['mean_ghgs']  # Assuming 'mean_ghgs' is the average per participant
        total_ghg_by_diet = data.groupby('diet_group').agg({
            'total_ghg': 'sum',
            'n_participants': 'sum',
            'avg_ghg_per_participant': 'mean'  # Calculating average GHG per participant
        }).reset_index()
        # Define a color map for the diet groups 
        color_map = {
            'fish': '#1f77b4', 
            'meat': '#ff7f0e', 
            'meat100': '#8c564b',  
            'meat50': '#d62728', 
            'vegan': '#9467bd', 
            'veggie': '#2ca02c'  
        }
        total_ghg_by_diet['color'] = total_ghg_by_diet['diet_group'].map(color_map)
        # Create a 3D bubble plot
        fig = go.Figure(data=[go.Scatter3d(
            x=total_ghg_by_diet['n_participants'],
            y=total_ghg_by_diet['total_ghg'],
            z=total_ghg_by_diet['avg_ghg_per_participant'],  # Use average GHG per participant for Z-axis
            mode='markers+text',
            marker=dict(
                size=total_ghg_by_diet['total_ghg'] / max(total_ghg_by_diet['total_ghg']) * 50,
                sizemode='diameter',
                color=total_ghg_by_diet['color'],
                showscale=False
            ),
            text=total_ghg_by_diet['diet_group'],
            textfont=dict(color='black')  # Set font color to black for darker labels
        )])
        fig.update_layout(
            #title='3D Bubble Plot of Diet Groups',
            scene=dict(
                xaxis_title='Number of Participants',
                yaxis_title='Total GHG Emissions',
                zaxis_title='Average GHG per Participant'
            ),
            legend_title="Diet Groups",
            margin=dict(l=0, r=0, b=0, t=30)
        )
        st.plotly_chart(fig, use_container_width=True)



def main():
    st.set_page_config(layout="wide")
    st.markdown("<h1 style='text-align: center;'>Diet, Environmental Impact and Nutrient Profiles Dashboard</h1>", unsafe_allow_html=True)

    # First row with Sankey Diagram and Lollipop Chart
    with st.container():
        col1, col2 = st.columns([2.5, 1.5])
        with col1:
            st.header(" ")
            st.markdown("<h3 style='text-align: center;'>Sankey Diagram of Participant Flows</h3>", unsafe_allow_html=True)
            display_sankey_diagram()
        with col2:
            st.header(" ")
            st.markdown("<h3 style='text-align: center;'>3D Bubble Plot of Diet Groups</h3>", unsafe_allow_html=True)
            display_3d_bubble_plot()

    # Second row for full-width Bubble Map
    with st.container():
        col1, col2 = st.columns([1.5, 2.5])
        with col1:
            st.header(" ")
            st.markdown("<h3 style='text-align: center;'>Horizontal Lollipop Chart</h3>", unsafe_allow_html=True)
            display_lollipop_chart()
        with col2:
            st.header(" ")
            st.markdown("<h3 style='text-align: center;'>Bubble Map of GHG Emissions by Country</h3>", unsafe_allow_html=True)
            display_bubble_map()

if __name__ == "__main__":
    main()

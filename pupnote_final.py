import streamlit as st
import pandas as pd
import os
from datetime import date
from PIL import Image
import seaborn as sns
import matplotlib.pyplot as plt



# Streamlit app title
st.title('PupNote')
st.write("PupNote, for tracking how chubby our chubby bubbys get.")

# Sidebar for navigation
menu = st.sidebar.selectbox('Menu', ['Home', 'Add New Log Entry', 'Edit/Delete'])

# Path to your CSV file
csv_file_path = 'chihuahua_data.csv'

# Function to read or create data from .csv file
# Function to read or create data from .csv file
def get_data(file_path):
    try:
        data = pd.read_csv(file_path)
        # Convert 'Date' column to datetime if it's not already
        if 'Date' in data.columns and not data['Date'].dtype == 'datetime64[ns]':
            data['Date'] = pd.to_datetime(data['Date'])
        return data
    except FileNotFoundError:
        # Create a new DataFrame if the file is not found
        return pd.DataFrame(columns=['Date', 'Name', 'Daily Weight (oz)'])


# Function to update data in the .csv file
def update_data(file_path, data):
    data.to_csv(file_path, index=False, date_format='%Y-%m-%d')

# Read or create existing data
existing_data = get_data(csv_file_path)

if menu == 'Home':
    # Sort the DataFrame by date
    existing_data = existing_data.sort_values(by='Date')

    # Create a bar chart of daily weights for each dog
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=existing_data['Date'].dt.date, y='Daily Weight (oz)', hue='Name', data=existing_data)
    plt.title('Daily Weight Over Time')
    plt.xticks(rotation=45)

    # Add weight labels on top of the bars
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(f'{height:.1f} oz', (p.get_x() + p.get_width() / 2., height),
                    ha='center', va='bottom', fontsize=8, color='black', xytext=(0, 5),
                    textcoords='offset points')

    st.pyplot(plt)

    # Display Chihuahua health data table
    st.header('Weight Data')
    st.dataframe(existing_data)


elif menu == 'Add New Log Entry':
    st.header('Add New Log Entry')

    # Input fields for new log entry
    new_date = st.date_input("Date", date.today())
    
    # Dropdown for selecting dog's name
    new_name = st.selectbox("Which Chubby Bubby?", ["Elio", "Eve", "Beau", "Emilio", "Enzo"])

    new_weight = st.number_input("Daily Weight (oz)", min_value=0.0, step=0.1)

    # Submit button to add new entry
    if st.button('Add Entry'):
        if new_name and new_weight > 0:
            # Create new entry
            new_entry = {
                'Date': new_date,
                'Name': new_name,
                'Daily Weight (oz)': new_weight
            }

            # Append new entry to existing data and update CSV
            existing_data = pd.concat([existing_data, pd.DataFrame([new_entry])], ignore_index=True)
            update_data(csv_file_path, existing_data)
            st.success('New log entry added successfully!')
        else:
            st.error('Please fill in all the details correctly.')

elif menu == 'Edit/Delete':
    st.header('Edit or Delete Dog Records')
    selected_dog = st.selectbox('Select Dog', existing_data['Name'].unique())
    selected_date = st.date_input('Select Date', date.today())

    # Filter record
    filtered_record = existing_data[(existing_data['Name'] == selected_dog) & (existing_data['Date'] == pd.Timestamp(selected_date))]

    if not filtered_record.empty:
        edited_weight = st.number_input("Daily Weight (oz)", value=filtered_record.iloc[0]['Daily Weight (oz)'])

        if st.button('Update Record'):
            existing_data.loc[filtered_record.index, 'Daily Weight (oz)'] = edited_weight
            update_data(csv_file_path, existing_data)
            st.success('Record Updated')
            st.rerun()

        if st.button('Delete Record'):
            existing_data = existing_data.drop(filtered_record.index)
            update_data(csv_file_path, existing_data)
            st.success('Record Deleted')
            st.rerun()
    else:
        st.write('No record found for this dog on the selected date.')

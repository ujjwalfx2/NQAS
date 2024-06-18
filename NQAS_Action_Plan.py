import pandas as pd
import numpy as np
import streamlit as st
import re
from io import BytesIO
import io
import base64
from PIL import Image


def generate_excel_download_link(df,fn):
    # Credit Excel: https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/5
    towrite = BytesIO()
    df.to_excel(towrite, index=False, header=True)  # write to BytesIO buffer
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()
    #href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="Rename_This_File.xlsx">Download </a>'
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download={fn}>Download </a>'
    return st.markdown(href, unsafe_allow_html=True)

#show wrong password msg box
def show_floating_message():
    st.markdown(
        """
        <style>
        .floating-box {
            position: fixed;
            top: 58%;
            left: 50%;
            transform: translate(-50%, -50%);
            border: 2px solid #f50a0a;
            background-color: #edb4bf;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
            z-index: 1000;
        }
        </style>
        <div class="floating-box">
            <h3>Wrong Password</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )

def formattable(df):
    table_df1 = df    
    #table_df1['% of Score'] = table_df1['% of Score'].str.rstrip('%').astype('float') / 100
    # Apply heatmap to the % Score column
    styled_df = table_df1.style.background_gradient(subset=["% of Score"], cmap='RdYlGn').set_properties(**{'font-weight': 'bold', 'color': 'black', 'border-color': 'light gray'})
    # Add custom styling for column headers
    styled_df = styled_df.set_table_styles(
        [{'selector': 'thead th', 'props': [('background-color', '#2196F3'), ('color', 'white')]}]
    )
    # Hide the index column
    styled_df = styled_df.hide(axis='index')
    # Convert styled dataframe to HTML
    html_table = styled_df.to_html()
    # Display the styled dataframe with heatmap
    st.markdown(html_table, unsafe_allow_html=True)
    return styled_df

# Function to convert styled dataframe to excel and get bytes
def styled_df_to_excel_bytes(styled_df1):
    styled_df=styled_df1
    with io.BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            styled_df.to_excel(writer, sheet_name='Sheet1', index=False)
        return buffer.getvalue()

def downloadbtn(df,fn,k):
    excel_bytes=df
    #show download button
    st.download_button(
        label="Download Excel",
        data=excel_bytes,
        #file_name="styled_dataframe.xlsx",
        file_name=fn,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        #key="download-excel"
        key=k
    )



st.set_page_config(page_title="NQAS Action Plan", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

#load all csv data in dataframe
df = pd.read_csv("NQAS Action Plan.csv", encoding='unicode_escape')

# hide menu and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            table-container {max}
            table-height {max}            
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)  # unsafe_allow_html allows us to embed html code

df.rename(columns={'Submissions[hwc_shc]':'Facility name', 'Master[Area of Concern]':'Area of Concern', 'Master[Standard]':'Standard', 'Master[ME_Code]':'ME_Code', 'Master[Question]':'Question', 'Submissions[Score]':'Score', 'Submissions[Action Plan]':'Action Plan', 'Master[Timeline]':'Timeline', 'Master[Responsibility]':'Responsibility'}, inplace=True)
col1, col2, col3, col4 = st.columns(4)  # Create 4 columns
with col1:    
    image = Image.open('USAID.png')   
    st.image(image)  
with col2:    
    image = Image.open('NHM.png')   
    st.image(image) 
with col3:    
    image = Image.open('NISHTHA.png')   
    st.image(image) 
with col4:    
    image = Image.open('Jhpiego.png')   
    st.image(image) 

st.markdown("""<div style="border: 2px solid #4CAF50; background-color: #17a2b8; color: white; padding: 5px; border-radius: 10px; width: 90%; margin: 20px auto;text-align: center;"><h3 style="color: white;">NQAS Action Plan</h3></div>""", unsafe_allow_html=True)
st.markdown("---")
# Taking user input
user_input = st.number_input("#### Enter Password to select your Health Facility:", help="Enter Facility Password to select your Health Facility", max_value=9999999999,value=None, placeholder="Type Facility Password...")
st.markdown("---")
if user_input is not None:
    if user_input in df['Submissions[Password]'].values:
        #first_row = df[df['Submissions[Password]'] == user_input].iloc[0]
        container = st.container(border=False)
        st.markdown("""<div><br></div>""", unsafe_allow_html=True)
        # Function to filter DataFrame based on user input
        def filter_dataframe(df, user_input):
            filtered_df = df[df['Submissions[Password]'] == user_input]
            return filtered_df

        # Filtering the DataFrame
        filtered_df = filter_dataframe(df, user_input)
        ifnew_filtered_df=filtered_df
        # Displaying the filtered DataFrame
        filtered_df = filtered_df.iloc[:, 1:]
        sorted_df = filtered_df.sort_values(by=['Score','Area of Concern', 'Standard','ME_Code'])
        Facility_Name=sorted_df.iloc[0]["Facility name"]
        container.markdown(f"""<div style="border: 2px solid #4CAF50; background-color: #f9f9f9; padding: 5px; border-radius: 10px; width: 60%; margin: 20px auto;text-align: center;"><h4>{Facility_Name}</h4></div>""", unsafe_allow_html=True)
        
        #Area of Concern
        areaofconcernsum = sorted_df.groupby('Area of Concern')['Score'].sum().reset_index()
        aareaofconcerncount = sorted_df.groupby('Area of Concern')['Score'].count().reset_index()
        mergedarea=pd.merge(areaofconcernsum,aareaofconcerncount, on=['Area of Concern'], how='outer')
        mergedarea['% Score'] = ((mergedarea['Score_x'] / (mergedarea['Score_y'] * 2)) * 100)
        # Formatting percentage to two decimal places
        mergedarea['% of Score'] = mergedarea['% Score'].map("{:.2f}".format)
        #display the value with % sign
        #mergedarea['% of Score'] = mergedarea['% Score'].map("{:.2f}%".format)
        areaofconcerncount=mergedarea[['Area of Concern','% of Score']]
        st.write("#### Area of Concern")
        #st.table(areaofconcerncount)       
        savearea=formattable(areaofconcerncount)
        excel_bytes = styled_df_to_excel_bytes(savearea)
        st.markdown("""<div><br></div>""", unsafe_allow_html=True)
        downloadbtn(excel_bytes,"Area of Concern.xlsx","area")
        st.markdown("""<div style="background: linear-gradient(to right, orange, yellow, green, blue, indigo, violet, red); height: 3px; width: 100%;"></div><br><br>""", unsafe_allow_html=True)


        #Standard wise scoring 
        #Grouping and calculating count, sum, and multiply count by 2 and calculate %
        standardsum = sorted_df.groupby('Standard')['Score'].sum().reset_index()
        standardcount = sorted_df.groupby('Standard')['Score'].count().reset_index()
        mergedstandard=pd.merge(standardsum,standardcount, on=['Standard'], how='outer')
        mergedstandard['% of Score'] = ((mergedstandard['Score_x'] / (mergedstandard['Score_y'] * 2)) * 100)
        # Formatting percentage to two decimal places
        mergedstandard['% of Score'] = mergedstandard['% of Score'].map("{:.2f}".format)
        standardcount=mergedstandard[['Standard','% of Score']]
        st.write("#### Standard wise Scoring")
        savestandard=formattable(standardcount)
        excel_bytes1 = styled_df_to_excel_bytes(savestandard)
        st.markdown("""<div><br></div>""", unsafe_allow_html=True)
        #downloadbtn(excel_bytes1)
        downloadbtn(excel_bytes1,"Standards.xlsx","standards")
        st.markdown("""<div style="background: linear-gradient(to right, orange, yellow, green, blue, indigo, violet, red); height: 3px; width: 100%;"></div><br><br>""", unsafe_allow_html=True)

        #Action Plan
        st.write(f"## Action Plan of :", Facility_Name)
        #Remove special characters '(', ')' from Facility_Name, then replace spaces with '_', so that we can pass the resulting filename as an argument and save the downloaded file using this processed filename 
        filename=re.sub(r'[^a-zA-Z0-9\s]', '', Facility_Name) + ".xlsx"        
        processed_filename = filename.replace(' ', '_') 
        styled_df1=sorted_df   
        styled_df1 = styled_df1.style.background_gradient(subset=['Score'], cmap='RdYlGn').set_properties(
            subset=['Score'], **{'font-weight': 'bold', 'text-align': 'center', 'color': 'black', 'border-color': 'light gray'})
        # Add custom styling for column headers
        styled_df = styled_df1.set_table_styles(
            [{'selector': 'thead th', 'props': [('background-color', '#2196F3'), ('color', 'white')]}]
        )

        generate_excel_download_link(styled_df1,processed_filename)
        #exclude facility name column
        exclude_column = "Facility name"
        sorted_df1=sorted_df.drop(columns=[exclude_column])
        
        styled_df = sorted_df1.style.background_gradient(subset=['Score'], cmap='RdYlGn').set_properties(
            subset=['Score'], **{'font-weight': 'bold', 'text-align': 'center', 'color': 'black', 'border-color': 'light gray'})
        # Add custom styling for column headers
        styled_df = styled_df.set_table_styles(
            [{'selector': 'thead th', 'props': [('background-color', '#2196F3'), ('color', 'white')]}]
        )
        styled_df = styled_df.hide(axis='index')        
        st.markdown(styled_df.to_html(), unsafe_allow_html=True)
        st.markdown("""<div><br></div>""", unsafe_allow_html=True)
        generate_excel_download_link(styled_df,processed_filename)
        st.markdown("""<div style="background: linear-gradient(to right, orange, yellow, green, blue, indigo, violet, red); height: 3px; width: 100%;"></div><br><br>""", unsafe_allow_html=True)
    else:
        show_floating_message()         
        
        

        
                

        
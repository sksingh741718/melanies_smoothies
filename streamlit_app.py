# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in
  your custom Smoothie!
  """
)

# text box
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# read from table and display in dataframe
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table('smoothies.public.fruit_options').select(col('FRUIT_NAME'),col('SEARCH_ON'))

# convert the snowpark dataframe to a panda dataframe so that we can use the LOC function
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to Five ingredients: '
    , my_dataframe, max_selections=5
    )

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        # new section to display smoothiefroot nutrition information
        st.subheader(fruit_chosen + ' Nutrition information')
        api_call_text = "https://my.smoothiefroot.com/api/fruit/" + search_on
        #st.write(api_call_text)
        smoothiefroot_response = requests.get(api_call_text)
        st_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order + """')"""
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")

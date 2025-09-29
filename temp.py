import streamlit as st
import pandas as pd
st.write("온도변환함수")
input_value = st.number_input("온도를 입력하세요:", format="%.2f")

if st.button('섭씨에서 화씨로 변환하기'):
     celsius = input_value
     fahrenheit = celsius * 9/5.0 + 32
     st.info(f"**{celsius:.2f} °C**는 **{fahrenheit:.2f} °F** 입니다.")

if st.button('화씨에서 섭씨로 변환하기'):

    fahrenheit = input_value
    celsius = (fahrenheit - 32) / 9.0 * 5
    st.info(f"**{fahrenheit:.2f} °F**는 **{celsius:.2f} °C** 입니다.")



    
    
     
     
     
     
    
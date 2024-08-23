# import asyncio
# from datetime import datetime
import streamlit as st
from navigation import landing, dashboard_ti, dashboard_ml, dashboard_yf2, dashboard_ti2
from streamlit.components.v1 import html
import warnings
warnings.filterwarnings(action='ignore')


@st.cache_resource
def initializer():
    call_list = ['NQ=F', '^VIX', 'ZB=F', 'JPY=X', ]
    dashboard_yf2.pre_load_data(call_list)
    # for c in call_list:
    #     inmemory.in_data[c] = load_data(c)
    print(' ! System Initializing Complete ! ')
# print(len(inmemory.in_data))
# dashboard_yf2.IN_DATA = inmemory.in_data.copy()


# Streamlit pages
st.set_page_config(layout = 'wide', page_title='Auto Signals')
# st.sidebar.image("https://res.cloudinary.com/crunchbase-production/image/upload/c_lpad,f_auto,q_auto:eco,dpr_1/z3ahdkytzwi1jxlpazje", width=50)
st.sidebar.image("./original_11.png", width=150)

# my_html = """
# <style>
#     .time {
#         font-size: 40px !important;
#         font-weight: 700 !important;
#         color: #ec5953 !important;
#     }
# </style>
# <script>
# function startTimer(duration, display) {
#     var timer = duration, minutes, seconds;
#     setInterval(function () {
#         minutes = parseInt(timer / 60, 10)
#         seconds = parseInt(timer % 60, 10);
#
#         minutes = minutes < 10 ? "0" + minutes : minutes;
#         seconds = seconds < 10 ? "0" + seconds : seconds;
#
#         display.textContent = minutes + ":" + seconds;
#
#         if (--timer < 0) {
#             timer = duration;
#         }
#     }, 1000);
# }
#
# window.onload = function () {
#     var fiveMinutes = 60 * 5,
#         display = document.querySelector('#time');
#     startTimer(fiveMinutes, display);
# };
# </script>
# <div class="time">Registration closes in <span id="time">05:00</span> minutes!</div>
# """
my_html = """
<style>
.clock {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translateX(-50%) translateY(-50%);
    color: #17D4FE;
    font-size: 40px;
    font-weight: bold;
    font-family: Orbitron;
    letter-spacing: 2px;
}
</style>
<script>
function showTime(){
    var date = new Date();
    var h = date.getHours(); // 0 - 23
    var m = date.getMinutes(); // 0 - 59
    var s = date.getSeconds(); // 0 - 59
    var session = "AM";
    
    if(h == 0){
        h = 12;
    }
    
    if(h > 12){
        h = h - 12;
        session = "PM";
    }
    
    h = (h < 10) ? "0" + h : h;
    m = (m < 10) ? "0" + m : m;
    s = (s < 10) ? "0" + s : s;
    
    var time = session + " " + h + ":" + m + ":" + s + " " + "(UTC+09:00)";
    document.getElementById("MyClockDisplay").innerText = time;
    document.getElementById("MyClockDisplay").textContent = time;
    
    setTimeout(showTime, 1000);   
}
window.onload = function () {
    showTime();
};
</script>
<div id="MyClockDisplay" class="clock" onload="showTime()"></div>
"""
html(my_html, height=35)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stPlotlyChart {
                height: 30vh !important;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown(
    """
    <style>
        [data-testid="stMetricValue"] {
            font-size: 30px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
        button[title^=Exit]+div [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
)

pages = {
    '🏠 Main Page': landing.page1,
    # '📈 Market Dashboard': dashboard_yf.pageII,
    '📈 Crossing Markets': dashboard_yf2.page2,
    '📊 Technical Analysis': dashboard_ti2.page3,
    '🛸 AI Predictions': dashboard_ml.calculator,
}

selected_page = st.sidebar.radio("Navigation", pages.keys())
pages[selected_page]()

if __name__ == '__main__':
    initializer()
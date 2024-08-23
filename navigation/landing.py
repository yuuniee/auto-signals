import streamlit as st
# import base64


@st.cache_data
def call_main_image():
    col1, col2, col3 = st.columns([0.2, 0.4, 0.2])
    col2.image('https://raw.githubusercontent.com/yuuniee/image-repository/main/3d9225136727009.620034af0e13f.gif',
               use_column_width=True, )  # width=1000)


def page1():
    call_main_image()
    # st.markdown("![Alt Text](D:/cryptodashboard-streamlit-main/3d9225136727009.620034af0e13f.gif)")
    """### gif from local file"""
    # file_ = open("./3d9225136727009.620034af0e13f.gif", "rb")
    # contents = file_.read()
    # data_url = base64.b64encode(contents).decode("utf-8")
    # file_.close()

    # f = open("./gif_code.txt", 'r')
    # data_url = f.read()
    # l_, c_, r_ = st.columns(3)
    # with c_:
    #     st.markdown(
    #         f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
    #         unsafe_allow_html=True,
    #     )

    st.markdown('''

    ----
    ## More Info
    
    ### 📨: [kiricsyuunie@gmail.com](mail:kiricsyuunie@gmail.com)
    ### 🍾: [The main image source](https://www.behance.net/gallery/136727009/Flipside-Crypto-Key-Visual-Design)
    # ''')
    st.info(
        "This site does not recommend investments and does not assume any liability arising from investments."
        # "INFO: This an open source project and you are very welcome to **contribute** your awesome "
        # "comments, questions, resources and apps as "
        # "[issues](https://github.com/Jeanfabra/cryptodashboard-streamlit/issues) or "
        # "[pull requests](https://github.com/Jeanfabra/cryptodashboard-streamlit/pulls) "
        # "to the [source code](https://github.com/Jeanfabra/cryptodashboard-streamlit)."

    )
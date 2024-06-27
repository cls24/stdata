import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pygwalker.api.streamlit import StreamlitRenderer
import altair as alt
st.set_page_config(
    page_title="6月销售数据报表",
    layout="wide"
)
st.subheader('6月整车销售数据报表', divider='rainbow')
# st.title('6月销售数据报表')
# print(df.dtypes)
def prosess(x):
    if type(x) == str:
        # print(x)
        return "".join(x.split(','))
    return x
# df = pd.read_excel('./pygw/经营日报-2024_06_22-17_49_20.xls')
# df['数量'] = df['数量'].apply(prosess).astype('float')
# df['数量'] = df['数量'].abs()
# df1 = df[df['基本单位']=='辆']
# df1 = df1[['单据日期','数量']]
# _df1 = df1.groupby(['单据日期']).sum()
# def plot_data(dataframe, x, y):
#     plt.figure(figsize=(10, 6))
#     sns.lineplot(data=dataframe, x=dataframe[x], y=dataframe[y])
#     return plt
#
# st.line_chart(_df1,y='数量',x_label ='日期',y_label='销售数量')




def df_process(df):
    # df['价税合计'] = df['价税合计'].apply(prosess).astype('float')
    # df['价税合计'] = df['价税合计'].abs()
    df1 = df[df['基本单位']=='辆']
    df1['数量'] = df1['数量'].astype('float')
    df1['数量'] = df1['数量'].abs()
    g = df1.groupby(['单据日期'])['数量'].sum()
    _dict = {'单据日期':g.index,'数量':g.values}
    return pd.DataFrame(_dict)

zc_df5 = df_process(pd.read_excel('./pygw/经营日报-2024_05.xls'))
zc_df6 = df_process(pd.read_excel('./pygw/经营日报-2024_06_27.xls'))
total5 = zc_df5['数量'].sum()
total6 = zc_df6['数量'].sum()
hcol1, hcol2,hcol3,hcol4,hcol5= st.columns(5)
with hcol1:
    st.metric(label="当月销量", value=str(int(total6))+'辆', delta=int(total6-total5))
chart6 = (
    alt.Chart(zc_df6,width=900)
    .mark_area(opacity=0.3)
    .encode(
        x="单据日期:T",
        y=alt.Y("数量:Q", stack=None),
        # color="Region:N",
    )
)
col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown("##### 月度销量走势")
        st.altair_chart(chart6)
with col2:
    col2.write(zc_df6)


chart_data = pd.read_excel('./pygw/车型汇总-2024_06.xls')
c = (
   alt.Chart(chart_data,width=500).mark_bar()
   .encode(x="商品名称", y="基本单位数量")
)

st.altair_chart(c)

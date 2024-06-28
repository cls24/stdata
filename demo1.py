import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pygwalker.api.streamlit import StreamlitRenderer
import plotly.figure_factory as ff
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


def df_process(df):
    # df['价税合计'] = df['价税合计'].apply(prosess).astype('float')
    # df['价税合计'] = df['价税合计'].abs()
    df1 = df[df['基本单位']=='辆']
    df1['数量'] = df1['数量'].astype('float')
    df1['数量'] = df1['数量'].abs()
    g = df1.groupby(['单据日期'])['数量'].sum()
    _dict = {'单据日期':g.index,'数量':g.values}
    return pd.DataFrame(_dict)

# zc_df5 = df_process(pd.read_excel('./pygw/经营日报-2024_05.xls'))
zc_df6 = df_process(pd.read_excel('./data/经营日报-2024_06.xls'))
total5 = 2400
total6 = zc_df6['数量'].sum()
hcol1, hcol2,hcol3,hcol4,hcol5= st.columns(5)
with hcol1:
    st.metric(label="当月销量", value=str(int(total6))+'辆', delta=int(total6-total5))
with hcol2:
    st.metric(label="日均销量", value=str(int(total6/30)) + '辆')
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
    # col2.write(zc_df6)
    st.dataframe(zc_df6, height=430)
# @st.cache_data
# def load_df_product():
#     df_product = pd.read_excel('./data/车型汇总-2024_06.xls')
#     df_product.sort_values(ascending=False, inplace=True, by='销售数量')
#     df_product.reset_index(drop=True, inplace=True)
#     return df_product[['商品名称','销售数量']]

# df_product = load_df_product()
col1, col2,col3, col4 = st.columns(4)
_df = pd.read_excel('./data/车型汇总-2024_06.xls')
with col1:
    with st.container(border=True):
        st.markdown("##### 车系销量占比")
        # st.write(alt.Chart(df_product).mark_bar().encode(
        #     x=alt.X('销售数量',  sort=None),
        #     y=alt.Y('商品名称'),
        #     # text='销售数量:Q'
        # ))
        # st.write(alt.Chart(df_product).mark_arc().encode(
        #     theta="销售数量",
        #     color="商品名称:N",
        #     text="销售数量:Q"
        #     # text='销售数量:Q'
        # ))
        base = alt.Chart(_df).encode(
            alt.Theta("销售数量:Q").stack(True),
            alt.Radius("销售数量").scale(type="sqrt", zero=True, rangeMin=20),
            color="商品名称:N",
        )
        c1 = base.mark_arc(innerRadius=20, stroke="#fff")
        c2 = base.mark_text(radiusOffset=10).encode(text="销量权重(%):Q")
        c1 + c2

with col2:
    with st.container(border=True):
        st.markdown("##### 车单价与销量")
        chart7 = (
            alt.Chart(_df).mark_point()
            .encode(
                x='单价',
                y='销售数量',
                size='销售数量',
                color="商品名称:N",
            )
        )

        st.altair_chart(chart7)



def load_df_customer(df_customer,y):
    df_customer.sort_values(ascending=False, inplace=True, by=y)
    df_customer.reset_index(drop=True, inplace=True)
    data = df_customer[y]
    p = data.cumsum() / data.sum()
    df_customer['p'] = p
    key = p[p > 0.8].index[0]
    key_num = data.index.tolist().index(key)
    # print('超过80%占比的节点值索引为：', key)
    # print('超过80%占比的节点值索引位置为：', key_num)
    key_product = data.loc[:key]
    return df_customer,'{:.2%}'.format(key/data.count())

def make_customer_chart(df,y):

    c_df = pd.DataFrame({'名称':_df['名称'],y:_df[y],'p':_df['p']})
    base = alt.Chart(c_df).encode(
        alt.X('名称',sort=None).title(None)
    )
    bar = base.mark_bar().encode(
        alt.Y(y,sort='ascending').title(y, titleColor='#57A44C'),
        alt.Y2('p'),
        color="名称:N"
    )
    line = base.mark_line(point=True,stroke='#5276A7', interpolate='monotone').encode(
        alt.Y('p').title('p', titleColor='#5276A7')
    )
    _c = alt.layer(bar, line).resolve_scale(
        y='independent'
    )
    return _c
with st.container(border=True):
    st.markdown("##### 经销商销量分析")
    genre = st.radio(
        "请选择要分析的数据",
        ["销售数量", "价税合计", "毛利"],
        # captions = ["销售数量", "价税合计", "毛利"],
        horizontal =True)
    print(genre)
    if genre == "销售数量":
        k = '销售数量'
    elif genre == "价税合计":
        k = '价税合计'
    else:
        k = '毛利'
    df_customer = pd.read_excel('./data/customer_summary-2024_05.xls')
    _df,percent = load_df_customer(df_customer, k)
    st.markdown("###### 百分之:"+percent + "的客户的"+k +"占比超过：80%")
    customer_chart = make_customer_chart(_df,k)
    st.altair_chart(customer_chart)


# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pygwalker.api.streamlit import StreamlitRenderer
import plotly.figure_factory as ff
import altair as alt
import datetime
import pygw.getdata,pygw.toolbox
st.set_page_config(
    page_title="销售数据报表",
    layout="wide"
)
st.subheader('月度整车销售数据报表', divider='rainbow')
# def prosess(x):
#     if type(x) == str:
#         # print(x)
#         return "".join(x.split(','))
#     return x

def df_process(df):
    # df['价税合计'] = df['价税合计'].apply(prosess).astype('float')
    # df['价税合计'] = df['价税合计'].abs()
    df1 = df[df['基本单位']=='辆']
    df1['数量'] = df1['数量'].astype('float')
    df1['数量'] = df1['数量'].abs()
    g = df1.groupby(['单据日期'])['数量'].sum()
    _dict = {'单据日期':g.index,'数量':g.values}
    return pd.DataFrame(_dict)

s = pygw.getdata.getCarparSession()
today = datetime.datetime.now()

dcol1, dcol2,dcol3, dcol4 = st.columns(4)
with dcol1:
    d = st.date_input(
        "选择查询日期",
        (today, today),
        # jan_1,
        # dec_31,
        format="YYYY-MM-DD",
        key='dcol1'
    )
with dcol2:
    d_before = st.date_input(
        "选择对比日期",
        (today, today),
        # jan_1,
        # dec_31,
        format="YYYY-MM-DD",
        key='dcol2'
    )
d1 = d[0].strftime("%Y-%m-%d")
d2 = d[1].strftime("%Y-%m-%d")
d_before1 = d_before[0].strftime("%Y-%m-%d")
d_before2 = d_before[1].strftime("%Y-%m-%d")
if st.button("查询"):
    hcol1, hcol2, hcol3, hcol4, hcol5 = st.columns(5)
    with hcol1:
        res = pygw.getdata.get_ddc_summary(s, d1, d2)
        res1 = pygw.getdata.get_ddc_summary(s, d_before1, d_before2)
        ddc_summary_df = pd.DataFrame(res)
        ddc_summary_before_df = pd.DataFrame(res1)
        total_now = ddc_summary_df['sum_qty'].sum()
        total_before = ddc_summary_before_df['sum_qty'].sum()
        days = pygw.toolbox.get_day_num(d1, d2)
        st.metric(label="当月销量", value=str(int(total_now))+'辆', delta=int(total_now-total_before))
    with hcol2:
        st.metric(label="日均销量", value=str(int(total_now/days)+1) + '辆')

    res2 = pygw.getdata.get_day_report(s, d1, d2)
    get_day_report_df = pd.DataFrame(res2)
    get_day_report_df = get_day_report_df[get_day_report_df['baseunitname'] == '辆']
    g = get_day_report_df.groupby(['billdate'])['qty'].sum()
    _dict = {'单据日期':g.index,'数量':g.values}
    _pd_get_day_report_df = pd.DataFrame(_dict)
    _pd_get_day_report_df['数量'] = _pd_get_day_report_df['数量'].abs()
    day_report_chart = (
        alt.Chart(_pd_get_day_report_df, width=900)
        .mark_area(opacity=0.3)
        .encode(
            x="单据日期:T",
            y=alt.Y("数量:Q", stack=None),
            # color="Region:N",
        )
    )
    with st.container(border=True):
        st.markdown("##### 月度销量走势")
        st.altair_chart(day_report_chart)

# baseunitname

# col1, col2 = st.columns(2)
# with col1:
#     with st.container(border=True):
#         st.markdown("##### 月度销量走势")
#         st.altair_chart(chart6)
# with col2:
#     # col2.write(zc_df6)
#     st.dataframe(zc_df6, height=430)
#
# col1, col2,col3, col4 = st.columns(4)
#
# all_ddc_df = pd.read_excel('./data/all_ddc.xlsx')
# ddc_summary_df = pd.read_excel('./data/ddc_summary.xlsx')
# ddc_summary_df['per'] = ddc_summary_df['qty']/ddc_summary_df['qty'].sum()
# ddc_summary_df = ddc_summary_df.round({'per': 3})
# with col1:
#     with st.container(border=True):
#         st.markdown("##### 车系销量占比")
#         base = alt.Chart(ddc_summary_df).encode(
#             alt.Theta("qty:Q").stack(True),
#             alt.Radius("qty").scale(type="sqrt", zero=True, rangeMin=20),
#             color="fullname:N",
#         )
#         c1 = base.mark_arc(innerRadius=20, stroke="#fff")
#         c2 = base.mark_text(radiusOffset=10).encode(text="per:Q")
#         c1 + c2
#
# with col2:
#     with st.container(border=True):
#         st.markdown("##### 车单价与销量")
#         chart7 = (
#             alt.Chart(ddc_summary_df).mark_point()
#             .encode(
#                 x='price',
#                 y='qty',
#                 size='qty',
#                 color="fullname:N",
#             )
#         )
#         st.altair_chart(chart7)
# with col3:
#     with st.container(border=True):
#         genre_ddc = st.radio(
#             "请选择要分析的车系",
#             ddc_summary_df['fullname'].tolist(),
#             )
#         parid = ddc_summary_df[ddc_summary_df['fullname']==genre_ddc]['typeid'].values[0]
#         genre_ddc_df = all_ddc_df[all_ddc_df['parid'] == parid]
#         genre_ddc_df.sort_values(ascending=False, inplace=True, by='qty')
#         genre_ddc_df.reset_index(drop=True, inplace=True)
#     # st.write(genre_ddc)
# with col4:
#     # scale = alt.Scale(domain=["line", "shade1", "shade2"], range=['red', 'lightblue', 'darkblue'])
#     with st.container(border=True):
#         genre_ddc_chart = alt.Chart(genre_ddc_df).mark_bar().encode(
#                 alt.Y('fullname', sort=None).title(None),
#             alt.X('qty', sort='ascending').title('qty', titleColor='#57A44C'),
#             # color="fullname:N"
#             # color=alt.Color('fullname:N', title='')
#         )
#         st.altair_chart(genre_ddc_chart)
# def load_df_customer(df_customer,y):
#     df_customer.sort_values(ascending=False, inplace=True, by=y)
#     df_customer.reset_index(drop=True, inplace=True)
#     data = df_customer[y]
#     p = data.cumsum() / data.sum()
#     df_customer['p'] = p
#     key = p[p > 0.8].index[0]
#     key_num = data.index.tolist().index(key)
#     # print('超过80%占比的节点值索引为：', key)
#     # print('超过80%占比的节点值索引位置为：', key_num)
#     key_product = data.loc[:key]
#     return df_customer,'{:.2%}'.format(key/data.count())
#
# def make_customer_chart(df,y):
#
#     c_df = pd.DataFrame({'名称':_df['名称'],y:_df[y],'p':_df['p']})
#     base = alt.Chart(c_df).encode(
#         alt.X('名称',sort=None).title(None)
#     )
#     bar = base.mark_bar().encode(
#         alt.Y(y,sort='ascending').title(y, titleColor='#57A44C'),
#         alt.Y2('p'),
#         color="名称:N"
#     )
#     line = base.mark_line(point=True,stroke='#5276A7', interpolate='monotone').encode(
#         alt.Y('p').title('p', titleColor='#5276A7')
#     )
#     _c = alt.layer(bar, line).resolve_scale(
#         y='independent'
#     )
#     return _c
# with st.container(border=True):
#     st.markdown("##### 经销商销量分析")
#     genre = st.radio(
#         "请选择要分析的数据",
#         ["销售数量", "价税合计", "毛利"],
#         # captions = ["销售数量", "价税合计", "毛利"],
#         horizontal =True)
#     # print(genre)
#     if genre == "销售数量":
#         k = '销售数量'
#     elif genre == "价税合计":
#         k = '价税合计'
#     else:
#         k = '毛利'
#     df_customer = pd.read_excel('./data/customer_summary-2024_06.xls')
#     _df,percent = load_df_customer(df_customer, k)
#     st.markdown("###### 百分之:"+percent + "的客户的"+k +"占比超过：80%")
#     customer_chart = make_customer_chart(_df,k)
#     st.altair_chart(customer_chart)

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

# @st.cache_data
def fetch_ddc_summary(s, _d1, _d2):
    res = pygw.getdata.get_ddc_summary(s, _d1, _d2)
    ddc_summary_before_df = pd.DataFrame(res)
    return ddc_summary_before_df

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
    # res = pygw.getdata.get_ddc_summary(s, d1, d2)
    # res1 = pygw.getdata.get_ddc_summary(s, d_before1, d_before2)
    ddc_summary_df = fetch_ddc_summary(s, d1, d2)
    ddc_summary_before_df = fetch_ddc_summary(s, d_before1, d_before2)
    total_before = ddc_summary_before_df['sum_qty'].sum()
    ddc_summary_df['per'] = ddc_summary_df['sum_qty'] / ddc_summary_df['sum_qty'].sum()
    ddc_summary_df = ddc_summary_df.round({'per': 3})
    total_now = ddc_summary_df['sum_qty'].sum()
    days = pygw.toolbox.get_day_num(d1, d2)
    ddc_summary_df.sort_values(ascending=False, inplace=True, by='sum_qty')
    ddc_summary_df_top3 = ddc_summary_df.head(3)
    top3_list = []
    for index, row in ddc_summary_df_top3.iterrows():
        typeid = row["typeid"]
        _ = pygw.getdata.get_one_ddc_detail(s,d1,d2,typeid)
        top3_list.append(pd.DataFrame(_))

    # accountqty
    get_all_ddc_detail_df = pygw.getdata.get_all_ddc_detail(s, d1, d2)
    get_all_ddc_detail_df = pd.DataFrame(get_all_ddc_detail_df)
    hcol1, hcol2, hcol3, hcol4, hcol5 = st.columns(5)
    with hcol1:
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
        alt.Chart(_pd_get_day_report_df)
        .mark_area(
            clip=True,
            interpolate='monotone',
            opacity=0.6
        )
        .encode(
            x="单据日期:T",
            y=alt.Y("数量:Q", stack=None),
            # color="Region:N",
        )
    )
    with st.container(border=True):
        st.markdown("##### 月度销量走势")
        st.altair_chart(day_report_chart,use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("##### 车系销量占比")
            base = alt.Chart(ddc_summary_df).encode(
                alt.Theta("sum_qty:Q").stack(True),
                alt.Radius("sum_qty").scale(type="sqrt", zero=True, rangeMin=20),
                color="fullname:N",
            )
            c1 = base.mark_arc(innerRadius=20, stroke="#fff")
            c2 = base.mark_text(radiusOffset=10).encode(text="per:Q")
            c1 + c2
    with col2:
        with st.container(border=True):
            st.markdown("##### 车单价与销量")
            chart7 = (
                alt.Chart(ddc_summary_df).mark_point()
                .encode(
                    x=alt.X('price').title('单价'),
                    y=alt.Y('sum_qty').title('总销量'),
                    size='sum_qty',
                    color="fullname:N",
                )
            )
            st.altair_chart(chart7)
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            top3_list[0].sort_values(ascending=False, inplace=True, by='qty')
            genre_ddc_chart1 = alt.Chart(top3_list[0]).mark_bar().encode(
                    alt.Y('fullname', sort=None).title(None),
                alt.X('qty', sort='ascending').title('销量', titleColor='#57A44C'),
                # color="fullname:N",
                color=alt.Color('fullname:N', title='车系')
            )
            st.altair_chart(genre_ddc_chart1)
    with col2:
        with st.container(border=True):
            top3_list[1].sort_values(ascending=False, inplace=True, by='qty')
            genre_ddc_chart2 = alt.Chart(top3_list[1]).mark_bar().encode(
                    alt.Y('fullname', sort=None).title(None),
                alt.X('qty', sort='ascending').title('销量', titleColor='#57A44C'),
                color=alt.Color('fullname:N', title='车系')
                # color=alt.Color('fullname:N', title='')
            )
            st.altair_chart(genre_ddc_chart2)
    with col3:
        with st.container(border=True):
            top3_list[2].sort_values(ascending=False, inplace=True, by='qty')
            genre_ddc_chart3 = alt.Chart(top3_list[2]).mark_bar().encode(
                    alt.Y('fullname', sort=None).title(None),
                alt.X('qty', sort='ascending').title('销量', titleColor='#57A44C'),
                color=alt.Color('fullname:N', title='车系')
                # color=alt.Color('fullname:N', title='')
            )
            st.altair_chart(genre_ddc_chart3)

    # with col3:
    #     with st.container(border=True):
    #         genre_ddc = st.radio(
    #             "请选择要分析的车系",
    #             ddc_summary_df['fullname'].tolist(),
    #             )

        # genre_ddc_df = all_ddc_df[all_ddc_df['parid'] == parid]
        # genre_ddc_df.sort_values(ascending=False, inplace=True, by='qty')
        # genre_ddc_df.reset_index(drop=True, inplace=True)
        #     st.write(genre_ddc)
    # with col4:
    #     # scale = alt.Scale(domain=["line", "shade1", "shade2"], range=['red', 'lightblue', 'darkblue'])
    #     with st.container(border=True):
    #
    #         parid = ddc_summary_df[ddc_summary_df['fullname']==genre_ddc]['typeid'].values[0]
    #         one_ddc_df = pygw.getdata.get_one_ddc_detail(s,d1,d2,parid)
    #         one_ddc_df = pd.DataFrame(one_ddc_df)
    #         genre_ddc_chart = alt.Chart(one_ddc_df).mark_bar().encode(
    #                 alt.Y('fullname', sort=None).title(None),
    #             alt.X('qty', sort='ascending').title('qty', titleColor='#57A44C'),
    #             # color="fullname:N"
    #             # color=alt.Color('fullname:N', title='')
    #         )
    #         st.altair_chart(genre_ddc_chart)
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

    res_customer = pygw.getdata.get_customer_summary(s,d1,d2)
    customer_summary_df = pd.DataFrame(res_customer)
    _df,percent = load_df_customer(customer_summary_df, 'sum_qty')

    c_df = pd.DataFrame({'fullname':_df['fullname'],'sum_qty':_df['sum_qty'],'p':_df['p']})
    base = alt.Chart(c_df).encode(
        alt.X('fullname',sort=None).title('名称')
    )
    bar = base.mark_bar().encode(
        alt.Y('sum_qty',sort='ascending').title('销量', titleColor='#57A44C'),
        alt.Y2('p'),
        color="fullname:N"
    )
    line = base.mark_line(point=True,stroke='#5276A7', interpolate='monotone').encode(
        alt.Y('p').title('p', titleColor='#5276A7')
    )
    _c = alt.layer(bar, line).resolve_scale(
        y='independent'
    )
    with st.container(border=True):
        st.markdown("##### 经销商销量分析")
        # genre = st.radio(
        #     "请选择要分析的数据",
        #     ["销售数量", "价税合计", "毛利"],
        #     # captions = ["销售数量", "价税合计", "毛利"],
        #     horizontal =True)
        # # print(genre)
        # if genre == "销售数量":
        #     k = '销售数量'
        # elif genre == "价税合计":
        #     k = '价税合计'
        # else:
        #     k = '毛利'

        st.markdown("###### 百分之:"+percent + "的客户产生的"+'销量' +"占比超过：80%")
        # customer_chart = make_customer_chart(_df,k)
        st.altair_chart(_c)

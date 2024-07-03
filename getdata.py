# -*- coding: utf-8 -*-
import openpyxl
import os,requests,json,re,datetime,time,asyncio
# from gevent import monkey; monkey.patch_all()
# import gevent
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
carpaHost = 'http://lyddc.routersoft.cn'
ptypeids = ['0003701686', '0003701687', '0003701688', '0003701689']
cookie = ''

def rows2dict(fields,rows):
    out = []
    for row in rows:
        obj = {}
        for i in range(len(row)):
            obj[fields[i]] = row[i]
        out.append(obj)
    return out

def getCarparSession():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36",
        'Connection': 'Keep-Alive'
    }
    s = requests.Session()
    s.headers = headers
    url = '/jxcTOP/CarpaServer/CarpaServer.LoginService.ajax/UserLogin'
    data = {"user":{"name":"28","password":"123123","isChange":"","verificationCodeId":"","verificationCode":"","database":"南京睿图","lockNum":"err","userRank":None,"HardDiskNo":"","MacAddress":"E89C253692EF"}}
    try:
        s.post(carpaHost + url,json=data)
        return s
    except Exception as e:
        return None
def dashrepl(matchobj):
    if matchobj.group(0):
        # print(matchobj.group(0))
        ts = re.findall('\d+',matchobj.group(0))[0]
        dateArray = datetime.datetime.utcfromtimestamp(int(ts[:10]))
        otherStyleTime = dateArray.strftime("%Y-%m-%d")
        # print(otherStyleTime)
        return '"'+otherStyleTime+'"'
    else:
        return ''

def get_one_ddc_detail(session,startdate,enddate,parid):
    # startdate = '2024-03-01'
    data = '{"formId":"2","clientInfo":{"SaleQueryDataSource":{"ConfigGUID":"6fed24d2_grid_0","PageSize":0,"ShowAll":false},"__ConfigGUID":"6fed24d2_0","__Params":{"parid":"00000","ktypeid":"","stypeid":"00001","saleflag":2,"buyType":0,"startdate":"2024-03-01","enddate":"2024-06-12","periodname":"(本期)","iscountsendptype":"1"},"__Grids":["6fed24d2_grid_0"],"__GridInfos":{"6fed24d2_grid_0":{"PermitGroupName":["ptype","baseInfo"],"NumberTypeNames":{"numberFields":{"qty":"qty","fzsl":"qty","nqty":"qty","price":"price","total":"total","taxtotal":"total"},"numberColumnTypeNames":["qty","price","total"]},"BaseInfoColumns":[{"ColumnName":"$ptype$typeid","TypeName":"ptype","DisplayFields":"usercode,fullname","DataField":"typeid","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false}],"defaultOrderField":null,"isDistributing":false,"distributingTypeName":"","ExpressionColumnInfo":{},"State":null}},"__FormGuid":"5d02f961-0150-4e98-b21d-91147a98d3cc","__Tag":null,"__Caches":{"__CorrelativeActionConfig":0,"__SkinConfig":0,"__ReportLimitData":0,"__CustomReportConfig":0,"__BusinessData":0,"__SelfDataType":0,"limit":2,"userconfig":69,"pricetrackconfig":0,"sysdata":280,"sysdata1":146,"userinfo":3,"digitconfig":72}}}'
    data = json.loads(data)
    data['clientInfo']['__Params']['startdate'] = startdate
    data['clientInfo']['__Params']['enddate'] = enddate
    url1 = '/jxcTOP/CarpaServer/CarpaServer.Sale.SaleQueryBaseService.ajax/_GetServerContextData'
    r = session.post(carpaHost + url1, json=data)
    data1 = '{"pagerId":"$2$SaleQueryDataSource","queryParams":{"parid":"0001000009","ktypeid":"","stypeid":"00001","saleflag":2,"buyType":0,"startdate":"2024-03-01","enddate":"2024-06-12","periodname":"(本期)","iscountsendptype":"1","sortfield":"","sorttype":"","QueryType":"sale","DAY":"","BEGINDate":"2024-03-01","OperatorID":"000010000700012"},"orders":null,"filter":null,"first":0,"count":30,"isFirst":false}'
    data1 = json.loads(data1)
    data1['queryParams']['startdate']= startdate
    data1['queryParams']['BEGINDate']= startdate
    data1['queryParams']['enddate']= enddate
    url1 = '/jxcTOP/Carpa.Web/Carpa.Web.Script.DataService.ajax/GetPagerDataEx '
    r = session.post(carpaHost + url1, json=data1)
    data1 = '{"pagerId":"$2$SaleQueryDataSource","queryParams":{"parid":"000100000900025","ktypeid":"","stypeid":"00001","saleflag":2,"buyType":0,"startdate":"2024-03-01","enddate":"2024-06-12","periodname":"(本期)","iscountsendptype":"1","sortfield":"","sorttype":"","QueryType":"sale","DAY":"","BEGINDate":"2024-03-01","OperatorID":"000010000700012"},"orders":null,"filter":null,"first":0,"count":999,"isFirst":false}'
    data1 = json.loads(data1)
    data1['queryParams']['startdate'] = startdate
    data1['queryParams']['BEGINDate'] = startdate
    data1['queryParams']['enddate'] = enddate
    data1['queryParams']['parid'] = parid
    r = session.post(carpaHost + url1, json=data1).json()
    return rows2dict(r['itemList']['fields'],r['itemList']['rows'])
    # parids = r.json()['itemList']['rows']
    # l = []
    # for p in parids:
    #     data1 = '{"pagerId":"$2$SaleQueryDataSource","queryParams":{"parid":"000100000900025","ktypeid":"","stypeid":"00001","saleflag":2,"buyType":0,"startdate":"2024-03-01","enddate":"2024-06-12","periodname":"(本期)","iscountsendptype":"1","sortfield":"","sorttype":"","QueryType":"sale","DAY":"","BEGINDate":"2024-03-01","OperatorID":"000010000700012"},"orders":null,"filter":null,"first":0,"count":30,"isFirst":false}'
    #     data1 = json.loads(data1)
    #     data1['queryParams']['startdate'] = startdate
    #     data1['queryParams']['BEGINDate'] = startdate
    #     data1['queryParams']['enddate'] = datetime.datetime.now().strftime('%Y-%m-%d')
    #     data1['queryParams']['parid'] = p[0]
    #     r = session.post(carpaHost + url1, json=data1).json()
    #     # print(r.text)
    #     l = l + rows2dict(r['itemList']['fields'],r['itemList']['rows'])
    # return l

def get_ddc_summary(session,startdate,enddate):
    url1 = '/jxcTOP/CarpaServer/CarpaServer.Sale.SaleQueryBaseService.ajax/_GetServerContextData '
    data1 = '{"formId":"2","clientInfo":{"SaleQueryDataSource":{"ConfigGUID":"6fed24d2_grid_0","PageSize":0,"ShowAll":false},"__ConfigGUID":"6fed24d2_0","__Params":{"parid":"00000","ktypeid":"0000200007","stypeid":"00001","saleflag":3,"buyType":0,"startdate":"2024-07-01","enddate":"2024-07-01","iscountsendptype":"1"},"__Grids":["6fed24d2_grid_0"],"__GridInfos":{"6fed24d2_grid_0":{"PermitGroupName":["ptype","baseInfo"],"NumberTypeNames":{"numberFields":{"qty":"qty","fzsl":"qty","nqty":"qty","price":"price","total":"total","taxtotal":"total"},"numberColumnTypeNames":["qty","price","total"]},"BaseInfoColumns":[{"ColumnName":"$ptype$typeid","TypeName":"ptype","DisplayFields":"usercode,fullname","DataField":"typeid","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false}],"defaultOrderField":null,"isDistributing":false,"distributingTypeName":"","ExpressionColumnInfo":{},"State":null}},"__FormGuid":"b7468aa8-34a2-4898-8143-3bfcd6f71650","__Tag":null,"__Caches":{"__CorrelativeActionConfig":0,"__SkinConfig":0,"__ReportLimitData":0,"__CustomReportConfig":0,"__BusinessData":0,"__SelfDataType":0,"limit":2,"userconfig":51,"pricetrackconfig":0,"sysdata":330,"sysdata1":228,"userinfo":0,"digitconfig":114}}}'
    # data1 = '{"formId":"2","clientInfo":{"BillIndexStatReportListDataSource":{"ConfigGUID":"9fdb1fca_grid_11","PageSize":0,"ShowAll":false},"__ConfigGUID":"9fdb1fca_0","__Params":{"stypeid":"00001","sfullname":"默认分支机构","billTypeName":"生产拆装单","kfullname":"西善桥-总部","showstockstop":false,"billtype":"11","startdate":"2024-06-01","enddate":"2024-06-29","btypeid":"","etypeid":"","ktypeid":"00002","ktypeid1":"","billcode":"","comment":"","showItem":"1","repname":"销售出库单","typeid":"00000","cz":"0","ifAssets":"0"},"__Grids":["9fdb1fca_grid_11"],"__GridInfos":{"9fdb1fca_grid_11":{"PermitGroupName":["ptype","baseInfo"],"NumberTypeNames":{"numberFields":{"qty":"qty","nprice":"price","ntotal":"total","ntaxtotal":"total","rqty":"qty","nrtotal":"total","cqty":"qty","nctotal":"total","mqty":"qty"},"numberColumnTypeNames":["qty","price","total"]},"BaseInfoColumns":[{"ColumnName":"$ptype$typeid","TypeName":"ptype","DisplayFields":"usercode,fullname","DataField":"typeid","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false}],"defaultOrderField":null,"isDistributing":false,"distributingTypeName":"","ExpressionColumnInfo":{},"State":null}},"__FormGuid":"3f94e01a-f506-4259-84f0-d050777aab26","__Tag":null,"__Caches":{"__CorrelativeActionConfig":0,"__SkinConfig":0,"__ReportLimitData":0,"__CustomReportConfig":0,"__BusinessData":0,"__SelfDataType":0,"limit":0,"userconfig":54,"pricetrackconfig":0,"sysdata":210,"sysdata1":102,"userinfo":0,"digitconfig":51}}}'
    data1 = json.loads(data1)
    session.post(carpaHost + url1, json=data1)
    url1 = '/jxcTOP/Carpa.Web/Carpa.Web.Script.DataService.ajax/GetPagerDataEx '
    # data1 = '{"pagerId":"$2$BillIndexStatReportListDataSource","queryParams":{"stypeid":"00001","sfullname":"默认分支机构","billTypeName":"生产拆装单","kfullname":"西善桥-总部","showstockstop":false,"billtype":"11","startdate":"2024-06-01","enddate":"2024-06-29","btypeid":"","etypeid":"","ktypeid":"00002","ktypeid1":"","billcode":"","comment":"","showItem":"1","repname":"销售出库单","typeid":"00000","cz":"0","ifAssets":"0","chvOperatorID":"000010000700012","VchType":"11","BeginDate":"2024-06-01","Parid":"0001000009","chvBtypeName":"","chvEtypeName":"","chvKtypeName":"00002","IFCheck":"t","chvKtypeName2":""},"orders":null,"filter":null,"first":0,"count":30,"isFirst":false}'
    # data1 = '{"pagerId":"$2$saleStatSource","queryParams":{"billType":"11","billTypeName":"销售出库单","inputType":"P","stypeid":"00001","sfullname":"默认分支机构","pfullname":"九号车-现用","ptypeid":"0001000009","kfullname":"九号整车总仓","showstockstop":false,"bTypeLx":null,"flag":"0","startDate":"2024-07-01","endDate":"2024-07-01","ptypecategoryid":"","ptypeproperty":"0","btypeid":"","dealbtypeid":"","etypeid":"","etypeid1":"","ktypeid":"0000200007","atypeid":"","dtypeid":"","explain":"","comment":"","chkDiscountQuery":"0","chkPe":0,"chkDx":"0","chkPf":"0","parid":"0001000009","chkXs":"0","chkPt":"0","chkRed":0,"delView":0,"isshowservice":true,"intPageNo":"1","intPageSize":50,"chvOperatorID":"000010000700012","chrFlag":"1","unitconvert":3},"orders":null,"filter":null,"first":0,"count":30,"isFirst":false}'
    data1 = '{"pagerId":"$2$SaleQueryDataSource","queryParams":{"parid":"0001000009","ktypeid":"0000200007","stypeid":"00001","saleflag":3,"buyType":0,"startdate":"2024-07-01","enddate":"2024-07-01","iscountsendptype":"1","sortfield":"","sorttype":"","QueryType":"sale","DAY":"","BEGINDate":"2024-07-01","OperatorID":"000010000700012"},"orders":null,"filter":null,"first":0,"count":9999,"isFirst":false}'
    data1 = json.loads(data1)
    data1['queryParams']['startdate'] = startdate
    data1['queryParams']['enddate'] = enddate
    r = session.post(carpaHost + url1, json=data1).json()
    print(r)
    return rows2dict(r['itemList']['fields'], r['itemList']['rows'])

def get_customer_summary(session,startdate,enddate):
    url1 = '/jxcTOP/CarpaServer/CarpaServer.Stat.StatTypeListBaseService.ajax/_GetServerContextData'
    data1 = '{"formId":"2","clientInfo":{"saleStatSource":{"ConfigGUID":"3e528339_grid_1000","PageSize":0,"ShowAll":false},"__ConfigGUID":"3e528339_0","__Params":{"startDate":"2024-04-01","endDate":"2024-06-30","ptypecategoryid":"","ptypeid":"","btypeid":"","dealbtypeid":"","etypeid":"","ktypeid":"0000200007","dtypeid":"","billType":"11,45,305,141,160,215","billTypeName":"销售出库单,销售退货单,零售单,委托代销结算单,销售换货单,零售退货单","explain":"","comment":"","chkDiscountQuery":"0","chkPe":"0","chkDx":"0","chkPf":"0","pfullname":"","kfullname":"九号整车总仓","atypeid":"","etypeid1":"","ptypeproperty":"0","flag":"0","bTypeLx":null,"sfullname":"默认分支机构","stypeid":"00001","inputType":"B","parid":"00000","chkXs":"0","chkPt":"0","chkRed":0,"delView":0,"isshowservice":false},"__Grids":["3e528339_grid_1000"],"__GridInfos":{"3e528339_grid_1000":{"PermitGroupName":["jtype","baseInfo"],"NumberTypeNames":{"numberFields":{"sum_qty":"qty","salecount":"qty","salebackcount":"qty","nqty":"qty","gift_qty":"qty","giftprice":"price","giftcosttotal":"total","price":"price","sum_discounttotal":"total","sum_total":"total","sum_taxtotal":"total","taxge":"total","costprice":"price","sum_costtotal":"total","pricetotal":"total","advantagetotal":"total","sharefee":"total","sum_maoli":"total","preferencemoney":"total","sum_maolilu":"percentage","zeropriceqty":"qty","qty_qz":"percentage","total_qz":"percentage","maoli_qz":"percentage","pjlirun":"total"},"numberColumnTypeNames":["qty","price","total","percentage"]},"BaseInfoColumns":[{"ColumnName":"$jtype$typeid","TypeName":"jtype","DisplayFields":"usercode,fullname","DataField":"typeid","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false}],"defaultOrderField":null,"isDistributing":false,"distributingTypeName":"","ExpressionColumnInfo":{},"State":null}},"__FormGuid":"c9085f86-9a92-454f-a6ab-ec463fde6509","__Tag":null,"__Caches":{"__CorrelativeActionConfig":0,"__SkinConfig":0,"__ReportLimitData":0,"__CustomReportConfig":0,"__BusinessData":0,"__SelfDataType":0,"limit":0,"userconfig":58,"pricetrackconfig":0,"sysdata":218,"sysdata1":102,"userinfo":0,"digitconfig":51}}}'
    data1 = json.loads(data1)
    # data1['queryParams']['startdate'] = startdate
    # data1['queryParams']['enddate'] = enddate
    r = session.post(carpaHost + url1, json=data1)
    url1 = '/jxcTOP/Carpa.Web/Carpa.Web.Script.DataService.ajax/GetPagerDataEx '
    # data1 = '{"pagerId":"$2$saleStatSource","queryParams":{"startDate":"2024-04-01","endDate":"2024-06-30","ptypecategoryid":"","ptypeid":"","btypeid":"","dealbtypeid":"","etypeid":"","ktypeid":"0000200007","dtypeid":"","billType":"11","billTypeName":"销售出库单","explain":"","comment":"","chkDiscountQuery":false,"chkPe":0,"chkDx":false,"chkPf":0,"pfullname":"","kfullname":"九号整车总仓","atypeid":"","etypeid1":"","ptypeproperty":"0","flag":"0","bTypeLx":null,"sfullname":"默认分支机构","stypeid":"00001","inputType":"B","parid":"0000100051","chkXs":0,"chkPt":"0","chkRed":0,"delView":0,"isshowservice":false,"intPageNo":"1","intPageSize":50,"chvOperatorID":"000010000700012","chrFlag":"1","unitconvert":3,"dealbfullname":"","bfullname":"","efullname":"","dfullname":"","areafullname":""},"orders":null,"filter":null,"first":0,"count":999,"isFirst":false}'
    data1 = '{"pagerId":"$2$saleStatSource","queryParams":{"startDate":"2024-07-01","endDate":"2024-07-01","ptypecategoryid":"00002","ptypeid":"000100000900001,000100000900002,000100000900003,000100000900004,000100000900005,000100000900029,000100000900006,000100000900020,000100000900021,000100000900022,000100000900023,000100000900024,000100000900025,000100000900026,000100000900027,000100000900028","btypeid":"0000100051","dealbtypeid":"","etypeid":"","ktypeid":"0000200007","dtypeid":"","billType":"11","billTypeName":"销售出库单","explain":"","comment":"","chkDiscountQuery":false,"chkPe":0,"chkDx":false,"chkPf":0,"pfullname":"九号车B系列;九号车C系列;九号车E系列;九号车其他;九号车A系列;九号车A2Z系列;九号车N系列;九号车C2021系列;九号车A+系列;九号车Bmax系列;九号车F系列;九号车Mmax系列;九号车M系列;九号车Q系列;九号车V系列;九号车D系列","bfullname":"九号-经销商","kfullname":"九号整车总仓","atypeid":"","etypeid1":"","ptypeproperty":"0","flag":"0","bTypeLx":null,"sfullname":"默认分支机构","stypeid":"00001","inputType":"B","ptypecategoryfullname":"电动车","showstockstop":false,"parid":"0000100051","chkXs":0,"chkPt":"0","chkRed":0,"delView":0,"isshowservice":false,"intPageNo":"1","intPageSize":50,"chvOperatorID":"000010000700012","chrFlag":"1","unitconvert":3,"dealbfullname":"","efullname":"","dfullname":"","areafullname":""},"orders":null,"filter":null,"first":0,"count":30,"isFirst":false}'
    data1 = json.loads(data1)
    data1['queryParams']['startdate'] = startdate
    data1['queryParams']['enddate'] = enddate
    r = session.post(carpaHost + url1, json=data1).json()
    # print(r)
    return rows2dict(r['itemList']['fields'], r['itemList']['rows'])
def get_one_customer_summary(session,startdate,enddate,parid):
    url1 = '/jxcTOP/CarpaServer/CarpaServer.Stat.StatTypeDetailBaseService.ajax/_GetServerContextData '
    data1 = '{"formId":"2","clientInfo":{"saleStatDetailSource":{"ConfigGUID":"7d401178_grid_1","PageSize":0,"ShowAll":false},"__ConfigGUID":"7d401178_0","__Params":{"startDate":"2024-04-01","endDate":"2024-06-30","ptypecategoryid":"","ptypeid":"","btypeid":"","dealbtypeid":"","etypeid":"","ktypeid":"0000200007","dtypeid":"","billType":"11,45,305,141,160,215","billTypeName":"销售出库单,销售退货单,零售单,委托代销结算单,销售换货单,零售退货单","explain":"","comment":"","chkDiscountQuery":"0","chkPe":0,"chkDx":"0","chkPf":"0","pfullname":"","kfullname":"九号整车总仓","atypeid":"","etypeid1":"","ptypeproperty":"0","flag":"0","bTypeLx":null,"sfullname":"默认分支机构","stypeid":"00001","inputType":"B","parid":"000010005100009","chkXs":"0","chkPt":"0","chkRed":0,"delView":0,"isshowservice":false,"intPageNo":"1","intPageSize":50,"chvOperatorID":"000010000700012","chrFlag":"1","unitconvert":3,"startdate":"2024-04-01","enddate":"2024-06-30"},"__Grids":["7d401178_grid_1"],"__GridInfos":{"7d401178_grid_1":{"PermitGroupName":["etype","stype","dtype","allsettlement","btype","etype","ktype","cargotype","ptype","baseInfo"],"NumberTypeNames":{"numberFields":{"rate":"exchangeRate","qty":"qty","munitqty":"qty","nqty":"qty","saletotal":"total","nsaletotal":"total","price":"price","nprice":"price","total":"total","ntotal":"total","taxtotal":"total","ntaxtotal":"total","discount":"discount","taxge":"total","costprice":"price","costtotal":"total","ptotal":"total","atotal":"total","sharefee":"total","maoli":"total","maolilu":"percentage","reconciliation":"total"},"numberColumnTypeNames":["exchangeRate","qty","total","price","discount","percentage"]},"BaseInfoColumns":[{"ColumnName":"$etype$sysdiy33_head","TypeName":"etype","DisplayFields":"fullname","DataField":"sysdiy33_head","RootLayerIdLength":0,"DisplayCaptions":"表头自定义33","DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":true,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":true,"SaveInitConfig":true,"IsDiyCol":true},{"ColumnName":"$stype$stypeid","TypeName":"stype","DisplayFields":"fullname","DataField":"stypeid","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false},{"ColumnName":"$dtype$dtypeid","TypeName":"dtype","DisplayFields":"fullname","DataField":"dtypeid","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false},{"ColumnName":"$allsettlement$btypeid","TypeName":"allsettlement","DisplayFields":"usercode,fullname","DataField":"btypeid","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false},{"ColumnName":"$btype$dealbtypeid","TypeName":"btype","DisplayFields":"usercode,fullname","DataField":"dealbtypeid","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false},{"ColumnName":"$etype$etypeid","TypeName":"etype","DisplayFields":"fullname","DataField":"etypeid","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false},{"ColumnName":"$ktype$ktypeid","TypeName":"ktype","DisplayFields":"fullname","DataField":"ktypeid","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false},{"ColumnName":"$cargotype$cargoid","TypeName":"cargotype","DisplayFields":"fullname","DataField":"cargoid","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false},{"ColumnName":"$ptype$ptypeid","TypeName":"ptype","DisplayFields":"usercode,fullname,entrycode","DataField":"ptypeid","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false}],"defaultOrderField":null,"isDistributing":false,"distributingTypeName":"","ExpressionColumnInfo":{},"State":null}},"__FormGuid":"5e1a816e-de87-48b9-ab7d-e02607171c78","__Tag":null,"__Caches":{"__CorrelativeActionConfig":0,"__SkinConfig":0,"__ReportLimitData":0,"__CustomReportConfig":0,"__BusinessData":0,"__SelfDataType":0,"limit":0,"userconfig":69,"pricetrackconfig":0,"sysdata":268,"sysdata1":130,"userinfo":0,"digitconfig":65}}}'
    data1 = json.loads(data1)
    r = session.post(carpaHost + url1, json=data1)
    print(r.text)
    data1 = '{"pagerId":"$2$saleStatDetailSource","queryParams":{"startDate":"2024-04-01","endDate":"2024-06-30","ptypecategoryid":"","ptypeid":"","btypeid":"","dealbtypeid":"","etypeid":"","ktypeid":"0000200007","dtypeid":"","billType":"11","billTypeName":"销售出库单","explain":"","comment":"","chkDiscountQuery":"0","chkPe":0,"chkDx":"0","chkPf":"0","pfullname":"","kfullname":"九号整车总仓","atypeid":"","etypeid1":"","ptypeproperty":0,"flag":"0","bTypeLx":null,"sfullname":"默认分支机构","stypeid":"00001","inputType":"B","parid":"000010005100009","chkXs":"0","chkPt":"0","chkRed":0,"delView":0,"isshowservice":false,"intPageNo":"1","intPageSize":50,"chvOperatorID":"000010000700012","chrFlag":"2","unitconvert":3,"startdate":"2024-04-01","enddate":"2024-06-30","nbillType":"11,45,305,141,160,215","sortfield":"","checkCode":"","checkName":"","priceMode":"0","brandtypeid":"","PageNo":1,"IsShowAll":false,"IsShowReconciliation":true},"orders":null,"filter":null,"first":0,"count":9999,"isFirst":true}'
    url1 = '/jxcTOP/Carpa.Web/Carpa.Web.Script.DataService.ajax/GetPagerDataEx '
    data1 = json.loads(data1)
    data1['queryParams']['startdate'] = startdate
    data1['queryParams']['enddate'] = enddate
    data1['queryParams']['parid'] = parid
    r = session.post(carpaHost + url1, json=data1)
    r = re.sub(r'new Date\(\d+\)', dashrepl, r.text)
    r = json.loads(r)
    return rows2dict(r['itemList']['fields'], r['itemList']['rows'])

def get_day_report(session,startdate,enddate):
    data = '{"formId":"2","clientInfo":{"BillIndexDayReportCxDataSource":{"ConfigGUID":"87cd39f8_grid_0","PageSize":999999,"ShowAll":false},"__ConfigGUID":"87cd39f8_0","__Params":{"stypeid":"00001","sfullname":"默认分支机构","billtype":"-1","billTypeName":"所有单据类型","kfullname":"九号整车总仓","showstockstop":false,"startdate":"2024-06-01","enddate":"2024-07-02","ptypecategoryid":"","ptypeid":"","dealbtypeid":"","etypeid":"","ktypeid":"0000200007","posid":"","yh":false,"dx":"0","flag":0},"__Grids":["87cd39f8_grid_0"],"__GridInfos":{"87cd39f8_grid_0":{"PermitGroupName":["etype","stype","btype","ktype","etype","ptype","posinfo","etype",null],"NumberTypeNames":{"numberFields":{"qty":"qty","discount":"discount","nsaleprice":"price","nsaletotal":"total","nprice":"price","ntotal":"total","tax":"tax","ntaxprice":"price","ntaxtotal":"total","ncostprice":"price","ncosttotal":"total","yh":"total","nmaoli":"total"},"numberColumnTypeNames":["qty","discount","price","total","tax"]},"BaseInfoColumns":[{"ColumnName":"$etype$sysdiy33_head","TypeName":"etype","DisplayFields":"fullname","DataField":"sysdiy33_head","RootLayerIdLength":0,"DisplayCaptions":"表头自定义33","DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":true,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":true,"SaveInitConfig":true,"IsDiyCol":true},{"ColumnName":"$stype$stypeid","TypeName":"stype","DisplayFields":"fullname","DataField":"stypeid","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false},{"ColumnName":"$btype$bname","TypeName":"btype","DisplayFields":"usercode,fullname","DataField":"bname","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false},{"ColumnName":"$ktype$kname","TypeName":"ktype","DisplayFields":"fullname","DataField":"kname","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false},{"ColumnName":"$etype$ename","TypeName":"etype","DisplayFields":"fullname","DataField":"ename","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false},{"ColumnName":"$ptype$pname","TypeName":"ptype","DisplayFields":"fullname","DataField":"pname","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false},{"ColumnName":"$posinfo$posid","TypeName":"posinfo","DisplayFields":"usercode,fullname","DataField":"posid","RootLayerIdLength":0,"DisplayCaptions":null,"DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false},{"ColumnName":"$etype$checke","TypeName":"etype","DisplayFields":"fullname","DataField":"checke","RootLayerIdLength":0,"DisplayCaptions":"制单人","DisableFields":null,"IsVisible":false,"DesignVisible":false,"DisplayIndex":0,"Index":0,"IsReadOnly":false,"IsEnabled":false,"AllowExpand":null,"AllowHide":false,"AllowAddColumn":false,"OnlyExpandVisible":null,"SaveInitVisible":false,"SaveInitConfig":false,"IsDiyCol":false}],"defaultOrderField":null,"isDistributing":false,"distributingTypeName":"","ExpressionColumnInfo":{},"State":null}},"__FormGuid":"8a1f7089-9b25-45c0-9e70-cc861f5d3594","__Tag":null,"__Caches":{"__CorrelativeActionConfig":0,"__SkinConfig":0,"__ReportLimitData":0,"__CustomReportConfig":0,"__BusinessData":0,"__SelfDataType":0,"limit":5,"userconfig":24,"pricetrackconfig":0,"sysdata":159,"sysdata1":121,"userinfo":22,"digitconfig":58}}}'
    url = '/jxcTOP/CarpaServer/CarpaServer.Vch.BillIndexDayReportCxService.ajax/_GetServerContextData '
    data = json.loads(data)
    data['clientInfo']['BillIndexDayReportCxDataSource']['PageSize'] = 9999
    data['clientInfo']['__Params']['startdate'] = startdate
    data['clientInfo']['__Params']['enddate'] = enddate
    r = session.post(carpaHost + url, json=data)
    r = re.sub(r"new Date\(.*?\)", dashrepl, r.text)
    # print(r)
    r = json.loads(r)
    rows = r['BillIndexDayReportCxDataSource']['FirstPageData']['rows']
    fields = r['BillIndexDayReportCxDataSource']['FirstPageData']['fields']
    _ = rows2dict(fields,rows)
    return _

if __name__ == '__main__':
    s = getCarparSession()
    path = '../data/'
    startdate = '2024-07-01'
    enddate = '2024-07-01'
    r = get_one_ddc_detail(s,startdate,enddate,'000100000900002')
    # r = get_ddc_summary(s,startdate,enddate)
    # r = get_day_report(s,startdate,enddate)
    # print(r)
    # df = pd.DataFrame(r)
    # df.to_excel(path+'ddc_summary.xlsx')
    # r = get_all_ddc(s, startdate, enddate)
    # df = pd.DataFrame(r)
    # df.to_excel(path+'all_ddc.xlsx')
    # print(r)
    p = '000010005100038'
    # get_customer_summary(s,startdate,enddate)
    # r = get_customer_summary(s,startdate,enddate)
    print(r)

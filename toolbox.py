import datetime


def get_day_num(d1,d2):
    date1 = datetime.datetime.strptime(d1, "%Y-%m-%d").date()  ##datetime.date(2018, 1, 6)
    date2 = datetime.datetime.strptime(d2, "%Y-%m-%d").date()  ##datetime.date(2018, 1, 9)
    Days = (date2 - date1).days
    return Days

def get_before_date(d1):
    time = d1.split('-')
    year = int(time[0])
    month = int(time[1]) - 1
    day = int(time[2])
    if month == 1:
        month = 12
        year -= 1

    time = datetime.datetime(year=year, month=month, day=day)
    return time.strftime("%Y-%m-%d")

if __name__ == '__main__':
    print(get_before_date('2024-07-011'))

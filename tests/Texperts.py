import sys
import inspect

sys.path.insert(0, '/home/olivier/Documents/PFE/is-odutfoy/src')

import experts

def Tmonth_to_number():
    assert experts.month_to_number('JAN') == 1
    assert experts.month_to_number('DEC') == 12

def Tnumber_to_month():
    assert experts.number_to_month(1) == 'JAN'
    assert experts.number_to_month(12) == 'DEC'

def Tdate_to_string():
    assert experts.date_to_string(2012, 2, 22) == 'FEB 22, 2012'
    assert experts.date_to_string(2013, 10, 15) == 'OCT 15, 2013'

def Tdate_before():
    assert experts.date_before('FEB 10, 2015', 'FEB 10, 2015')

    assert experts.date_before('FEB 10, 2015', 'FEB 11, 2015')
    assert not experts.date_before('FEB 11, 2015', 'FEB 10, 2015')

    assert experts.date_before('FEB 10, 2015', 'FEB 10, 2016')
    assert not experts.date_before('FEB 10, 2016', 'FEB 10, 2015')

    assert experts.date_before('JAN 10, 2015', 'FEB 10, 2015')
    assert not experts.date_before('FEB 10, 2016', 'JAN 10, 2015')

def Tdate_in():
    assert experts.date_in('FEB 10, 2015', 'FEB 10, 2015', 'FEB 10, 2015')
    assert experts.date_in('FEB 10, 2015', 'FEB 09, 2015', 'FEB 10, 2015')
    assert experts.date_in('FEB 10, 2015', 'FEB 10, 2015', 'FEB 11, 2015')

    assert experts.date_in('FEB 11, 2015', 'FEB 10, 2015', 'FEB 12, 2015')
    assert not experts.date_in('FEB 09, 2015', 'FEB 10, 2015', 'FEB 12, 2015')

    assert experts.date_in('FEB 11, 2015', 'JAN 10, 2015', 'MAR 12, 2015')
    assert not experts.date_in('FEB 11, 2015', 'MAR 10, 2015', 'APR 12, 2015')

    assert experts.date_in('FEB 11, 2015', 'FEB 12, 2014', 'FEB 13, 2016')
    assert not experts.date_in('FEB 11, 2013', 'MAR 10, 2014', 'APR 12, 2015')

def Tis_leap_year():
    assert experts.is_leap_year(2000)
    assert experts.is_leap_year(2004)
    assert not experts.is_leap_year(1900)
    assert not experts.is_leap_year(2002)

def Tdate_add():
    #WARNING : FOR NOW DATE ARE REWRITTEN WITHOUT A 0 in front in case the day is < 10
    assert experts.date_add('FEB 11, 2015', 0) == 'FEB 11, 2015'
    assert experts.date_add('FEB 11, 2015', 1) == 'FEB 12, 2015'
    assert experts.date_add('FEB 27, 2015', 3) == 'MAR 02, 2015'
    assert experts.date_add('FEB 27, 2016', 3) == 'MAR 01, 2016'
    assert experts.date_add('MAR 28, 2015', 5) == 'APR 02, 2015'
    assert experts.date_add('APR 28, 2015', 5) == 'MAY 03, 2015'
    assert experts.date_add('DEC 31, 2015', 1) == 'JAN 01, 2016'


for function in inspect.getmembers(sys.modules[__name__], inspect.isfunction):
    function[1]()
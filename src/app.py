import streamlit as st
import SessionState

from datetime import date
from random import sample 

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from wealth import WealthManager

from utils import download_link, wrap_text, today

import json


def data_loader():
    uploaded_file = None

    st.subheader('Import Data')

    uploaded_file = st.file_uploader("Choose a file", type=['json'])

    if uploaded_file is not None:
        data_dict = json.load(uploaded_file)
        ss.wealth_manager.import_data(data_dict)
        st.success('Data Loaded')
        st.button('OK')


ss = SessionState.get(wealth_manager=None, max_char_slider=False, max_char=30)
try:
    st.set_option('deprecation.showPyplotGlobalUse', False)
except Exception:
    pass

st.title('Wealth Management Dashboard')

if ss.wealth_manager is None:
    ss.wealth_manager = WealthManager()

action = st.selectbox('Choose an action', ('Home',
                                           'Funds details',
                                           'Create new fund',
                                           'Deposit',
                                           'Withdraw',
                                           'Update Current Value',
                                           'Edit Fund Information',
                                           'Import/Export Data'))

if action == 'Home':
    st.header('Home')

    cur_val_list = []
    total_investment_list = []
    profit_list = []
    platform_list = []
    maturity_list = []

    fund_list = ss.wealth_manager.get_funds_name_list(exclude_sold=True)

    if len(fund_list) == 0:
        st.write('No funds have been added yet, please add new funds or load data')

        data_loader()
    else:
        for fund_name in fund_list:
            cur_val_list.append(ss.wealth_manager.get_fund_cur_val(fund_name))
            total_investment_list.append(ss.wealth_manager.get_fund_total_investment(fund_name))
            profit_list.append(ss.wealth_manager.get_fund_profit(fund_name))
            maturity_list.append(ss.wealth_manager.get_fund_maturity(fund_name))

        home_df = {'Fund Name': fund_list,
                   'Current Value': cur_val_list,
                   'Total Investment': total_investment_list,
                   'Profit': profit_list}

        home_df = pd.DataFrame(home_df)

        processed_fund_names = []

        if st.button('Adjust Character Width'):
            ss.max_char_slider = ~ ss.max_char_slider

        if ss.max_char_slider:
            max_char = st.slider('Character Width', min_value=1, max_value=100, value=ss.max_char)
            ss.max_char = max_char
        else:
            max_char = ss.max_char

        for fund_name in fund_list:
            processed_text = wrap_text(fund_name, max_char)
            processed_fund_names.append(processed_text)

        # Display Piechart
        fig1 = plt.figure(figsize=(12,10))
        ax = fig1.gca()
        ax.pie(x=cur_val_list, autopct='%1.1f%%', labels=processed_fund_names)
        plt.title('Distribution of funds')
        fig1.tight_layout()
        st.pyplot(fig1)

        # Display barchart fluid and fixed funds
        expanded_cur_val_list = []
        ind = [0, 1]
        for i, fund_name in enumerate(fund_list):
            cur_val = cur_val_list[i]
            if maturity_list[i] is None:
                cur_val = [cur_val, 0]
            else:
                cur_val = [0, cur_val]
            expanded_cur_val_list.append(cur_val)

        fig2 = plt.figure(figsize=(8,8))
        ax = fig2.gca()
        bottom = [0, 0]
        hatch_list = ['/', '|', '-', '+', 'x', 'o', 'O', '.', '*']
        for i, cur_val in enumerate(expanded_cur_val_list):
            hatch_pattern = sample(hatch_list, 1)[0]
            ax.bar(ind, cur_val, bottom=bottom, label=fund_list[i], hatch=hatch_pattern)
            bottom[0] += cur_val[0]
            bottom[1] += cur_val[1]
        plt.xlim((-0.5, 3.5))
        fig2.legend()
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.set_xticks(ind)
        ax.set_xticklabels(['FLuid funds', 'Fixed funds'])
        plt.ylabel('Amount ($)')
        fig2.tight_layout()

        st.pyplot(fig2)

        st.button('Refresh')

        st.write(home_df.style.format({'Current Value': '${:.2f}',
                                       'Total Investment': '${:.2f}',
                                       'Profit': '${:.2f}'}))

        total_wealth = home_df['Current Value'].sum()
        st.write(f'Total Wealth = ${"{:.2f}".format(total_wealth)}')

elif action == 'Funds details':
    st.header('Funds details')

    fund_list = ss.wealth_manager.get_funds_name_list(exclude_sold=False)
    if len(fund_list) == 0:
        st.write('No funds have been added yet, please add new funds or load data')

        data_loader()
    else:

        fund_name = st.selectbox('Choose a fund', fund_list)

        platform = ss.wealth_manager.get_fund_platform(fund_name)
        cur_val = ss.wealth_manager.get_fund_cur_val(fund_name)
        total_investment = ss.wealth_manager.get_fund_total_investment(fund_name)
        profit = ss.wealth_manager.get_fund_profit(fund_name)
        maturity = ss.wealth_manager.get_fund_maturity(fund_name)

        st.markdown(f'**Fund Name: ** {fund_name}')
        st.markdown(f'**Platform: ** {platform}')
        st.markdown(f'**Current Valuation: ** {cur_val}')
        st.markdown(f'**Total Investment: ** {total_investment}')

        if profit >= 0:
            st.markdown(f'**Profit/Loss: ** {profit}')
        else:
            st.markdown(f'**Profit/Loss: ** <span style="color:red">{profit}</span>', unsafe_allow_html=True)

        if maturity is not None:
            st.markdown(f'**Maturity: ** {maturity}')
        else:
            st.markdown(f'**Maturity: ** Non applicable')

        val_history_df = ss.wealth_manager.get_fund_history_df(fund_name)
        transact_history_df = ss.wealth_manager.get_fund_transaction_df(fund_name)

        freq = st.selectbox('Frequency', ['Day', 'Month', 'Year'])
        freq_dict = {'Day': 'D',
                     'Month': 'M',
                     'Year': 'Y'}
        freq = freq_dict[freq]

        val_history_df = val_history_df.resample(freq).bfill()
        val_history_df['Total Investment'] = total_investment

        val_history_df.plot()
        try:
            plt.ylim((0,val_history_df.Valuation.max()))
        except ValueError:
            st.error('Not enough data for the selected frequency')
        plt.ylabel('Valuation ($)')
        plt.xlabel('Time ($)')
        st.pyplot()

        st.write('Valuation History')
        st.write(val_history_df.style.format({'Valuation': '${:.2f}'}))
        st.write('Transaction History')
        st.write(transact_history_df.style.format({'Amount': '${:.2f}'}))


elif action == 'Create new fund':

    st.header('Create new fund')

    fund_name = st.text_input('Fund Name')
    remarks = st.text_input('Remarks')
    platform = st.text_input('Platform')
    initial_investment = st.number_input('Initial Investment')

    maturity_radio = st.radio('Is there a maturity date', ('Yes', 'No'))
    if maturity_radio == 'Yes':
        maturity = st.date_input('Maturity Date')
    else:
        maturity = None

    if st.button('Create'):
        status_code = 0
        if fund_name == '':
            st.error('Fund Name cannot be empty')
            status_code = 1
        
        if remarks == '':
            remarks = None
        if platform == '':
            platform = None
        
        if status_code != 1:
            try:
                ss.wealth_manager.new_fund(fund_name,
                                           remarks,
                                           platform,
                                           initial_investment,
                                           maturity)
                st.success(f'{fund_name} have been added successfully')
            except KeyError:
                st.error(f'{fund_name} have already been taken')

elif action == 'Deposit':

    st.header('Deposit funds')

    fund_list = ss.wealth_manager.get_funds_name_list(exclude_sold=True)

    if len(fund_list) == 0:
        st.write('No funds have been added yet, please add new funds or load data')

        data_loader()
    else:

        fund_name = st.selectbox('Choose a fund', fund_list)

        transact_date = str(st.date_input('Deposit Date'))

        amount = st.number_input('Deposit Amount')

        transact_remark = st.text_input('Remarks')

        if st.button('Deposit'):
            ss.wealth_manager.fund_transact(fund_name,
                                            amount,
                                            transact_date,
                                            transact_remark=transact_remark)
            st.success(f'${amount} deposit into {fund_name}')

elif action == 'Withdraw':

    st.header('Withdraw funds')

    fund_list = ss.wealth_manager.get_funds_name_list(exclude_sold=True)

    if len(fund_list) == 0:
        st.write('No funds have been added yet, please add new funds or load data')

        data_loader()
    else:

        fund_name = st.selectbox('Choose a fund', fund_list)

        transact_date = str(st.date_input('Withdrawal Date'))

        amount = -st.number_input('Withdrawal Amount')
        transact_remark = st.text_input('Remarks')

        if st.button('Withdraw'):
            ss.wealth_manager.fund_transact(fund_name,
                                            amount,
                                            transact_date,
                                            transact_remark=transact_remark)

            st.success(f'${amount} withdraw from {fund_name}')

        if st.button('Sell all units'):
            ss.wealth_manager.fund_transact(fund_name,
                                            amount,
                                            transact_date,
                                            transact_remark=transact_remark,
                                            sold=True)

            st.success(f'{fund_name} sold!')

elif action == 'Update Current Value':

    st.header('Update Current Valuation of funds')

    fund_list = ss.wealth_manager.get_funds_name_list(exclude_sold=True)

    if len(fund_list) == 0:
        st.write('No funds have been added yet, please add new funds or load data')

        data_loader()
    else:

        fund_name = st.selectbox('Choose a fund', fund_list)

        old_value = ss.wealth_manager.get_fund_cur_val(fund_name)

        cur_value = st.number_input('Current valuation', value=old_value)

        if st.button('Update'):

            ss.wealth_manager.fund_update_cur_val(fund_name,
                                                  cur_value)
            st.success(f'Current valuation for {fund_name} updated')

elif action == 'Edit Fund Information':

    st.header('Edit Fund Information')

    fund_list = ss.wealth_manager.get_funds_name_list(exclude_sold=False)

    if len(fund_list) == 0:
        st.write('No funds have been added yet, please add new funds or load data')

        data_loader()
    else:

        fund_name = st.selectbox('Choose a fund', fund_list)

        fund_remarks = ss.wealth_manager.get_fund_remarks(fund_name)
        fund_platform = ss.wealth_manager.get_fund_platform(fund_name)
        fund_maturity = ss.wealth_manager.get_fund_maturity(fund_name)

        remarks = st.text_input('Remarks', value=fund_remarks)
        platform = st.text_input('Platform', value=fund_platform)

        if fund_maturity is None:
            maturity_radio = st.radio('Is there a maturity date', ('Yes', 'No'), 1)
        else:
            maturity_radio = st.radio('Is there a maturity date', ('Yes', 'No'), 0)

        if maturity_radio == 'Yes':
            if fund_maturity is None:
                maturity = st.date_input('Maturity Date')
            else:
                fund_maturity = date.fromisoformat(fund_maturity)
                maturity = st.date_input('Maturity Date', value=fund_maturity)
        else:
            maturity = None

        if st.button('Update'):
            ss.wealth_manager.fund_edit_info(fund_name,
                                             remarks,
                                             platform,
                                             maturity)
            st.success(f'Information for {fund_name} updated')
 

elif action == 'Import/Export Data':

    st.header('Update Current Valuation of funds')

    json_export = ss.wealth_manager.export_data()

    st.subheader('Export Data')

    today_date = today()

    export_link = download_link(json_export,
                                f'wealth_manager_{today_date}.json',
                                'Download json data')

    st.markdown(export_link, unsafe_allow_html=True)

    data_loader()







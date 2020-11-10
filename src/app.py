import streamlit as st
import SessionState

from datetime import date

import pandas as pd
import matplotlib.pyplot as plt

from wealth import WealthManager

from utils import download_link, wrap_text, today


import json

ss = SessionState.get(wealth_manager=None, max_char_slider=False, max_char=30)

st.title('Wealth Management Dashboard')

if ss.wealth_manager is None:
    ss.wealth_manager = WealthManager()

action = st.selectbox('Choose an action', ('Home',
                                           'Create new funds',
                                           'Deposit',
                                           'Withdraw',
                                           'Update Current Value',
                                           'Edit Fund Information',
                                           'Import/Export Data'))

fund_list = ss.wealth_manager.get_funds_name_list()

if action == 'Home':
    st.header('Home')

    cur_val_list = []
    total_investment_list = []
    profit_list = []
    platform_list = []

    if len(fund_list) == 0:
        st.write('No funds have been added yet, please add new funds or load data')
    else:

        for fund_name in fund_list:
            platform_list.append(ss.wealth_manager.get_fund_platform(fund_name))
            cur_val_list.append(ss.wealth_manager.get_fund_cur_val(fund_name))
            total_investment_list.append(ss.wealth_manager.get_fund_total_investment(fund_name))
            profit_list.append(ss.wealth_manager.get_fund_profit(fund_name))

        home_df = {'Fund Name': fund_list,
                   'Platform': platform_list,
                   'Current Value': cur_val_list,
                   'Total Investment': total_investment_list,
                   'Profit': profit_list}

        home_df = pd.DataFrame(home_df)
        home_df[['Current Value', 'Total Investment', 'Profit']] = home_df[['Current Value', 'Total Investment', 'Profit']].astype('int')

        processed_fund_names = [fund_name if len(fund_name) < 30 else fund_name.replace(' ', '\n') for fund_name in fund_list]

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

        fig = plt.figure(figsize=(12,10))
        ax = fig.gca()
        ax.pie(x=cur_val_list, autopct='%1.1f%%', labels=processed_fund_names)
        fig.tight_layout()
        st.pyplot(fig)

        st.write(home_df)

        total_wealth = home_df['Current Value'].sum()
        st.write(f'Total Wealth = ${total_wealth}')

elif action == 'Create new funds':

    st.header('Create new funds')

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

    if len(fund_list) == 0:
        st.write('No funds have been added yet, please add new funds or load data')
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

    if len(fund_list) == 0:
        st.write('No funds have been added yet, please add new funds or load data')
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

elif action == 'Update Current Value':

    st.header('Update Current Valuation of funds')

    if len(fund_list) == 0:
        st.write('No funds have been added yet, please add new funds or load data')
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

    if len(fund_list) == 0:
        st.write('No funds have been added yet, please add new funds or load data')
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

    uploaded_file = None

    st.header('Update Current Valuation of funds')

    json_export = ss.wealth_manager.export_data()

    st.subheader('Export Data')

    today_date = today()

    export_link = download_link(json_export,
                                f'wealth_manager_{today_date}.json',
                                'Download json data')

    st.markdown(export_link, unsafe_allow_html=True)

    st.subheader('Import Data')

    uploaded_file = st.file_uploader("Choose a file", type=['json'])

    if uploaded_file is not None:
        data_dict = json.load(uploaded_file)
        ss.wealth_manager.import_data(data_dict)
        st.success('Data Loaded')












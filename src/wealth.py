import json
from utils import today


class WealthManager:
    def __init__(self):
        self.fund_dict = {}

    def new_fund(self, fund_name, remarks, platform, initial_investment=0.0, maturity=None):
        if fund_name in self.fund_dict.keys():
            raise KeyError('This fund name have already been used')

        new_fund = Funds(fund_name, remarks, platform, initial_investment, maturity)
        self.fund_dict[fund_name] = new_fund


    def fund_update_cur_val(self, fund_name, cur_value):
        self.fund_dict[fund_name].update_cur_val(cur_value)

    def fund_transact(self, fund_name, amount, transact_date, prev_value=None, transact_remark=None):
        self.fund_dict[fund_name].transact(amount, transact_date, prev_value, transact_remark)

    def fund_edit_info(self, fund_name, remarks, platform, maturity=None):
        self.fund_dict[fund_name].edit_info(remarks, platform, maturity)

    def export_data(self):
        output_dict = {fund_name: fund_obj.save_data()
                       for fund_name, fund_obj in self.fund_dict.items()}

        output_json = json.dumps(output_dict)

        return output_json

    def import_data(self, data_dict):

        for fund_name, fund_data_dict in data_dict.items():
            fund = Funds(fund_name)
            fund.load_data(fund_data_dict)
            self.fund_dict[fund_name] = fund

    def get_funds_name_list(self):
        funds_name_list = list(self.fund_dict.keys())
        return funds_name_list

    def get_fund_cur_val(self, fund_name):
        return self.fund_dict[fund_name].cur_val

    def get_fund_total_investment(self, fund_name):
        return self.fund_dict[fund_name].total_investment

    def get_fund_platform(self, fund_name):
        return self.fund_dict[fund_name].platform

    def get_fund_profit(self, fund_name):
        investment = self.get_fund_total_investment(fund_name)
        cur_val = self.get_fund_cur_val(fund_name)
        return cur_val - investment

    def get_fund_maturity(self, fund_name):
        return self.fund_dict[fund_name].maturity

    def get_fund_remarks(self, fund_name):
        return self.fund_dict[fund_name].remarks

class Funds:
    def __init__(self, name, remarks=None, platform=None, initial_investment=None, maturity=None):
        self.name = name
        self.remarks = remarks
        self.platform = platform
        self.total_investment = initial_investment
        self.cur_val = initial_investment

        if maturity is not None:
            maturity = str(maturity)
        self.maturity = maturity

        self.transaction = {today(): initial_investment}
        self.transaction_remark = {today(): 'Funds Created'}
        self.history = {today(): initial_investment}

    def update_cur_val(self, cur_value):
        self.history[today()] = cur_value
        self.cur_val = cur_value

    def transact(self, amount, transact_date, prev_value=None, transact_remark=None):
        if prev_value is None:
            prev_value = self.cur_val

        cur_value = prev_value + amount

        if transact_date is not None:
            transact_date = str(transact_date)

        self.transaction[transact_date] = amount
        self.transaction_remark[transact_date] = transact_remark
        self.history[transact_date] = cur_value
        self.total_investment += amount
        self.cur_val = cur_value

    def edit_info(self, remarks, platform, maturity):
        self.remarks = remarks
        self.platform = platform
        if maturity is not None:
            maturity = str(maturity)
        self.maturity = maturity

    def save_data(self):
        output_dict = {'name': self.name,
                       'remarks': self.remarks,
                       'platform': self.platform,
                       'total_investment': self.total_investment,
                       'cur_val': self.cur_val,
                       'maturity': self.maturity,
                       'transaction': self.transaction,
                       'history': self.history}
        return output_dict

    def load_data(self, fund_data_dict):
        self.remarks = fund_data_dict['remarks']
        self.platform = fund_data_dict['platform']
        self.total_investment = fund_data_dict['total_investment']
        self.cur_val = fund_data_dict['cur_val']
        self.maturity = fund_data_dict['maturity']
        self.transaction = fund_data_dict['transaction']
        self.history = fund_data_dict['history']







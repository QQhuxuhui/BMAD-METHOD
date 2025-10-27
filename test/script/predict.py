# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import time
import os
from datetime import timedelta
import collections
import random
import torch
import torch.nn as nn
import torch.nn.functional as F
import statistics

DAY_TOTAL_SECONDS = 24 * 60 * 60


class ReplayBuffer:
    def __init__(self, buffer_limit=997 * 10):
        self.buffer = collections.deque(maxlen=buffer_limit)

    def put(self, transition):
        self.buffer.append(transition)

    def sample(self, n):
        mini_batch = random.sample(self.buffer, n)
        s_lst, a_lst, r_lst, s_prime_lst, done_mask_lst = [], [], [], [], []

        for transition in mini_batch:
            s, a, r, s_prime, done_mask = transition
            s_lst.append(s)
            a_lst.append([a])
            r_lst.append([r])
            s_prime_lst.append(s_prime)
            done_mask_lst.append([done_mask])
        return torch.tensor(s_lst, dtype=torch.float), torch.tensor(a_lst), \
            torch.tensor(r_lst), torch.tensor(s_prime_lst, dtype=torch.float), \
            torch.tensor(done_mask_lst)

    def size(self):
        return len(self.buffer)


class Qnet(nn.Module):
    def __init__(self, n_action=16):
        super(Qnet, self).__init__()
        self.fc1 = nn.Linear(15, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, n_action)

    def forward(self, x):
        x = F.tanh(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

    def sample_action(self, obs, epsilon=0):
        out = self.forward(obs)
        coin = random.random()
        if coin < epsilon:
            return random.randint(0, 8)
        else:
            return out.argmax().item()


def masked_argmin(x, condition):
    valid_idx = np.where(condition)[0]
    return valid_idx[x[valid_idx].argmin()]


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = False
    torch.backends.cudnn.enabled = False


class DataLoader:
    def __init__(self, folder):
        self.folder = folder
        self.all_equipment_number, self.switching_time_dict = self.get_switching_time_dict()
        self.planning_start_date, self.planning_start_time, self.equipment_dict, self.working_calendar_summary = self.get_working_calendar()
        self.process_route = self.get_process_route()
        self.product_demand, self.processing_time = self.get_product_demand()
        self.total_order_num = self.product_demand['订单号'].nunique()
        self.available_equipment_number = self.product_demand['可用设备'].values
        self.work_order_equipment = self.product_demand['工单设备'].values
        self.work_order_weight = self.product_demand['权重'].values
        self.order_start_index = self.product_demand['开始索引'].values
        self.order_current_index = self.product_demand['当前索引'].values + 1
        self.demanded_date = self.product_demand['需求日期'].values
        self.order_number = self.product_demand['订单号'].values
        self.work_order_number = self.product_demand['工单号'].values
        self.operation_number = self.product_demand['工序号'].values
        self.product_number = self.product_demand['产品号'].values
        self.material_number = self.product_demand['瓶颈物料号'].values
        self.quantity_demanded = self.product_demand['需求量'].values
        self.mean_process_time = self.product_demand['加工时长'].values
        self.remain_mean_process_time = self.product_demand['剩余加工时长'].values
        self.max_demanded_date = np.zeros(len(self.product_demand), dtype=int)
        self.min_demanded_date = np.zeros(len(self.product_demand), dtype=int)
        self.job_total_process_time = self.product_demand['总加工时长'].values
        for work_order_id, equipment_numbers in enumerate(self.available_equipment_number):
            df_demand_date = self.working_calendar_summary[self.working_calendar_summary['生产日期'] == self.demanded_date[work_order_id]]
            df_demand_date = df_demand_date[df_demand_date['设备号'].isin(equipment_numbers)]
            self.max_demanded_date[work_order_id] = np.max(df_demand_date['交期换算时刻'])
            self.min_demanded_date[work_order_id] = np.min(df_demand_date['交期换算时刻'])

    def get_switching_time_dict(self):
        df_switching_time = pd.read_csv(os.path.join(self.folder, '切换时间.csv'), dtype={'设备号': str, '前产品': str, '后产品': str, '切换时间（分钟）': int})
        all_equipment_number = list(df_switching_time['设备号'].unique())
        switching_time_dict = {equipment_number: {} for equipment_number in all_equipment_number}
        for idx, (equipment_number, pre_product, after_product, duration) in df_switching_time.iterrows():
            switching_time_dict[equipment_number][pre_product, after_product] = duration * 60
            switching_time_dict[equipment_number][pre_product, pre_product] = 0
            switching_time_dict[equipment_number][after_product, after_product] = 0
            switching_time_dict[equipment_number]['', pre_product] = 0
            switching_time_dict[equipment_number]['', after_product] = 0
        return all_equipment_number, switching_time_dict

    def get_working_calendar(self):
        working_calendar = pd.read_csv(os.path.join(self.folder, '工作日历.csv'), dtype={'设备号': str, '班次': str})
        for col in ['开始时间', '结束时间']:
            working_calendar[col] = pd.to_datetime(working_calendar[col])
        planning_start_date = pd.to_datetime(working_calendar['开始时间'].dt.date.min())
        planning_end_date = pd.to_datetime(working_calendar['开始时间'].dt.date.max())
        planning_start_time = pd.to_datetime(working_calendar['开始时间'].min())
        working_calendar['生产日期'] = working_calendar['结束时间'].dt.strftime('%Y-%m-%d')
        working_calendar['开始时间'] = (working_calendar['开始时间'] - planning_start_time).dt.total_seconds().astype(int)
        working_calendar['结束时间'] = (working_calendar['结束时间'] - planning_start_time).dt.total_seconds().astype(int)
        working_calendar['排名'] = working_calendar.groupby(['设备号', '生产日期'])['开始时间'].transform('rank').values

        working_calendar = working_calendar.sort_values(by=['设备号', '开始时间', '结束时间']).reset_index(drop=True)
        equipment_dict = {equipment_number: {} for equipment_number in self.all_equipment_number}
        for equipment_number, g in working_calendar.groupby('设备号'):
            start_time = g['开始时间'].values
            end_time = g['结束时间'].values
            duration_time = end_time - start_time
            equipment_dict[equipment_number] = {'开始时间': start_time,
                                                '结束时间': end_time,
                                                '结束日期': (end_time / 24 / 60 / 60 + 8 / 24).astype(int),
                                                '持续时间': duration_time,
                                                '排名': g['排名'].values,
                                                }
        working_calendar_summary = pd.pivot_table(working_calendar, index=['生产日期'], columns=['设备号'], values='结束时间', aggfunc='max')
        for x in pd.date_range(planning_start_date, planning_end_date, freq='D'):
            if x.strftime('%Y-%m-%d') not in working_calendar_summary.index:
                working_calendar_summary.loc[x.strftime('%Y-%m-%d')] = [np.nan] * len(self.all_equipment_number)
        working_calendar_summary = working_calendar_summary.sort_values(by='生产日期')
        working_calendar_summary = working_calendar_summary.ffill().fillna(0).astype(int).reset_index()
        working_calendar_summary = pd.melt(working_calendar_summary, id_vars=['生产日期'], value_name='交期换算时刻', var_name='设备号')
        return planning_start_date, planning_start_time, equipment_dict, working_calendar_summary

    def get_process_route(self):
        process_route = pd.read_csv(os.path.join(self.folder, '工艺路线.csv'), dtype={'工艺路线类型': str, '工序号': int, '设备号': str, '每个产品单位加工时间（秒）': int})
        process_route = pd.pivot_table(process_route, index=['工艺路线类型', '工序号'], columns=['设备号'], values='每个产品单位加工时间（秒）', aggfunc='max', fill_value=0)
        process_route['可用设备'] = process_route[self.all_equipment_number].apply(lambda row: row[row > 0].index.tolist(), axis=1).tolist()
        process_route['工单设备'] = process_route[self.all_equipment_number].apply(lambda row: row[row != 0].idxmin() if (row != 0).any() else None, axis=1).tolist()
        process_route['加工时长'] = process_route[self.all_equipment_number].apply(lambda row: np.mean(row[row > 0]), axis=1).values
        return process_route

    def get_product_demand(self):
        product_demand = pd.read_csv(os.path.join(self.folder, '产品需求.csv'),
                                     parse_dates=['需求日期'],
                                     dtype={'需求量': int, '订单号': str, '工单号': str, '工序号': int, '产品号': str, '工艺路线类型': str, '瓶颈物料号': str})
        product_demand['瓶颈物料号'] = product_demand['瓶颈物料号'].fillna('')
        product_demand['需求日期'] = product_demand['需求日期'].dt.strftime('%Y-%m-%d')
        product_demand = product_demand.merge(self.process_route, how='left', left_on=['工艺路线类型', '工序号'], right_on=['工艺路线类型', '工序号'])
        for equipment_number in self.equipment_dict:
            product_demand[equipment_number] = product_demand[equipment_number] * product_demand['需求量']
        product_demand = product_demand.sort_values(by=['需求日期', '订单号', '工单号']).reset_index(drop=True)
        product_demand['权重'] = 1 / product_demand.groupby(['订单号'])['工序号'].transform('count').values
        product_demand['到达日期'] = np.where(product_demand['工序号'] > 1, 99 * DAY_TOTAL_SECONDS, 0).astype(int)
        product_demand['加工时长'] = product_demand['加工时长'] * product_demand['需求量']
        order_process_time = product_demand.groupby(['订单号'])['加工时长'].transform('sum').values
        order_cum_process_time = product_demand.groupby(['订单号'])['加工时长'].transform('cumsum').values
        product_demand['剩余加工时长'] = order_process_time - order_cum_process_time
        product_demand['总加工时长'] = order_process_time
        product_demand = product_demand.sort_values(by=['需求日期', '总加工时长', '权重', '产品号', '订单号', '工单号'], ascending=[True, False, False, True, True, True]).reset_index(drop=True)
        product_demand['当前索引'] = product_demand.index.values
        product_demand['开始索引'] = product_demand.groupby(['订单号'])['当前索引'].transform('min').values
        product_demand['订单是否完成'] = np.where(product_demand.index.values == product_demand.groupby(['订单号'])['当前索引'].transform('max').values, 1, 0)
        product_demand['日内最长总加工时长'] = product_demand.groupby('需求日期')['总加工时长'].transform('max').values
        product_demand['组内最长总加工时长'] = product_demand.groupby('工艺路线类型')['总加工时长'].transform('max').values
        # demand_date = np.sort(product_demand['需求日期'].unique())
        product_demand['建议后生产1'] = np.where(product_demand['总加工时长'].isin(np.sort(product_demand['总加工时长'].unique())[-8:]), 1, 0)
        product_demand['建议后生产2'] = np.where(product_demand['总加工时长'] == product_demand['组内最长总加工时长'], 1, 0)
        return product_demand, product_demand[self.all_equipment_number].values


class FJSP(DataLoader):
    def __init__(self, folder):
        super().__init__(folder)
        # 初始化总体参数
        self.material_limit = {}
        self.upkeep = set()
        self.upkeep_log = []
        self.order_logs = set()
        self.process_logs = []
        self.total_processing_time = 0
        self.total_switching_time = 0
        self.A1, self.A2, self.A3 = 0, 1, 1
        # 初始化设备参数
        for equipment_number in self.all_equipment_number:
            self.equipment_dict[equipment_number]['时段唯一工单'] = set()
            self.equipment_dict[equipment_number]['保养模式'] = []
            self.equipment_dict[equipment_number]['需要保养'] = np.where(self.equipment_dict[equipment_number]['排名'] == 1, 1, 0)
        self.equipment_pre_product = {equipment_number: '' for equipment_number in self.all_equipment_number}
        self.equipment_first_time = np.array([self.equipment_dict[equipment_number]['开始时间'].min() for equipment_number in self.all_equipment_number], dtype=int)
        self.equipment_last_time = np.array([self.equipment_dict[equipment_number]['开始时间'].min() for equipment_number in self.all_equipment_number], dtype=int)
        self.equipment_start_time = {equipment_number: 0 for equipment_number in self.all_equipment_number}
        self.equipment_first_time_max = 0
        for equipment_number in self.all_equipment_number:
            self.equipment_start_time[equipment_number] = int(self.equipment_dict[equipment_number]['开始时间'].min())
        # 初始化任务参数
        self.order_done = np.zeros(len(self.product_demand), dtype=int)
        self.order_is_on_time = np.zeros(len(self.product_demand), dtype=int)
        self.work_order_done = np.ones(len(self.product_demand), dtype=int)
        self.work_order_arrive_time = np.zeros(len(self.product_demand), dtype=int)
        self.work_order_start_time = np.zeros(len(self.product_demand), dtype=int)
        self.work_order_switching_time = np.zeros(len(self.product_demand), dtype=int)
        self.work_order_end_time = np.zeros(len(self.product_demand), dtype=int)
        self.work_order_end_day = np.zeros(len(self.product_demand), dtype=int)
        self.work_order_delta_a3 = np.zeros(len(self.product_demand), dtype=int)
        self.upkeep_flag = np.zeros(len(self.product_demand), dtype=int)
        self.state = None

    # 执行任务时 选择不会影响维保的 或者 执行前插入维保单
    def reset(self):
        # 初始化总体参数
        self.material_limit = self.update_material_limit()
        self.order_logs = set()
        self.upkeep = set()
        self.upkeep_log = []
        self.process_logs = []
        self.total_processing_time = 0
        self.total_switching_time = 0
        self.A1, self.A2, self.A3 = 0, 1, 1
        # 更新设备参数
        for equipment_number in self.all_equipment_number:
            self.equipment_dict[equipment_number]['时段唯一工单'] = set()
            self.equipment_dict[equipment_number]['保养模式'] = 0
            self.equipment_dict[equipment_number]['需要保养'] = np.where(self.equipment_dict[equipment_number]['排名'] == 1, 1, 0)
        self.equipment_pre_product = {equipment_number: '' for equipment_number in self.all_equipment_number}
        self.equipment_first_time = np.array([self.equipment_dict[equipment_number]['开始时间'].max() for equipment_number in self.all_equipment_number], dtype=int)
        self.equipment_last_time = np.array([self.equipment_dict[equipment_number]['开始时间'].min() for equipment_number in self.all_equipment_number], dtype=int)
        self.equipment_first_time_max = np.max(self.equipment_last_time)
        for equipment_number in self.all_equipment_number:
            self.equipment_start_time[equipment_number] = int(self.equipment_dict[equipment_number]['开始时间'].min())
        # 更新任务参数
        self.order_done = self.product_demand['订单是否完成'].values.astype(int)
        self.order_is_on_time = np.zeros(len(self.product_demand), dtype=int)
        self.work_order_arrive_time = np.where(self.product_demand['建议后生产1'] == 1,
                                               int((pd.to_datetime('2025-06-16') - self.planning_start_time).total_seconds()),
                                               self.product_demand['到达日期'].values)
        self.work_order_arrive_time = np.where(self.product_demand['建议后生产2'] == 1,
                                               int((pd.to_datetime('2025-06-29') - self.planning_start_time).total_seconds()),
                                               self.work_order_arrive_time)
        self.work_order_done = np.where(self.operation_number == 1, 0, 1)
        self.work_order_start_time = np.zeros(len(self.product_demand), dtype=int)
        self.work_order_switching_time = np.zeros(len(self.product_demand), dtype=int)
        self.work_order_end_time = np.zeros(len(self.product_demand), dtype=int)
        self.work_order_end_day = np.zeros(len(self.product_demand), dtype=int)
        self.work_order_delta_a3 = np.zeros(len(self.product_demand), dtype=int)
        self.upkeep_flag = np.zeros(len(self.product_demand), dtype=int)
        # 更新任务的可开始时间
        for work_order_id in np.where(self.work_order_done == 0)[0]:
            self.update_work_order(work_order_id)
        self.get_state()
        return self.state

    def update_material_limit(self):
        bottleneck_material = pd.read_csv(os.path.join(self.folder, '瓶颈物料.csv'), parse_dates=['供应日期'], dtype={'物料号': str, '供应数量': int})
        bottleneck_material['供应日期'] = (bottleneck_material['供应日期'] - self.planning_start_date).dt.days
        material_limit = {material_number: np.zeros(bottleneck_material['供应日期'].max() + 1, dtype=int) for material_number in bottleneck_material['物料号'].unique()}
        bottleneck_material = bottleneck_material.groupby(['物料号', '供应日期'], as_index=False)['供应数量'].sum()
        for idx, (material_number, supply_day, supply_quantity) in bottleneck_material.iterrows():
            material_limit[material_number][supply_day] = int(supply_quantity)
        material_limit[''] = np.zeros(bottleneck_material['供应日期'].max() + 1, dtype=int) + np.sum(self.quantity_demanded)
        return material_limit

    def get_state(self):
        time_condition = self.work_order_done == 0
        # 表示系统中工件数量与总工件数 量之比
        f1 = len(self.order_logs) / self.total_order_num
        # 表示设备利用率
        f2 = self.total_processing_time / np.max(self.equipment_last_time) / 5
        # 表示系统中候选工件最小开始加工时间归一化公式
        work_order_start_time = self.work_order_start_time[time_condition]
        f3 = np.mean(work_order_start_time) / np.max(work_order_start_time)
        f4 = np.median(work_order_start_time) / np.max(work_order_start_time)
        # 表示系统中候选工件最小剩余加工时间归一化公式
        di_t = (self.min_demanded_date[time_condition] - self.work_order_end_time[time_condition]) / self.mean_process_time[time_condition]
        if np.max(di_t):
            f5 = np.median(di_t) / np.max(di_t)
            f6 = np.mean(di_t) / np.max(di_t)
        else:
            f5 = 0
            f6 = 0
        di_t = (self.max_demanded_date[time_condition] - self.work_order_end_time[time_condition]) / self.mean_process_time[time_condition]
        if np.max(di_t):
            f7 = np.median(di_t) / np.max(di_t)
            f8 = np.mean(di_t) / np.max(di_t)
        else:
            f7 = 0
            f8 = 0
        # 表示系统内候选工件最小延迟归一化公式
        delay_time = self.min_demanded_date - (self.work_order_end_time + self.remain_mean_process_time)
        delay_time = delay_time[time_condition]
        if np.max(delay_time):
            f9 = np.min(delay_time) / np.max(delay_time)
            f10 = np.mean(delay_time) / np.max(delay_time)
        else:
            f9 = 0
            f10 = 0
        delay_time = self.max_demanded_date - (self.work_order_end_time + self.remain_mean_process_time)
        delay_time = delay_time[time_condition]
        if np.max(delay_time):
            f11 = np.min(delay_time) / np.max(delay_time)
            f12 = np.mean(delay_time) / np.max(delay_time)
        else:
            f11 = 0
            f12 = 0
        self.state = [self.A1, self.A2, self.A3, f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12]

    def update_work_order(self, work_order_id):
        work_order_arrive_time = self.work_order_arrive_time[work_order_id]
        log = []
        for equipment_number in self.available_equipment_number[work_order_id]:
            equipment_idx = self.all_equipment_number.index(equipment_number)
            processing_time = self.processing_time[work_order_id, equipment_idx]
            switching_time = self.switching_time_dict[equipment_number][self.equipment_pre_product[equipment_number], self.product_number[work_order_id]]
            total_time = processing_time + switching_time
            quantity_demanded, material_number = self.quantity_demanded[work_order_id], self.material_number[work_order_id]
            start_time = np.maximum(work_order_arrive_time, self.equipment_start_time[equipment_number])
            end_time = start_time + total_time
            upkeep_flag, upkeep_time, period_end_time, i, end_day = 0, 0, 0, -1, 0
            for period_start_time, period_end_time, end_day, flag, rank in zip(self.equipment_dict[equipment_number]['开始时间'],
                                                                               self.equipment_dict[equipment_number]['结束时间'],
                                                                               self.equipment_dict[equipment_number]['结束日期'],
                                                                               self.equipment_dict[equipment_number]['需要保养'],
                                                                               self.equipment_dict[equipment_number]['排名']):
                if self.material_limit[material_number][end_day] >= quantity_demanded:
                    if period_end_time > start_time:

                        if flag == 1:
                            upkeep_time = 1800
                            # 模式2 工单任务立即开始 保养任务后延
                            start_time_bak = np.maximum(period_start_time, start_time)
                            if period_end_time - start_time_bak - 1 >= total_time + upkeep_time:
                                start_time = start_time_bak
                                end_time = start_time_bak + total_time
                                upkeep_flag = 2
                                if period_start_time not in self.equipment_dict[equipment_number]['时段唯一工单']:
                                    if self.equipment_dict[equipment_number]['保养模式'] == 2:
                                        switching_time = 0
                                break
                            # 模式1: 保养任务立即开始 工单任务后延
                            upkeep_start_time = np.maximum(self.equipment_start_time[equipment_number], period_start_time)
                            upkeep_end_time = upkeep_start_time + upkeep_time
                            start_time_bak = np.maximum(start_time_bak, upkeep_end_time)
                            if period_end_time - start_time_bak >= total_time:
                                start_time = start_time_bak
                                end_time = start_time_bak + total_time
                                switching_time = 0
                                upkeep_flag = 1
                                break
                        else:
                            upkeep_time = 0
                            if period_start_time not in self.equipment_dict[equipment_number]['时段唯一工单']:
                                if self.equipment_dict[equipment_number]['保养模式'] == 2:
                                    switching_time = 0
                            start_time_bak = np.maximum(period_start_time, start_time)
                            if period_end_time - start_time_bak - 1 >= total_time:
                                start_time = start_time_bak
                                end_time = start_time_bak + total_time
                                upkeep_flag = 0
                                break
            # 处理左进和右进
            if (equipment_number, end_day) in self.upkeep:
                delta_a3 = (1 - (self.total_switching_time + switching_time) / ((self.total_processing_time + 1800 * len(self.upkeep) + total_time) / 2)) - self.A3
            else:
                delta_a3 = (1 - (self.total_switching_time + switching_time) / ((self.total_processing_time + 1800 * len(self.upkeep) + upkeep_time + total_time) / 2)) - self.A3
            equipment_last_time = self.equipment_last_time.copy()
            if upkeep_flag == 2:
                equipment_last_time[equipment_idx] = period_end_time - 1
            else:
                equipment_last_time[equipment_idx] = end_time
            if end_time <= self.max_demanded_date[work_order_id]:
                log.append([0, 0, start_time, end_time, switching_time, equipment_number, upkeep_flag, end_day, delta_a3])
            else:
                x = equipment_last_time - self.equipment_first_time
                delta_a2 = 1 - np.sum(np.abs(x - np.mean(x))) / (np.sum(x) / 2) - self.A2
                score = -(0.3 * delta_a2 + 0.2 * delta_a3)
                log.append([1, score, start_time, end_time, switching_time, equipment_number, upkeep_flag, end_day, delta_a3])
        a, b, start_time, end_time, switching_time, equipment_number, upkeep_flag, end_day, delta_a3 = sorted(log)[0]
        self.work_order_delta_a3[work_order_id] = delta_a3
        self.work_order_start_time[work_order_id] = start_time
        self.work_order_end_time[work_order_id] = end_time
        self.work_order_switching_time[work_order_id] = switching_time
        self.work_order_equipment[work_order_id] = equipment_number
        self.work_order_end_day[work_order_id] = end_day
        self.upkeep_flag[work_order_id] = upkeep_flag

    def step(self, action):
        s = self.state
        score = self.A1 * 50 + self.A2 * 30 + self.A3 * 20
        time_condition = self.work_order_done == 0
        work_order_first_time = np.min(self.work_order_start_time[time_condition])
        condition = (self.work_order_start_time == work_order_first_time) & time_condition
        condition_crx = (self.work_order_end_time + self.remain_mean_process_time <= self.max_demanded_date) & condition
        y = np.maximum(self.work_order_end_time - self.work_order_start_time + self.total_processing_time, 1)
        delta_a3 = self.A3 - (1 - (self.total_switching_time + self.work_order_switching_time) / (y * 2))

        if np.sum(condition_crx):
            if action == 0:
                work_order_id = masked_argmin(self.max_demanded_date + delta_a3, condition_crx)
            elif action == 1:
                if len(self.process_logs) <= len(self.all_equipment_number):
                    work_order_id = masked_argmin(self.max_demanded_date + self.work_order_weight, condition_crx)
                else:
                    work_order_id = masked_argmin(self.max_demanded_date + delta_a3, condition_crx)
            elif action == 2:
                work_order_id = masked_argmin(self.max_demanded_date + delta_a3 + self.work_order_weight, condition_crx)
            elif action == 3:
                work_order_id = masked_argmin(self.max_demanded_date + self.work_order_weight * (0.01 + self.work_order_switching_time), condition_crx)
            elif action == 4:
                work_order_id = masked_argmin(self.max_demanded_date + self.work_order_switching_time / y, condition_crx)
            elif action == 5:
                work_order_id = masked_argmin(self.max_demanded_date + self.work_order_switching_time + delta_a3, condition_crx)
            elif action == 6:
                work_order_id = masked_argmin(self.max_demanded_date + (1 + self.work_order_switching_time) / (self.total_processing_time + 1), condition_crx)
            else:
                work_order_id = masked_argmin(self.max_demanded_date + self.work_order_weight * self.work_order_switching_time, condition_crx)
        else:
            mode_machine = statistics.multimode(self.work_order_equipment[condition])
            is_mode_machine = np.where(np.isin(self.work_order_equipment, mode_machine), 0, 1)
            work_order_id = masked_argmin(delta_a3 + is_mode_machine, condition)
        order_number = self.order_number[work_order_id]
        equipment_number = self.work_order_equipment[work_order_id]
        start_time = self.work_order_start_time[work_order_id]
        end_time = self.work_order_end_time[work_order_id]
        switching_time = self.work_order_switching_time[work_order_id]
        product_number = self.product_number[work_order_id]
        equipment_idx = self.all_equipment_number.index(equipment_number)
        upkeep_flag = self.upkeep_flag[work_order_id]
        for period_start_time, period_end_time in zip(self.equipment_dict[equipment_number]['开始时间'], self.equipment_dict[equipment_number]['结束时间']):
            if period_start_time <= start_time:
                if period_end_time >= end_time:
                    self.equipment_dict[equipment_number]['时段唯一工单'].add(period_start_time)
                    self.equipment_dict[equipment_number]['保养模式'] = upkeep_flag
                    if upkeep_flag == 1:
                        self.upkeep_log.append([equipment_number, equipment_number + "-1", 1, equipment_number, '8888', start_time - 1800, start_time])
                        self.equipment_first_time[equipment_idx] = np.minimum(self.equipment_first_time[equipment_idx], start_time - 1800)
                        break
                    if upkeep_flag == 2:
                        self.upkeep_log.append([equipment_number, equipment_number + "-1", 1, equipment_number, '8888', period_end_time - 1801, period_end_time - 1])
                        break
        self.work_order_done[work_order_id] = 1
        if self.order_done[work_order_id] == 0:
            if not self.order_done[work_order_id]:
                self.work_order_arrive_time[work_order_id + 1] = end_time
                self.work_order_done[work_order_id + 1] = 0
        self.order_logs.add(order_number)
        order_number, work_order_number, operation_number = self.order_number[work_order_id], self.work_order_number[work_order_id], self.operation_number[work_order_id]
        self.process_logs.append([order_number, work_order_number, operation_number, equipment_number, product_number, start_time, end_time])
        self.equipment_pre_product[equipment_number] = product_number
        self.equipment_first_time[equipment_idx] = np.minimum(start_time, self.equipment_first_time[equipment_idx])
        self.equipment_last_time[equipment_idx] = np.maximum(end_time, self.equipment_last_time[equipment_idx])
        self.total_switching_time = self.total_switching_time + switching_time
        self.total_processing_time = self.total_processing_time + (end_time - start_time)
        day = self.work_order_end_day[work_order_id]
        if upkeep_flag == 0:
            for period_start_time, period_end_time, period_end_day in zip(self.equipment_dict[equipment_number]['开始时间'], self.equipment_dict[equipment_number]['结束时间'], self.equipment_dict[equipment_number]['结束日期']):
                if day == period_end_day:
                    self.upkeep_log.append([equipment_number, equipment_number + "-1", 1, equipment_number, '8888', period_end_time - 1801, period_end_time - 1])
                    break
        self.upkeep.add((equipment_number, day))
        is_on_time = end_time <= self.max_demanded_date[work_order_id]
        self.order_is_on_time[self.order_start_index[work_order_id]:self.order_current_index[work_order_id]] = is_on_time
        self.A1 = np.sum(self.order_is_on_time[self.work_order_done == 1] * self.work_order_weight[self.work_order_done == 1]) / self.total_order_num
        if upkeep_flag == 2:
            for period_start_time, period_end_time in zip(self.equipment_dict[equipment_number]['开始时间'], self.equipment_dict[equipment_number]['结束时间']):
                if period_start_time <= start_time:
                    if period_end_time >= end_time:
                        self.equipment_last_time[equipment_idx] = period_end_time - 1
                        break
        else:
            self.equipment_last_time[equipment_idx] = end_time
        x = self.equipment_last_time - self.equipment_first_time
        self.A2 = 1 - np.sum(np.abs(x - np.mean(x))) / (np.sum(x) / 2)
        self.A3 = 1 - self.total_switching_time / (self.total_processing_time + 1800 * len(self.upkeep)) * 2
        material_number = self.material_number[work_order_id]
        self.material_limit[material_number][day] = self.material_limit[material_number][day] - self.quantity_demanded[work_order_id]
        self.equipment_start_time[equipment_number] = np.maximum(self.equipment_start_time[equipment_number], end_time)
        if not self.order_done[work_order_id]:
            self.update_work_order(work_order_id + 1)
        condition1 = (self.processing_time[:, equipment_idx] > 0) & (self.work_order_done == 0)
        condition2 = (self.material_number == material_number) & (self.work_order_done == 0)
        for work_order_id in np.where(condition1 | condition2)[0]:
            self.update_work_order(work_order_id)
        r = self.A1 * 50 + self.A2 * 30 + self.A3 * 20 - score
        if np.mean(self.work_order_done) < 1:
            self.get_state()
            return s, r, self.state, False
        else:
            return s, r, self.state, True

    def result(self, result_path):
        df_process = pd.DataFrame(self.process_logs, columns=['订单号', '工单号', '工序号', '设备号', '产品号', '开始时间', '结束时间'])
        upkeep = pd.DataFrame(self.upkeep_log, columns=['订单号', '工单号', '工序号', '设备号', '产品号', '开始时间', '结束时间'])
        result = pd.concat([df_process, upkeep])
        for col in ['开始时间', '结束时间']:
            result[col] = (result[col] * timedelta(seconds=1) + pd.to_datetime(self.planning_start_time)).dt.strftime('%Y-%m-%d %H:%M:%S')
        result = result.sort_values(by=['开始时间']).reset_index(drop=True)
        result['product_date'] = pd.to_datetime(result['开始时间']).dt.date
        result = result.drop_duplicates(subset=['订单号', '工单号', '工序号', '设备号', '产品号', 'product_date'], keep='first')
        result = result.drop(['product_date'], axis=1)
        result.to_csv(result_path, index=False, encoding='utf-8-sig')


def predict_main(raw_data_folder, prediction_result_path, model_path="./data/user_data/agent.pth"):
    t = time.time()
    q = torch.load(model_path, weights_only=False)
    env = FJSP(folder=raw_data_folder)
    env.reset()
    s = env.state
    while True:
        action = q.sample_action(torch.from_numpy(np.array(s)).float())
        s_prime, _, s, done = env.step(action=action)  # 0
        if done:
            break
    score = env.A1 * 50 + env.A2 * 30 + env.A3 * 20
    if score > 95.1:
        env.result(prediction_result_path)
        print(f"Elapsed:{time.time() - t:.2f}s, Model:{model_path}, Score:{score:.4f}, A1:{env.A1 * 100:.4f}, A2:{env.A2 * 100:.4f}, A3:{env.A3 * 100:.4f}")


if __name__ == '__main__':
    predict_main("./data/raw_data/决赛", "./data/prediction_result/result.csv", "./data/user_data/agent.pth")

"""
产线排产结果评估脚本
用于计算排产结果的各项指标并输出最终得分
"""
import pandas as pd
import numpy as np
from datetime import timedelta
from itertools import pairwise


def load_switching_data(file_path):
    """
    加载设备切换时间数据
    
    Args:
        file_path (str): 切换时间数据文件路径
        
    Returns:
        dict: 以"设备号+前产品+后产品"为键，切换时间为值的字典
    """
    switching_data = pd.read_csv(file_path, dtype={
        '设备号': str, 
        '前产品': str, 
        '后产品': str, 
        '切换时间（分钟）': int
    })
    switching = {}
    for idx, (machine, pre_product, after_product, duration) in switching_data.iterrows():
        switching[machine + pre_product + after_product] = duration * 60
    return switching


def load_process_route(file_path):
    """
    加载工艺路线数据

    Args:
        file_path (str): 切换工艺路线文件路径
        
    Returns:
        pandas.DataFrame: 工艺路线数据
    """
    process_route = pd.read_csv(file_path, dtype={
        '设备号': str,
        '工序号': int,
        '每个产品单位加工时间（秒）': int
    })
    return process_route


def load_work_calendar(file_path):
    """
    加载工作日历数据
    
    Args:
        file_path (str): 工作日历文件路径
        
    Returns:
        pandas.DataFrame: 工作日历数据
    """
    work_calendar = pd.read_csv(file_path, dtype={
        '设备号': str,
    })
    for col in ['开始时间', '结束时间']:
        work_calendar[col] = pd.to_datetime(work_calendar[col])
    return work_calendar


def load_and_process_result(file_path):
    """
    加载并初步处理排产结果数据
    
    Args:
        file_path (str): 排产结果文件路径
        
    Returns:
        pandas.DataFrame: 处理后的排产结果数据
    """
    result = pd.read_csv(file_path, dtype={
        '订单号': str,
        '工单号': str,
        '工序号': int,
        '设备号': str,
        '产品号': str
    })
    result = result.sort_values(by='开始时间').reset_index(drop=True)
    result['开始时间'] = pd.to_datetime(result['开始时间'])
    result['结束时间'] = pd.to_datetime(result['结束时间'])
    result['工作时长'] = (result['结束时间'] - result['开始时间']).dt.total_seconds()
    return result


def load_demand_data(file_path):
    """
    加载产品需求数据
    
    Args:
        file_path (str): 产品需求数据文件路径
        
    Returns:
        pandas.DataFrame: 产品需求数据
    """
    demand = pd.read_csv(file_path, dtype={
        '订单号': str, 
        '工单号': str, 
        '工序号': int, 
        '产品号': str, 
        '瓶颈物料号': str
    })
    demand['需求日期'] = pd.to_datetime(demand['需求日期'])
    return demand


def check_equipment(result, work_calendar):
    """
    检查设备使用是否符合规则
    
    每台设备只能加工某件产品的一种工序，且一旦开始不能中断

    Args:
        result (pandas.DataFrame): 合并后的产品需求与排产结果数据
        work_calendar (pandas.DataFrame): 工作日历数据
        
    Returns:
        tuple: (是否有错误(bool), 错误信息(str))
    """
    for k, g in result.groupby("设备号"):
        df = g.reset_index(drop=True).copy()
        st = df['结束时间']
        et = df['开始时间']
        for s, e in zip(st, et):
            if len(work_calendar.query("设备号==@k and 开始时间<=@s and 结束时间>=@e")):
                pass
            else:
                return True, "设备%s在%s开始工作,在%s结束，与工作日历不匹配" % (k, e, s)
        for i in range(1, len(df)):
            if st[i - 1] > et[i]:
                return True, "设备%s在%s开始工作，但%s才结束" % (k, et[i], st[i - 1])
    return False, ''


def check_order(result, process_route, switching):
    """
    检查订单工序是否符合规则
    
    每台设备只能加工某件产品的一种工序，且一旦开始不能中断

    Args:
        result (pandas.DataFrame): 合并后的产品需求与排产结果数据
        process_route (pandas.DataFrame): 工艺路线数据
        switching (dict): 设备切换时间字典
        
    Returns:
        tuple: (是否有错误(bool), 错误信息(str))
    """
    result_bak = result[result['产品号']!='8888'].merge(process_route, on=['设备号', '工序号', '工艺路线类型'], how='left')
    result_bak['切换时间'] = result_bak['工作时长'] - result_bak['需求量'] * result_bak['每个产品单位加工时间（秒）']
    result_bak = result_bak.sort_values(by=['设备号', '开始时间']).reset_index(drop=True)
    for equipment_id, group in result_bak.groupby("设备号"):
        df = group.reset_index(drop=True).copy()
        products = df['产品号'].values
        for i in range(1, len(group)):
            pre_product, after_product = products[i - 1], products[i]
            switch_time = switching.get(equipment_id + pre_product + after_product, 0)
            if df['切换时间'][i] != switch_time:
                return True, "工单号:" + df['工单号'][i] + "切换时间计算错误，应该为" + str(int(switch_time))
    for k, g in result_bak.groupby("订单号"):
        df = g.sort_values(by=['工序号']).reset_index(drop=True).copy()
        number = df['工序号'].values
        st = df['结束时间']
        et = df['开始时间']
        for i in range(1, len(df)):
            if st[i - 1] > et[i]:
                return True, "订单号工序异常，%s工序%s在%s开始工作，但工序%s在%s才结束" % (k, number[i], et[i], number[i-1], st[i - 1])
    return False, ''


def calculate_a1_score(result):
    """
    计算订单准时完成率指标(A1)
    
    Args:
        result (pandas.DataFrame): 合并后的产品需求与排产结果数据
        
    Returns:
        float: A1指标得分
    """
    df_a1 = result.groupby(["订单号"]).agg({
        '结束时间': 'max', 
        '需求日期': 'min'
    }).reset_index().dropna()
    
    df_a1['score'] = np.where(
        df_a1['结束时间'] <= df_a1['需求日期'] + timedelta(days=1), 1, 0
    )
    a1 = np.sum(df_a1['score']) / len(df_a1)
    return a1


def calculate_a2_score(result):
    """
    计算设备利用率均衡度指标(A2)
    
    Args:
        result (pandas.DataFrame): 合并后的排产结果数据
        
    Returns:
        float: A2指标得分
    """
    df_a2 = result.groupby(["设备号"], as_index=False).agg({
        '结束时间': 'max', 
        '开始时间': 'min'
    })
    
    reference_time = pd.to_datetime('2025-05-06 08:00:00')
    df_a2['结束时间'] = (df_a2['结束时间'] - reference_time).dt.total_seconds()
    df_a2['开始时间'] = (df_a2['开始时间'] - reference_time).dt.total_seconds()
    
    x = df_a2['结束时间'] - df_a2['开始时间']
    a2 = 1 - np.sum(np.abs(x - np.mean(x))) / (np.sum(x) / 2)
    return a2


def calculate_a3_score(result, switching):
    """
    计算生产切换效率指标(A3)
    
    Args:
        result (pandas.DataFrame): 合并后的排产结果数据
        switching (dict): 设备切换时间字典
        
    Returns:
        float: A3指标得分
    """
    total_processing_time = result['工作时长'].sum()
    total_switch_time = 0
    
    for equipment_id, group in result.groupby("设备号"):
        products = group['产品号'].values
        for pre_product, after_product in pairwise(products):
            total_switch_time += switching.get(
                equipment_id + pre_product + after_product, 0
            )
    
    a3 = 1 - 2 * total_switch_time / total_processing_time
    return a3


def main():
    """主函数"""
    # 加载切换时间数据
    switching = load_switching_data('/usr/src/workspace/github/QQhuxuhui/BMAD-METHOD/test/data/切换时间.csv')
    
    # 加载工艺路线数据
    process_route = load_process_route("/usr/src/workspace/github/QQhuxuhui/BMAD-METHOD/test/data/工艺路线.csv")
    # 加载并处理排产结果数据
    result = load_and_process_result("/usr/src/workspace/github/QQhuxuhui/BMAD-METHOD/test/aps-outputs/code/data/output/排产结果.csv")
    # 加载产品需求数据并合并
    demand = load_demand_data("/usr/src/workspace/github/QQhuxuhui/BMAD-METHOD/test/data/产品需求.csv")
    # 加载工作日历数据
    work_calendar = load_work_calendar("/usr/src/workspace/github/QQhuxuhui/BMAD-METHOD/test/data/工作日历.csv")
    # 加载物料数据
    material = pd.read_csv("/usr/src/workspace/github/QQhuxuhui/BMAD-METHOD/test/data/瓶颈物料.csv", dtype={'物料号': str})
    result = result.merge(demand, on=['订单号', '工单号', '工序号', '产品号'], how='left')
    result['生产日期'] = result['开始时间'].dt.date
    material['供应日期'] = pd.to_datetime(material['供应日期']).dt.date
    df_use = result.groupby(["瓶颈物料号", "生产日期"])['需求量'].sum()
    material_use = material.merge(df_use, how='left', left_on=['物料号', '供应日期'], right_on=["瓶颈物料号", "生产日期"])
    for i, row in material_use.iterrows():
        if row['需求量'] > row['供应数量']:
            print(f"{row['瓶颈物料号']}{row['生产日期']}供应量为{row['供应数量']}, 而需求数量为{row['需求量']}")
    flag, info = check_equipment(result, work_calendar)
    if flag:
        print(info)
    flag, info = check_order(result, process_route, switching)
    if flag:
        print(info)
    # 计算各项指标
    a1 = calculate_a1_score(result)
    a2 = calculate_a2_score(result)
    a3 = calculate_a3_score(result, switching)
    # 输出结果
    score = a1 * 50 + a2 * 30 + a3 * 20
    print("A1 =", a1 * 100, "A2 =", a2 * 100, "A3 =", a3 * 100, "Score =", score)
    # A1=97.53521126760563,A2=97.04079001930282,A3=93.32376980924711


if __name__ == "__main__":
    main()

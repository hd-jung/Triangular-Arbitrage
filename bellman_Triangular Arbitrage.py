import itertools
import pandas as pd
import sys

df = pd.read_excel('exchange_rate_predictions_3.xlsx', index_col=0)
df.columns = df.columns.str.replace('=X', '')
# 컬럼 이름을 세 글자 튜플로 변경
df.columns = [tuple(col[i:i + 3] for i in range(0, len(col), 3)) for col in df.columns]
# 변경된 데이터프레임 출력
tp = tuple(df.columns)
target_exchange_rates = []
for idx in range(len(df)):
    exchange_rates = {}  # 반복마다 새로운 딕셔너리를 생성
    for i in tp:
        exchange_rates[i] = df[i].values[idx]
    target_exchange_rates.append(exchange_rates)


def generate_all_exchange_paths(exchange_rates, currencies):
    paths = []

    def dfs(path):
        nonlocal paths
        current_currency = path[-1]

        if len(path) >= 2:  # 최소 두 나라가 포함된 경로부터 고려
            paths.append(path)

        if len(path) == len(currencies):
            # 모든 나라를 포함하는 경로가 완성됨
            return

        for next_currency in currencies:
            if next_currency not in path:
                if (current_currency, next_currency) in exchange_rates:
                    # 환율 정보가 있는 경우에만 다음 나라로 진행
                    dfs(path + [next_currency])

    for currency in currencies:
        dfs([currency])

    return paths


def find_optimal_exchange_path(exchange_rates, start_currency, target_currency, start_amount=10000):
    currencies = set(itertools.chain(*exchange_rates.keys()))
    # print(currencies)
    optimal_path = None
    max_rate_of_return = -1  # 초기값 설정

    all_paths = generate_all_exchange_paths(exchange_rates, currencies)

    for path in all_paths:
        if path[0] != start_currency or path[-1] != target_currency:
            continue

        rate_of_return = calculate_rate_of_return(exchange_rates, path, start_amount)

        if rate_of_return > max_rate_of_return:
            max_rate_of_return = rate_of_return
            optimal_path = path

    return optimal_path, max_rate_of_return


def calculate_rate_of_return(exchange_rates, path, start_amount):
    rate = 1.0
    for i in range(len(path) - 1):
        rate *= exchange_rates[(path[i], path[i + 1])]
    return rate


# print(df['(USD), (JPY)'])

start_currency = 'USD'
target_currency = 'EUR'

date_range = pd.date_range(start='2023-01-01', end='2027-12-31', freq='MS')
op_paths = []
max_returns = []
for idx, exchange_rate in enumerate(target_exchange_rates):
    optimal_path, max_rate_of_return = find_optimal_exchange_path(exchange_rate, start_currency, target_currency,
                                                              start_amount=10000)

    if optimal_path:
        print(f"optimal arbitrage opportunities found for {start_currency} -> {target_currency}.")
        print("Optimal Exchange Path:", " -> ".join(optimal_path))
        print("Maximum Rate of Return:", max_rate_of_return)
    else:
        print(f"No optimal arbitrage opportunities found for {start_currency} -> {target_currency}.")


    op_paths.append(" -> ".join(optimal_path))
    max_returns.append(max_rate_of_return)

cal_df = pd.DataFrame({'date': date_range, 'optimal_path': op_paths, 'max_rate_of_return': max_returns})
cal_df.to_csv(f'{start_currency}_to_{target_currency}_return_rates_normalPred.csv')
import yaml
import math

with open('../configs/risk.yaml') as f:
    cfg = yaml.safe_load(f)

def compute_size(account_balance, stop_pips, pip_value=0.01):
    # fixed fractional: risk_pct of balance
    risk = cfg['risk_per_trade']  # e.g., 0.005 for 0.5%
    dollars_at_risk = account_balance * risk
    # approximate position size = dollars_at_risk / (stop_pips * pip_value)
    size = dollars_at_risk / (stop_pips * pip_value)
    return max(size, 0)

if __name__ == '__main__':
    print(compute_size(10000, 20))

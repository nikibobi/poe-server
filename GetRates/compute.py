import torch
import torch.nn.functional as F

from .constants import CURRENCY, RATES, LEAGUE, ITEM, LR

def compute(items, user, rates=RATES, league=LEAGUE, item=ITEM, lr=LR, **kwargs):
    amounts = torch.tensor([item['amount'] for item in items])
    currency_indexes = torch.tensor([CURRENCY.index(item['currency']) for item in items], dtype=torch.long)
    chaos_index = CURRENCY.index('chaos')
    currency = F.one_hot(currency_indexes, len(CURRENCY)).to(dtype=torch.float)
    rates = torch.tensor(rates)
    rates[chaos_index] = 1

    while True:
        values = amounts * torch.mv(currency, rates)
        ordered, i = torch.sort(values)
        j = torch.arange(values.nelement())
        diff = i - j
        grad = torch.matmul(diff.to(dtype=torch.float), currency)
        rates -= lr * grad
        rates[chaos_index] = 1
        if torch.eq(values, ordered).all():
            break

    output = dict(zip(CURRENCY, rates.tolist()))
    return output

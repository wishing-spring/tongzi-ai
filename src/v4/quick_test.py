import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..','..','src'))
from v4.v4 import LingxiV4
from v3.eco_pool import EcoPool
import v3.eco_pool as ep; ep.F0=32

v4=LingxiV4()
v4.add_pool(EcoPool('🔥快生',tau=3,fit_min=2,birth_rate=1.5,flow_back=True,density_max=128,stagnation_window=2,jitter_bits=5))
v4.add_pool(EcoPool('⚡涌动',tau=5,fit_min=2,birth_rate=1.2,flow_back=True,density_max=96,stagnation_window=2,jitter_bits=5))

tests=[('你好','社交'),('打死你滚开','暴力'),('我爱你','情感'),('今天天气真好','自然'),('吃饭了吗','日常')]
for t,l in tests:
    reply,r = v4.chat(t)
    print(f'[{l}] {t} → {reply}')
print()
print(v4.status())

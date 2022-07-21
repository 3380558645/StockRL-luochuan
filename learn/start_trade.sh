nohup python -u ./trader.py -m 'a2c'  >./nohup_trade/A2C.log 2>&1 &
nohup python -u ./trader.py -m 'ddpg'  >./nohup_trade/DDPG.log 2>&1 &
nohup python -u ./trader.py -m 'ppo'  >./nohup_trade/PPO.log 2>&1 &
nohup python -u ./trader.py -m 'td3'  >./nohup_trade/TD3.log 2>&1 &
nohup python -u ./trader.py -m 'sac'  >./nohup_trade/SAC.log 2>&1 &
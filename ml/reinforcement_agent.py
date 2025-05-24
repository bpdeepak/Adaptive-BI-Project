import psycopg2
import pandas as pd
import numpy as np
import joblib
import random

# RL Libraries
import gym
from stable_baselines3 import DQN

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="adaptive_bi",
    user="bi_user",
    password="bi_pass"
)

# Load data
query = """
SELECT quantity, price AS unit_price, price * quantity AS total_value
FROM orders;
"""
df = pd.read_sql(query, conn)
print("✅ Data loaded for RL agent:", df.shape)

# Preprocess
scaler = joblib.load('models/order_value_scaler.pkl')
X = df[['quantity', 'unit_price']]
X_scaled = scaler.transform(X)

# Define simple custom Gym environment
class OrderValueEnv(gym.Env):
    def __init__(self, data):
        super(OrderValueEnv, self).__init__()
        self.data = data
        self.current_step = 0
        self.action_space = gym.spaces.Discrete(2)  # 0 = hold, 1 = adjust
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(data.shape[1],), dtype=np.float32)

    def reset(self):
        self.current_step = 0
        return self.data[self.current_step]

    def step(self, action):
        reward = -abs(self.data[self.current_step, 0] * self.data[self.current_step, 1] - action)
        self.current_step += 1
        done = self.current_step >= len(self.data)
        obs = self.data[self.current_step] if not done else np.zeros_like(self.data[0])
        return obs, reward, done, {}

    def render(self, mode='human'):
        pass

env = OrderValueEnv(X_scaled)

# Train RL Agent
model = DQN('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=10000)

# Save agent
model.save('models/order_value_dqn_agent')
print("✅ RL agent saved to disk.")
# Close database connection
conn.close()
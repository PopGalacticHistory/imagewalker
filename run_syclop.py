from image_env_mnist1 import Image_env1
from RL_brain_b import DeepQNetwork
import numpy as np
import time
import SYCLOP_env as syc
from misc import *
hp=HP()
hp.max_episode = 3000
hp.steps_per_episode = 10000
hp.steps_between_learnings = 1000

def local_observer(sensor,agent):
    return np.concatenate([np.abs(sensor.dvs_view[5,:].reshape([-1])),10*agent.qdot])

def run_env():
    old_policy_map=0
    step = 0
    for episode in range(hp.max_episode):
        observation = local_observer(sensor,agent)
        for step in range(hp.steps_per_episode):
            action = RL.choose_action(observation)
            reward.update_rewards(sensor = sensor, agent = agent)
            agent.act(action)
            sensor.update(scene,agent)
            observation_  = local_observer(sensor,agent) #todo: generalize
            RL.store_transition(observation, action, reward.reward, observation_)
            recorder.record([agent.q_ana[0],agent.q[0],agent.qdot[0],reward.rewards[0],reward.rewards[1],reward.reward])
            if (step > 100) and (step % hp.steps_between_learnings == 0):
                RL.learn()
            observation = observation_
            step += 1
            if step%1000 ==0:
                print(episode,step)
                # policy_map = np.array([np.argmax(RL.compute_q_eval(np.eye(10)), axis=1),
                #                         np.argmax(RL.compute_q_eval(debu2el), axis=1)])
                # if np.max(np.abs(old_policy_map - policy_map))>0:
                #     print(policy_map)
                #     print('policy_change')
                #     print(policy_map-old_policy_map)
                #     print('--------------------------------')
                #     old_policy_map = policy_map
            if step%10000 ==0:
                    recorder.plot()
                    RL.dqn.save_nwk_param('temp3.nwk')

if __name__ == "__main__":

    vertical_edge_mat = np.zeros([28,28])
    vertical_edge_mat[:,14:] = 1.0
    recorder = Recorder(n=6)
    debu2el = np.diag(np.ones([10-1]),k=1)+np.eye(10)
    # debu2el = debu2el[:-1,:]

    scene = syc.Scene(image_matrix=vertical_edge_mat)
    sensor = syc.Sensor()
    agent = syc.Agent(max_q = [scene.maxx-sensor.hp.winx,scene.maxy-sensor.hp.winy])
    reward = syc.Rewards()
    RL = DeepQNetwork(len(agent.hp.action_space), sensor.hp.winx+2,#sensor.frame_size+2,
                      reward_decay=0.9,
                      e_greedy=0.99,
                      e_greedy0=0.25,
                      replace_target_iter=10,
                      memory_size=30000,
                      e_greedy_increment=0.001,
                      state_table=None
                      )


    hp.scene = scene.hp
    hp.sensor = sensor.hp
    hp.agent = agent.hp
    hp.reward = reward.hp
    hp.RL = RL.hp

    run_env()



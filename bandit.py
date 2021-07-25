import random
import numpy as np


class Bandit:
    """A useful class containing the multi-armed bandit and all its actions.

    Attributes:
        actions The actions that can be performed
    """

    def __init__(self, candidates):
        self.actions = list(candidates)

    def random(self):
        return random.choice(self.actions)

    def has_action(self, action):
        return action in self.actions

    def payoffs(self, all_payoffs):
        payoffs = dict()
        for action in self.actions:
            if all_payoffs.get(action):
                payoffs[action] = all_payoffs.get(action)
        return payoffs


def epsilon_greedy_agent(bandit, pay_offs, current_round, epsilon=0.2, initial_rounds=1):
    """Use the epsilon-greedy algorithm by performing the action with the best average
    pay-off with the probability (1-epsilon), otherwise pick a random action to keep exploring."""

    # Get only payoffs of actions on the bandit
    pay_offs = bandit.payoffs(pay_offs)

    # sometimes randomly pick an action to explore
    if random.random() < epsilon or current_round <= initial_rounds or len(pay_offs) == 0:
        a = bandit.random()
    # otherwise pick the best one thus far
    else:
        # check for the lever with the best average payoff
        new_dict = {}
        for key, val in pay_offs.items():
            new_dict[key] = np.mean(val)
        a = max(new_dict, key=new_dict.get)

    return a


def update_payoff(pay_offs, action, reward):
    # update rewards
    if action in pay_offs:
        pay_offs[action].append(reward)
    else:
        pay_offs[action] = [reward]

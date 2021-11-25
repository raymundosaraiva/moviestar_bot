import numpy as np
from copy import deepcopy
from sklearn.linear_model import LogisticRegression
from contextualbandits.online import EpsilonGreedy


def policy(actions, context_to_predict, context_features, context_actions, rewards, exploit):
    n_choices = len(actions)
    if n_choices == 1:
        return actions[0]
    np.random.seed(n_choices)
    # Turning logistic regression into contextual bandits policy
    base_algorithm = LogisticRegression(solver='liblinear')
    # until there are at least 2 observations of each class, will use this prior
    beta_prior = ((3. / n_choices, 4), 2)
    # The base algorithm is embedded in EpsilonGreedy metaheuristic
    epsilon_greedy = EpsilonGreedy(deepcopy(base_algorithm), nchoices=n_choices,
                                   beta_prior=beta_prior, explore_prob=0.9999)
    # fitting the context
    if context_features and exploit:
        epsilon_greedy.fit(X=np.array(context_features), a=np.array(context_actions), r=np.array(rewards))
    # choosing action
    action = epsilon_greedy.predict(X=np.array([context_to_predict]), exploit=exploit).astype('uint8')
    return actions[int(action)]


def update_payoff(pay_offs, action, reward):
    # update rewards
    if action in pay_offs:
        pay_offs[action].append(reward)
    else:
        pay_offs[action] = [reward]

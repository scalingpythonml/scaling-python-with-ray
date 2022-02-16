import ray
from ray.rllib import agents
ray.init()
config = {
    # Environment (RLlib understands openAI gym registered strings).
    'env': 'CartPole-v0',
    # Use 4 environment workers (aka "rollout workers") that parallelly
    # collect samples from their own environment clone(s).
    "num_workers": 4,
    'framework': 'tf2',
    'eager_tracing': True,
    'model': {
        'fcnet_hiddens': [64, 64],
        'fcnet_activation': 'relu',
    },
    # Set up a separate evaluation worker set for the
    # `trainer.evaluate()` call after training (see below).
    'evaluation_num_workers': 1,
    # Only for evaluation runs, render the env.
    'evaluation_config': {
        "render_env": True,
    },
    'gamma': 0.9,
    'lr': 1e-2,
    'train_batch_size': 256,
}

# Create RLlib Trainer.
trainer = agents.ppo.PPOTrainer(config=config)

# Run it for n training iterations. A training iteration includes
# parallel sample collection by the environment workers as well as
# loss calculation on the collected batch and a model update.
for i in range(5):
    print(f"Iteration {i}, training results {trainer.train()}")

# Evaluate the trained Trainer (and render each timestep to the shell's
# output).
trainer.evaluate()
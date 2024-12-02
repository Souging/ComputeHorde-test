# ComputeHorde (Subnet 12 of Bittensor)

ComputeHorde is a specialized subnet within the Bittensor network that provides the compute power of networkless GPU-equipped servers. 
Unlike other subnets in Bittensor, ComputeHorde focuses on delivering reliable, decentralized access to computing resources for validation tasks.

The primary purpose of ComputeHorde is to decentralize and democratize the hardware required by validators of other subnets. 
By removing reliance on centralized cloud providers, ComputeHorde ensures the Bittensor network remains true to its goal of decentralized resilience.

---

## Key Features

- **Decentralized Compute for Validators**  
  ComputeHorde aims to become the go-to decentralized source for hardware needed to validate other subnets. 
  This is crucial for avoiding dependency on centralized services, which contradicts Bittensor's ethos.
  
- **Fair and Verified Work**  
  ComputeHorde employs mechanisms to ensure miners provide authentic and fair compute work:
  - Validate tasks from all validators equally, regardless of their stake.
  - Handle both **organic** (external) and **synthetic** (validation-only) tasks.
  - Match jobs to the advertised hardware (e.g., ensuring A6000 GPUs are actually used for tasks requiring them).
  - Prevent malicious behaviors like "weight-copying" through innovative validation mechanisms.

- **Scalable Mining with Executors**  
  Each miner in ComputeHorde can spawn multiple **executors**, virtual machines performing individual compute tasks. 
  This removes the 256 miner (UID) limit and significantly scales the available computing power.

- **Hardware Classes**  
  ComputeHorde introduces hardware classes to create a free market for GPU resources, balancing cost-effectiveness with performance. Currently, the supported classes are:
  - **A6000** (available now)
  - **A100** (coming soon)  
  The goal is to support all GPU types required by validators across Bittensor subnets.

- **Facilitating Organic Jobs**  
  Facilitators connect external requests from validators of other subnets to ComputeHorde, encouraging miners to execute organic tasks alongside synthetic ones.

---

## Components

### **Facilitator**
- Acts as a gateway for organic requests (from other subnets’ validators) to enter ComputeHorde.
- Sends tasks to validators, who then distribute them to miners.

### **Validator**
- Receives organic requests via the Facilitator or generates synthetic tasks for validation.
- Distributes tasks to miners and evaluates the results:
  - Organic results are returned to external requesters.
  - Synthetic results adjust miners' scores.

### **Miner**
- Accepts job requests from validators.
- Manages **executors** to perform tasks and sends results back to validators.

### **Executor**
- A virtual machine spawned by a miner to perform a single dockerized task.
- Operates in a restricted environment, with limited network access necessary for:
  - Communicating with miners.
  - Downloading docker images.
  - Handling job data.
- Executors form a **horde** under a miner and are assigned hardware classes.

---

## Innovations to Highlight

### Discouraging Weight-Copying
- **Commit-Reveal Scheme**: Validators post hidden weights and reveal them in the next epoch, minimizing the impact of weight-copying.
- **Executor Dancing**: Miners randomly move GPUs across multiple UIDs, further reducing the effectiveness of copying old weights.

### Encouraging Actual Mining
- Synthetic tasks are designed to run only on specific hardware (e.g., A6000 GPUs), ensuring miners deliver the advertised compute power.
- Incentives for completing organic tasks.

### Democratizing Mining
- Miners can scale their operations by spawning multiple executors, breaking traditional limits and enabling cost-effective participation.

---

## Goals

1. **Expand Hardware Support**  
   Add support for all GPU classes required by other Bittensor subnets.

2. **Introduce Paid Organic Jobs**  
   Allow the free market to regulate demand and prioritize cost-effective hardware.

3. **Support Long-Running Jobs**  
   Implement accounting mechanisms for miners to be rewarded proportionally, even for incomplete long-running tasks.

4. **Fair Resource Sharing**  
   Allocate resources based on validators' stakes while allowing low-stake validators access when demand is low.

5. **Strengthen Security**  
   Introduce safeguards to prevent exploitation and ensure a fair environment for all participants.

---

## Repository Overview

This repository contains the reference implementations of key ComputeHorde components:

- **Validator**: A reference implementation requiring a Trusted Miner for cross-checking synthetic tasks.
- **Miner**: Default miner setup with a single executor.
- **Executor**: Base implementation for executing dockerized jobs. Users can create custom executor managers to scale and optimize mining efficiency.

# What is this

This repository contains reference implementations of

1. Validator
2. Miner
3. Executor

of the ComputeHorde BitTensor SubNet. Running etc. is explained in each component's README.

# ComputeHorde

![ComputeHorde.png](ComputeHorde.png)

Data flow looks like this:

1. **Facilitator** is an internet facing app charging users for accepting jobs from them, which are then passed on to validators.
1. **Validator** has the same meaning as in other Bittensor subnets. 
   It receives organic requests (requests from end users) or generates synthetic ones itself, sends them to miners and reads the results. 
   Results for organic traffic are then passed back to end users, while synthetic traffic is used to adjust miners' scores. [See validator's README for more details](validator/README.md)
1. **Miner** has the same meaning as in other Bittensor subnets. It receives job requests from validators, spawns executors to do the actual work and sends the results back to validators.
   [See miner's README for more details](miner/README.md)
1. **Executor** is a virtual machine managed by a single miner, spawned to perform a single dockerized job, and is scrapped afterwards. 
   Its access to the network is limited to necessary bits needed to execute a job, 
   i.e. communicate with a miner, download the docker image that runs the job, download the docker image containing executor app, and mount the job data volume. 
   Executors have hardware classes assigned and together form the horde of a miner.
   [See executor's README for more details](executor/README.md)

# Scoring -- outdated

Currently miners are rewarded for providing the time of networkless GPU-equipped servers, proportionally to their efficiency. Each miner can (for now) provide only their fastest Executor.

In February 2024 this will change - subnet will define more resource types andValidators will reward miners more for providing resources that are in higher demand. The system will quickly fill to capacity with organic traffic.

# Incoming changes -- outdated
* Introduce hardware classes to create a free market that delivers the most cost-effective hardware, rather than solely focusing on the strongest hardware.
* Organic jobs should not be free to allow the free market to regulate demand on hardware classes effectively.
* Support long-running jobs by accounting for miners' work in 10-minute intervals, ensuring they can be paid for unfinished long-running jobs.
* Implement rules and safeguards to prevent malicious actors from exploiting the network, ensuring a fair and secure environment for all participants.
* Develop a resource-sharing system that allocates resources proportionally to each user's stake. However, also allow low-stake users to utilize network resources freely when there is no competing demand from other users.
* Implement a mechanism for miner servers to reject jobs for a given hardware class if accepting the job would result in a financial loss for the miner.
* Ensure that benchmark jobs are paid in the same manner as organic jobs: job duration multiplied by the hardware class multiplier and the benchmark value.
* When a new miner is registered, require all validators to benchmark the miner's hardware classes with extended timeouts to accurately assess their capabilities.
* When a new validator registers, they must benchmark every other miner in the network to maintain an up-to-date and comprehensive understanding of available resources. Until a miner is benchmarked by the validator, the validator defaults to 1 as the locally_measured_efficiency_factor for that miner.
* Miners will have the ability to modify their hardware class availability manifest at a frequency of once every 2 hours. In the event that a miner has available executors, they are obligated to accept assigned jobs and cannot reject them. Should a miner reject a job under such circumstances, the validator will impose a penalty by lowering the hardware class local multiplier for all tasks associated with that miner.


```python
points = {}
for miner in miners:
    for hardware_class in miner.executors:
        executor = miner.executors[hardware_class]
        hardware_class_relative_value = hardware_classes[hardware_class].relative_value
        points[miner.hotkey] = (
            hardware_class_relative_value
            * executor.locally_measured_efficiency_factor
            * executor.total_worked_seconds
        )
```

# Running

This repository contains reference implementations of

1. Validator
2. Miner
3. Executor

of the ComputeHorde BitTensor SubNet. 
In the following sections you can find instructions on running [Validator](#Validator) and [Miner](#Miner).
There are more details in each component's README and in the [Troubleshooting](#Troubleshooting) section below.

## Validator

ComputeHorde validator is built out of three components
1. trusted miner (requires A6000 - the only GPU supported now) for cross-validation
1. two S3 buckets for sharing LLM data (lots of small text files)
1. validator machine (standard, non-GPU) - for regular validating & weight-setting

The steps, performed by running installation scripts **on your local machine**, which has your wallet files. For clarity, **these installation scripts are not run on the machine that will become the trusted miner or the validator**, the scripts will connect through SSH to those machines from your local machine:
1. [setup trusted miner](/validator#setting-up-a-trusted-miner-for-cross-validation) 
1. [provision S3 buckets for prompts and answers](/validator#provision-s3-buckets-for-prompts-and-answers) 
1. [setup validator](#validator-setup)

### Validator setup

#### Upgrading already existing deployment

Prepare a trusted miner and S3 buckets (find out how using the links above). 
Then, set the [environment variables](#deploying-from-scratch) directly in the `.env` file of your **validator** instance and restart your validator:

```
$ docker compose down --remove-orphans && docker compose up -d
```

#### Deploying from scratch

Set the following environment variables in a terminal on your **local machine** (on the machine where you have your wallet files):

```sh
export TRUSTED_MINER_ADDRESS=...
export TRUSTED_MINER_PORT=...

export S3_BUCKET_NAME_PROMPTS=...
export S3_BUCKET_NAME_ANSWERS=...

export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=...
```

Note: The `AWS_DEFAULT_REGION` property is optional. Use it when your buckets are not in your default AWS region.

Export `AWS_ENDPOINT_URL` to use another cloud object storage (s3-compatible) provider. If not given, AWS S3 will be used.

Then execute the following command from the same terminal session:

```shell
curl -sSfL https://github.com/backend-developers-ltd/ComputeHorde/raw/master/install_validator.sh | bash -s - SSH_DESTINATION HOTKEY_PATH
```

Replace:
- `SSH_DESTINATION` with your server's connection info (i.e. `username@1.2.3.4`)
- `HOTKEY_PATH` with the path of your hotkey (i.e. `~/.bittensor/wallets/my-wallet/hotkeys/my-hotkey`)

This script installs the necessary tools in the server, copies the public keys,  and starts the validator with the corresponding runner and the default config.

If you want to change the default config, see [Validator runner README](validator/envs/runner/README.md) for details.

If you want to trigger jobs from the validator see [Validator README](validator/docs/validator.md) for details.

If anything seems wrong, check the [troubleshooting](#troubleshooting) section.

## Miner

To quickly start a miner, create an Ubuntu Server and execute the following command from your local machine (where you have your wallet files).

```shell
curl -sSfL https://github.com/backend-developers-ltd/ComputeHorde/raw/master/install_miner.sh | bash -s - production SSH_DESTINATION HOTKEY_PATH
```

Replace `SSH_DESTINATION` with your server's connection info (i.e. `username@1.2.3.4`)
and `HOTKEY_PATH` with the path of your hotkey (i.e. `~/.bittensor/wallets/my-wallet/hotkeys/my-hotkey`).
This script installs necessary tools in the server, copies the keys, and starts the miner with the corresponding runner and default config.

If you want to change the default config, see [Miner runner README](miner/envs/runner/README.md) for details.


## Checking that your miner works properly

1. Check if your miner is reachable from a machine different from the miner: `curl {ADDRESS}:{PORT}/admin/login/ -i`.
   Both `PORT` and `ADDRESS` can be obtained from the metagraph. If everything is ok the first line should read
   `HTTP/1.1 200 OK`. By default, the address is automatically determined by bittensor lib, but you can input 
   your own in .env
2. Check if you're getting any jobs and what the outcomes are. An admin panel for that is coming but for now you
   achieve that with `docker-compose exec miner-runner docker-compose exec db psql postgres -U postgres -c 'select *
   from miner_acceptedjob order by id desc;`

# Migrating servers

If you need to move your miner or validator to a new server,
see the [migration guide](/docs/migration.md).

# Troubleshooting

## How to dump the logs

The ComputeHorde software starts several Docker containers. The most relevant logs are from containers with names ending in `app-1`.

To view these logs:
1. SSH into the machine (validator or miner).
1. Run `docker ps` to find the name of the appropriate container (e.g., `compute_horde_miner-app-1`).
1. Run `docker logs CONTAINER_NAME`.


## How to restart the services

To perform a hard restart of all ComputeHorde Docker containers, run the following commands:

```bash
docker compose down --remove-orphans
docker compose up
```

Afterwards, use `docker ps` to verify that the containers have started successfully.

## How to delete persistent volumes

To start fresh and remove all persistent data, follow these steps:

1. Stop the validator or miner (all running containers)
1. Run `docker volume ls` to list all existing volumes and identify the ones to delete.
   Key volumes to consider:
    - Miner: `miner_db_data`, `miner_redis_data`
    - Validator: `validator_db`, `validator_redis`, `validator_static`
1. Run the following command to remove all Docker volumes:
   ```bash
   docker volume rm $(docker volume ls -q)
   ```
1. Start the validator or miner again

## How to fix issues with installing `cuda-drivers`

Miner installation may occasionally fail with an error about the system being unable to install the `cuda-drivers` package. 
This issue is often caused by mismatched drivers already installed before running the installation script.

To resolve this:
1. Run the following command on the miner machine to purge any conflicting NVIDIA packages:
   ```bash
   sudo apt-get purge -y '^nvidia-.*'
   ```
1. Re-run the `install_miner.sh` script from your local machine.

## How to check if NVIDIA Drivers are working and the GPU is usable

To verify the health of the NVIDIA setup, run the following command on the miner machine:
```bash
docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```

If the output indicates a problem (especially immediately after installation), a [restart of the services](#how-to-restart-the-services) may help.


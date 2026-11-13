# Cloud Deployment: AWS Elastic Beanstalk

This section describes with code how to deploy the containerized service to the cloud using **AWS Elastic Beanstalk**.

Elastic Beanstalk runs the Docker image on AWS. It starts the instances, keeps the application running, and scales it with traffic. The project's `Dockerfile` works unchanged: it exposes port `9696`, and Elastic Beanstalk's reverse proxy routes incoming HTTP requests on port `80` to port `9696` inside the container.

## Prerequisites

- An AWS account.
- An IAM user with an access key, and the AWS CLI configured with `aws configure` (region `eu-north-1`, output `json`). Never commit the keys.
- Docker running locally, for the local test step.
- `model.bin` created by `python -m src.train`, **committed to the repository**. When a Git repository is present, Elastic Beanstalk packages the latest committed state (`HEAD`) and ignores anything excluded by `.gitignore` (such as `data/`).

## Steps

### 1. Install the EB CLI
Install the EB CLI into the project's virtual environment. It is a deployment tool and not part of the container runtime, so it does not go into `requirements.txt`:

```bash
source .venv/bin/activate
pip install awsebcli
```

### 2. Initialise the application
Initialise the Elastic Beanstalk application in the project folder:

```bash
eb init -p docker -r eu-north-1 delivery-duration
```

### 3. Test the container locally
Test the container locally first. Elastic Beanstalk builds the image and runs it on port 9696:

```bash
eb local run --port 9696
```

In a second terminal, run predict_test.py (which defaults to http://localhost:9696 and sends a POST request to /predict):

```bash
python predict_test.py
```

Stop the local container(Ctrl + C) once verified.

### 4. Deploy to AWS
Create the environment in AWS. This takes a few minutes and prints the environment URL when ready:

```bash
eb create delivery-duration-env --single
```

--single runs one instance without a load balancer. That is cheaper and enough for this project.

### 5. Test the deployed cloud service
Pass the environment URL to predict_test.py using --url. The URL needs no port number because Elastic Beanstalk listens on standard HTTP port 80 and forwards traffic to port 9696 inside the container:

```bash
python predict_test.py --url http://<environment-url>
```
Example output:
{'predicted_delivery_minutes': ...}

### 6. Terminate the environment
When finished, delete the environment so AWS stops charging for it:

```bash
eb terminate delivery-duration-env
```

>> Notes
- The environment URL is public. Anyone who finds it can call the model. Terminate the environment after grading or testing.

- Elastic Beanstalk uses .gitignore and .ebignore to decide what to upload. data/ is ignored, which keeps the upload small.

import Image from '@theme/IdealImage';


# MishikaLLM Proxy - 1K RPS Load test on locust 

Tutorial on how to get to 1K+ RPS with MishikaLLM Proxy on locust


## Pre-Testing Checklist
- [ ] Ensure you're using the **latest `-stable` version** of mishikallm
    - [Github releases](https://github.com/BerriAI/mishikallm/releases)
    - [mishikallm docker containers](https://github.com/BerriAI/mishikallm/pkgs/container/mishikallm)
    - [mishikallm database docker container](https://github.com/BerriAI/mishikallm/pkgs/container/mishikallm-database)
- [ ] Ensure you're following **ALL** [best practices for production](./proxy/production_setup.md)
- [ ] Locust - Ensure you're Locust instance can create 1K+ requests per second
    - 👉 You can use our **[maintained locust instance here](https://locust-load-tester-production.up.railway.app/)**
    - If you're self hosting locust
        - [here's the spec used for our locust machine](#machine-specifications-for-running-locust)
        - [here  is the locustfile.py used for our tests](#locust-file-used-for-testing)
- [ ] Use this [**machine specification for running mishikallm proxy**](#machine-specifications-for-running-mishikallm-proxy)
- [ ] **Enterprise MishikaLLM** - Use `prometheus` as a callback in your `proxy_config.yaml` to get metrics on your load test
    Set `mishikallm_settings.callbacks` to monitor success/failures/all types of errors
    ```yaml
    mishikallm_settings:
        callbacks: ["prometheus"] # Enterprise MishikaLLM Only - use prometheus to get metrics on your load test
    ```

**Use this config for testing:**

**Note:**  we're currently migrating to aiohttp which has 10x higher throughput. We recommend using the `aiohttp_openai/` provider for load testing.

```yaml
model_list:
  - model_name: "fake-openai-endpoint"
    mishikallm_params:
      model: aiohttp_openai/any
      api_base: https://your-fake-openai-endpoint.com/chat/completions
      api_key: "test"
```


## Load Test - Fake OpenAI Endpoint

### Expected Performance

| Metric | Value |
|--------|-------|
| Requests per Second | 1174+ |
| Median Response Time | `96ms` |
| Average Response Time | `142.18ms` |

### Run Test

1. Add `fake-openai-endpoint` to your proxy config.yaml and start your mishikallm proxy
mishikallm provides a hosted `fake-openai-endpoint` you can load test against

```yaml
model_list:
  - model_name: fake-openai-endpoint
    mishikallm_params:
      model: aiohttp_openai/fake
      api_key: fake-key
      api_base: https://exampleopenaiendpoint-production.up.railway.app/

mishikallm_settings:
  callbacks: ["prometheus"] # Enterprise MishikaLLM Only - use prometheus to get metrics on your load test
```

2. `pip install locust`

3. Create a file called `locustfile.py` on your local machine. Copy the contents from the mishikallm load test located [here](https://github.com/BerriAI/mishikallm/blob/main/.github/workflows/locustfile.py)

4. Start locust
  Run `locust` in the same directory as your `locustfile.py` from step 2

  ```shell
  locust -f locustfile.py --processes 4
  ```

5. Run Load test on locust

  Head to the locust UI on http://0.0.0.0:8089

  Set **Users=1000, Ramp Up Users=1000**, Host=Base URL of your MishikaLLM Proxy

6. Expected results 

  <Image img={require('../img/locust_load_test1.png')} />

## Load test - Endpoints with Rate Limits

Run a load test on 2 LLM deployments each with 10K RPM Quota. Expect to see ~20K RPM

### Expected Performance

- We expect to see 20,000+ successful responses in 1 minute
- The remaining requests **fail because the endpoint exceeds it's 10K RPM quota limit - from the LLM API provider**

| Metric | Value |
|--------|-------|
| Successful Responses in 1 minute | 20,000+ |
| Requests per Second | ~1170+ |
| Median Response Time | `70ms` |
| Average Response Time | `640.18ms` |

### Run Test

1. Add 2 `gemini-vision` deployments on your config.yaml. Each deployment can handle 10K RPM. (We setup a fake endpoint with a rate limit of 1000 RPM on the `/v1/projects/bad-adroit-crow` route below )

:::info

All requests with `model="gemini-vision"` will be load balanced equally across the 2 deployments.

:::

```yaml
model_list:
  - model_name: gemini-vision
    mishikallm_params:
      model: vertex_ai/gemini-1.0-pro-vision-001
      api_base: https://exampleopenaiendpoint-production.up.railway.app/v1/projects/bad-adroit-crow-413218/locations/us-central1/publishers/google/models/gemini-1.0-pro-vision-001
      vertex_project: "adroit-crow-413218"
      vertex_location: "us-central1"
      vertex_credentials: /etc/secrets/adroit_crow.json
  - model_name: gemini-vision
    mishikallm_params:
      model: vertex_ai/gemini-1.0-pro-vision-001
      api_base: https://exampleopenaiendpoint-production-c715.up.railway.app/v1/projects/bad-adroit-crow-413218/locations/us-central1/publishers/google/models/gemini-1.0-pro-vision-001
      vertex_project: "adroit-crow-413218"
      vertex_location: "us-central1"
      vertex_credentials: /etc/secrets/adroit_crow.json

mishikallm_settings:
  callbacks: ["prometheus"] # Enterprise MishikaLLM Only - use prometheus to get metrics on your load test
```

2. `pip install locust`

3. Create a file called `locustfile.py` on your local machine. Copy the contents from the mishikallm load test located [here](https://github.com/BerriAI/mishikallm/blob/main/.github/workflows/locustfile.py)

4. Start locust
  Run `locust` in the same directory as your `locustfile.py` from step 2

  ```shell
  locust -f locustfile.py --processes 4 -t 60
  ```

5. Run Load test on locust

  Head to the locust UI on http://0.0.0.0:8089 and use the following settings

  <Image img={require('../img/locust_load_test2_setup.png')} />

6. Expected results
    - Successful responses in 1 minute = 19,800 = (69415 - 49615)
    - Requests per second = 1170
    - Median response time = 70ms
    - Average response time = 640ms

  <Image img={require('../img/locust_load_test2.png')} />


## Prometheus Metrics for debugging load tests

Use the following [prometheus metrics to debug your load tests / failures](./proxy/prometheus)

| Metric Name          | Description                          |
|----------------------|--------------------------------------|
| `mishikallm_deployment_failure_responses`              | Total number of failed LLM API calls for a specific LLM deployment. Labels: `"requested_model", "mishikallm_model_name", "model_id", "api_base", "api_provider", "hashed_api_key", "api_key_alias", "team", "team_alias", "exception_status", "exception_class"` |
| `mishikallm_deployment_cooled_down`             | Number of times a deployment has been cooled down by MishikaLLM load balancing logic. Labels: `"mishikallm_model_name", "model_id", "api_base", "api_provider", "exception_status"` |



## Machine Specifications for Running Locust

| Metric | Value |
|--------|-------|
| `locust --processes 4`  | 4|
| `vCPUs` on Load Testing Machine | 2.0 vCPUs |
| `Memory` on Load Testing Machine | 450 MB |
| `Replicas` of Load Testing Machine | 1 |

## Machine Specifications for Running MishikaLLM Proxy

👉 **Number of Replicas of MishikaLLM Proxy=4** for getting 1K+ RPS

| Service | Spec | CPUs | Memory | Architecture | Version|
| --- | --- | --- | --- | --- | --- | 
| Server | `t2.large`. | `2vCPUs` | `8GB` | `x86` |


## Locust file used for testing 

```python
import os
import uuid
from locust import HttpUser, task, between

class MyUser(HttpUser):
    wait_time = between(0.5, 1)  # Random wait time between requests

    @task(100)
    def mishikallm_completion(self):
        # no cache hits with this
        payload = {
            "model": "fake-openai-endpoint",
            "messages": [{"role": "user", "content": f"{uuid.uuid4()} This is a test there will be no cache hits and we'll fill up the context" * 150 }],
            "user": "my-new-end-user-1"
        }
        response = self.client.post("chat/completions", json=payload)
        if response.status_code != 200:
            # log the errors in error.txt
            with open("error.txt", "a") as error_log:
                error_log.write(response.text + "\n")
    


    def on_start(self):
        self.api_key = os.getenv('API_KEY', 'sk-1234')
        self.client.headers.update({'Authorization': f'Bearer {self.api_key}'})
```
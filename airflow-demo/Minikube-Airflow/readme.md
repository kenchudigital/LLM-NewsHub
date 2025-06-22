# Airflow (Minikube)

[DOCUMENTATION LINK](https://airflow.apache.org/docs/apache-airflow/stable/howto/index.html)

Tutorial in Medium [LINK](!https://medium.com/@rupertarup/getting-started-with-airflow-deploying-your-first-pipeline-on-kubernetes-0014495e6c92)

<details>

<summary>⚠️ Caution</summary>


This procedure can be useful for learning and exploration. However, adapting it for use in real-world situations can be complicated and the docker compose file does not provide any security guarantees required for production system. Making changes to this procedure will require specialized expertise in Docker & Docker Compose, and the Airflow community may not be able to help you.

For that reason, we recommend using ubernetes with the Official Airflow Community Helm Chart when you are ready to run Airflow in production.

</details>

<br>

> Due to the above suggestion, I decide to set up `Kubernetes` locally and deploy Apache Airflow using `Helm`.

🫶 By the way, in this documentation, I mainly use `Mac` so, I will try my best to provide the instruction of `Window` but, if there is any issues in `Window`, please Google Search or ask ChatGPT to fix by yourself !

##  A. Using Minikube

### STEP 1: PREPARE DOCKER

I believe every has the `DOCKER` which is a cute 🐳 in your computer, right ?


![DOCKER](../img/docker.jpg)


If not, please follow the [LINK](!https://www.docker.com/get-started/) to install your cute  !

### STEP 2: INSTALL

Mac:

```
brew install minikube
```

For Window or Others: [LINK](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fbinary+download)

If you successfully installed, then:

```python
minikube --help # see the flag
```

<details>

<summary>⚠️ M1 & M2 POTENIAL ISSUE </summary>

<br>

If you see the below warning, please use `arch` command to check the computer is it `arm64` or you changed to x86_64 such as `i386`. If you installed the wrong architecture, please switch and install again !!!

<br>

> You are trying to run the amd64 binary on an M1 system.                                             
> Please consider running the darwin/arm64 binary instead.                                              
> Download at https://github.com/kubernetes/minikube/releases/download/v1.30.1/minikube-darwin-arm64   


However, even I re-install minikube, the warning is still here:

```
minikube config set WantUpdateNotification false
```

Finally, disable the notice. 

</details>

### STEP 3: INTERACT WITH MINIKUBE

```bash 
minikube start --cpus 6 --memory 10240
```

Recommend to use below for not need to `kubectl port-forward` or `remember the node port` providing the user friendly URL like: http://airflow.local/. Thanks for ingress controller ! 

```bash 
minikube status

# It should be:
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured
```


```bash
minikube addons enable ingress 
```

> Please be patient to wait a long time for 🔎  Verifying ingress addon...
> 
> Finally: `The 'ingress' addon is enabled`

Then use this command: 

```bash
minikube tunnel 

# create the router of this clustering minikube
```

You should see the below results:

✅  Tunnel successfully started

📌  NOTE: Please do not close this terminal as this process must stay alive for the tunnel to be accessible ...


<details>

<summary> Other Command </summary>

```bash
minikube start --cpus 6 --memory 10240 --driver=docker # FOr recommded 10 GB and 6cpu from: https://github.com/outerbounds/airflow-on-minikube
minikube start --memory 8192 --cpus 4 # you can set more resources for minikube
minikube statu
minikube stop
minikube start
minikube logs
minikube delete
```

You will see your node as below command:

```bash
kubectl get nodes
```

</details>

## STEP 4 HELM CHART

Install Airlow through `HELM CHART` can be referenec this [LINK](!https://airflow.apache.org/docs/helm-chart/stable/index.html) !

Now, you need to open a new terminal for installing `AIRFLOW` via HELM CHART !


Installing the chart:


```bash
helm repo add apache-airflow https://airflow.apache.org
```

```bash
helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace
# {Helm Chart Release Name} & {Name Space}
```

Please waiting the installation ... 

Check your Helm stats:

```bash
helm status airflow --namespace airflow
```

For checking:

Check Kubernetes pods:

```bash
kubectl get pods -n airflow
```

I TRY  `minikube tunnel` BUT SEEMS NOT WORKING SO:

open another terminal:

You can see the this svc / pod:
```
kubectl get svc -n airflow
```

```bash
Airflow Webserver: kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow
```

> Default username and password in airflow: admin
> 
> Default username and password in postgres: postgres
> 
> Port: 5432

IF WORK: can go to localhost:8080 to go to Airflow. However, it still can help to access to pod when Kubenete run locally.

### DONE ! YOU GUYS MASTER THE KUBUNETE AND HELM CHART RIGHT NOW !!!

Go to http://localhost:8080/

You can login your airflow:


### STEP 5: CONFIG

Next, I have already edit the configuration and done for you:


```
kubectl apply -f Airflow/postgresql-statefulset.yaml

kubectl apply -f Airflow/airflow-webserver.yaml
```

<details>

<summary> How to Config </summary>

helm get values airflow --namespace airflow --all > values.yaml

vim values.yaml

change and update: helm upgrade airflow apache/airflow --namespace airflow -f values.yaml

Check1: helm get values airflow --namespace airflow --all 

Check2: kubectl get pods --namespace airflow

</details>

<details>

<summary> Explain for above command </summary>

Because of the postgresql out of resource:

You need to edit the yaml file:

```
kubectl edit statefulset airflow-postgresql -n airflow
```

kubectl get deployment airflow-webserver -n airflow -o yaml > airflow-webserver.yaml

</detail>


Here is the link of [Production Guide](!https://airflow.apache.org/docs/helm-chart/stable/production-guide.html#webserver-secret-key)
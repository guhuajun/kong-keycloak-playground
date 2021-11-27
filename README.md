# Kong Keycloak Playground

## Introduction

Please feel free to start a discussion for this demo porject. I can help you to understanding this demo. But for a serious setup in production environment, please do ask an expert from Kong and keycloak community.

I am using a Dell T3431 (4x Xeon CPU and 64GB memory) workstation as the host machine, but you can use a different setup, it depends on the number of components that you will use.

## Steps

###  Before you start

Prepare a linux server with Docker installed, like running CentOS in Virulabox.

### Start a local docker registry

Start a local docker registry to 

```bash
docker-compose -f docker-compose.registry.yaml up -d
```

### Install tools

Install k3d

```bash
wget -q -O - https://raw.githubusercontent.com/rancher/k3d/main/install.sh | bash
```

Install helm

```bash
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```

Download latest kubernets dashboard manifest file (Using proxy if you cannot download it directlly)

```bash
curl https://raw.githubusercontent.com/kubernetes/dashboard/v2.1.0/aio/deploy/recommended.yaml --proxy http://localhost:1080 -o recommended.yaml
```

### Certificates

Using EasyPKI to generate cetificates. I am using Contoso in this demo, please feel free to guess my background.

```bash
rm -rf /root/ca

docker run -t --rm -e PKI_ROOT="/opt/ca" -e PKI_ORGANIZATION="Contoso" -e PKI_ORGANIZATIONAL_UNIT="ITO" -e PKI_COUNTRY="US" -e PKI_PROVINCE="WA" -e PKI_LOCALITY="Redmond" -v /root/ca:/opt/ca creatdevsolutions/easypki:v1.0.1 create --filename root --ca "rootca"


docker run -t --rm -e PKI_ROOT="/opt/ca" -e PKI_ORGANIZATION="Contoso" -e PKI_ORGANIZATIONAL_UNIT="ITO" -e PKI_COUNTRY="US" -e PKI_PROVINCE="WA" -e PKI_LOCALITY="Redmond" -v /root/ca:/opt/ca creatdevsolutions/easypki:v1.0.1 create --ca-name root --filename intermediate --intermediate "intca"


docker run -t --rm -e PKI_ROOT="/opt/ca" -e PKI_ORGANIZATION="Contoso" -e PKI_ORGANIZATIONAL_UNIT="ITO" -e PKI_COUNTRY="US" -e PKI_PROVINCE="WA" -e PKI_LOCALITY="Redmond" -v /root/ca:/opt/ca creatdevsolutions/easypki:v1.0.1 create --ca-name intermediate --dns "*.apps.k3d.contoso.com" "*.apps.k3d.contoso.com"


docker run -t --rm -e PKI_ROOT="/opt/ca" -e PKI_ORGANIZATION="Contoso" -e PKI_ORGANIZATIONAL_UNIT="ITO" -e PKI_COUNTRY="US" -e PKI_PROVINCE="WA" -e PKI_LOCALITY="Redmond" -v /root/ca:/opt/ca creatdevsolutions/easypki:v1.0.1 create --ca-name intermediate --dns "*.api.k3d.contoso.com" "*.api.k3d.contoso.com"


docker run -t --rm -e PKI_ROOT="/opt/ca" -e PKI_ORGANIZATION="Contoso" -e PKI_ORGANIZATIONAL_UNIT="ITO" -e PKI_COUNTRY="US" -e PKI_PROVINCE="WA" -e PKI_LOCALITY="Redmond" -v /root/ca:/opt/ca creatdevsolutions/easypki:v1.0.1 create --ca-name intermediate --dns "*.tools.k3d.contoso.com" "*.tools.k3d.contoso.com"
```

Then install root ca cert and intermediate ca cert into your browser. It's Firefox for me.

### Cluster

Create a K3D cluster without Traefik. You may adjust the agents number and other parameters.

```bash
k3d cluster create devbox --agents 4 \
--api-port 127.0.0.1:6443 -p 80:80@loadbalancer -p 443:443@loadbalancer \
--k3s-server-arg "--no-deploy=traefik" --registry-config "registry/registry.yaml"
```

### Traefik

Deploy Traefik 2.0

```bash
helm repo add traefik https://containous.github.io/traefik-helm-chart
cd charts
helm fetch traefik/traefik --untar
kubectl apply -f traefik/ingress.yaml
helm install traefik charts/traefik -f traefik/values.yaml
```

### Kubernetes Dashboard

Deploy Kubernetes Dashboard with SSL protection.

```bash
kubectl apply -f k8s/dashboard/
kubectl apply -f k8s/dashboard/roles/
kubectl create secret tls tools-wildcard-cert --namespace kubernetes-dashboard --key certs/wildcard.tools.k3d.contoso.com.key --cert /root/ca/intermediate/certs/wildcard.tools.k3d.contoso.com.crt
kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep admin-user | awk '{print $1}')
```

### Creates Certificates in K8S default namespace

```bash
kubectl create secret tls apps-wildcard-cert --namespace default --key certs/wildcard.apps.k3d.contoso.com.key --cert /root/ca/intermediate/certs/wildcard.apps.k3d.contoso.com.crt

kubectl create secret tls api-wildcard-cert --namespace default --key certs/wildcard.api.k3d.contoso.com.key --cert /root/ca/intermediate/certs/wildcard.api.k3d.contoso.com.crt

kubectl create secret tls tools-wildcard-cert --namespace default --key certs/wildcard.tools.k3d.contoso.com.key --cert /root/ca/intermediate/certs/wildcard.tools.k3d.contoso.com.crt
```

Create a bundle file

```bash
cat certs/intermediate.crt certs/root.crt > certs/bundle.pem
```

### Monitoring

```bash
kubectl apply -f monitoring/namespace.yaml
kubectl create secret tls tools-wildcard-cert --namespace monitoring --key certs/wildcard.tools.k3d.contoso.com.key --cert /root/ca/intermediate/certs/wildcard.tools.k3d.contoso.com.crt
```

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm search repo prometheus-community
helm fetch prometheus-community/kube-prometheus-stack --untar

helm install -n monitoring prometheues charts/kube-prometheus-stack -f monitoring/values.yaml
helm upgrade -n monitoring prometheues charts/kube-prometheus-stack -f monitoring/values.yaml
```

Change the registry of kube-state-metrics.

```bash
kubectl -n=monitoring patch deployment/prometheues-kube-state-metrics --patch "$(cat monitoring/ksm-patch.yaml)"
```

### Keycloak

```bash
helm repo add codecentric https://codecentric.github.io/helm-charts
cd charts
helm fetch codecentric/keycloak --untar

# import realm file to api.k3d.contoso.com domain

# modify values file then install
helm install keycloak charts/keycloak -f keycloak/values.yaml

# upgrade
helm upgrade keycloak charts/keycloak -f keycloak/values.yaml
```

### Kong

```bash
helm repo add kong https://charts.konghq.com
cd charts/
helm fetch kong/kong --untar

docker pull kong:2.2
docker tag kong:2.2 192.168.0.31:5000/k3d/kong:2.2
# docker pull kong-docker-kubernetes-ingress-controller.bintray.io/kong-ingress-controller:1.1
# docker tag kong-docker-kubernetes-ingress-controller.bintray.io/kong-ingress-controller:1.1 192.168.0.31:5000/k3d/kong-ingress-controller:1.1
```

update values.yaml

```bash
kubectl apply -f kong/namespace.yaml
kubectl create secret tls api-wildcard-cert --namespace kong --key certs/wildcard.api.k3d.contoso.com.key --cert /root/ca/intermediate/certs/wildcard.api.k3d.contoso.com.crt
kubectl create secret tls tools-wildcard-cert --namespace kong --key certs/wildcard.tools.k3d.contoso.com.key --cert /root/ca/intermediate/certs/wildcard.tools.k3d.contoso.com.crt
kubectl -n kong apply -f kong/kong-configmap.yaml
helm install -n kong kong charts/kong -f kong/values.yaml
kubectl -n kong apply -f kong/konga/

# fix name resolution issue for keycloak
kubectl -n=kong patch deployment/kong-kong --patch "$(cat kong/keycloak-patch.yaml)"

# fix wildcard name resolution issue for traefik, replace the name with *.api.k3d.contoso.com or something else.
kubectl -n=kong edit ingress/kong-kong-proxy

# In Kong Contanier, load precreated config
kong config db_import /tmp/kong.yml
```

IMPORTANT: Open Konga, check Paths values in route details. Add '/' to fix issue.

### Applications

```bash
docker-compose -f docker-compose.app.yaml build
docker-compose -f docker-compose.app.yaml push
```

```bash
kubectl apply -f k8s/deploy/locust
kubectl apply -f k8s/deploy/apps
kubectl apply -f k8s/deploy/scapybox
```

#### Locust Tests

```bash
locust --host https://backend01.api.k3d.contoso.com --headless -u 20 -r 2 -t 10s
```

### Keycloak Intialization

Open Keycloak web page, add realm by using relam/realm-export.json file.
create apiadmin user and assign manage-users role in Keycloak Realm (Users -> Role Mappings -> Client Roles -> realm-management)
run python new_users.py

### Clean-ups

```bash
k3d cluster delete devbox
```

## References

[Creating a local development kubernetes cluster with k3s and traefik proxy](https://codeburst.io/creating-a-local-development-kubernetes-cluster-with-k3s-and-traefik-proxy-7a5033cb1c2d)  
[traefik](https://github.com/stevegroom/traefikGateway/blob/master/traefik/docker-compose.yaml)  
[Prometheus](https://github.com/prometheus-community/helm-charts)  
[Keycloak Example](https://github.com/vchrisb/tanzu-ui/blob/29df772a9be89f2b6d11e966e18cc5527c1d555e/kubernetes/keycloak/README.md)  
[OpenID Permissions](https://docs.microsoft.com/zh-cn/graph/permissions-reference#openid-permissions)  
[ID Tokens](https://docs.microsoft.com/en-us/azure/active-directory/develop/id-tokens) 
[Active Directory Claims Mapping](https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-claims-mapping)  
[Azure AD](https://stackoverflow.com/questions/62593370/how-to-set-up-azure-active-directory-to-return-tenant-id-and-other-attributes-to)  
[Token formats and ownership, accessTokenAcceptedVersion](https://docs.microsoft.com/zh-cn/azure/active-directory/develop/access-tokens#token-formats-and-ownership)

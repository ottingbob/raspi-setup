
include env/.env
export $(shell sed 's/=.*//' env/.env)
# Import vars such as:
# REGISTRY_HOST REGISTRY_PORT
REGISTRY_URL := $(REGISTRY_HOST):$(REGISTRY_PORT)

BUILDER_NAME    := pibuilder
IMAGE_NAME      := pibuild
IMAGE_TAG       := 0.0.6
ARM_32_ARCH     := .armv7l
ARM_64_ARCH     := .aarm64
DOCKER_IMG      := $(IMAGE_NAME):$(IMAGE_TAG)
DOCKER_REPO_TAG := $(REGISTRY_URL)/$(DOCKER_IMG)
ARM_32_REPO_TAG := $(DOCKER_REPO_TAG)$(ARM_32_ARCH)
ARM_64_REPO_TAG := $(DOCKER_REPO_TAG)$(ARM_64_ARCH)

new-builder:
	docker buildx create --name $(BUILDER_NAME)

# Naturally this fails with a x509: cert signed up unknown authority error...
# docker buildx build --platform linux/arm64 -t $(DOCKER_REPO_TAG) --push .
#
# docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t $(DOCKER_IMG) --load .
build-arm:
	docker buildx use $(BUILDER_NAME) && \
		docker buildx build --platform linux/arm64 -t $(ARM_64_REPO_TAG) --load . && \
		docker push $(ARM_64_REPO_TAG) && \
		docker buildx build --platform linux/arm/v7 -t $(ARM_32_REPO_TAG) --load . && \
		docker push $(ARM_32_REPO_TAG)

docker-run:
	docker build -t $(DOCKER_IMG) .
	docker run --rm --name pybuildr -p=5000:5000 $(DOCKER_IMG) 

# -addext "subjectAltName = DNS:registry.local-pi.net"
generate-certs:
	mkdir -p certs
	openssl req \
		-newkey rsa:4096 -nodes -sha256 -keyout certs/domain.key \
		-addext "subjectAltName = IP:$(REGISTRY_HOST)" \
		-x509 -days 365 -out certs/domain.crt \
		-subj '/C=US/ST=CA/L=SanFrancisco/O=MyCompany/OU=RND/CN=mysite.com/'
	kubectl create secret generic --from-file=certs/domain.crt --from-file=certs/domain.key --dry-run=client docker-tls-data --namespace docker-registry -o yaml > docker-tls-data.yml

k8s-deploy:
	kubectl create deploy python-arm64 --image $(ARM_64_REPO_TAG) --port=5000 --dry-run=client -o yaml > deploy.yml
	# Make sure we always pull new version
	sed -i '/^.*- image:.*/a \\t\timagePullPolicy: Always' deploy.yml
	sed -i '/^.*resources: {}/c\
		    resources: {}\
	        volumeMounts:\
          - name: host-mon-data\
            mountPath: /app/mon\
      volumes:\
        - name: host-mon-data\
          hostPath:\
            path: /tmp/mon' deploy.yml
	expand -t 4 deploy.yml > deploy2.yml
	mv deploy2.yml deploy.yml

k8s-svc:
	kubectl create svc nodeport python-arm64 --tcp=5000:5000 --node-port=30005 --dry-run=client -o yaml > pysvc.yml

k8s-yamls: k8s-deploy k8s-svc

generate: build-arm k8s-yamls

send-k8s-files:
	./scripts/send-files.sh ubuntu $(REGISTRY_HOST) deploy.yml pysvc.yml

send-mon-scripts:
	./scripts/send-files.sh ubuntu $(REGISTRY_HOST) scripts/mon.py
	./scripts/send-files.sh ubuntu $(NFS_HOST) scripts/mon.py

clean:
	rm -r certs/ __pycache__/ deploy.yml pysvc.yml tags > /dev/null 2>&1

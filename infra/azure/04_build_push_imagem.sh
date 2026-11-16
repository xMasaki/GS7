#!/usr/bin/env bash
# =====================================================================
#  AcessaCidade — 04. Build e push da imagem para o Azure Container Registry
# =====================================================================
#  Classificação dos comandos deste script:
#    az acr show / az acr repository show-tags ................ [SOMENTE LEITURA]
#    az acr login ............................................. [SOMENTE LEITURA] (token temporário no Docker local)
#    az acr build ............................................. [CRIA RECURSOS/CUSTO] (ACR Tasks: build na nuvem;
#                                                               NÃO exige Docker local)
#    docker build / docker push ............................... [CRIA RECURSOS/CUSTO] (armazenamento no ACR)
#  Uso (na raiz do repositório):
#    ACR_NAME="<acr>" TAG="<tag>" MODO=acrbuild|docker ./infra/azure/04_build_push_imagem.sh
#  Se a assinatura bloquear ACR Tasks ("TasksOperationsNotAllowed"), use MODO=docker.
# =====================================================================
set -euo pipefail
: "${ACR_NAME:?Defina ACR_NAME (terraform output -raw acr_name)}"
IMAGE_NAME="${IMAGE_NAME:-acessacidade}"
MODO="${MODO:-acrbuild}"
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
TAG="${TAG:-$(git rev-parse --short=12 HEAD 2>/dev/null || date +manual-%Y%m%d%H%M)}"
DOCKERFILE="06-Secure-DevOps-Cloud/docker/Dockerfile"

# [SOMENTE LEITURA]
LOGIN_SERVER="$(az acr show --name "$ACR_NAME" --query loginServer --output tsv)"
IMAGEM="${LOGIN_SERVER}/${IMAGE_NAME}:${TAG}"
echo "Imagem: ${IMAGEM}"

if [ "$MODO" = "acrbuild" ]; then
  # [CRIA RECURSOS/CUSTO] build na nuvem (não precisa de Docker)
  az acr build --registry "$ACR_NAME" --image "${IMAGE_NAME}:${TAG}" --file "$DOCKERFILE" --build-arg "VCS_REF=${TAG}" .
else
  # [CRIA RECURSOS/CUSTO]
  docker build -f "$DOCKERFILE" -t "$IMAGEM" --build-arg "VCS_REF=${TAG}" .
  # [SOMENTE LEITURA]
  az acr login --name "$ACR_NAME"
  docker push "$IMAGEM"
fi

# [SOMENTE LEITURA]
az acr repository show-tags --name "$ACR_NAME" --repository "$IMAGE_NAME" --orderby time_desc --top 5 --output table
echo
echo "Próximo passo (fase 2): terraform apply -var deploy_container=true -var image_tag=${TAG}"

# Operar o pacote com Devin

Este é o roteiro operacional, não uma skill instalada no Devin. Comece aqui após baixar o repositório. Não precisa do histórico do chat. Não existem credenciais incluídas.

## 1. Validar o pacote sem AWS

Pré-requisitos: Linux/macOS, Python 3.10+, AWS CLI v2, Terraform 1.9+ e Docker quando for executar containers. Terraform 1.13.4 é a versão usada na validação local. O provider AWS está fixado; upgrades exigem nova validação.

```bash
python3 -m unittest discover -s tests -v
terraform -chdir=infra/terraform init -backend=false
terraform -chdir=infra/terraform validate
terraform -chdir=infra/terraform test
```

O teste Terraform usa provider simulado; não cria recursos. Init baixa o provider. A disponibilidade de ferramentas não comprova acesso à conta.

## 2. Preparar configuração local

Copie o exemplo para um arquivo ignorado pelo Git e substitua TODOS os identificadores fictícios:

```bash
mkdir -p .local
cp config/environment.example.json .local/environment.json
chmod 600 .local/environment.json
```

Preencher profile, conta confirmada independentemente, região, VPC, subnet, AMI Amazon Linux 2023 x86_64 homologada, tipo x86_64, owner, data de revisão de custos, retenção e egress TCP permitido. A instância m6i.xlarge e retenção 30 dias do exemplo NÃO são sizing ou política aprovados.

Não colocar token, secret, senha ou kubeconfig nesse JSON. Campos desconhecidos são rejeitados. Este módulo não suporta AMI corporativa customizada sem adaptação revisada.

Você autentica no ambiente onde o Devin executa:

```bash
aws sso login --profile NOME_DO_PROFILE
python3 scripts/poc.py preflight --config .local/environment.json --out .local/preflight.json
python3 scripts/poc.py tfvars --config .local/environment.json --out .local/environment.tfvars.json
```

Os scripts não sobrescrevem arquivos. Para nova tentativa use outro nome; preserve a evidência antiga. Preflight confirma STS e subnet/VPC; não testa acesso à aplicação nem todas as permissões de provisionamento.

## 3. Revisar ambiente antes do plan

O Devin deve apresentar conta, região, subnet/VPC, AMI, sizing, retenção, destino dos testes, orçamento e motivo das regras de saída. Não derive conta esperada apenas do retorno do profile; compare com a conta autorizada.

- EC2 será privada, sem SSH/ingress; acesso por SSM.
- É necessário caminho de saída para SSM, pacotes AL2023, registros de imagens e S3, além dos alvos. Egress explícito no SG não cria rotas/NAT/endpoints.
- NAT, VPC endpoints, DNS, acesso aos alvos e permissões dos leitores NÃO são criados por este módulo.
- Não ampliar egress para toda a internet sem revisão. Sem caminho de pacotes/SSM, o bootstrap pode falhar mesmo com apply bem-sucedido.
- Role da EC2: SSM e acesso ao prefixo dast/ do bucket criado. Não leva SSO do operador. Containers não recebem automaticamente credenciais do host.
- S3 usa SSE-S3 e versionamento. Se houver exigência de KMS, permissions boundary, SCP ou backend remoto, adaptar antes de aplicar.
- Backend é local nesta primeira versão; proteger e transferir state por canal corporativo aprovado. Não operar simultaneamente com states diferentes.

Para Kubernetes, consultar apenas o contexto e namespace escolhidos:

```bash
kubectl --context CONTEXTO -n NAMESPACE get deployments,services,ingresses -o wide
argocd --server SERVIDOR app get APLICACAO -o tree
```

Esses comandos não são necessários para hospedar a EC2. Não executar sync, refresh forçado, ler Secrets nem exportar manifests completos como parte da descoberta.

## 4. Gerar e revisar o plano de infraestrutura

Execute em um subshell sem credenciais de ambiente que possam prevalecer sobre o profile:

```bash
(
  unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_SECURITY_TOKEN
  unset AWS_ROLE_ARN AWS_WEB_IDENTITY_TOKEN_FILE AWS_CONTAINER_CREDENTIALS_FULL_URI
  unset AWS_CONTAINER_CREDENTIALS_RELATIVE_URI AWS_DEFAULT_PROFILE
  export AWS_EC2_METADATA_DISABLED=true
  terraform -chdir=infra/terraform init
  terraform -chdir=infra/terraform plan -var-file=../../.local/environment.tfvars.json -out=../../.local/provision.tfplan
)
```

Não commitar state, plano ou tfvars. Apresentar o plan e obter autorização da criação, permissões e custos. Não há script de auto-apply.

Após aprovação, repetir a conferência STS com o mesmo profile e usar o mesmo ambiente limpo do comando acima:

```bash
terraform -chdir=infra/terraform apply ../../.local/provision.tfplan
terraform -chdir=infra/terraform output
```

Revisar plano antigo se configuração, sessão ou janela mudar. Usar o comando SSM exibido no output. Verificar no host:

```bash
sudo cloud-init status --wait
sudo systemctl is-active docker amazon-ssm-agent
python3 --version
```

Bootstrap instala Docker/Python; não baixa este Git, não instala Compose, não transfere aplicações e não inicia scanners. Transferir código revisado por mecanismo autorizado, sem PAT na instância. O port dos scanners ainda precisa ser concluído.

## 5. Experimentar medição e HTML agora

Exemplo totalmente local, sem scan:

```bash
python3 scripts/measure.py --run-id demo-local --synthetic --timeout 10 --out .local/demo-run -- python3 -c "print('demonstracao de medicao')"
python3 scripts/poc.py report --input .local/demo-run/execution.json --out .local/demo-report
python3 scripts/poc.py verify --directory .local/demo-report
```

Abrir .local/demo-report/index.html no navegador. Outro exemplo inclui achado e cobertura fictícios:

```bash
python3 scripts/poc.py report --input examples/execution.synthetic.json --out .local/example-report
```

Para uma execução real, substituir o comando após -- pelo comando autorizado; omitir --synthetic. Nunca passar segredos como argumentos. Opcional: repetir --container NOME para coletar docker stats de containers existentes identificados. O coletor não descobre nem lança containers.

O medidor registra tempo monotônico, início/fim, código de saída, timeout e recursos dos subprocessos locais. CPU/memória do docker CLI não são os recursos do workload: estes exigem --container. Não há ainda collector de métricas do alvo, preços AWS ou importador nativo de findings dos scanners.

Timeout encerra o grupo de processos local. Containers detached/remotos podem continuar: conferir e encerrar somente os recursos identificados do run. O limite não é um mecanismo completo de segurança de scan. Códigos não-zero do scanner podem significar achados, não falha do motor; o medidor guarda o código, e a classificação DAST depende do futuro adaptador.

Arquivos stdout.raw.log e stderr.raw.log são privados e podem conter segredos. Não são incluídos no HTML. O filtro do relatório é uma defesa adicional, não um sanitizador universal: revisão humana antes de publicação.

## 6. Publicar somente o pacote revisado

Preencher bucket e chave a partir dos outputs e da identidade do run. Confirmar o hash do manifesto em registro independente.

```bash
python3 scripts/poc.py verify --directory .local/demo-report
aws s3 cp .local/demo-report/ s3://BUCKET/dast/APLICACAO/AMBIENTE/RELEASE/COMMIT/RUN/ --recursive --profile NOME_DO_PROFILE --region REGIAO --only-show-errors
```

Use a pasta do relatório real após revisão, não a pasta raw. Verificar identidade da conta antes de upload e que o run ainda não existe. Para consulta autenticada, baixar index.html via AWS CLI/console e abrir localmente. Site público e URL pré-assinada não são criados automaticamente. Link no GitHub summary não concede acesso ao S3.

## 7. Revisão obrigatória pelo Devin

Entregar ao operador: divergências do ambiente, plano de recursos/custo, resultado de preflight, testes locais, evidência de bootstrap, limitações e próximo passo. Não declarar DAST concluído porque a infraestrutura subiu.

Sem auto-destroy. ExpiresOn é só tag: marcar responsável por parar/remover a instância. EBS, S3 e versões anteriores podem continuar cobrando. A retenção das versões antigas conta a partir de quando se tornam não atuais, podendo exceder a janela nominal. Bucket não vazio bloqueia destroy; revisar retenção/exportação antes de limpeza. Jamais usar force_destroy para contornar isso.

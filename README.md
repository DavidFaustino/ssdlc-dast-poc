# SSDLC DAST PoC

Validar DAST em dois microserviços no playground AWS, medindo segurança, tempo, consumo de recursos e custo. Publicar relatório HTML privado com evidências e orientação de correção. **DefectDojo fica para a segunda etapa.**

**Estado em 07/10/2026:** pacote operacional inicial implementado localmente: diagnóstico AWS somente leitura, geração de tfvars, Terraform EC2/S3/IAM, medição de comandos, relatório HTML e verificação de integridade. Infraestrutura não provisionada; integração completa dos scanners e skill Devin ainda pendentes.

**Primeiro marco:** métricas e conclusão de duas aplicações de teste, condicionadas à disponibilidade dos alvos, acessos e execução. Prazos e destinatários específicos ficam fora deste repositório.

## Comece aqui

**Para usar o que já está pronto:** [RUNBOOK do Devin](docs/RUNBOOK-DEVIN.md). Ele contém os comandos completos desde SSO até revisão do Terraform, medição e publicação manual. Execute primeiro os testes locais, sem AWS:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/poc.py --help
python3 scripts/poc.py report --input examples/execution.synthetic.json --out .local/example-report
```

Abra .local/example-report/index.html. É um exemplo sintético, não resultado de scan. O comando recusa sobrescrever uma pasta existente.

### Arquivos operacionais

- scripts/poc.py: preflight STS/subnet, configuração Terraform, HTML e manifesto/verificação.
- scripts/measure.py: tempo, exit code, timeout, recursos dos subprocessos e docker stats opcional.
- infra/terraform/: EC2 privada em VPC/subnet existentes, role SSM/S3, bucket privado e testes simulados.
- config/environment.example.json: parâmetros fictícios para substituir localmente; sem credenciais.
- examples/execution.synthetic.json: exemplo de entrada do relatório.
- tests/: testes de regressão sem chamadas reais à AWS.

O medidor executa somente o comando explicitamente fornecido pelo operador. Ele não descobre alvos, implementa autenticação de APIs nem configura scanners sozinho. O HTML inicial apresenta dados normalizados; adaptadores ZAP/Nuclei/Schemathesis, métricas do alvo e cálculo de preços ainda precisam ser conectados.

| Preciso entender | Onde consultar |
|---|---|
| Desenho e escolhas de infraestrutura | [Arquitetura](docs/ARQUITETURA.md) |
| Funcionalidades, etapas e critérios de entrega | [Plano](docs/PLANO.md) |
| Relatório, evidências, métricas e FinOps | [Contrato de resultados](docs/RESULTADOS-E-METRICAS.md) |
| Assumir o trabalho durante as férias | [Passagem de trabalho](docs/HANDOFF.md) |
| O que já foi testado e pode ser reutilizado | [Histórico e origem](docs/HISTORICO-E-REUSO.md) |

Para a primeira revisão, leia **este README e Arquitetura**. O restante é consulta por tarefa.

## Escopo da primeira entrega

- Dois alvos identificados por aplicação, ambiente, release, commit e digest.
- ZAP, Nuclei, Schemathesis e testes direcionados aplicáveis ao escopo autorizado.
- Trace de execução, métricas dos executores e, quando acessível, do alvo.
- HTML técnico, métricas e evidências sanitizadas no S3 privado.
- Contexto de remediação e especificação da skill reutilizável para Devin Enterprise.
- Resultado repetível, com limitações explícitas; sem promessa de cobrir milhares de serviços.

Fora desta entrega: DefectDojo, IAST/RASP, agente AI local, novos dashboards Wiz e plataforma completa de escala. O disparo pós-ArgoCD é evolução; não bloqueia a medição manual no playground.

## Estrutura e crescimento

Este repositório pessoal é o ponto de manutenção do pacote portátil e genérico. Evidências históricas e configurações específicas de organizações ficam fora dele. Não duplicar estes planos em outro dossiê.

Código atual está em scripts/, infra/ e tests/. A skill Devin e o port dos scanners serão adicionados depois; o RUNBOOK já orienta o agente sem depender de instalação de skill. Resultados reais e configuração ficam em .local/ ou armazenamento autorizado, fora do Git.

## Validação antes do GitHub

- [ ] Aprovar arquitetura e executor do playground.
- [ ] Definir se os alvos serão corporativos autorizados ou aplicações-modelo.
- [ ] Nomear executor e substituto; confirmar acessos e datas.
- [x] Mantenedor autorizou publicação do pacote genérico no repositório pessoal em 07/10/2026.
- [x] URL recebida; visibilidade pública solicitada explicitamente pelo mantenedor.
- [x] Conteúdo selecionado revisado; configurações reais, estado Terraform e evidências locais excluídos.

Repositório privado não substitui autorização corporativa. Não inserir dados internos para “completar” exemplos. Consulte as regras de [trabalho para agentes](AGENTS.md).

# Plano e funcionalidades

**Estado em 07/10/2026:** documentação e pacote operacional inicial preparados. Scripts de preflight, medição, relatório e Terraform disponíveis; integração completa dos scanners ainda pendente. Não há autorização implícita para scan ou provisionamento.

## Etapas e critérios de saída

| Etapa | Trabalho | Pronto quando | Dependência |
|---|---|---|---|
| 0 — Revisar | Arquitetura, escopo e substituto | Decisões registradas no handoff | Validação do solicitante |
| 1 — Empacotar | Reaproveitar código local, retirar dependência obrigatória de DefectDojo, fixar versões | Execução sintética reproduzível com instruções reais | Revisão de código/licenças/segredos |
| 2 — Preparar AWS | Executor, conectividade, identidade, armazenamento e telemetria | Preflight dos dois alvos aprovado | Acessos e escopo autorizados |
| 3 — Executar | Perfis definidos e repetições comparáveis | Evidências por alvo/perfil com estados explícitos | Estabilidade e massa de teste |
| 4 — Relatar | HTML, pacote de evidências, custo e contexto de correção | Publicação privada consultável e hashes conferidos | Sanitização e revisão humana |
| 5 — Concluir | Comparativo, limites e recomendação | Entrega revisada para destinatários autorizados | Validação do responsável |

Sequência sugerida: primeiro revisão/acessos/preflight; depois execução e consolidação; por fim revisão e entrega. O cronograma de cada adoção fica no seu controle privado. Atraso de acesso exige replanejar ou usar modelos, nunca inventar métricas.

## Funcionalidades previstas na primeira etapa

- [ ] Preflight: autorização, URL permitida, contrato, conectividade, sessão e identidade da release.
- [ ] Execução limitada por ferramenta, alvo e perfil; timeout/retry explícitos.
- [ ] Eventos por etapa e métricas temporais, incluindo falhas.
- [ ] Normalização sem esconder proveniência nem fundir achados sem critério.
- [ ] HTML com três visões: segurança, execução/validação, desempenho/FinOps.
- [ ] Publicação privada por aplicação/versão/run e link no summary do GitHub quando integrado.
- [ ] Roteiro de correção por achado e contexto consumível pelo Devin.
- [ ] Especificar, implementar e validar a skill Devin no formato suportado pela integração Enterprise.
- [ ] Verificar isolamento, limites, sanitização, integridade e cleanup.

Para cumprir a data, priorizar execução e evidências. Integração automática GitHub/ArgoCD e instalação da skill podem ficar pendentes explicitamente; não bloquear o relatório manual por esses itens. Achados relevantes continuam exigindo orientação de investigação.

## Experimento de desempenho

Medir execução de um alvo por vez antes de aumentar concorrência. Proposta: uma inicialização fria identificada e três repetições comparáveis por perfil prioritário, se a janela permitir. Informar o número real de amostras. Não prometer p95 representativo com poucas observações.

Comparar sequencial/paralelo apenas mantendo escopo, versão, limites e massa equivalentes. Separar impacto da aplicação de contenção do host e tráfego externo. Definir limiares de erro/latência/recursos com o owner antes do teste e interromper quando atingidos.

## Validações obrigatórias do pacote

- Alvo fora da allowlist, redirecionamento indevido ou segredo exposto: execução/publicação bloqueada.
- Token expirado ou rota protegida não exercitada: estado explícito, nunca sucesso silencioso.
- Timeout ou relatório obrigatório ausente: parcial/bloqueado conforme a condição.
- Alvo mudou de versão: não aproveitar como aprovação da versão final.
- Evidência adulterada: conferência do manifesto deve acusar divergência.
- HTML: conteúdo do alvo escapado; nenhum script ou markup injetado por resposta HTTP.
- Pacote de relatório deve abrir sem depender do filesystem do notebook.
- Reteste cria outro run e referencia o anterior; não sobrescreve evidência histórica.

## Implementação do pacote operacional em 07/10

Autorizada a preparação local pelo solicitante; sem apply, scan ou push. Implementação nesta sessão, preservando o repositório recém-criado ainda sem commit.

- [x] Testar primeiro CLI de preflight/tfvars, rejeição de conta divergente, campos secretos, sobrescrita e HTML inseguro.
- [x] Implementar scripts Python sem dependências externas; preflight só leitura e parâmetros explícitos.
- [x] Implementar Terraform EC2 privada em rede existente, S3 privado e role limitada; validar configuração sem AWS.
- [x] Implementar medidor com timeout e relatório/manifesto; testes de falha, timeout e adulteração.
- [x] Entregar RUNBOOK para Devin, exemplos genéricos e atualizar README/handoff com limites reais.

Decisão de implementação: EC2 é opção preparada, não arquitetura corporativa aprovada. O port completo dos scanners permanece separado; esta entrega permite provisionar após revisão, diagnosticar e medir comandos autorizados. Testes locais não chamam AWS nem scanners reais. Publicação do pacote genérico em repositório público autorizada pelo usuário em 07/10/2026; essa autorização não inclui implantação ou scans.

## Segunda etapa

DefectDojo e ciclo integrado de achados; trigger pós-ArgoCD e gate de promoção; fila, quotas, autoscaling e dimensionamento em QA. IAST/RASP e agentes AI locais permanecem fora da primeira entrega.

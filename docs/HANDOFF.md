# Passagem de trabalho

Atualizado em **07/10/2026**. Ponto de retomada: pacote operacional local disponível; usar [RUNBOOK do Devin](RUNBOOK-DEVIN.md) para preencher parâmetros, conferir ambiente e revisar o plan antes de provisionar.

## Situação em uma página

| Item | Situação |
|---|---|
| Documentação e desenhos | Criados para validação |
| Git local | Branch main; origin DavidFaustino/ssdlc-dast-poc; pacote preparado para publicação |
| GitHub remoto | Publicação e mudança para público autorizadas pelo mantenedor em 07/10/2026; consultar GitHub para estado atual |
| Código executável deste pacote | preflight/tfvars, medidor, HTML/manifesto e Terraform EC2/S3 implementados; port dos scanners pendente |
| Playground e alvos | Acesso, executor e dois serviços por confirmar |
| Relatórios AWS | Ainda não gerados |
| Skill Devin | Requisitos registrados; não implementada/instalada |
| DefectDojo | Segunda etapa, não dependência atual |

## Decisões pendentes para destravar

| Pergunta | Quem precisa responder | Registro |
|---|---|---|
| Cluster pronto ou EC2 temporária? Região? | Solicitante e responsável de infraestrutura | Pendente |
| Dois serviços, versões, rotas e identidades autorizadas? | Owners das aplicações | Pendente |
| APIs reais acessíveis ou modelos no playground? | Solicitante e infraestrutura | Pendente |
| S3, acesso autenticado e retenção? | Responsáveis corporativos | Pendente |
| Limites de impacto e janela de teste? | Owners e operador | Pendente |
| Quem executa e quem assume nas férias? | Solicitante | Nomes, disponibilidade e acessos pendentes |
| Aprovação de conteúdo no Git pessoal? | Solicitante | Publicação do pacote genérico e visibilidade pública autorizadas em 07/10/2026; configurações reais e evidências excluídas |

Papéis acima são propostas de participação, não pessoas já designadas. Não registrar credenciais nesta tabela.

## Primeiro dia de quem assumir

1. Ler README e Arquitetura, depois conferir esta lista.
2. Verificar branch, alterações locais e último commit; não sobrescrever trabalho em andamento.
3. Confirmar os itens de acesso/autorização antes de qualquer ação de rede.
4. Retomar a primeira etapa não concluída do Plano. Não reinstalar o laboratório nem reexecutar todos os estudos por falta de contexto.
5. Ao concluir: atualizar estado, evidência, próximo passo e bloqueio nesta página. Resultados experimentais novos pertencem ao armazenamento autorizado.

## Histórico deste pacote

- **07/10/2026 — verificação local:** 11 testes Python aprovados; Terraform formatado e validado, com 2 testes de plano usando AWS simulada aprovados; bootstrap com sintaxe verificada; integridade do relatório sintético verificada. Revisão corrigiu encerramento de descendentes em timeout, cancelamento SIGTERM com evidência parcial e mensagens de configuração que poderiam expor valores. Isto não valida implantação real nem cobertura DAST.
- **07/10/2026:** requisitos organizados a partir da discussão: dois serviços, playground primeiro, relatório HTML privado, métricas/evidências, FinOps, apoio Devin e DefectDojo posteriormente.
- **07/10/2026 — preparação operacional:** scripts Python e opção Terraform EC2 criados; validar os comandos pelo RUNBOOK. Sem apply, scan, push ou acesso AWS nesta preparação.
- Próxima ação: conferir o ambiente via preflight no computador de trabalho, revisar se EC2 atende, preencher os parâmetros locais e revisar o plan. Completar port de scanners e importadores de findings antes de prometer relatório DAST completo.

## Contingência do prazo

Se rede/identidade não estiverem disponíveis em tempo, decidir explicitamente entre aplicações-modelo e replanejamento. Se uma coleta falhar, informar a lacuna. Não fabricar números para cumprir prazo. Se houver falha de isolamento, credencial exposta ou impacto acima do limite acordado, parar e registrar pelo processo autorizado.

# Contribuir

Usar uma branch curta por requisito, por exemplo `feat/REQ-F-009-stock`. Commits futuros devem explicar problema e efeito, e referenciar o ID do requisito quando aplicável. Não alterar a prompt original nem incluir `instance/`, contas reais ou segredos.

Instalar `requirements-dev.txt`; executar `scripts/check.py` com `PYTHONPATH=src` e, para fluxos visuais, `scripts/e2e.py`. Alterações de domínio exigem cenários positivos, erros, permissões e invariantes relevantes. Não criar testes artificiais para uma percentagem de cobertura.

Atualizar requisitos/matriz/manuais e ADRs quando a decisão mudar. Criar PR com resultado de checks e evidência. Exigir revisão de outro elemento e CI verde antes de merge/release. Sem equipa/revisor configurado nesta entrega, essa aprovação permanece pendente.

Usar SemVer; criar tags `vMAJOR.MINOR.PATCH` apenas para releases efetivamente aprovadas. Não reescrever histórico partilhado. Dependabot propõe updates; rever compatibilidade e scan antes de aceitar. Proteger a branch principal no alojamento quando o repositório for publicado.

Licenciamento de distribuição a confirmar pelo titular, ver LICENSE. Não foi criado um código de conduta de comunidade porque não existe comunidade estabelecida nesta baseline; deve ser adotado se for aberta a contribuições públicas.

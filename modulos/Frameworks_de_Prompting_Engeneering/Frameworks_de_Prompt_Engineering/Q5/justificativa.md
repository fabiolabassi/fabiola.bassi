O componente Before reproduz o manifest original com diagnóstico explícito dos 7 problemas: réplica única, :latest, secrets em plaintext, ausência de resources/probes/securityContext e falta de pdb.

O componente After especifica cada requisito da versão modernizada em checklist numerado (réplicas, imagem, secretKeyRef, resources, probes, securityContext, RollingUpdate, pdb) com valores e nomes concretos (chronos-api-secrets, /healthz, /ready, runAsUser: 1000)

O componente Bridge instrui sobre o formato de saída (dois YAMLs separados por ---, comentários inline explicativos, sem markdown externo), funcionando como a ponte entre o estado atual e o entregável esperado yaml válido pronto para kubectl apply.
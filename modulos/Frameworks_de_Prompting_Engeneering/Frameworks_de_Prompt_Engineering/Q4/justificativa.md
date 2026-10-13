O componente Task especifica inequivocamente o entregável. Query sqk para postgresql, recorte de 6 meses a partir de 2026-04-24, groupby mês+categoria, duas métricas, e o uso final (gráficos de crescimento para apresentação da pm ao CEO).

O componente Action fornece o DDL completo das tabelas, as regras de negócio explícitas (filtro de status, conversão de centavos, formato YYYY-MM com TO_CHAR, nomes exatos das colunas de saída), eliminando qualquer suposição por parte do modelo sobre o schema.

O componente Goal orienta para qualidade de execução, usar índices existentes, evitar ctes desnecessárias, retornar exatamente as colunas esperadas e entregar apenas sql puro (sem markdown), alinhando o output ao uso direto no ledger e na apresentação.
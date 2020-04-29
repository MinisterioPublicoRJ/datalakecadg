# Datalake CADG

Serviço para recebimento de dados de parceiros do Estado do Rio de Janeiro
pelo convênio firmado entre MPRJ e Governo do Estado do Rio de Janeiro.

[https://datalakecadg.mprj.mp.br](https://datalakecadg.mprj.mp.br)

# Executando testes de integração com HDFS

```
chmod +x integrations_tests.sh

./integrations_tests.sh METHOD_NAME USERNAME SECRET_KEY HDFS_URI [FILEPATH, SCHEMA_PATH]
```

`FILEPATH` = caminho até o arquivo que será enviado ao HDFS com extensão .csv.gz

`SCHEMA_PATH` = caminho até o arquivo contendo o schema com extensão .json

**OBS**: Caso os argumentos `FILEPATH` e `SCHEMA_PATH` não forem fornecidos, o teste
será executado com os arquivos que estão em `methodmapping/tests/fixtures/`

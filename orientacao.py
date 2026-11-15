class Orientacao:
    def __init__(
        self,
        id: int,
        categoria: str,
        titulo: str,
        palavras_chave: list[str],
        resposta: str,
        documentos: list[str],
        onde: str,
        fonte: str,
        verificado_em: str,
    ):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    def exibir(self) -> None:
        print(f"\n{self.titulo} [{self.categoria}]")
        print(self.resposta)
        print("Documentos necessários:")
        for documento in self.documentos:
            print(f"  - {documento}")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print("Aviso: este assistente não é canal oficial.")

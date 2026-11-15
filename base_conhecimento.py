from datetime import date

class BaseConhecimento:
    def __init__(
            self, 
                categoria: str, 
                titulo: str, 
                palavras_chave: list[str], 
                resposta: str, 
                documentos: list[str], 
                onde: str, 
                fonte: str, 
                verificado_em: date
        ):
        
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = []
    
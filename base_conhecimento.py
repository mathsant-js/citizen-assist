import json
import unicodedata
from pathlib import Path

from orientacao import Orientacao


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    caracteres = []
    for caractere in texto:
        if unicodedata.combining(caractere):
            continue
        caracteres.append(caractere if caractere.isalnum() else " ")
    return " ".join("".join(caracteres).split())


class BaseConhecimento:
    def __init__(self, caminho: str | Path):
        self.caminho = Path(caminho)
        self.orientacoes: list[Orientacao] = []

    def carregar(self) -> None:
        with self.caminho.open(encoding="utf-8") as arquivo:
            registros = json.load(arquivo)
        if not isinstance(registros, list):
            raise ValueError("A base de conhecimento deve conter uma lista de orientações.")
        self.orientacoes = [Orientacao(**registro) for registro in registros]

    def categorias(self) -> list[str]:
        return list(dict.fromkeys(orientacao.categoria for orientacao in self.orientacoes))

    def por_categoria(self, categoria: str) -> list[Orientacao]:
        return [
            orientacao for orientacao in self.orientacoes
            if orientacao.categoria == categoria
        ]

    def pontuar(self, pergunta: str, orientacao: Orientacao) -> int:
        pergunta = normalizar(pergunta)
        pergunta_delimitada = f" {pergunta} "
        palavras_chave = {normalizar(termo) for termo in orientacao.palavras_chave}
        palavras_chave.discard("")
        pontos_palavras_chave = 3 * sum(
            f" {termo} " in pergunta_delimitada for termo in palavras_chave
        )

        palavras_titulo = set(normalizar(orientacao.titulo).split())
        palavras_pergunta = {palavra for palavra in pergunta.split() if len(palavra) >= 4}
        return pontos_palavras_chave + len(palavras_pergunta & palavras_titulo)

    def buscar(self, pergunta: str) -> list[tuple[int, Orientacao]]:
        resultados = [
            (self.pontuar(pergunta, orientacao), orientacao)
            for orientacao in self.orientacoes
        ]
        return sorted(resultados, key=lambda resultado: resultado[0], reverse=True)

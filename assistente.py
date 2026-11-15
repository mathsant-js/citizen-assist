import csv
from datetime import date
from pathlib import Path
from time import time

from base_conhecimento import BaseConhecimento


class Assistente:
    def __init__(self, nome: str, base: BaseConhecimento):
        self.nome = nome
        self.base = base
        self.historico: list[dict] = []

    def perguntar(self) -> None:
        inicio = time()
        while True:
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()
            if pergunta == "0":
                return
            if not pergunta:
                print("Digite uma pergunta.")
                continue
            if "@" in pergunta or sum(caractere.isdigit() for caractere in pergunta) >= 8:
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva a pergunta.")
                continue
            break

        resultados = self.base.buscar(pergunta)
        if not resultados or resultados[0][0] < 3:
            print("Não encontrei uma orientação. Tente outras palavras ou navegue por categoria.")
            self.registrar("pergunta", pergunta, None, False, 1, inicio)
            return

        pontos, orientacao = resultados[0]
        confianca = "ALTA" if pontos >= 6 else "MÉDIA"
        print(f"\nConfiança da resposta: {confianca} ({pontos} pontos)")
        orientacao.exibir()

        alternativas = [
            alternativa.titulo
            for pontos_alternativa, alternativa in resultados[1:3]
            if pontos_alternativa >= 3
        ]
        if alternativas:
            print("\nOutras orientações relacionadas:")
            for titulo in alternativas:
                print(f"  - {titulo}")

        ajudou = self._pedir_feedback()
        self.registrar("pergunta", pergunta, orientacao.id, ajudou, 1, inicio)

    def navegar(self) -> None:
        inicio = time()
        categorias = self.base.categorias()
        if not categorias:
            print("Nenhuma categoria disponível.")
            return

        while True:
            print("\nCategorias")
            opcao = self._escolher(categorias)
            if opcao == 0:
                return

            categoria = categorias[opcao - 1]
            print(f"\n{categoria}")
            orientacoes = self.base.por_categoria(categoria)
            opcao = self._escolher([orientacao.titulo for orientacao in orientacoes])
            if opcao == 0:
                continue

            orientacao = orientacoes[opcao - 1]
            orientacao.exibir()
            ajudou = self._pedir_feedback()
            self.registrar("categoria", "", orientacao.id, ajudou, 1, inicio)
            return

    def registrar(
        self,
        origem: str,
        pergunta: str,
        id_orientacao: int | None,
        ajudou: bool,
        tentativas: int,
        inicio: float,
    ) -> None:
        self.historico.append({
            "data": date.today().isoformat(),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": id_orientacao is not None,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": round(time() - inicio, 1),
        })

    def indicadores(self) -> dict:
        total = len(self.historico)
        encontrados = [registro for registro in self.historico if registro["encontrou"]]
        return {
            "respostas_encontradas": round(100 * len(encontrados) / total, 1) if total else 0.0,
            "taxa_acerto": (
                round(100 * sum(registro["ajudou"] for registro in encontrados) / len(encontrados), 1)
                if encontrados else 0.0
            ),
            "tempo_medio": (
                round(sum(registro["tempo_segundos"] for registro in encontrados) / len(encontrados), 1)
                if encontrados else 0.0
            ),
            "tentativas_por_atendimento": (
                round(sum(registro["tentativas"] for registro in self.historico) / total, 1)
                if total else 0.0
            ),
            "duvidas_sem_solucao": [
                registro["pergunta"] for registro in self.historico
                if registro["pergunta"] and not registro["ajudou"]
            ],
        }

    def exportar_csv(self, caminho: str | Path = "data/atendimentos.csv") -> None:
        campos = [
            "data", "origem", "pergunta", "id_orientacao", "encontrou",
            "ajudou", "tentativas", "tempo_segundos",
        ]
        with Path(caminho).open("w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(self.historico)

    @staticmethod
    def _escolher(opcoes: list[str]) -> int:
        escolhas = {str(numero): numero for numero in range(len(opcoes) + 1)}
        for numero, rotulo in enumerate(opcoes, start=1):
            print(f"{numero}. {rotulo}")
        print("0. Voltar")
        while True:
            entrada = input("Escolha uma opção: ").strip()
            if entrada in escolhas:
                return escolhas[entrada]
            print("Opção inválida.")

    @staticmethod
    def _pedir_feedback() -> bool:
        while True:
            resposta = input("Essa orientação respondeu sua dúvida? (s/n): ").strip().lower()
            if resposta in ("s", "n"):
                return resposta == "s"
            print("Digite s ou n.")

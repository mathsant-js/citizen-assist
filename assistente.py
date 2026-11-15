import csv
import json
import re
from datetime import date
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import time

from base_conhecimento import BaseConhecimento


CAMPOS_ATENDIMENTO = {
    "data": (str,),
    "origem": (str,),
    "pergunta": (str,),
    "id_orientacao": (int, type(None)),
    "encontrou": (bool,),
    "ajudou": (bool,),
    "tentativas": (int,),
    "tempo_segundos": (int, float),
}

APRESENTACAO_COM_NOME = re.compile(
    r"\b(?:meu\s+nome(?:\s+completo)?(?:\s+[eé]\b|\s*:)|me\s+chamo\b)",
    re.IGNORECASE,
)


class Assistente:
    def __init__(
        self, nome: str, base: BaseConhecimento, caminho_historico: str | Path | None = None,
    ):
        self.nome = nome
        self.base = base
        self.historico: list[dict] = []
        self.notas_facilidade: list[int] = []
        self.caminho_historico: Path | None = None
        if caminho_historico is not None:
            caminho = Path(caminho_historico)
            try:
                self._carregar_historico(caminho)
            except (OSError, ValueError):
                print("Não foi possível ler o histórico. Os dados desta sessão ficarão em memória.")
            else:
                self.caminho_historico = caminho

    def perguntar(self) -> None:
        inicio = time()
        tentativas = 0
        ultima_pergunta = ""
        print("\nNão inclua nome, CPF, telefone ou e-mail na pergunta.")
        while True:
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()
            if pergunta == "0":
                if tentativas:
                    self.registrar("pergunta", ultima_pergunta, None, False, tentativas, inicio)
                return
            if not pergunta:
                print("Digite uma pergunta.")
                continue
            if (
                "@" in pergunta
                or sum(caractere.isdigit() for caractere in pergunta) >= 8
                or APRESENTACAO_COM_NOME.search(pergunta)
            ):
                print("Atenção: remova os dados pessoais e reescreva a pergunta.")
                continue
            tentativas += 1
            ultima_pergunta = pergunta
            resultados = self.base.buscar(pergunta)
            if resultados and resultados[0][0] >= 3:
                break
            print("Não encontrei uma orientação. Tente outras palavras ou volte para navegar por categoria.")

        fim_busca = time()
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
        self.registrar("pergunta", pergunta, orientacao.id, ajudou, tentativas, inicio, fim=fim_busca)

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
            fim_busca = time()
            orientacao.exibir()
            ajudou = self._pedir_feedback()
            self.registrar("categoria", "", orientacao.id, ajudou, 1, inicio, fim=fim_busca)
            return

    def registrar(
        self,
        origem: str,
        pergunta: str,
        id_orientacao: int | None,
        ajudou: bool,
        tentativas: int,
        inicio: float,
        *,
        fim: float | None = None,
    ) -> None:
        if fim is None:
            fim = time()
        self.historico.append({
            "data": date.today().isoformat(),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": id_orientacao is not None,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": round(fim - inicio, 1),
        })
        self._salvar_historico()

    def avaliar_facilidade(self) -> None:
        while True:
            nota = input("Qual nota você dá para a facilidade de uso? (1 a 5): ").strip()
            if nota in ("1", "2", "3", "4", "5"):
                self.notas_facilidade.append(int(nota))
                self._salvar_historico()
                return
            print("Digite uma nota de 1 a 5.")

    def indicadores(self) -> dict:
        total = len(self.historico)
        encontrados = [registro for registro in self.historico if registro["encontrou"]]
        titulos_por_id = {orientacao.id: orientacao.titulo for orientacao in self.base.orientacoes}
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
            "facilidade_uso": (
                round(sum(self.notas_facilidade) / len(self.notas_facilidade), 1)
                if self.notas_facilidade else None
            ),
            "duvidas_sem_solucao": [
                registro["pergunta"] or titulos_por_id.get(
                    registro["id_orientacao"], f"Orientação #{registro['id_orientacao']}"
                )
                for registro in self.historico
                if not registro["ajudou"]
                and (registro["pergunta"] or registro["id_orientacao"] is not None)
            ],
        }

    def exportar_csv(self, caminho: str | Path = "data/atendimentos.csv") -> None:
        with Path(caminho).open("w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.DictWriter(
                arquivo, fieldnames=list(CAMPOS_ATENDIMENTO), extrasaction="ignore",
            )
            escritor.writeheader()
            escritor.writerows(self.historico)

    def _carregar_historico(self, caminho: Path) -> None:
        try:
            conteudo = caminho.read_text(encoding="utf-8")
        except FileNotFoundError:
            return
        if not conteudo.strip():
            return

        dados = json.loads(conteudo)
        if isinstance(dados, list):
            dados = {"atendimentos": dados, "notas_facilidade": []}
        if not isinstance(dados, dict):
            raise ValueError("Formato do histórico inválido.")

        atendimentos = dados.get("atendimentos")
        notas = dados.get("notas_facilidade", [])
        if not isinstance(atendimentos, list) or not all(
            isinstance(registro, dict) and all(
                campo in registro and type(registro[campo]) in tipos
                for campo, tipos in CAMPOS_ATENDIMENTO.items()
            )
            for registro in atendimentos
        ):
            raise ValueError("Atendimentos do histórico inválidos.")
        if not isinstance(notas, list) or not all(
            type(nota) is int and 1 <= nota <= 5 for nota in notas
        ):
            raise ValueError("Notas de facilidade do histórico inválidas.")

        self.historico = atendimentos
        self.notas_facilidade = notas

    def _salvar_historico(self) -> None:
        caminho = self.caminho_historico
        if caminho is None:
            return

        dados = {"atendimentos": self.historico, "notas_facilidade": self.notas_facilidade}
        temporario = None
        try:
            with NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=caminho.parent, delete=False,
            ) as arquivo:
                temporario = Path(arquivo.name)
                json.dump(dados, arquivo, ensure_ascii=False, indent=2)
                arquivo.write("\n")
            temporario.replace(caminho)
        except OSError:
            print("Não foi possível gravar o histórico. Os dados continuam disponíveis nesta sessão.")
        finally:
            if temporario is not None:
                try:
                    temporario.unlink(missing_ok=True)
                except OSError:
                    pass

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

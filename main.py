from pathlib import Path

from assistente import Assistente
from base_conhecimento import BaseConhecimento


def main() -> None:
    pasta_dados = Path(__file__).resolve().parent / "data"
    base = BaseConhecimento(pasta_dados / "base_conhecimento.json")
    try:
        base.carregar()
    except (OSError, ValueError, TypeError):
        print("Não foi possível carregar a base de conhecimento. Confira o arquivo JSON.")

    assistente = Assistente("Citizen Assist AI", base)
    while True:
        print(f"\n{assistente.nome}")
        print("1. Perguntar")
        print("2. Navegar por categoria")
        print("3. Consultar indicadores")
        print("4. Exportar atendimentos")
        print("0. Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            return
        if opcao == "1":
            assistente.perguntar()
        elif opcao == "2":
            assistente.navegar()
        elif opcao == "3":
            indicadores = assistente.indicadores()
            print(f"Respostas encontradas: {indicadores['respostas_encontradas']}%")
            print(f"Taxa de acerto: {indicadores['taxa_acerto']}%")
            print(f"Tempo médio nos atendimentos com resposta: {indicadores['tempo_medio']} s")
            print(f"Tentativas por atendimento: {indicadores['tentativas_por_atendimento']}")
            print("Dúvidas sem solução:")
            for pergunta in indicadores["duvidas_sem_solucao"]:
                print(f"  - {pergunta}")
        elif opcao == "4":
            if not assistente.historico:
                print("Nenhum atendimento nesta sessão para exportar.")
                continue
            try:
                assistente.exportar_csv(pasta_dados / "atendimentos.csv")
            except OSError:
                print("Não foi possível gravar o arquivo CSV.")
            else:
                print("Atendimentos exportados para data/atendimentos.csv.")
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()

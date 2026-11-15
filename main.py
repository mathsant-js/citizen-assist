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

    assistente = Assistente("Citizen Assist AI", base, pasta_dados / "historico.json")
    try:
        executar_menu(assistente, pasta_dados)
    except (EOFError, KeyboardInterrupt):
        print("\nAtendimento encerrado.")


def executar_menu(assistente: Assistente, pasta_dados: Path) -> None:
    while True:
        print(f"\n{assistente.nome}")
        print("1. Perguntar")
        print("2. Navegar por categoria")
        print("3. Consultar indicadores")
        print("4. Exportar atendimentos")
        print("0. Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            assistente.avaliar_facilidade()
            return
        if opcao == "1":
            assistente.perguntar()
        elif opcao == "2":
            assistente.navegar()
        elif opcao == "3":
            indicadores = assistente.indicadores()
            print(f"Respostas encontradas: {indicadores['respostas_encontradas']}%")
            print(f"Taxa de acerto: {indicadores['taxa_acerto']}%")
            print(f"Tempo médio para encontrar uma orientação: {indicadores['tempo_medio']} s")
            print(f"Tentativas por atendimento: {indicadores['tentativas_por_atendimento']}")
            facilidade = indicadores["facilidade_uso"]
            if facilidade is None:
                print("Facilidade de uso: sem avaliações.")
            else:
                print(f"Facilidade de uso: {facilidade:.1f}/5")
            print("Dúvidas sem solução:")
            duvidas = indicadores["duvidas_sem_solucao"]
            if duvidas:
                for duvida in duvidas:
                    print(f"  - {duvida}")
            else:
                print("  Nenhuma registrada.")
        elif opcao == "4":
            if not assistente.historico:
                print("Nenhum atendimento registrado para exportar.")
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

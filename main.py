"""SmartChef MVP — CLI interativa."""

import asyncio
from smartchef import ChefEngine, NutritionConsultant


async def main() -> None:
    print("\n🍳 Bem-vindo ao SmartChef MVP!\n")

    ingredientes = input("Liste seus ingredientes (separados por vírgula): ").strip()
    tempo = int(input("Tempo disponível (minutos): ").strip())

    print("\n⏳ Gerando receita com IA...\n")
    engine = ChefEngine()
    receita = await engine.gerar_receita(ingredientes=ingredientes, tempo_minutos=tempo)

    print(f"📖 {receita.nome_receita}  ({receita.dificuldade.value})")
    print(NutritionConsultant.resumo(receita.macros))
    print(f"📝 {len(receita.passos)} passos  [fonte: {receita.fonte}]\n")

    print("─" * 50)
    print("Digite 'proximo' para avançar, 'repetir' para reouvir, 'sair' para encerrar.\n")

    idx = 0
    while idx < len(receita.passos):
        print(f"  Passo {idx + 1}/{len(receita.passos)}: {receita.passos[idx]}\n")

        cmd = input(">> ").strip().lower()
        if cmd == "proximo":
            idx += 1
        elif cmd == "repetir":
            continue
        elif cmd == "sair":
            break
        else:
            print("Comando não reconhecido. Use: proximo | repetir | sair")

    print("\n✅ Bom apetite! Até a próxima.")


if __name__ == "__main__":
    asyncio.run(main())

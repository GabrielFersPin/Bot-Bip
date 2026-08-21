import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Bot-Bip: Sistema modular de seguimiento diario y analítica.")
    parser.add_argument(
        "agent",
        choices=["bot", "dashboard"],
        nargs="?",
        default="bot",
        help="Agente a ejecutar: 'bot' (Telegram Bot) o 'dashboard' (Streamlit Analytics Dashboard)."
    )

    args = parser.parse_args()

    if args.agent == "bot":
        print("🤖 Iniciando Telegram Bot Agent...")
        from bot.telegram_bot import main as run_bot
        run_bot()
    elif args.agent == "dashboard":
        print("📊 Iniciando Dashboard Agent...")
        os.system("streamlit run dashboard/app.py")

if __name__ == "__main__":
    main()

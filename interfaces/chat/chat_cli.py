# interfaces/chat/chat_cli.py

from interfaces.chat.chat_adapter import ChatAdapter
from tools.reply import Reply


def run_chat(snapshot_provider):
    """
    snapshot_provider: callable returning dict
    """
    adapter = ChatAdapter()

    print("A7DO Chat CLI (type 'exit' to quit)")
    while True:
        cmd = input("> ").strip()
        if cmd.lower() in ("exit", "quit"):
            break

        snapshot = snapshot_provider()
        reply: Reply = adapter.system_status(snapshot)

        print(f"[{reply.level.upper()}] {reply.message}")
        if reply.payload:
            for k, v in reply.payload.items():
                print(f"  {k}: {v}")

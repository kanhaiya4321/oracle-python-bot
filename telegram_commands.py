import logging


class TelegramCommandProcessor:
    def __init__(self, notifier, config_store):
        self.notifier = notifier
        self.config_store = config_store
        self.offset = None

    def process_pending_updates(self):
        updates = self.notifier.get_updates(offset=self.offset, timeout=1)
        for update in updates:
            self.offset = update["update_id"] + 1
            self._process_update(update)

    def _process_update(self, update):
        message = update.get("message") or {}
        text = (message.get("text") or "").strip()
        chat_id = message.get("chat", {}).get("id")

        if not text or not chat_id:
            return
        if not text.startswith("/"):
            self.notifier.send_message(
                "Use /help to see supported commands.",
                chat_id=chat_id,
            )
            return

        parts = text.split()
        command = parts[0].split("@")[0].lower()
        args = parts[1:]

        handlers = {
            "/help": self._handle_help,
            "/list": self._handle_list,
            "/add": self._handle_add,
            "/remove": self._handle_remove,
            "/setlabel": self._handle_setlabel,
        }

        handler = handlers.get(command)
        if not handler:
            self.notifier.send_message("Unknown command. Use /help.", chat_id=chat_id)
            return

        try:
            handler(chat_id, args)
        except Exception as exc:
            logging.exception("Failed to process telegram command")
            self.notifier.send_message(f"Command failed: {exc}", chat_id=chat_id)

    def _handle_help(self, chat_id, _args):
        self.notifier.send_message(
            (
                "Commands:\n"
                "/list\n"
                "/add <portfolio_id> [label]\n"
                "/remove <portfolio_id>\n"
                "/setlabel <portfolio_id> <label>"
            ),
            chat_id=chat_id,
            parse_mode=None,
        )

    def _handle_list(self, chat_id, _args):
        portfolios = self.config_store.list_portfolios()
        if not portfolios:
            self.notifier.send_message("No portfolios configured.", chat_id=chat_id)
            return

        lines = ["Tracked portfolios:"]
        for portfolio in portfolios:
            lines.append(f"{portfolio['portfolio_id']} | {portfolio['label']}")
        self.notifier.send_message("\n".join(lines), chat_id=chat_id, parse_mode=None)

    def _handle_add(self, chat_id, args):
        if not args:
            self.notifier.send_message("Usage: /add <portfolio_id> [label]", chat_id=chat_id)
            return

        portfolio_id = args[0]
        label = " ".join(args[1:]) if len(args) > 1 else None
        portfolio = self.config_store.upsert_portfolio(portfolio_id=portfolio_id, label=label)

        self.notifier.send_message(
            (
                f"Tracking portfolio {portfolio['portfolio_id']}\n"
                f"Label: {portfolio['label']}\n"
                "Excel: binance_trades.xlsx\n"
                "It will be picked up automatically in the next loop."
            ),
            chat_id=chat_id,
            parse_mode=None,
        )

    def _handle_remove(self, chat_id, args):
        if not args:
            self.notifier.send_message("Usage: /remove <portfolio_id>", chat_id=chat_id)
            return

        removed = self.config_store.remove_portfolio(args[0])
        if removed:
            self.notifier.send_message(f"Removed portfolio {args[0]}.", chat_id=chat_id, parse_mode=None)
        else:
            self.notifier.send_message(f"Portfolio {args[0]} was not found.", chat_id=chat_id, parse_mode=None)

    def _handle_setlabel(self, chat_id, args):
        if len(args) < 2:
            self.notifier.send_message("Usage: /setlabel <portfolio_id> <label>", chat_id=chat_id)
            return

        portfolio_id = args[0]
        label = " ".join(args[1:])
        portfolio = self.config_store.get_portfolio(portfolio_id)
        if not portfolio:
            self.notifier.send_message(f"Portfolio {portfolio_id} was not found.", chat_id=chat_id)
            return

        updated = self.config_store.upsert_portfolio(
            portfolio_id=portfolio_id,
            label=label,
            enabled=portfolio["enabled"],
        )
        self.notifier.send_message(
            f"Updated label for {portfolio_id} to {updated['label']}.",
            chat_id=chat_id,
            parse_mode=None,
        )

import os
import sqlite3
import json
import csv
import asyncio
import re
import warnings
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timezone, timedelta
from telethon import TelegramClient
from telethon.tl.types import User, PeerChannel
from telethon.errors import SessionPasswordNeededError

warnings.filterwarnings("ignore", message="Using async sessions support is an experimental feature")

# -----------  SETTINGS  -----------
ALL_CHANNELS = ['MarketTwits', 'Crypto Headlines', 'The Экономист', 'Финам Инвестиции', 'Банкста']   # <-- EDIT HERE
ROOT_DIR     = Path("telegram_channels_latest_news")

ROOT_DIR.mkdir(exist_ok=True)
# -----------------------------------

def safe_name(name: str) -> str:
    return re.sub(r'[^-\w.]', '_', name).strip('_')

@dataclass
class MessageData:
    message_id: int
    date: str
    sender_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    message: str
    reply_to: Optional[int]

class TelegramLatestScraper:
    def __init__(self):
        self.state_file = ROOT_DIR / 'state.json'
        self.state = self.load_state()
        self.client: Optional[TelegramClient] = None
        self.batch_size = 100
        self.db_connections: Dict[str, sqlite3.Connection] = {}
        if 'title_map' not in self.state:
            self.state['title_map'] = {}

    # ---------- state ----------
    def load_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except Exception:
                pass
        return {'api_id': None, 'api_hash': None, 'channels': {}, 'title_map': {}}

    def save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    # ---------- database ----------
    def get_db(self, channel_id: str) -> sqlite3.Connection:
        if channel_id not in self.db_connections:
            title = safe_name(self.state['title_map'].get(channel_id, channel_id))
            folder = ROOT_DIR / title
            folder.mkdir(exist_ok=True)
            db_path = folder / f'{title}.db'
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.execute('''CREATE TABLE IF NOT EXISTS messages
                            (id INTEGER PRIMARY KEY, message_id INTEGER UNIQUE, date TEXT,
                             sender_id INTEGER, first_name TEXT, last_name TEXT, username TEXT,
                             message TEXT, reply_to INTEGER)''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_message_id ON messages(message_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_date ON messages(date)')
            conn.execute('PRAGMA journal_mode=WAL')
            conn.commit()
            self.db_connections[channel_id] = conn
        return self.db_connections[channel_id]

    def close_db(self):
        for conn in self.db_connections.values():
            conn.close()
        self.db_connections.clear()

    def insert_batch(self, channel_id: str, messages: List[MessageData]):
        if not messages:
            return
        conn = self.get_db(channel_id)
        data = [(m.message_id, m.date, m.sender_id, m.first_name,
                 m.last_name, m.username, m.message, m.reply_to) for m in messages]
        conn.executemany('INSERT OR IGNORE INTO messages VALUES (NULL,?,?,?,?,?,?,?,?)', data)
        conn.commit()

    # ---------- scrape ----------
    async def scrape_channel(self, channel_id: str):
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        print(f"\n scraping last 24 h  (since {since.strftime('%Y-%m-%d %H:%M')} UTC)")
        try:
            entity = await self.client.get_entity(
                PeerChannel(int(channel_id)) if channel_id.startswith('-') else channel_id)
        except Exception as e:
            print(f"  cannot resolve channel {channel_id}: {e}")
            return

        conn = self.get_db(channel_id)
        last_id = self.state['channels'].get(channel_id, 0)
        batch, processed = [], 0

        async for msg in self.client.iter_messages(entity, offset_id=last_id, reverse=False):
            if msg.date.replace(tzinfo=timezone.utc) < since:
                break
            sender = await msg.get_sender() if msg.sender_id else None
            batch.append(MessageData(
                message_id=msg.id,
                date=msg.date.strftime('%Y-%m-%d %H:%M:%S'),
                sender_id=msg.sender_id,
                first_name=getattr(sender, 'first_name', None) if isinstance(sender, User) else None,
                last_name=getattr(sender, 'last_name', None) if isinstance(sender, User) else None,
                username=getattr(sender, 'username', None) if isinstance(sender, User) else None,
                message=msg.message or '',
                reply_to=msg.reply_to_msg_id if msg.reply_to else None
            ))
            processed += 1
            if len(batch) >= self.batch_size:
                self.insert_batch(channel_id, batch)
                batch.clear()
        if batch:
            self.insert_batch(channel_id, batch)

        # update last id
        newest = conn.execute('SELECT MAX(message_id) FROM messages').fetchone()[0] or 0
        self.state['channels'][channel_id] = newest
        self.save_state()
        print(f"  saved {processed} new messages")

        # export
        await self.export_channel(channel_id)

    # ---------- export ----------
    async def export_channel(self, channel_id: str):
        title = safe_name(self.state['title_map'].get(channel_id, channel_id))
        folder = ROOT_DIR / title
        try:
            self.to_csv(channel_id, title, folder)
            self.to_json(channel_id, title, folder)
            print(f"  exported  {title}")
        except Exception as e:
            print(f"  export error  {title}: {e}")

    def to_csv(self, channel_id: str, title: str, folder: Path):
        conn = self.get_db(channel_id)
        csv_path = folder / f'{title}.csv'
        cur = conn.execute('SELECT * FROM messages ORDER BY date')
        cols = [d[0] for d in cur.description]
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(cols)
            while True:
                rows = cur.fetchmany(1000)
                if not rows:
                    break
                writer.writerows(rows)

    def to_json(self, channel_id: str, title: str, folder: Path):
        conn = self.get_db(channel_id)
        json_path = folder / f'{title}.json'
        cur = conn.execute('SELECT * FROM messages ORDER BY date')
        cols = [d[0] for d in cur.description]
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write('[\n')
            first = True
            while True:
                rows = cur.fetchmany(1000)
                if not rows:
                    break
                for row in rows:
                    if not first:
                        f.write(',\n')
                    first = False
                    f.write(json.dumps(dict(zip(cols, row)), ensure_ascii=False, indent=2))
            f.write('\n]')

    # ---------- auth ----------
    async def auth(self):
        if not all([self.state.get('api_id'), self.state.get('api_hash')]):
            print("=== API credentials needed (get from https://my.telegram.org) ===")
            self.state['api_id'] = int(input("API ID: "))
            self.state['api_hash'] = input("API Hash: ")
            self.save_state()

        self.client = TelegramClient(str(ROOT_DIR / 'session'), self.state['api_id'], self.state['api_hash'])
        await self.client.connect()
        if await self.client.is_user_authorized():
            print("✅ already authenticated")
            return True

        print("\n=== phone-number login ===")
        phone = input("phone: ")
        await self.client.send_code_request(phone)
        code = input("code: ")
        try:
            await self.client.sign_in(phone, code)
            print("✅ phone login success")
            return True
        except SessionPasswordNeededError:
            pw = input("2FA password: ")
            await self.client.sign_in(password=pw)
            print("✅ 2FA login success")
            return True

    # ---------- main flow ----------
    async def run(self):
        print("=== Telegram Latest-24h Scraper ===")
        if not await self.auth():
            print("auth failed – exiting")
            return

        print("\n🔍  discovering joined channels …")
        joined = {}
        async for d in self.client.iter_dialogs():
            if d.id == 777000:
                continue
            joined[d.title] = str(d.id)

        wanted_lower = {t.lower() for t in ALL_CHANNELS}
        matched = {t: i for t, i in joined.items() if t.lower() in wanted_lower}
        if not matched:
            print("⚠️  no target channels found in joined dialogs – exiting")
            return

        print(f"✅ matched: {', '.join(matched)}")
        for title, cid in matched.items():
            self.state['title_map'][cid] = title
            if cid not in self.state['channels']:
                self.state['channels'][cid] = 0
        self.save_state()

        print("\n🚀  scraping latest 24 h …")
        for title, cid in matched.items():
            print(f"\n– {title}")
            await self.scrape_channel(cid)

        print("\n✅  all done – exiting")
        self.close_db()
        await self.client.disconnect()

# ------------------ run ------------------
async def main():
    scraper = TelegramLatestScraper()
    await scraper.run()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\ninterrupted – bye")

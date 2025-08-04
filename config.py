"""
Configuration settings for Nikkei 225 Analysis Tool
"""

# Base URL for Nikkei data
BASE_URL = "https://indexes.nikkei.co.jp/nkave/index"

# User agent for web requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Default headers for HTTP requests
DEFAULT_HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ja,en-US;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Default data folder
DEFAULT_BASE_FOLDER = "nikkei_local"

# Top 20 stocks by market cap (Nikkei-based, updated manually)
# Last updated: 2025-08
TOP_20_MARKET_CAP = [
    ('7203', 'トヨタ自動車'),
    ('8306', '三菱ＵＦＪフィナンシャル・グループ'),
    ('6758', 'ソニーグループ'),
    ('6501', '日立製作所'),
    ('9984', 'ソフトバンクグループ'),
    ('7974', '任天堂'),
    ('9983', 'ファーストリテイリング'),
    ('8316', '三井住友フィナンシャルグループ'),
    ('6098', 'リクルートホールディングス'),
    ('9432', '日本電信電話'),
    ('8058', '三菱商事'),
    ('6861', 'キーエンス'),
    ('8035', '東京エレクトロン'),
    ('4063', '信越化学工業'),
    ('8001', '伊藤忠商事'),
    ('4519', '中外製薬'),
    ('9433', 'ＫＤＤＩ'),
    ('7267', 'ホンダ'),
    ('8031', '三井物産'),
    ('6367', 'ダイキン工業'),
]
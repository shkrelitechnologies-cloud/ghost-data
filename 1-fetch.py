import json, urllib.request, datetime, time

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'ghost-data-bot'})
    return json.load(urllib.request.urlopen(req, timeout=25))

out = {}
try:
    tick = get('https://www.okx.com/api/v5/market/tickers?instType=SWAP')['data']
    tick.sort(key=lambda t: -float(t.get('volCcy24h') or 0))
    top = [t['instId'] for t in tick[:30] if t['instId'].endswith('-USDT-SWAP')]
    vols = {t['instId']: float(t.get('volCcy24h') or 0) for t in tick}
    rows = []
    for inst in top:
        try:
            f = get(f'https://www.okx.com/api/v5/public/funding-rate?instId={inst}')['data'][0]
            rows.append({'coin': inst.replace('-USDT-SWAP',''), 'fr': round(float(f['fundingRate'])*100,4), 'vol': int(vols.get(inst,0))})
        except Exception: pass
        time.sleep(0.2)
    out['funding'] = rows
except Exception as e:
    out['funding_error'] = str(e)

pools = []
for net in ['eth','bsc','solana','base','arbitrum']:
    try:
        d = get(f'https://api.geckoterminal.com/api/v2/networks/{net}/new_pools?page=1')
        for p in d['data'][:6]:
            a = p['attributes']
            tx = (a.get('transactions') or {}).get('h1') or {}
            pools.append({'net': net, 'pair': a.get('name',''), 'price': a.get('base_token_price_usd',''),
                          'created': (a.get('pool_created_at') or '')[:16].replace('T',' '),
                          'tx1h': tx.get('buys',0)+tx.get('sells',0)})
    except Exception: pass
    time.sleep(0.4)
out['pools'] = pools
out['updated'] = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
json.dump(out, open('data.json','w'), indent=1)
print('ok', len(out.get('funding',[])), len(pools))

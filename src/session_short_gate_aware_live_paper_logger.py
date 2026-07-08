from __future__ import annotations

import argparse, csv, json, time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import numpy as np
import pandas as pd

API_BASE = 'https://www.okx.com'
CANDLES_ENDPOINT = '/api/v5/market/candles'


def utc_now(): return pd.Timestamp.now(tz='UTC')
def iso(ts: Any) -> str:
    if ts is None or pd.isna(ts): return ''
    return pd.Timestamp(ts).tz_convert('UTC').isoformat().replace('+00:00','Z')

def append_csv(path: Path, row: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open('a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists: w.writeheader()
        w.writerow(row)

def write_rows(path: Path, rows: list[dict], cols: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows: w.writerow({c:r.get(c,'') for c in cols})

def read_records(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0: return []
    try: return pd.read_csv(path).fillna('').to_dict('records')
    except Exception: return []

def discover_coins(base: Path, coins_arg: str, exclude: set[str]) -> list[str]:
    if coins_arg.strip().upper() not in {'AUTO','ALL'}:
        return sorted({x.strip().upper() for x in coins_arg.split(',') if x.strip()} - exclude)
    coins=[]
    for d in base.iterdir():
        if not d.is_dir() or d.name.startswith('_'): continue
        coin=d.name.upper()
        if coin in exclude: continue
        inst=f'{coin}-USDT-SWAP'
        if list((d/'raw').glob(f'**/{inst}_1m_*.csv')): coins.append(coin)
    return sorted(set(coins))

def fetch_1m(inst_id: str, limit=180, retries=3, sleep_sec=0.05) -> pd.DataFrame:
    url=f'{API_BASE}{CANDLES_ENDPOINT}?{urlencode({"instId":inst_id,"bar":"1m","limit":str(limit)})}'
    last=''
    for a in range(1,retries+1):
        try:
            req=Request(url, headers={'User-Agent':'edge-session-short-gate-aware/1.0','Accept':'application/json'})
            with urlopen(req, timeout=15) as resp: js=json.loads(resp.read().decode('utf-8'))
            if str(js.get('code'))!='0': raise RuntimeError(f"OKX code={js.get('code')} msg={js.get('msg')}")
            rows=[]
            for r in js.get('data',[]):
                if len(r)<8: continue
                rows.append({'ts':pd.to_numeric(r[0], errors='coerce'),'open':pd.to_numeric(r[1], errors='coerce'),
                             'high':pd.to_numeric(r[2], errors='coerce'),'low':pd.to_numeric(r[3], errors='coerce'),
                             'close':pd.to_numeric(r[4], errors='coerce'),'vol':pd.to_numeric(r[5], errors='coerce') if len(r)>5 else np.nan,
                             'volCcy':pd.to_numeric(r[6], errors='coerce') if len(r)>6 else np.nan,
                             'volCcyQuote':pd.to_numeric(r[7], errors='coerce') if len(r)>7 else np.nan,
                             'confirm':str(r[8]) if len(r)>8 else '1'})
            df=pd.DataFrame(rows)
            if df.empty: return df
            df['time']=pd.to_datetime(df['ts'], unit='ms', utc=True, errors='coerce')
            for c in ['open','high','low','close','vol','volCcy','volCcyQuote']: df[c]=pd.to_numeric(df[c], errors='coerce')
            df=df.dropna(subset=['time','open','high','low','close']).drop_duplicates('time').sort_values('time').reset_index(drop=True)
            df=df[df['confirm'].astype(str)=='1'].copy()
            if df['volCcyQuote'].isna().all(): df['volCcyQuote']=(df.get('volCcy',df['vol'])*df['close'])
            close=df['close'].astype(float)
            df['ret1_bps']=close.pct_change()*10000
            df['ret3_bps']=(close/close.shift(3)-1)*10000
            df['ret5_bps']=(close/close.shift(5)-1)*10000
            df['ret60_bps']=(close/close.shift(60)-1)*10000
            df['range_bps']=(df['high']-df['low'])/df['open'].replace(0,np.nan)*10000
            return df.reset_index(drop=True)
        except (HTTPError,URLError,TimeoutError,json.JSONDecodeError,RuntimeError) as e:
            last=repr(e); time.sleep(sleep_sec*a*2)
    raise RuntimeError(f'OKX 1m fetch failed for {inst_id}. Last error: {last}')

@dataclass
class Pending:
    signal_id:str; inst_id:str; coin:str; family_key:str; family:str; strategy:str; side:str
    signal_time:str; target_entry_time:str; planned_exit_time:str
    signal_hour_utc:int; min_ret60_bps:float; entry_delay_minutes:int; hold_minutes:int
    signal_close:float; signal_ret1_bps:float; signal_ret3_bps:float; signal_ret5_bps:float; signal_ret60_bps:float
    signal_vol_quote:float; signal_range_bps:float; created_at:str

@dataclass
class Position:
    position_id:str; inst_id:str; coin:str; family_key:str; family:str; strategy:str; side:str; signal_id:str
    signal_time:str; entry_time:str; planned_exit_time:str; signal_hour_utc:int; min_ret60_bps:float
    entry_delay_minutes:int; hold_minutes:int; raw_entry_close:float; entry_price:float; notional:float; equity_before:float
    signal_close:float; signal_ret1_bps:float; signal_ret3_bps:float; signal_ret5_bps:float; signal_ret60_bps:float
    signal_vol_quote:float; signal_range_bps:float; entry_vol_quote:float; entry_range_bps:float
    entry_slip_bps:float; exit_slip_bps:float; fee_bps_total:float; stress_extra_bps:float

class Logger:
    def __init__(self,args):
        self.a=args; self.base=Path(args.base_dir); self.out=Path(args.out_dir); self.out.mkdir(parents=True, exist_ok=True)
        self.family_key='session_short'; self.family='session_ret60_reversal_short'
        self.strategy=f'session_ret60_reversal_short_h{args.signal_hour_utc}_m{int(args.min_ret60_bps)}_hold{args.hold_minutes}'
        self.signals=self.out/'signals.csv'; self.pending_path=self.out/'pending_entries.csv'; self.open_path=self.out/'open_positions.csv'
        self.closed_path=self.out/'closed_trades.csv'; self.reject_path=self.out/'rejected_entries.csv'; self.err_path=self.out/'errors.csv'
        self.hb_path=self.out/'heartbeat.csv'; self.state_path=self.out/'state.json'
        self.coins=discover_coins(self.base,args.coins,{x.strip().upper() for x in args.exclude.split(',') if x.strip()})
        self.pending={}; self.open={}; self.seen=set(); self.equity=float(args.start_equity); self.closed_count=0; self.errors=0
        self.load_state()
        (self.out/'session_short_gate_aware_config.json').write_text(json.dumps({'strategy':self.strategy,'coins':len(self.coins),'settings':vars(args)},indent=2),encoding='utf-8')
    def load_state(self):
        for r in read_records(self.signals):
            if str(r.get('signal_id','')): self.seen.add(str(r.get('signal_id','')))
        for r in read_records(self.pending_path):
            try:
                if str(r.get('status','pending')) not in {'','pending'}: continue
                p=Pending(**{k: r.get(k) for k in Pending.__dataclass_fields__.keys()})
                # cast relevant fields
                for k in ['signal_hour_utc','entry_delay_minutes','hold_minutes']: setattr(p,k,int(getattr(p,k)))
                for k in ['min_ret60_bps','signal_close','signal_ret1_bps','signal_ret3_bps','signal_ret5_bps','signal_ret60_bps','signal_vol_quote','signal_range_bps']: setattr(p,k,float(getattr(p,k)))
                self.pending[p.signal_id]=p; self.seen.add(p.signal_id)
            except Exception: pass
        for r in read_records(self.open_path):
            try:
                pos=Position(**{k: r.get(k) for k in Position.__dataclass_fields__.keys()})
                for k in ['signal_hour_utc','entry_delay_minutes','hold_minutes']: setattr(pos,k,int(getattr(pos,k)))
                for k in ['min_ret60_bps','raw_entry_close','entry_price','notional','equity_before','signal_close','signal_ret1_bps','signal_ret3_bps','signal_ret5_bps','signal_ret60_bps','signal_vol_quote','signal_range_bps','entry_vol_quote','entry_range_bps','entry_slip_bps','exit_slip_bps','fee_bps_total','stress_extra_bps']: setattr(pos,k,float(getattr(pos,k)))
                self.open[pos.position_id]=pos
            except Exception: pass
        closed=read_records(self.closed_path); self.closed_count=len(closed)
        if closed:
            try: self.equity=float(closed[-1]['equity_after'])
            except Exception: pass
    def save(self):
        pr=[]
        for p in self.pending.values():
            d=asdict(p); d['status']='pending'; pr.append(d)
        write_rows(self.pending_path, pr, ['status']+list(Pending.__dataclass_fields__.keys()))
        write_rows(self.open_path, [asdict(x) for x in self.open.values()], list(Position.__dataclass_fields__.keys()))
        self.state_path.write_text(json.dumps({'updated_at':iso(utc_now()),'equity':self.equity,'open':len(self.open),'pending':len(self.pending),'closed_count':self.closed_count,'errors':self.errors,'coins':len(self.coins),'strategy':self.strategy,'require_global_gate':self.a.require_global_gate},indent=2),encoding='utf-8')
    def log_error(self,where,inst,e):
        self.errors+=1; append_csv(self.err_path, {'log_time':iso(utc_now()),'where':where,'inst_id':inst,'error_type':type(e).__name__,'error':str(e)})
    def heartbeat(self):
        append_csv(self.hb_path, {'log_time':iso(utc_now()),'equity':self.equity,'open_positions':len(self.open),'pending_entries':len(self.pending),'closed_count':self.closed_count,'errors':self.errors,'coins':len(self.coins),'strategy':self.strategy,'require_global_gate':self.a.require_global_gate})
    def should_scan(self):
        now=utc_now()
        return self.a.scan_all_day or (now.hour==self.a.signal_hour_utc and now.minute<=self.a.scan_window_minutes)
    def candle_at(self,df,target):
        m=df['time']==pd.Timestamp(target).tz_convert('UTC')
        return None if not m.any() else df.loc[m].iloc[-1]
    def scan_coin(self,coin):
        inst=f'{coin}-USDT-SWAP'
        try: df=fetch_1m(inst,self.a.candle_limit,sleep_sec=self.a.request_sleep)
        except Exception as e: self.log_error('scan_fetch',inst,e); return
        if df.empty or len(df)<70: return
        now=utc_now(); x=df[df['time']>=now-pd.Timedelta(minutes=self.a.signal_backfill_minutes)].copy()
        x=x[x['time'].dt.hour==self.a.signal_hour_utc]
        sigs=x[(x['ret60_bps']>=self.a.min_ret60_bps)&(x['volCcyQuote']>=self.a.min_signal_vol_quote)&(x['range_bps']<=self.a.max_signal_range_bps)].sort_values('time')
        for _,sig in sigs.iterrows():
            st=pd.Timestamp(sig['time']).tz_convert('UTC'); sid=f"{coin}_{self.strategy}_{st.strftime('%Y%m%dT%H%M%SZ')}"
            if sid in self.seen: continue
            self.seen.add(sid); target=st+pd.Timedelta(minutes=self.a.entry_delay_minutes); exit_t=target+pd.Timedelta(minutes=self.a.hold_minutes)
            p=Pending(sid,inst,coin,self.family_key,self.family,self.strategy,'short',iso(st),iso(target),iso(exit_t),self.a.signal_hour_utc,self.a.min_ret60_bps,self.a.entry_delay_minutes,self.a.hold_minutes,float(sig['close']),float(sig['ret1_bps']),float(sig['ret3_bps']),float(sig['ret5_bps']),float(sig['ret60_bps']),float(sig['volCcyQuote']),float(sig['range_bps']),iso(now))
            self.pending[p.signal_id]=p; append_csv(self.signals, {'type':'signal_pending_short',**asdict(p)})
            print(f'[SIGNAL] {coin} ret60={p.signal_ret60_bps:.1f} entry={p.target_entry_time}')
    def gate(self, signal_id):
        if not self.a.require_global_gate: return 'ALLOW','gate_not_required'
        gp=Path(self.a.global_gate_path)
        if not gp.exists() or gp.stat().st_size==0: return 'WAIT','gate_file_missing'
        try: g=pd.read_csv(gp)
        except Exception: return 'WAIT','gate_file_read_error'
        if g.empty: return 'WAIT','gate_empty'
        m=(g.get('family_key','').astype(str)==self.family_key)&(g.get('signal_id','').astype(str)==signal_id)
        if not m.any(): return 'WAIT','gate_signal_missing'
        r=g.loc[m].iloc[-1]; d=str(r.get('decision','')).upper(); reason=str(r.get('reason',''))
        if d=='ALLOW': return 'ALLOW',reason or 'gate_allow'
        if d=='BLOCK': return 'BLOCK',reason or 'gate_block'
        return 'WAIT',f'gate_unknown_{d}'
    def process_pending(self,p):
        now=utc_now(); target=pd.Timestamp(p.target_entry_time).tz_convert('UTC')
        if now < target+pd.Timedelta(minutes=1): return
        decision,reason=self.gate(p.signal_id)
        if decision=='WAIT':
            if now > target+pd.Timedelta(minutes=self.a.pending_max_wait_minutes):
                append_csv(self.reject_path, {'type':'entry_reject','reason':f'global_gate_timeout_{reason}','log_time':iso(now),**asdict(p)})
                self.pending.pop(p.signal_id,None)
            return
        if decision=='BLOCK':
            append_csv(self.reject_path, {'type':'entry_reject','reason':f'global_gate_block_{reason}','log_time':iso(now),**asdict(p)})
            self.pending.pop(p.signal_id,None); return
        try: df=fetch_1m(p.inst_id,self.a.candle_limit,sleep_sec=self.a.request_sleep)
        except Exception as e: self.log_error('pending_fetch',p.inst_id,e); return
        row=self.candle_at(df,target)
        if row is None: return
        raw=float(row['close']); vol=float(row.get('volCcyQuote',np.nan)); rng=float(row.get('range_bps',np.nan))
        if (not np.isfinite(vol)) or vol<self.a.min_entry_vol_quote:
            append_csv(self.reject_path, {'type':'entry_reject','reason':'low_entry_vol_quote','log_time':iso(now),**asdict(p),'raw_entry_close':raw,'entry_vol_quote':vol,'entry_range_bps':rng}); self.pending.pop(p.signal_id,None); return
        if np.isfinite(rng) and rng>self.a.max_entry_range_bps:
            append_csv(self.reject_path, {'type':'entry_reject','reason':'high_entry_range_bps','log_time':iso(now),**asdict(p),'raw_entry_close':raw,'entry_vol_quote':vol,'entry_range_bps':rng}); self.pending.pop(p.signal_id,None); return
        if len(self.open)>=self.a.max_positions or any(o.coin==p.coin for o in self.open.values()):
            append_csv(self.reject_path, {'type':'entry_reject','reason':'local_limit_or_same_coin','log_time':iso(now),**asdict(p),'raw_entry_close':raw,'entry_vol_quote':vol,'entry_range_bps':rng}); self.pending.pop(p.signal_id,None); return
        entry_price=raw*(1-self.a.entry_slip_bps/10000); notional=self.equity*self.a.paper_fraction
        pos=Position(f"{p.coin}_{self.strategy}_{target.strftime('%Y%m%dT%H%M%SZ')}",p.inst_id,p.coin,p.family_key,p.family,p.strategy,'short',p.signal_id,p.signal_time,iso(target),p.planned_exit_time,p.signal_hour_utc,p.min_ret60_bps,p.entry_delay_minutes,p.hold_minutes,raw,entry_price,notional,self.equity,p.signal_close,p.signal_ret1_bps,p.signal_ret3_bps,p.signal_ret5_bps,p.signal_ret60_bps,p.signal_vol_quote,p.signal_range_bps,vol,rng,self.a.entry_slip_bps,self.a.exit_slip_bps,self.a.fee_bps_total,self.a.stress_extra_bps)
        self.open[pos.position_id]=pos; self.pending.pop(p.signal_id,None); append_csv(self.signals, {'type':'open_short',**asdict(pos),'global_gate_reason':reason})
        print(f'[OPEN] {p.coin} notional={notional:.2f} gate={reason}')
    def process_exit(self,pos):
        now=utc_now(); exit_t=pd.Timestamp(pos.planned_exit_time).tz_convert('UTC')
        if now < exit_t+pd.Timedelta(minutes=1): return
        try: df=fetch_1m(pos.inst_id,self.a.candle_limit,sleep_sec=self.a.request_sleep)
        except Exception as e: self.log_error('exit_fetch',pos.inst_id,e); return
        row=self.candle_at(df,exit_t)
        if row is None: return
        raw_exit=float(row['close']); exit_price=raw_exit*(1+pos.exit_slip_bps/10000); gross=pos.entry_price/exit_price-1; net=gross-pos.fee_bps_total/10000; stress=net-pos.stress_extra_bps/10000
        pnl=pos.notional*net; eq0=self.equity; self.equity+=pnl; self.closed_count+=1
        append_csv(self.closed_path, {'close_id':f"close_{pos.position_id}_{exit_t.strftime('%Y%m%dT%H%M%SZ')}",'position_id':pos.position_id,'inst_id':pos.inst_id,'coin':pos.coin,'family_key':pos.family_key,'family':pos.family,'strategy':pos.strategy,'side':'short','signal_id':pos.signal_id,'signal_time':pos.signal_time,'entry_time':pos.entry_time,'exit_time':iso(exit_t),'planned_exit_time':pos.planned_exit_time,'hold_minutes_actual':(exit_t-pd.Timestamp(pos.entry_time)).total_seconds()/60,'raw_entry_close':pos.raw_entry_close,'raw_exit_close':raw_exit,'entry_price':pos.entry_price,'exit_price':exit_price,'entry_slip_bps':pos.entry_slip_bps,'exit_slip_bps':pos.exit_slip_bps,'fee_bps_total':pos.fee_bps_total,'stress_extra_bps':pos.stress_extra_bps,'gross_ret':gross,'realistic_net_ret':net,'stress_net_ret':stress,'net_ret':net,'notional':pos.notional,'pnl':pnl,'stress_pnl':pos.notional*stress,'equity_before':eq0,'equity_after':self.equity,'signal_ret60_bps':pos.signal_ret60_bps,'entry_vol_quote':pos.entry_vol_quote,'entry_range_bps':pos.entry_range_bps})
        self.open.pop(pos.position_id,None); print(f'[CLOSE] {pos.coin} net={net:.4f} pnl={pnl:.4f} equity={self.equity:.2f}')
    def run_once(self):
        self.heartbeat(); self.save()
        for p in list(self.pending.values()): self.process_pending(p)
        for o in list(self.open.values()): self.process_exit(o)
        if self.should_scan():
            for i,c in enumerate(self.coins,1):
                self.scan_coin(c)
                if i%25==0: print(f'  scanned {i}/{len(self.coins)}')
                time.sleep(self.a.request_sleep)
        for p in list(self.pending.values()): self.process_pending(p)
        self.heartbeat(); self.save(); print(f'[{iso(utc_now())}] equity={self.equity:.2f} open={len(self.open)} pending={len(self.pending)} closed={self.closed_count} errors={self.errors}')
    def run_forever(self):
        print('='*90); print('SESSION RET60 REVERSAL SHORT - GATE-AWARE LIVE PAPER LOGGER'); print('REAL ORDERS: NO'); print('out_dir:',self.out); print('strategy:',self.strategy); print('coins:',len(self.coins)); print('require_global_gate:',self.a.require_global_gate); print('='*90)
        while True:
            try: self.run_once()
            except KeyboardInterrupt: self.save(); print('\nStopped.'); raise
            except Exception as e: self.log_error('main_loop','',e); self.save(); print('[ERROR]',type(e).__name__,e)
            time.sleep(self.a.poll_seconds)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--base_dir',default=r'C:\Users\alike\OneDrive\Desktop\edge_lab_new')
    ap.add_argument('--out_dir',default=r'C:\Users\alike\OneDrive\Desktop\edge_lab_new\live_session_ret60_reversal_short_paper')
    ap.add_argument('--coins',default='AUTO'); ap.add_argument('--exclude',default='BTC,ETH')
    ap.add_argument('--start_equity',type=float,default=1000.0); ap.add_argument('--paper_fraction',type=float,default=0.05); ap.add_argument('--max_positions',type=int,default=2)
    ap.add_argument('--signal_hour_utc',type=int,default=8); ap.add_argument('--scan_window_minutes',type=int,default=10); ap.add_argument('--scan_all_day',action='store_true')
    ap.add_argument('--min_ret60_bps',type=float,default=100.0); ap.add_argument('--entry_delay_minutes',type=int,default=2); ap.add_argument('--hold_minutes',type=int,default=720)
    ap.add_argument('--min_signal_vol_quote',type=float,default=100000.0); ap.add_argument('--min_entry_vol_quote',type=float,default=100000.0); ap.add_argument('--max_signal_range_bps',type=float,default=2000.0); ap.add_argument('--max_entry_range_bps',type=float,default=2000.0)
    ap.add_argument('--entry_slip_bps',type=float,default=25.0); ap.add_argument('--exit_slip_bps',type=float,default=25.0); ap.add_argument('--fee_bps_total',type=float,default=25.0); ap.add_argument('--stress_extra_bps',type=float,default=50.0)
    ap.add_argument('--candle_limit',type=int,default=180); ap.add_argument('--signal_backfill_minutes',type=int,default=12); ap.add_argument('--pending_max_wait_minutes',type=int,default=10); ap.add_argument('--request_sleep',type=float,default=0.03); ap.add_argument('--poll_seconds',type=float,default=60.0)
    ap.add_argument('--require_global_gate',action='store_true'); ap.add_argument('--global_gate_path',default=r'C:\Users\alike\OneDrive\Desktop\edge_lab_new\global_risk_manager\global_gate_decisions.csv')
    Logger(ap.parse_args()).run_forever()
if __name__=='__main__': main()

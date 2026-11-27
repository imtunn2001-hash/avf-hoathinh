# -*- coding: utf-8 -*-
"""Do nhip giong doc (khong can nghe): toc do am tiet, khoang nghi, do dai cum, cao do (F0), do to.
Dung: python3 nhip.py file.wav [nhan]  -> in bang + ghi file.json
"""
import json, sys, subprocess, numpy as np
from scipy.signal import butter, sosfiltfilt, find_peaks

SR = 16000


def load(path):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'])
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def band(x, lo, hi):
    return sosfiltfilt(butter(4, [lo, hi], 'band', fs=SR, output='sos'), x)


def f0_track(x, hop):
    """YIN rut gon, 75-400 Hz."""
    W = 640; tmin, tmax = SR // 400, SR // 75; out = []
    for s in range(0, len(x) - W - tmax, hop):
        fr = x[s:s + W + tmax]
        d = np.array([np.sum((fr[:W] - fr[t:t + W]) ** 2) for t in range(tmin, tmax)])
        cm = d / (np.cumsum(d) / np.arange(1, len(d) + 1) + 1e-9)
        i = np.argmin(cm)
        out.append(SR / (i + tmin) if cm[i] < 0.25 else np.nan)
    return np.array(out)


def analyse(path, name):
    x = load(path); v = band(x, 120, 3800)
    hop = 160  # 10 ms
    n = len(v) // hop
    e = np.array([np.sqrt(np.mean(v[i * hop:(i + 1) * hop] ** 2)) for i in range(n)])
    edb = 20 * np.log10(e + 1e-6)
    ref = np.percentile(edb, 95)
    # 25/11: video co nhac nen -> nen (floor) = phan vi 8% trong cua so 4 s; noi = cao hon nen 9 dB
    from scipy.ndimage import percentile_filter, uniform_filter1d
    sm = uniform_filter1d(edb, 5)
    floor = percentile_filter(sm, 8, size=400)
    speech = sm > floor + 9
    # lam min: bo lo nho < 40 ms, gop khoang lang < 90 ms
    sp = speech.copy()
    # tim cac doan lang
    pauses = []; i = 0
    while i < n:
        if not sp[i]:
            j = i
            while j < n and not sp[j]: j += 1
            if j - i >= 12 and i > 0 and j < n: pauses.append((i / 100, (j - i) / 100))
            i = j
        else: i += 1
    # am tiet: dinh bao nang luong 300-2500 Hz
    env = np.abs(band(x, 300, 2500))
    k = int(SR * 0.03); env = np.convolve(env, np.ones(k) / k, 'same')[::hop]
    envdb = 20 * np.log10(env + 1e-6)
    fl2 = floor[:len(envdb)] if len(floor) >= len(envdb) else np.pad(floor, (0, len(envdb) - len(floor)), 'edge')
    pk, _ = find_peaks(envdb, distance=9, prominence=4.0, height=fl2 + 10)
    # cum noi = giua 2 khoang nghi >= 120 ms
    bounds = [0.0] + [p[0] for p in pauses] + [n / 100]
    ends = [p[0] for p in pauses] + [n / 100]
    starts = [0.0] + [p[0] + p[1] for p in pauses]
    f0 = f0_track(x, hop * 2)  # 20 ms
    t_f0 = np.arange(len(f0)) * 0.02
    st = 12 * np.log2(f0 / np.nanmedian(f0))
    phr = []
    for a, b in zip(starts, ends):
        if b - a < 0.15: continue
        ns = int(np.sum((pk / 100 >= a) & (pk / 100 < b)))
        m = (t_f0 >= a) & (t_f0 < b) & ~np.isnan(st)
        seg = st[m]
        head = np.nanmean(seg[:max(1, len(seg) // 4)]) if len(seg) > 4 else np.nan
        tail = np.nanmean(seg[-max(1, len(seg) // 4):]) if len(seg) > 4 else np.nan
        phr.append({'t': round(a, 2), 'dur': round(b - a, 2), 'am_tiet': ns, 'toc_do': round(ns / max(b - a, .1), 2),
                    'cao_do_tb': round(float(np.nanmean(seg)), 1) if len(seg) else None,
                    'dau_cum': round(float(head), 1) if head == head else None, 'cuoi_cum': round(float(tail), 1) if tail == tail else None,
                    'bien_do': round(float(np.nanpercentile(seg, 90) - np.nanpercentile(seg, 10)), 1) if len(seg) > 5 else None})
    talk = sum(p['dur'] for p in phr)
    syl = sum(p['am_tiet'] for p in phr)
    pl = np.array([p[1] for p in pauses])
    stv = st[~np.isnan(st)]
    res = {
        'ten': name, 'dai_s': round(n / 100, 1), 'thoi_gian_noi_s': round(talk, 1),
        'am_tiet': syl, 'toc_do_am_tiet_s': round(syl / max(talk, 1), 2), 'toc_do_ca_bai': round(syl / (n / 100), 2),
        'f0_trung_vi_hz': round(float(np.nanmedian(f0)), 1),
        'cao_do_lech_chuan_bc': round(float(np.std(stv)), 2), 'cao_do_p10_p90_bc': round(float(np.percentile(stv, 90) - np.percentile(stv, 10)), 2),
        'so_nghi': len(pauses), 'nghi_moi_phut': round(len(pauses) / (n / 6000), 1),
        'nghi_tb_s': round(float(pl.mean()), 3) if len(pl) else 0,
        'nghi_p25_p50_p75_p90': [round(float(np.percentile(pl, q)), 2) for q in (25, 50, 75, 90)] if len(pl) else [],
        'nghi_ngan_120_250': int(np.sum((pl >= .12) & (pl < .25))), 'nghi_vua_250_500': int(np.sum((pl >= .25) & (pl < .5))), 'nghi_dai_500': int(np.sum(pl >= .5)),
        'cum_am_tiet_tb': round(float(np.mean([p['am_tiet'] for p in phr])), 1),
        'cum_am_tiet_p25_p50_p75': [int(np.percentile([p['am_tiet'] for p in phr], q)) for q in (25, 50, 75)],
        'ha_giong_cuoi_cum_bc': round(float(np.nanmean([p['dau_cum'] - p['cuoi_cum'] for p in phr if p['dau_cum'] is not None and p['cuoi_cum'] is not None])), 2),
        'do_to_lech_chuan_db': round(float(np.std(edb[speech])), 2),
        'cum': phr,
    }
    return res


if __name__ == '__main__':
    r = analyse(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else sys.argv[1])
    json.dump(r, open(sys.argv[1] + '.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in r.items() if k != 'cum'}, ensure_ascii=False, indent=1))
    for p in r['cum'][:40]: print(p)

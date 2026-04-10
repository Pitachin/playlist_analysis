import os
import time
import pandas as pd
from pyncm import apis
from tqdm import tqdm

MUSIC_U = "00DBEC852A10183F4AA739A793BA8F079857268846F63DCFF1C0FE36CF561C34847AF7ED4E4B04F9C4FE2D213733BAADBA3BCEE5196C85D19E373C849074DE21C69707247A28B417CAFCE2ABACB6D99265373D757A84C56ECDD9AF5D54E5F4C9FDAB7948FCB8E679B508200413389EBDCF974814167906AD549E6D73AE1087B40BA02592469DFA0176A62390BF7298020EB494C56BDFA6A16513A38A0C008CFC3AF164FC1ECB55E5507F8A75D34316A526B8468E12E4453EFB7B18E6A25F5B7E8BF90BDD51B33E6FFB9CE38D32475E108AF985D76DE6C03BE072A99EA39D589A55340CE8571A189B4E56223C8AB45B12B9976096E2D53D3E5F8D168E0AE2A236FFE2CCC520D3FD45DB7799F1DB80E31BD1F3344BE304098C10BB1AAAEFE805695031E850DB2C3D2AF94B54313AE1CADDCE31C7F06C190F7288611A3582AAFB81E0EF92B1BBE7D3765374ECD63FCE4079A57969206ED4A41A67E5BADD779C5CC67FA637ADBC3C693B5994BB923BBADED3447053FE2CC590EE2E4BEDAD8CCC27D859CBE00B1AECB796CFC831A63F0940501BB6AD0F1424ABB22F35581A0E85F6C28B"
PLAYLIST_ID = "2584370810"
OUTPUT_PATH = "my_music_dataset.csv"

def init_login():
    """驗證身份證"""
    apis.login.LoginViaCookie(f"MUSIC_U={MUSIC_U}")
    user_info = apis.login.GetCurrentLoginInfo()
    if 'profile' in user_info:
        print(f">>> 成功認證！用戶名：{user_info['profile']['nickname']}")
        return True
    return False

def run():
    if not init_login():
        print(">>> 登入失敗，請檢查 MUSIC_U")
        return

    # 1. 拿歌單列表
    pl_detail = apis.playlist.GetPlaylistDetails(PLAYLIST_ID)
    tracks = pl_detail['playlist']['trackIds']
    id_to_time = {str(t['id']): t['at'] for t in tracks}
    song_ids = list(id_to_time.keys())
    
    print(f">>> 發現 {len(song_ids)} 首歌，開始搬運...")
    
    all_data = []

    # 2. 爬取循環 (tqdm 會顯示進度條)
    for sid in tqdm(song_ids):
        try:
            # 獲取歌名和歌手
            detail = apis.track.GetTrackDetail(sid)
            name = detail['songs'][0]['name']
            artist = detail['songs'][0]['ar'][0]['name']
            
            # 獲取歌詞
            lrc_info = apis.track.GetTrackLyrics(sid)
            lyric = lrc_info.get('lrc', {}).get('lyric', '[純音樂]')
            
            all_data.append({
                'song_id': sid,
                'name': name,
                'artist': artist,
                'add_time': id_to_time.get(sid),
                'lyric': lyric
            })
            
            # 禮貌延遲 0.3 秒，MacBook 就不會被封鎖
            time.sleep(0.3)
            
            # 每 10 首保存一次，防止程序中斷
            if len(all_data) % 10 == 0:
                pd.DataFrame(all_data).to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
                
        except Exception:
            continue

    # 最終儲存
    pd.DataFrame(all_data).to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    print(f"\n>>> 全部完成！數據保存在 {OUTPUT_PATH}")

if __name__ == "__main__":
    run()
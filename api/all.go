package main

import (
	"net/http"
	"strings"
	"sync"
)

func all(w http.ResponseWriter, r *http.Request) {
	wg := sync.WaitGroup{}
	wg.Add(3)

	data := map[string]any{}
	lock := sync.Mutex{}
	var err0 error

	go func() {
		defer wg.Done()

		hopeData, err := hopeData()
		if err != nil {
			err0 = err
			return
		}

		lock.Lock()
		defer lock.Unlock()
		data["hope"] = hopeData
	}()

	go func() {
		defer wg.Done()

		chainId := r.URL.Query().Get("chain_id")
		pairAddr := r.URL.Query().Get("pair_address")

		if chainId == "" {
			chainId = "ethereum"
		}

		if pairAddr == "" {
			pairAddr = "0xa9ad6a54459635a62e883dc99861c1a69cf2c5b3"   // LT / USDT
			pairAddr += ",0x1c2ad915cd67284cdbc04507b11980797cf51b22" // HOPE / USDT
			pairAddr += ",0x11b815efb8f581194ae79006d24e0d814b7697f6" // WETH / USDT
			pairAddr += ",0x9db9e0e53058c89e5b94e29621a205198648425b" // WBTC / USDT
		}

		dexData, err := dexScreenerData(chainId, pairAddr)
		if err != nil {
			err0 = err
			return
		}

		lock.Lock()
		defer lock.Unlock()
		data["dex"] = dexData
	}()

	go func() {
		defer wg.Done()

		quote := r.URL.Query().Get("quote")
		base := r.URL.Query().Get("base")

		if quote == "" {
			quote = "USD"
		}

		if base == "" {
			base = "BTC,ETH,TON,FIL"
		}
		bases := strings.Split(base, ",")
		bases = Map(bases, strings.ToLower)

		bitcomData, err := bitcomData(bases, quote)
		if err != nil {
			err0 = err
			return
		}

		lock.Lock()
		defer lock.Unlock()
		data["bitcom"] = bitcomData
	}()

	wg.Wait()

	if err0 != nil {
		replyErr(w, err0)
		return
	}

	reply(w, &Res{Data: data})
}

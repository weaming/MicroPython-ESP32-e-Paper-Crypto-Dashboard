package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
)

type DexScreenerRes struct {
	Pairs []*Pair `json:"pairs"`
	Pair  *Pair   `json:"pair"`
}

type Pair struct {
	ChainID     string   `json:"chainId"`
	DexID       string   `json:"dexId"`
	URL         string   `json:"url"`
	PairAddress string   `json:"pairAddress"`
	Labels      []string `json:"labels,omitempty"`
	BaseToken   struct {
		Address string `json:"address"`
		Name    string `json:"name"`
		Symbol  string `json:"symbol"`
	} `json:"baseToken"`
	QuoteToken struct {
		Address string `json:"address"`
		Name    string `json:"name"`
		Symbol  string `json:"symbol"`
	} `json:"quoteToken"`
	PriceNative string `json:"priceNative"`
	PriceUsd    string `json:"priceUsd"`
}

func dexscreener(w http.ResponseWriter, r *http.Request) {
	chainId := r.URL.Query().Get("chain_id")
	pairAddr := r.URL.Query().Get("pair_address")

	if chainId == "" {
		chainId = "ethereum"
	}

	if pairAddr == "" {
		pairAddr = "0xa9ad6a54459635a62e883dc99861c1a69cf2c5b3" // LT / USDT
		// pairAddr += ",0x1c2ad915cd67284cdbc04507b11980797cf51b22" // HOPE / USDT
		// pairAddr += ",0x11b815efb8f581194ae79006d24e0d814b7697f6" // WETH / USDT
		// pairAddr += ",0x9db9e0e53058c89e5b94e29621a205198648425b" // WBTC / USDT
	}

	data, err := dexScreenerData(chainId, pairAddr)
	if err != nil {
		replyErr(w, err)
		return
	}
	reply(w, &Res{Data: data})
}

func dexScreenerData(chainId, pairAddr string) (any, error) {
	url := fmt.Sprintf("https://api.dexscreener.com/latest/dex/pairs/%s/%s", chainId, pairAddr)
	log.Println(chainId, pairAddr, url)

	res, err := client.Get(url)
	if err != nil {
		return nil, err
	}

	data, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	v := DexScreenerRes{}
	err = json.Unmarshal(data, &v)
	if err != nil {
		return nil, err
	}

	ret := map[string]any{}
	for _, x := range v.Pairs {
		pair := x.BaseToken.Symbol + "-" + x.QuoteToken.Symbol
		ret[pair] = x.PriceUsd
	}

	return ret, nil
}

package main

import (
	"encoding/json"
	"io"
	"log"
	"net/http"

	"github.com/shopspring/decimal"
)

const hopePlaces = 5

type HopeRes struct {
	HopePriceList  [][]float64     `json:"hope_price_list"`
	BtcIndexPrice  decimal.Decimal `json:"btc_index_price"`
	EthIndexPrice  decimal.Decimal `json:"eth_index_price"`
	HopeIndexPrice decimal.Decimal `json:"hope_index_price"`
}

func hope(w http.ResponseWriter, r *http.Request) {
	data, err := hopeData()
	if err != nil {
		replyErr(w, err)
		return
	}
	reply(w, &Res{Data: data})
}

func hopeData() (any, error) {
	url := "https://hope.money/hope-index-stage-2?period=3600"
	log.Println(url)

	res, err := client.Get(url)
	if err != nil {
		return nil, err
	}

	data, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	v := HopeRes{}
	err = json.Unmarshal(data, &v)
	if err != nil {
		return nil, err
	}

	return map[string]any{
		"btc":  v.BtcIndexPrice.StringFixed(hopePlaces),
		"eth":  v.EthIndexPrice.StringFixed(hopePlaces),
		"hope": v.HopeIndexPrice.StringFixed(hopePlaces),
		"ts":   v.HopePriceList[1][1],
	}, nil
}

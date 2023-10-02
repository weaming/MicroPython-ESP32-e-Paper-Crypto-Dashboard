package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"strings"
)

type BitcomRes struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
	Data    []struct {
		IndexName       string `json:"index_name"`
		IndexPrice      string `json:"index_price"`
		PairDisplayName string `json:"pair_display_name"`
	} `json:"data"`
}

func bitcom(w http.ResponseWriter, r *http.Request) {
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

	data, err := bitcomData(bases, quote)
	if err != nil {
		replyErr(w, err)
		return
	}
	reply(w, &Res{Data: data})
}

func bitcomData(bases []string, quote string) (any, error) {
	url := fmt.Sprintf("https://api.bit.com/um/v1/index_price?quote_currency=%s", quote)
	log.Println(bases, quote, url)

	res, err := client.Get(url)
	if err != nil {
		return nil, err
	}

	data, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}

	v := BitcomRes{}
	err = json.Unmarshal(data, &v)
	if err != nil {
		return nil, err
	}

	ret := map[string]any{}
	for _, x := range v.Data {
		k := strings.ToLower(strings.SplitN(x.IndexName, "-", 2)[0])
		if In(bases, k) {
			ret[k] = x.IndexPrice
		}
	}

	return ret, nil
}

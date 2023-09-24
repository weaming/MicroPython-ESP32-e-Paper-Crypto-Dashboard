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
		base = "BTC,ETH"
	}
	bases := strings.Split(base, ",")
	bases = Map(bases, strings.ToLower)

	log.Println(bases, quote)
	res, err := client.Get(fmt.Sprintf("https://api.bit.com/um/v1/index_price?quote_currency=%s", quote))
	if err != nil {
		replyErr(w, err)
		return
	}

	data, err := io.ReadAll(res.Body)
	if err != nil {
		replyErr(w, err)
		return
	}

	v := BitcomRes{}
	err = json.Unmarshal(data, &v)
	if err != nil {
		replyErr(w, err)
		return
	}

	ret := map[string]any{}
	for _, x := range v.Data {
		k := strings.ToLower(strings.SplitN(x.IndexName, "-", 2)[0])
		if In(bases, k) {
			ret[k] = x.IndexPrice
		}
	}
	reply(w, &Res{Data: ret})
}

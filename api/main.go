package main

import (
	"flag"
	"log"
	"net/http"
	"time"
)

var (
	client = NewHTTPClient(time.Second * 5)
	ok     = 0
	fail   = 1
)

type Res struct {
	Code  int    `json:"code"`
	Error string `json:"error"`
	Data  any    `json:"data"`
}

func main() {
	listen := flag.String("l", ":8080", "listen host:port")
	flag.Parse()

	http.HandleFunc("/bitcom/index", bitcom)
	http.HandleFunc("/hope/index", hope)
	http.HandleFunc("/dexscreener/pairs", dexscreener)
	http.HandleFunc("/all", all)

	log.Printf("listen on %v", *listen)
	err := http.ListenAndServe(*listen, nil)
	if err != nil {
		panic(err)
	}
}

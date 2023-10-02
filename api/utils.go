package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"
)

func replyErr(w http.ResponseWriter, err error) {
	reply(w, &Res{Code: fail, Error: err.Error()})
}

func reply(w http.ResponseWriter, r *Res) {
	bs, err := json.Marshal(r)
	if err != nil {
		log.Printf("marshal err: %v", err)
		bs = []byte(err.Error())
	}
	_, err = w.Write(bs)
	if err != nil {
		log.Printf("write err: %v", err)
	}
}

func replyBytes(w http.ResponseWriter, bs []byte) {
	_, err := w.Write(bs)
	if err != nil {
		log.Printf("write err: %v", err)
	}
}

func NewHTTPClient(timeout time.Duration) *http.Client {
	tr := &http.Transport{
		MaxIdleConnsPerHost: 1024,
		MaxIdleConns:        0,
	}
	return &http.Client{
		Transport: tr,
		Timeout:   timeout * time.Second,
	}
}

func str(v any) string {
	return fmt.Sprintf("%v", v)
}

package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"pricing/internal/config"
	"pricing/internal/pricing"
	"pricing/internal/structs"
)

func main() {
	if len(os.Args) != 2 {
		log.Fatalf("usage: %s <config file>", os.Args[0])
	}

	cfg := config.LoadConfig(os.Args[1])

	pricingFuncs := make(map[string]pricing.PricingFunc)

	for eventId, eventCfg := range cfg.Events {
		pricingFuncs[eventId] = pricing.NewPricingFunction(&eventCfg)
	}

	mux := http.NewServeMux()

	mux.HandleFunc("POST /price-cart", func(w http.ResponseWriter, req *http.Request) {
		var request structs.PricingRequest
		err := json.NewDecoder(req.Body).Decode(&request)
		if err != nil {
			http.Error(w, http.StatusText(http.StatusUnprocessableEntity), http.StatusUnprocessableEntity)
			return
		}

		pricingFunc, funcOk := pricingFuncs[request.CartData.EventId]
		if !funcOk {
			log.Printf("no event: %v", request.CartData.EventId)
			http.NotFound(w, req)
			return
		}

		result, err := pricingFunc(&request)
		if err != nil {
			log.Printf("error during pricing: %v", err)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}

		err = json.NewEncoder(w).Encode(result)
		if err != nil {
			log.Printf("error marshaling pricing result: %v", err)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
		}
	})

	server := http.Server{
		Addr:    "0.0.0.0:8000",
		Handler: mux,
	}
	log.Printf("listening on %v", server.Addr)
	server.ListenAndServe()
}

package pricing

import (
	"pricing/internal/config"
	"pricing/internal/structs"
)

type PricingFunc func(req *structs.PricingRequest) (*structs.PricingResult, error)

func NewPricingFunction(eventCfg *config.EventConfig) PricingFunc {
	funcs := []PricingFunc{
		NewDefaultPricingFunc(eventCfg),
	}

	if eventCfg.ScriptDir != "" {
		scripts := GetPricingScripts(eventCfg.ScriptDir)
		funcs = append(funcs, scripts...)
	}

	return func(req *structs.PricingRequest) (*structs.PricingResult, error) {
		return priceCart(funcs, req)
	}
}

func priceCart(funcs []PricingFunc, req *structs.PricingRequest) (*structs.PricingResult, error) {
	bind := makeBind(req)
	res := &structs.PricingResult{
		Currency: req.Currency,
	}

	var err error

	for _, f := range funcs {
		res, err = bind(res, err, f)
	}

	return res, err
}

func makeBind(initialReq *structs.PricingRequest) func(res *structs.PricingResult, err error, pricingFunc PricingFunc) (*structs.PricingResult, error) {
	return func(res *structs.PricingResult, err error, pricingFunc PricingFunc) (*structs.PricingResult, error) {
		if err != nil {
			return nil, err
		}

		req := structs.PricingRequest{
			Currency:   res.Currency,
			CartData:   initialReq.CartData,
			PrevResult: res,
		}

		return pricingFunc(&req)
	}
}

package pricing

import (
	"fmt"
	"pricing/internal/config"
	"pricing/internal/structs"

	"github.com/Open-Event-Systems/gonjaexpr/logic"
	"github.com/nikolalohinski/gonja/v2/exec"
)

type defaultPricer struct {
	config *config.EventConfig
	req    *structs.PricingRequest
	ctx    *exec.Context
}

// Get the default pricing function.
func NewDefaultPricingFunc(config *config.EventConfig) PricingFunc {
	pricingFunc := func(req *structs.PricingRequest) (*structs.PricingResult, error) {
		ctx := exec.NewContext(map[string]any{
			"currency": req.Currency,
			"event_id": req.CartData.EventId,
			"meta":     req.CartData.Meta,
		})

		pricer := defaultPricer{
			config: config,
			req:    req,
			ctx:    ctx,
		}

		res, err := pricer.price()
		if err != nil {
			return nil, err
		}

		return res, nil
	}

	return pricingFunc
}

func (p *defaultPricer) price() (*structs.PricingResult, error) {
	result := structs.PricingResult{
		Currency:      p.req.Currency,
		Registrations: []structs.PricingResultRegistration{},
	}
	for _, reg := range p.req.CartData.Registrations {
		regRes, err := p.handleRegistration(&reg)
		if err != nil {
			return nil, err
		}
		result.Registrations = append(result.Registrations, *regRes)
		result.TotalPrice += regRes.TotalPrice
	}

	return &result, nil
}

func (p *defaultPricer) handleRegistration(reg *structs.CartRegistration) (*structs.PricingResultRegistration, error) {
	regCtx := p.ctx.Inherit()
	regCtx.Set("registration", map[string]any{
		"id":   reg.Id,
		"old":  reg.Old,
		"new":  reg.New,
		"meta": reg.Meta,
	})

	regRes := structs.PricingResultRegistration{
		Id:        reg.Id,
		Name:      getDisplayName(regCtx, p.config),
		LineItems: []structs.LineItem{},
	}

	for _, lineItemCfg := range p.config.LineItems {
		liRes, err := p.handleLineItem(regCtx, &lineItemCfg)
		if err != nil {
			return nil, err
		}
		if liRes != nil {
			regRes.LineItems = append(regRes.LineItems, *liRes)
			regRes.TotalPrice += liRes.TotalPrice
		}
	}

	return &regRes, nil
}

func (p *defaultPricer) handleLineItem(regCtx *exec.Context, li *config.LineItemConfig) (*structs.LineItem, error) {
	cond, err := li.When.Evaluate(regCtx)
	if err != nil {
		return nil, err
	}

	if !logic.ToBoolean(cond) {
		return nil, nil
	}

	liRes := structs.LineItem{
		Id:          li.Id,
		Name:        li.Name,
		Description: li.Description,
		Price:       li.Price,
		Modifiers:   []structs.Modifier{},
		TotalPrice:  li.Price,
	}

	for _, m := range li.Modifiers {
		mRes, err := p.handleModifier(regCtx, &m)
		if err != nil {
			return nil, err
		}
		if mRes != nil {
			liRes.Modifiers = append(liRes.Modifiers, *mRes)
			liRes.TotalPrice += m.Amount
		}
	}

	return &liRes, nil
}

func (p *defaultPricer) handleModifier(regCtx *exec.Context, m *config.ModifierConfig) (*structs.Modifier, error) {
	cond, err := m.When.Evaluate(regCtx)
	if err != nil {
		return nil, err
	}

	if !logic.ToBoolean(cond) {
		return nil, nil
	}

	return &structs.Modifier{
		Id:     m.Id,
		Name:   m.Name,
		Amount: m.Amount,
	}, nil
}

func getDisplayName(regCtx *exec.Context, cfg *config.EventConfig) string {
	displayName, err := cfg.DisplayName.Evaluate(regCtx)
	if err != nil {
		return ""
	}

	return fmt.Sprintf("%v", displayName)
}

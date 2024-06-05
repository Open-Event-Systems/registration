package pricing

import (
	"pricing/internal/config"
	"pricing/internal/structs"
	"reflect"
	"testing"
)

func TestScripts(t *testing.T) {
	cfg := config.LoadConfig("default_test.yml")
	cfg.ScriptDir = "../../scripts"
	pricingFunc := NewPricingFunction(cfg)

	req := structs.PricingRequest{
		Currency: "USD",
		CartData: structs.CartData{
			EventId: "example-event",
			Registrations: []structs.CartRegistration{{
				Id: "reg1",
				Old: structs.JSON{
					"options": []string{},
				},
				New: structs.JSON{
					"options":    []string{"basic"},
					"first_name": "Reg",
					"last_name":  "Test",
				},
			}},
		},
		PrevResult: &structs.PricingResult{
			Currency: "USD",
			Registrations: []structs.PricingResultRegistration{{
				Id:   "reg1",
				Name: "Reg",
				LineItems: []structs.LineItem{{
					Id:         "item",
					Name:       "Item",
					Price:      200,
					TotalPrice: 200,
				}},
				TotalPrice: 200,
			}},
			TotalPrice: 200,
		},
	}

	res, err := pricingFunc(&req)
	if err != nil {
		panic(err)
	}

	expected := structs.PricingResult{
		Currency: "USD",
		Registrations: []structs.PricingResultRegistration{{
			Id:   "reg1",
			Name: "Reg", // hack...
			LineItems: []structs.LineItem{{
				Id:    "basic",
				Name:  "Basic Registration",
				Description: "Basic registration.",
				Price: 5000,
				Modifiers: []structs.Modifier{{
					Id:     "discount",
					Name:   "Discount",
					Amount: -100,
				}},
				TotalPrice: 4900,
			}},
			TotalPrice: 4900,
		}},
		TotalPrice: 4900,
	}

	if !reflect.DeepEqual(*res, expected) {
		t.Errorf("expected %+v, got %+v", expected, *res)
	}
}

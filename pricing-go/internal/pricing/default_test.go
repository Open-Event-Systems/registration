package pricing

import (
	"pricing/internal/config"
	"pricing/internal/structs"
	"reflect"
	"testing"
)

func TestDefaultPricing(t *testing.T) {
	cfg := config.LoadConfig("default_test.yml")
	pricingFunc := NewDefaultPricingFunc(cfg)

	t.Run("basic", func(t *testing.T) {
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
						"first_name": "Example",
						"last_name":  "Reg",
					},
				}},
			},
		}

		res, err := pricingFunc(&req)
		if err != nil {
			panic(err)
		}

		expected := structs.PricingResult{
			Currency:   "USD",
			TotalPrice: 5000,
			Registrations: []structs.PricingResultRegistration{{
				Id:   "reg1",
				Name: "Example",
				LineItems: []structs.LineItem{{
					Id:          "basic",
					Name:        "Basic Registration",
					Description: "Basic registration.",
					Price:       5000,
					Modifiers: []structs.Modifier{},
					TotalPrice:  5000,
				}},
				TotalPrice: 5000,
			}},
		}

		if !reflect.DeepEqual(*res, expected) {
			t.Fatalf("expected %+v, got %+v", expected, *res)
		}
	})

	t.Run("early bird", func(t *testing.T) {
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
						"first_name": "Example",
						"last_name":  "Reg",
						"early_bird": true,
					},
				}},
			},
		}

		res, err := pricingFunc(&req)
		if err != nil {
			panic(err)
		}

		expected := structs.PricingResult{
			Currency:   "USD",
			TotalPrice: 4000,
			Registrations: []structs.PricingResultRegistration{{
				Id:   "reg1",
				Name: "Example",
				LineItems: []structs.LineItem{{
					Id:          "basic",
					Name:        "Basic Registration",
					Description: "Basic registration.",
					Price:       5000,
					Modifiers: []structs.Modifier{{
						Id:     "early-bird",
						Name:   "Early Bird",
						Amount: -1000,
					}},
					TotalPrice: 4000,
				}},
				TotalPrice: 4000,
			}},
		}

		if !reflect.DeepEqual(*res, expected) {
			t.Fatalf("expected %+v, got %+v", expected, *res)
		}
	})

	t.Run("sponsor", func(t *testing.T) {
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
						"options":    []string{"basic", "sponsor"},
						"first_name": "Example",
						"last_name":  "Reg",
						"early_bird": true,
					},
				}},
			},
		}

		res, err := pricingFunc(&req)
		if err != nil {
			panic(err)
		}

		expected := structs.PricingResult{
			Currency:   "USD",
			TotalPrice: 6500,
			Registrations: []structs.PricingResultRegistration{{
				Id:   "reg1",
				Name: "Example",
				LineItems: []structs.LineItem{{
					Id:          "basic",
					Name:        "Basic Registration",
					Description: "Basic registration.",
					Price:       5000,
					Modifiers: []structs.Modifier{{
						Id:     "early-bird",
						Name:   "Early Bird",
						Amount: -1000,
					}},
					TotalPrice: 4000,
				}, {
					Id:          "sponsor",
					Name:        "Sponsor Upgrade",
					Description: "Sponsor level upgrade.",
					Price:       2500,
					Modifiers: []structs.Modifier{},
					TotalPrice: 2500,
				}},
				TotalPrice: 6500,
			}},
		}

		if !reflect.DeepEqual(*res, expected) {
			t.Fatalf("expected %+v, got %+v", expected, *res)
		}
	})
}

package structs

type Modifier struct {
	Id     string `json:"id,omitempty"`
	Name   string `json:"name,omitempty"`
	Amount int    `json:"amount"`
}

type LineItem struct {
	Id          string     `json:"id,omitempty"`
	Name        string     `json:"name"`
	Description string     `json:"description,omitempty"`
	Price       int        `json:"price"`
	TotalPrice  int        `json:"total_price"`
	Modifiers   []Modifier `json:"modifiers,omitempty"`
}

type PricingResultRegistration struct {
	Id         string     `json:"id"`
	Name       string     `json:"name"`
	TotalPrice int        `json:"total_price"`
	LineItems  []LineItem `json:"line_items"`
}

type PricingResult struct {
	Currency      string                      `json:"currency"`
	TotalPrice    int                         `json:"total_price"`
	Registrations []PricingResultRegistration `json:"registrations"`
}

type JSON map[string]any

type CartRegistration struct {
	Id   string `json:"id"`
	Old  JSON   `json:"old"`
	New  JSON   `json:"new"`
	Meta JSON   `json:"meta"`
}

type CartData struct {
	EventId       string             `json:"event_id"`
	Registrations []CartRegistration `json:"registrations"`
	Meta          JSON               `json:"meta"`
}

type PricingRequest struct {
	Currency   string         `json:"currency"`
	CartData   CartData       `json:"cart_data"`
	PrevResult *PricingResult `json:"prev_result"`
}

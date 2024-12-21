package api

import (
	"context"
	"time"
)

type Waiter struct {
	delay int
}

func (w *Waiter) Wait(ctx context.Context) {
	curDelay := w.delay

	if curDelay < 2 {
		curDelay = 2
	}

	w.delay = curDelay * 2

	if w.delay > 60 {
		w.delay = 60
	}

	wait, cancel := context.WithTimeout(ctx, time.Duration(curDelay)*time.Second)
	defer cancel()

	<-wait.Done()
}

func (w *Waiter) Reset() {
	w.delay = 2
}
